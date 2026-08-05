import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  DataTable,
  Flag,
  LessonLink,
  NumberField,
  Panel,
  Stat,
  Td,
  money,
  num,
  pct,
} from '../../components/ui/SimUI.jsx'
import { PERIODS_PER_YEAR, annualisedStats, fetchQuote } from '../../data/market.js'
import { getTool } from '../../data/simulator.js'

/**
 * Monte Carlo projection built on a stock's own historical drift and
 * volatility, using geometric Brownian motion.
 *
 * The original app called this an "AI Predictor". It was Monte Carlo then too,
 * and the honest framing matters more than the label: this shows the SPREAD of
 * outcomes a random walk with these parameters produces. It is not a forecast,
 * and the page says so repeatedly on purpose.
 */
const RUNS = 3000

function mulberry32(seed) {
  return function () {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function normal(rand) {
  let u = 0
  let v = 0
  while (u === 0) u = rand()
  while (v === 0) v = rand()
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
}

function simulate({ price, drift, vol, days }) {
  const rand = mulberry32(20260805)
  const dt = 1 / 252
  const finals = []

  for (let i = 0; i < RUNS; i++) {
    let p = price
    for (let d = 0; d < days; d++) {
      // Geometric Brownian motion: the standard textbook price model.
      p *= Math.exp((drift - (vol * vol) / 2) * dt + vol * Math.sqrt(dt) * normal(rand))
    }
    finals.push(p)
  }

  finals.sort((a, b) => a - b)
  const at = (q) => finals[Math.min(finals.length - 1, Math.floor((q / 100) * finals.length))]
  const belowStart = finals.filter((f) => f < price).length

  return {
    p5: at(5),
    p10: at(10),
    p25: at(25),
    p50: at(50),
    p75: at(75),
    p90: at(90),
    p95: at(95),
    lossOdds: (belowStart / RUNS) * 100,
  }
}

export default function AiPredictor() {
  const tool = getTool('predictor')
  const [input, setInput] = useState('AAPL')
  const [symbol, setSymbol] = useState('AAPL')
  const [months, setMonths] = useState(12)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = useCallback(async (sym) => {
    setLoading(true)
    setError(null)
    try {
      setData(await fetchQuote(sym, '5y'))
    } catch (e) {
      setData(null)
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load(symbol)
  }, [symbol, load])

  const model = useMemo(() => {
    if (!data?.points?.length || !Number.isFinite(months) || months < 1) return null
    const closes = data.points.map((p) => p.c)
    const per = PERIODS_PER_YEAR[data.interval] ?? 252
    const { drift, vol, samples } = annualisedStats(closes, per)
    if (!Number.isFinite(drift) || !Number.isFinite(vol)) return null

    const price = data.price ?? closes[closes.length - 1]
    const days = Math.round((months / 12) * 252)
    return { ...simulate({ price, drift, vol, days }), price, drift, vol, samples, days }
  }, [data, months])

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

      <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-5 py-4 dark:border-rose-500/30 dark:bg-rose-500/10">
        <p className="text-sm leading-relaxed text-rose-900 dark:text-rose-200">
          <strong className="font-bold">This is not a prediction, and nobody can make one.</strong>{' '}
          It runs {RUNS.toLocaleString()} random walks using this stock's own past volatility. The
          spread it produces is the point; any single number in it is not a forecast, and the real
          future is not obliged to look like the past.
        </p>
      </div>

      <form onSubmit={submit} className="mt-8 flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-sm font-medium text-ink-700 dark:text-ink-300" htmlFor="pt">
            Ticker
          </label>
          <input
            id="pt"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="mt-1.5 w-40 rounded-lg border border-ink-200 bg-white px-3 py-2.5 font-mono uppercase text-ink-900 focus:border-emerald-500 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
          />
        </div>
        <div className="w-40">
          <NumberField label="Months ahead" value={months} onChange={setMonths} step={1} min={1} max={120} />
        </div>
        <button type="submit" className="btn-primary mb-0.5">
          Run
        </button>
      </form>

      {loading && <Panel className="mt-6"><p className="text-ink-500 dark:text-ink-400">Loading five years of history…</p></Panel>}

      {error && !loading && (
        <Panel className="mt-6">
          <p className="font-semibold text-rose-600 dark:text-rose-400">{error}</p>
        </Panel>
      )}

      {model && !loading && (
        <div className="mt-6 space-y-6">
          <div className="grid gap-4 sm:grid-cols-4">
            <Stat label="Current price" value={money(model.price, 2)} sub={data.symbol} />
            <Stat
              label="Historical volatility"
              value={pct(model.vol * 100, 0)}
              sub="Annualised, from 5 years"
              tone={model.vol > 0.35 ? 'warn' : 'neutral'}
            />
            <Stat
              label="Historical drift"
              value={pct(model.drift * 100, 0)}
              sub="Annualised, past 5 years"
              tone={model.drift > 0 ? 'good' : 'bad'}
            />
            <Stat
              label="Runs below today"
              value={pct(model.lossOdds, 0)}
              sub={`After ${months} month(s)`}
              tone="warn"
            />
          </div>

          <Panel title={`The spread after ${months} month(s)`}>
            <DataTable head={['Percentile', 'Price', 'Change from today']}>
              {[
                ['5th (bad)', model.p5],
                ['10th', model.p10],
                ['25th', model.p25],
                ['50th (median)', model.p50],
                ['75th', model.p75],
                ['90th', model.p90],
                ['95th (good)', model.p95],
              ].map(([label, value]) => {
                const change = ((value - model.price) / model.price) * 100
                return (
                  <tr key={label}>
                    <Td className="font-medium text-ink-900 dark:text-white">{label}</Td>
                    <Td>{money(value, 2)}</Td>
                    <Td
                      className={
                        change >= 0
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-rose-600 dark:text-rose-400'
                      }
                    >
                      {change >= 0 ? '+' : ''}
                      {pct(change)}
                    </Td>
                  </tr>
                )
              })}
            </DataTable>
            <p className="mt-4 text-sm text-ink-500 dark:text-ink-400">
              The gap between the 10th and 90th percentile is{' '}
              {money(model.p90 - model.p10, 2)}, which is{' '}
              {pct(((model.p90 - model.p10) / model.price) * 100, 0)} of today's price. Every one of
              those futures came from the same inputs.
            </p>
          </Panel>

          <Panel title="What this actually tells you">
            <ul className="space-y-2.5">
              <Flag level="bad" title="The model assumes the future resembles the past">
                Drift and volatility are measured from {model.samples} historical periods. A company
                whose business changes, or a market regime that shifts, breaks that assumption
                completely. The 2019 numbers for an airline told you nothing useful about 2020.
              </Flag>
              <Flag level="warn" title="Random walks understate real crashes">
                A normal distribution produces extreme days far less often than markets actually do.
                Treat the bad end of this table as optimistic rather than worst-case.
              </Flag>
              <Flag level="info" title="A drift of any size is not a promise">
                The historical drift here is {pct(model.drift * 100, 0)} a year. Feeding a past
                return into a forward model is the single most common way people convince themselves
                a projection is a plan.
              </Flag>
              <Flag level="good" title="What it is genuinely good for">
                Sizing. If the 10th percentile outcome would seriously hurt you, the position is too
                big, and that judgement does not require the model to be right about the future.
              </Flag>
            </ul>
            <LessonLink to={tool.lesson} name={tool.lessonName} />
          </Panel>
        </div>
      )}
    </div>
  )
}
