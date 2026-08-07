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

// Each range picks the coarsest interval that still gives enough bars to draw
// the indicators. A US session is 6.5 hours, so 5m gives 78 bars in a day and
// 15m gives 130 across five days: enough for a 50-period average to appear.
const RANGES = {
  '1d': { range: '1d', interval: '5m' },
  '5d': { range: '5d', interval: '15m' },
  '1mo': { range: '1mo', interval: '1d' },
  '6mo': { range: '6mo', interval: '1d' },
  '1y': { range: '1y', interval: '1d' },
  '5y': { range: '5y', interval: '1wk' },
  max: { range: 'max', interval: '1mo' },
}

// Intervals measured in minutes, as opposed to 1d / 1wk / 1mo.
const INTRADAY = new Set(['1m', '2m', '5m', '15m', '30m', '60m', '90m'])

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
          'Mozilla/5.0 (compatible; FinLitPro/1.0; +https://www.finlitpro.org)',
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
    const q = result.indicators?.quote?.[0] ?? {}
    const closes = q.close ?? []
    const opens = q.open ?? []
    const highs = q.high ?? []
    const lows = q.low ?? []
    const volumes = q.volume ?? []

    // Yahoo pads gaps with nulls. Drop them so the client never charts a hole.
    // Full OHLC is returned so the chart can draw candlesticks; open/high/low
    // fall back to the close when a bar is partially missing, which keeps the
    // candle degenerate rather than absent.
    const points = []
    for (let i = 0; i < result.timestamp.length; i++) {
      const c = closes[i]
      if (typeof c !== 'number' || !Number.isFinite(c)) continue
      const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : c)
      points.push({
        t: result.timestamp[i] * 1000,
        o: num(opens[i]),
        h: num(highs[i]),
        l: num(lows[i]),
        c,
        v: Number.isFinite(volumes[i]) ? volumes[i] : null,
      })
    }

    if (points.length < 2) {
      return res.status(404).json({ error: `Not enough price history for "${symbol}".` })
    }

    // Cache at the edge: quotes do not need to be second-accurate for a course,
    // and this keeps us well clear of Yahoo's rate limiting. Intraday ranges
    // get a shorter window, since a 1D chart that is five minutes stale is
    // visibly wrong in a way a 1Y chart is not.
    const intraday = INTRADAY.has(interval)
    res.setHeader(
      'Cache-Control',
      intraday ? 's-maxage=60, stale-while-revalidate=120' : 's-maxage=300, stale-while-revalidate=600'
    )

    return res.status(200).json({
      symbol: meta.symbol ?? symbol,
      name: meta.longName ?? meta.shortName ?? symbol,
      currency: meta.currency ?? 'USD',
      exchange: meta.fullExchangeName ?? meta.exchangeName ?? null,
      price: meta.regularMarketPrice ?? points[points.length - 1].c,
      // What "the previous close" means depends on the bar size.
      //
      // On daily bars the previous bar IS the previous trading day, so that is
      // the comparison. Yahoo's own `chartPreviousClose` is the close before
      // the whole requested range, which on a 1y chart makes today look up 50%.
      //
      // On intraday bars the previous bar is only minutes earlier, which is not
      // a day change at all. The right number there is `previousClose`, which
      // is the prior session's close whatever range was asked for. It is NOT
      // `chartPreviousClose`: that is the close before the whole window, so on
      // a 5d range it sits five days back and reports the week's move as the
      // day's. The range-start close is returned separately either way.
      previousClose: intraday
        ? (meta.previousClose ?? meta.chartPreviousClose ?? points[0].c)
        : points[points.length - 2].c,
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
