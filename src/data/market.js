/**
 * Market data access and the indicator maths the course teaches.
 *
 * Prices come from /api/quote, a thin server-side proxy for Yahoo Finance
 * (the browser cannot call Yahoo directly, since it sends no CORS headers).
 * Everything below that is computed here in the browser, so the arithmetic is
 * inspectable rather than hidden behind a service.
 */

export async function fetchQuote(symbol, range = '1y') {
  const res = await fetch(`/api/quote?symbol=${encodeURIComponent(symbol)}&range=${range}`)
  let body = null
  try {
    body = await res.json()
  } catch {
    throw new Error('The market data service returned something unreadable.')
  }
  if (!res.ok) throw new Error(body?.error ?? 'Could not load that ticker.')
  return body
}

/** Simple moving average. Returns an array aligned to `values`, null before period. */
export function sma(values, period) {
  const out = new Array(values.length).fill(null)
  let sum = 0
  for (let i = 0; i < values.length; i++) {
    sum += values[i]
    if (i >= period) sum -= values[i - period]
    if (i >= period - 1) out[i] = sum / period
  }
  return out
}

/**
 * Relative Strength Index, Wilder's smoothing, default 14 periods.
 * Returns 0..100, null until there is enough history.
 */
export function rsi(values, period = 14) {
  const out = new Array(values.length).fill(null)
  if (values.length <= period) return out

  let gain = 0
  let loss = 0
  for (let i = 1; i <= period; i++) {
    const change = values[i] - values[i - 1]
    if (change >= 0) gain += change
    else loss -= change
  }
  gain /= period
  loss /= period

  const rsiAt = (g, l) => (l === 0 ? 100 : 100 - 100 / (1 + g / l))
  out[period] = rsiAt(gain, loss)

  for (let i = period + 1; i < values.length; i++) {
    const change = values[i] - values[i - 1]
    const up = change >= 0 ? change : 0
    const down = change < 0 ? -change : 0
    gain = (gain * (period - 1) + up) / period
    loss = (loss * (period - 1) + down) / period
    out[i] = rsiAt(gain, loss)
  }
  return out
}

/** Log returns between consecutive closes. */
export function logReturns(values) {
  const out = []
  for (let i = 1; i < values.length; i++) {
    if (values[i - 1] > 0 && values[i] > 0) out.push(Math.log(values[i] / values[i - 1]))
  }
  return out
}

/**
 * Annualised drift and volatility from a price series.
 * `periodsPerYear` is 252 for daily bars, 52 for weekly, 12 for monthly.
 */
export function annualisedStats(values, periodsPerYear = 252) {
  const r = logReturns(values)
  if (r.length < 2) return { drift: NaN, vol: NaN, samples: r.length }

  const mean = r.reduce((s, x) => s + x, 0) / r.length
  const variance = r.reduce((s, x) => s + (x - mean) ** 2, 0) / (r.length - 1)
  const sd = Math.sqrt(variance)

  return {
    drift: mean * periodsPerYear,
    vol: sd * Math.sqrt(periodsPerYear),
    samples: r.length,
  }
}

/** Largest peak-to-trough fall in the series, as a positive percentage. */
export function maxDrawdown(values) {
  let peak = -Infinity
  let worst = 0
  for (const v of values) {
    if (v > peak) peak = v
    const dd = (peak - v) / peak
    if (dd > worst) worst = dd
  }
  return worst * 100
}

export const PERIODS_PER_YEAR = { '1d': 252, '1wk': 52, '1mo': 12 }
