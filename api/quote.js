/**
 * GET /api/quote?symbol=AAPL&range=1y
 *
 * Server-side proxy for Yahoo Finance chart data.
 *
 * This exists because Yahoo's endpoints send no CORS headers, so a browser
 * cannot call them directly from finlitpro.org. Running the fetch here also
 * keeps the site's only network dependency in one auditable place. No API key
 * is involved: the endpoint is public, we simply cannot reach it from the page.
 *
 * Returns a normalised, trimmed payload rather than Yahoo's raw envelope, so
 * the front end never has to know their schema.
 */

// Letters, digits, dot, dash, caret (indices like ^GSPC), equals (futures).
// Anything else is rejected rather than interpolated into an outbound URL.
const SYMBOL_RE = /^[A-Za-z0-9.\-^=]{1,12}$/

const RANGES = {
  '1mo': { range: '1mo', interval: '1d' },
  '6mo': { range: '6mo', interval: '1d' },
  '1y': { range: '1y', interval: '1d' },
  '5y': { range: '5y', interval: '1wk' },
  max: { range: 'max', interval: '1mo' },
}

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET')
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const symbol = String(req.query.symbol ?? '').trim().toUpperCase()
  const rangeKey = String(req.query.range ?? '1y')

  if (!SYMBOL_RE.test(symbol)) {
    return res.status(400).json({
      error: 'Invalid ticker. Use letters, digits, dots or dashes, up to 12 characters.',
    })
  }

  const { range, interval } = RANGES[rangeKey] ?? RANGES['1y']
  const url =
    `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}` +
    `?range=${range}&interval=${interval}`

  try {
    const upstream = await fetch(url, {
      headers: {
        // Yahoo rejects requests with no browser-like agent.
        'User-Agent':
          'Mozilla/5.0 (compatible; StockGuide/1.0; +https://www.finlitpro.org)',
        Accept: 'application/json',
      },
      signal: AbortSignal.timeout(9000),
    })

    if (!upstream.ok) {
      return res
        .status(upstream.status === 404 ? 404 : 502)
        .json({ error: `No data for "${symbol}". Check the ticker and try again.` })
    }

    const json = await upstream.json()
    const result = json?.chart?.result?.[0]
    if (!result?.timestamp?.length) {
      return res.status(404).json({ error: `No price history returned for "${symbol}".` })
    }

    const meta = result.meta ?? {}
    const closes = result.indicators?.quote?.[0]?.close ?? []
    const volumes = result.indicators?.quote?.[0]?.volume ?? []

    // Yahoo pads gaps with nulls. Drop them so the client never charts a hole.
    const points = []
    for (let i = 0; i < result.timestamp.length; i++) {
      const c = closes[i]
      if (typeof c !== 'number' || !Number.isFinite(c)) continue
      points.push({
        t: result.timestamp[i] * 1000,
        c,
        v: Number.isFinite(volumes[i]) ? volumes[i] : null,
      })
    }

    if (points.length < 2) {
      return res.status(404).json({ error: `Not enough price history for "${symbol}".` })
    }

    // Cache at the edge: quotes do not need to be second-accurate for a course,
    // and this keeps us well clear of Yahoo's rate limiting.
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600')

    return res.status(200).json({
      symbol: meta.symbol ?? symbol,
      name: meta.longName ?? meta.shortName ?? symbol,
      currency: meta.currency ?? 'USD',
      exchange: meta.fullExchangeName ?? meta.exchangeName ?? null,
      price: meta.regularMarketPrice ?? points[points.length - 1].c,
      // Yahoo's `chartPreviousClose` is the close BEFORE the requested range,
      // not the prior trading day, so it is useless for a day-change figure
      // (on a 1y range it makes today look up 50%). The previous bar's close
      // is the real comparison; the range-start close is returned separately
      // for anyone who wants the period return.
      previousClose: points[points.length - 2].c,
      rangeStartClose: meta.chartPreviousClose ?? null,
      fiftyTwoWeekHigh: meta.fiftyTwoWeekHigh ?? null,
      fiftyTwoWeekLow: meta.fiftyTwoWeekLow ?? null,
      range,
      interval,
      points,
    })
  } catch (err) {
    const timedOut = err?.name === 'TimeoutError' || err?.name === 'AbortError'
    return res.status(timedOut ? 504 : 502).json({
      error: timedOut
        ? 'The market data provider took too long to respond. Try again.'
        : 'Could not reach the market data provider.',
    })
  }
}
