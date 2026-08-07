import { useEffect, useMemo, useState } from 'react'
import PriceChart from './PriceChart.jsx'
import { fetchQuote, maxDrawdown } from '../../data/market.js'

/**
 * A real, live chart embedded in a lesson, with the numbers computed from the
 * data rather than written into the prose.
 *
 * The point of the Examples track is that the reader sees an actual price
 * history instead of a hypothetical. That means the figures move, so the
 * component derives and displays them (period return, peak, trough, worst
 * drawdown) and the surrounding lesson text describes the SHAPE. Nothing in
 * the prose can go stale, because no number is hard-coded into it.
 *
 * Degrades to a plain note if the quote service is unreachable, so a lesson
 * never breaks because a third party is down.
 */
function fmtMonth(ts) {
  return new Date(ts).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

function fmtMoney(v, currency = 'USD') {
  return v.toLocaleString('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: v < 10 ? 2 : 0,
  })
}

export default function StockExample({ ticker, range = '5y', caption }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let live = true
    fetchQuote(ticker, range)
      .then((d) => live && setData(d))
      .catch((e) => live && setError(e.message))
    return () => {
      live = false
    }
  }, [ticker, range])

  const stats = useMemo(() => {
    if (!data?.points?.length) return null
    const pts = data.points
    const closes = pts.map((p) => p.c)
    const first = closes[0]
    const last = closes[closes.length - 1]

    let peakI = 0
    let troughI = 0
    closes.forEach((c, i) => {
      if (c > closes[peakI]) peakI = i
      if (c < closes[troughI]) troughI = i
    })

    // Fall from the highest point to the latest price, which is what a holder
    // who bought at the top is actually looking at.
    const fromPeak = ((last - closes[peakI]) / closes[peakI]) * 100

    return {
      first,
      last,
      periodReturn: ((last - first) / first) * 100,
      peak: closes[peakI],
      peakAt: pts[peakI].t,
      trough: closes[troughI],
      troughAt: pts[troughI].t,
      fromPeak,
      drawdown: maxDrawdown(closes),
      startAt: pts[0].t,
      endAt: pts[pts.length - 1].t,
    }
  }, [data])

  if (error) {
    return (
      <div className="my-8 rounded-xl border border-ink-200 bg-ink-50 px-5 py-4 dark:border-ink-800 dark:bg-ink-900/40">
        <p className="text-sm text-ink-600 dark:text-ink-300">
          The live chart for {ticker} could not load right now ({error}) You can pull the same chart
          up yourself on Yahoo Finance by searching {ticker} and setting the range to five years.
        </p>
      </div>
    )
  }

  if (!data || !stats) {
    return (
      <div className="my-8 animate-pulse rounded-xl border border-ink-200 p-5 dark:border-ink-800">
        <div className="h-4 w-40 rounded bg-ink-200 dark:bg-ink-800" />
        <div className="mt-4 h-48 rounded bg-ink-100 dark:bg-ink-900" />
      </div>
    )
  }

  const cur = data.currency
  const up = stats.periodReturn >= 0

  return (
    <figure className="my-8 rounded-2xl border border-ink-200 bg-white p-5 dark:border-ink-800 dark:bg-ink-900/40 sm:p-6">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="text-base font-bold text-ink-900 dark:text-white">
          {data.symbol}
          <span className="ml-2 text-sm font-normal text-ink-500 dark:text-ink-400">{data.name}</span>
        </p>
        <p className="text-xs text-ink-400 dark:text-ink-500">
          {fmtMonth(stats.startAt)} to {fmtMonth(stats.endAt)} · live data
        </p>
      </div>

      <div className="mt-4">
        <PriceChart points={data.points} currency={cur} />
      </div>

      <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-3 border-t border-ink-100 pt-4 text-sm dark:border-ink-800 sm:grid-cols-4">
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-400 dark:text-ink-500">
            Over this period
          </dt>
          <dd
            className={`mt-0.5 font-bold tabular-nums ${up ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}
          >
            {up ? '+' : ''}
            {stats.periodReturn.toFixed(0)}%
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-400 dark:text-ink-500">Peak</dt>
          <dd className="mt-0.5 font-bold tabular-nums text-ink-900 dark:text-white">
            {fmtMoney(stats.peak, cur)}
          </dd>
          <dd className="text-xs text-ink-400 dark:text-ink-500">{fmtMonth(stats.peakAt)}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-400 dark:text-ink-500">Low</dt>
          <dd className="mt-0.5 font-bold tabular-nums text-ink-900 dark:text-white">
            {fmtMoney(stats.trough, cur)}
          </dd>
          <dd className="text-xs text-ink-400 dark:text-ink-500">{fmtMonth(stats.troughAt)}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-400 dark:text-ink-500">
            Worst fall
          </dt>
          <dd className="mt-0.5 font-bold tabular-nums text-rose-600 dark:text-rose-400">
            {stats.drawdown.toFixed(0)}%
          </dd>
          <dd className="text-xs text-ink-400 dark:text-ink-500">peak to trough</dd>
        </div>
      </dl>

      {caption && (
        <figcaption className="mt-4 text-sm leading-relaxed text-ink-600 dark:text-ink-300">
          {caption}
        </figcaption>
      )}
    </figure>
  )
}
