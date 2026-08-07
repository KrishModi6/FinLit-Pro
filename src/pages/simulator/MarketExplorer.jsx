import { useCallback, useEffect, useMemo, useState } from 'react'
import { Flag, LessonLink, Panel, Stat, money, num, pct } from '../../components/ui/SimUI.jsx'
import AdvancedChart from '../../components/ui/AdvancedChart.jsx'
import {
  PERIODS_PER_YEAR,
  annualisedStats,
  fetchQuote,
  isIntraday,
  maxDrawdown,
  rsi,
} from '../../data/market.js'
import { getTool } from '../../data/simulator.js'

const RANGES = [
  ['1d', '1D'],
  ['5d', '5D'],
  ['1mo', '1M'],
  ['6mo', '6M'],
  ['1y', '1Y'],
  ['5y', '5Y'],
  ['max', 'Max'],
]

export default function MarketExplorer() {
  const tool = getTool('market')
  const [input, setInput] = useState('AAPL')
  const [symbol, setSymbol] = useState('AAPL')
  const [range, setRange] = useState('1y')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = useCallback(async (sym, rng) => {
    setLoading(true)
    setError(null)
    try {
      setData(await fetchQuote(sym, rng))
    } catch (e) {
      setData(null)
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load(symbol, range)
  }, [symbol, range, load])

  const analysis = useMemo(() => {
    if (!data?.points?.length) return null
    const closes = data.points.map((p) => p.c)
    const per = PERIODS_PER_YEAR[data.interval] ?? 252
    const { drift, vol } = annualisedStats(closes, per)
    const rsiSeries = rsi(closes)
    const first = closes[0]
    const last = closes[closes.length - 1]

    const intraday = isIntraday(data.interval)

    return {
      intraday,
      rsiNow: rsiSeries[rsiSeries.length - 1],
      vol: vol * 100,
      drift: drift * 100,
      drawdown: maxDrawdown(closes),
      periodReturn: ((last - first) / first) * 100,
      // Meaningful on daily and intraday bars, where the API hands back a
      // previous close that really is the prior session's. On weekly or
      // monthly data the previous bar is a week or a month ago, which is not
      // a day change, so there is nothing honest to show.
      dayChange:
        (data.interval === '1d' || intraday) && data.previousClose && data.price
          ? ((data.price - data.previousClose) / data.previousClose) * 100
          : null,
      // The chart draws a 50-period average, so this is the one worth flagging.
      enoughForSma50: closes.length >= 50,
      bars: closes.length,
    }
  }, [data])

  const submit = (e) => {
    e.preventDefault()
    const next = input.trim().toUpperCase()
    if (next) setSymbol(next)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <form onSubmit={submit} className="mt-8 flex flex-wrap items-center gap-3">
        <label className="sr-only" htmlFor="ticker">
          Ticker symbol
        </label>
        <input
          id="ticker"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="AAPL"
          className="w-40 rounded-lg border border-ink-200 bg-white px-3 py-2.5 font-mono uppercase text-ink-900 focus:border-emerald-500 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
        />
        <button type="submit" className="btn-primary">
          Load
        </button>
        <div className="flex gap-1 rounded-lg border border-ink-200 p-1 dark:border-ink-700">
          {RANGES.map(([key, label]) => (
            <button
              key={key}
              type="button"
              onClick={() => setRange(key)}
              className={`rounded px-2.5 py-1 text-sm font-medium transition ${
                range === key
                  ? 'bg-ink-900 text-white dark:bg-white dark:text-ink-900'
                  : 'text-ink-500 hover:text-ink-900 dark:text-ink-400 dark:hover:text-white'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <span className="text-sm text-ink-400 dark:text-ink-500">
          Try VOO, MSFT, JNJ, GME, ^GSPC
        </span>
      </form>

      {loading && (
        <Panel className="mt-6">
          <div className="animate-pulse space-y-3" aria-label="Loading market data">
            <div className="h-5 w-48 rounded bg-ink-200 dark:bg-ink-800" />
            <div className="h-56 rounded bg-ink-100 dark:bg-ink-900" />
          </div>
        </Panel>
      )}

      {error && !loading && (
        <Panel className="mt-6">
          <p className="font-semibold text-rose-600 dark:text-rose-400">{error}</p>
          <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">
            Tickers are exact. Use VOO rather than "Vanguard", and add the exchange suffix for
            non-US listings.
          </p>
        </Panel>
      )}

      {data && analysis && !loading && (
        <div className="mt-6 space-y-6">
          <Panel>
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <div>
                <h2 className="text-xl font-bold text-ink-900 dark:text-white">
                  {data.symbol}
                  <span className="ml-2 text-base font-normal text-ink-500 dark:text-ink-400">
                    {data.name}
                  </span>
                </h2>
                <p className="mt-0.5 text-xs text-ink-400 dark:text-ink-500">{data.exchange}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold tabular-nums text-ink-900 dark:text-white">
                  {money(data.price, 2)}
                </p>
                {analysis.dayChange != null && (
                  <p
                    className={`text-sm font-semibold tabular-nums ${
                      analysis.dayChange >= 0
                        ? 'text-emerald-600 dark:text-emerald-400'
                        : 'text-rose-600 dark:text-rose-400'
                    }`}
                  >
                    {analysis.dayChange >= 0 ? '+' : ''}
                    {pct(analysis.dayChange, 2)} since previous close
                  </p>
                )}
              </div>
            </div>

            <div className="mt-6">
              <AdvancedChart points={data.points} currency={data.currency} />
            </div>
          </Panel>

          <div className="grid gap-4 sm:grid-cols-4">
            <Stat
              label="Return over range"
              value={`${analysis.periodReturn >= 0 ? '+' : ''}${pct(analysis.periodReturn)}`}
              tone={analysis.periodReturn >= 0 ? 'good' : 'bad'}
            />
            <Stat
              label="Annualised volatility"
              value={pct(analysis.vol, 0)}
              sub="Standard deviation of returns"
              tone={analysis.vol > 35 ? 'warn' : 'neutral'}
            />
            <Stat
              label="Worst drawdown"
              value={pct(analysis.drawdown, 0)}
              sub="Peak to trough, in range"
              tone={analysis.drawdown > 30 ? 'bad' : 'neutral'}
            />
            <Stat
              label="RSI (14)"
              value={Number.isFinite(analysis.rsiNow) ? num(analysis.rsiNow, 0) : 'n/a'}
              sub={
                analysis.rsiNow > 70
                  ? 'Conventionally "overbought"'
                  : analysis.rsiNow < 30
                    ? 'Conventionally "oversold"'
                    : 'Middle of the range'
              }
              tone={analysis.rsiNow > 70 || analysis.rsiNow < 30 ? 'warn' : 'neutral'}
            />
          </div>

          <Panel title="Reading this chart">
            <ul className="space-y-2.5">
              {analysis.vol > 35 && (
                <Flag level="warn" title={`Annualised volatility of ${pct(analysis.vol, 0)} is high`}>
                  A broad index fund typically runs nearer 15 to 20. At this level, swings of several
                  percent in a day are ordinary rather than newsworthy, and position size matters far
                  more than entry price.
                </Flag>
              )}
              {analysis.drawdown > 40 && (
                <Flag level="bad" title={`This fell ${pct(analysis.drawdown, 0)} from its peak within this range`}>
                  Recovering that requires a gain of{' '}
                  {pct((100 / (100 - analysis.drawdown) - 1) * 100, 0)}. That asymmetry is the whole
                  argument for sizing positions before you need to.
                </Flag>
              )}
              {analysis.rsiNow > 70 && (
                <Flag level="info" title="RSI above 70 does not mean it is about to fall">
                  A strong stock can sit above 70 for months. RSI describes momentum that has already
                  happened; it does not schedule a reversal.
                </Flag>
              )}
              {!analysis.enoughForSma50 && (
                <Flag
                  level="info"
                  title={`Only ${analysis.bars} bars in this range, so the 50-period average is missing`}
                >
                  A 50-period average needs 50 bars before it can plot a single point. Widen the
                  range and it appears.
                </Flag>
              )}
              {analysis.intraday && (
                <Flag level="info" title="Annualised figures from a few sessions are not comparable">
                  The volatility above scales the moves between bars minutes apart up to a yearly
                  number. A quiet session reads low and a jumpy one reads high, and neither tells you
                  much, because it is one or two days of evidence stretched across a year. Read it
                  off the 1Y view if you want a figure worth quoting.
                </Flag>
              )}
              <Flag level="info" title="Every overlay here is built from past prices">
                The moving averages and the Bollinger band are all made of prices that have already
                happened, so they lag by construction. They are useful for seeing whether today's move
                is unusual, not for timing anything. Toggle them off in the legend and the chart tells
                you the same story.
              </Flag>
            </ul>
            <LessonLink to={tool.lesson} name={tool.lessonName} />
          </Panel>
        </div>
      )}
    </div>
  )
}
