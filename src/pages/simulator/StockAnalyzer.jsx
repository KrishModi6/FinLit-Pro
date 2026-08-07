import { useMemo, useState } from 'react'
import {
  Flag,
  LessonLink,
  NumberField,
  Panel,
  Stat,
  TextField,
  num,
} from '../../components/ui/SimUI.jsx'
import { BLANK, analyse } from '../../data/analyze.js'
import { getTool } from '../../data/simulator.js'

/** Shared input block, reused by Compare so both tools ask for the same numbers. */
export function MetricInputs({ v, set }) {
  return (
    <div className="space-y-4">
      <TextField label="Ticker or name" value={v.ticker} onChange={(x) => set({ ticker: x })} placeholder="e.g. AAPL" />
      <NumberField label="Share price" prefix="$" value={v.price} onChange={(x) => set({ price: x })} step={1} />
      <NumberField
        label="Market cap"
        suffix="B"
        value={v.marketCapB}
        onChange={(x) => set({ marketCapB: x })}
        step={1}
        hint="In billions. A $3 trillion company is 3000."
      />
      <NumberField label="P/E ratio" value={v.pe} onChange={(x) => set({ pe: x })} step={0.5} />
      <NumberField label="EPS" prefix="$" value={v.eps} onChange={(x) => set({ eps: x })} step={0.1} hint="Negative if the company loses money." />
      <NumberField label="Beta" value={v.beta} onChange={(x) => set({ beta: x })} step={0.05} />
      <NumberField label="Dividend yield" suffix="%" value={v.divYield} onChange={(x) => set({ divYield: x })} step={0.1} />
      <NumberField label="Debt to equity" value={v.debtToEquity} onChange={(x) => set({ debtToEquity: x })} step={0.1} />
      <NumberField label="Revenue growth" suffix="%" value={v.revGrowth} onChange={(x) => set({ revGrowth: x })} step={1} />
    </div>
  )
}

/** Score breakdown bar list, also reused by Compare. */
export function ScoreParts({ parts }) {
  return (
    <ul className="space-y-3">
      {parts.map((p) => (
        <li key={p.label}>
          <div className="flex items-baseline justify-between gap-3 text-sm">
            <span className="font-medium text-ink-800 dark:text-ink-200">{p.label}</span>
            <span className="shrink-0 tabular-nums text-ink-500 dark:text-ink-400">
              {p.points}/{p.max}
            </span>
          </div>
          <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-ink-200 dark:bg-ink-800">
            <div
              className={`h-full rounded-full ${p.points === p.max ? 'bg-emerald-500' : p.points === 0 ? 'bg-rose-500' : 'bg-amber-500'}`}
              style={{ width: `${(p.points / p.max) * 100}%` }}
            />
          </div>
          <p className="mt-1 text-xs text-ink-400 dark:text-ink-500">{p.note}</p>
        </li>
      ))}
    </ul>
  )
}

export default function StockAnalyzer() {
  const tool = getTool('analyzer')
  const [v, setV] = useState({ ...BLANK, ticker: '' })
  const set = (patch) => setV((s) => ({ ...s, ...patch }))

  const result = useMemo(() => analyse(v), [v])

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <div className="mt-10 grid gap-6 lg:grid-cols-[22rem,1fr] lg:items-start">
        <Panel title="From the quote page">
          <MetricInputs v={v} set={set} />
          <p className="mt-4 text-xs text-ink-400 dark:text-ink-500">
            Every one of these is on a free Yahoo Finance quote page, mostly under the Statistics tab.
          </p>
        </Panel>

        {/* min-w-0: grid children default to min-width:auto, which would stop
            narrow screens from shrinking this column. */}
        <div className="min-w-0 space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat
              label="Stability score"
              value={`${result.score}/100`}
              sub={result.band.label}
              tone={result.band.tone === 'neutral' ? 'neutral' : result.band.tone}
            />
            <Stat label="Size" value={result.cap.label} sub={`${num(v.marketCapB, 1)}B market cap`} />
            <Stat
              label="Profitable"
              value={result.profitable ? 'Yes' : 'No'}
              sub={`EPS ${Number.isFinite(v.eps) ? `$${num(v.eps)}` : 'unknown'}`}
              tone={result.profitable ? 'good' : 'bad'}
            />
          </div>

          <Panel title={`How ${v.ticker || 'this company'} scored`}>
            <ScoreParts parts={result.parts} />
            <p className="mt-5 rounded-lg bg-ink-50 px-4 py-3 text-sm text-ink-500 dark:bg-ink-900/50 dark:text-ink-400">
              This score organises what you looked up. It is not a rating, not a recommendation, and it
              cannot see the things that actually sink companies, such as fraud, a lost lawsuit or a
              competitor nobody priced in.
            </p>
          </Panel>

          {result.signals.length > 0 && (
            <Panel title="What the numbers are telling you">
              <ul className="space-y-2.5">
                {result.signals.map((s) => (
                  <Flag key={s.title} level={s.level} title={s.title}>
                    {s.detail}
                  </Flag>
                ))}
              </ul>
            </Panel>
          )}

          <Panel title="Sizing implication">
            <p className="text-sm leading-relaxed text-ink-600 dark:text-ink-300">
              Stability is an input to <strong className="text-ink-900 dark:text-white">how much</strong> you
              hold, not a verdict on whether the company is good. On the Hard track's 1 to 2 percent rule, a
              position scoring {result.score}/100 sits at the{' '}
              {result.score >= 75 ? 'core' : result.score >= 50 ? 'satellite' : 'speculative'} end, which
              means{' '}
              {result.score >= 75
                ? 'it can reasonably be a larger, long-held position.'
                : result.score >= 50
                  ? 'a moderate position with a clear reason for holding it.'
                  : 'a deliberately small position that you can afford to lose entirely.'}
            </p>
          </Panel>

          <LessonLink to={tool.lesson} name={tool.lessonName} />
        </div>
      </div>
    </div>
  )
}
