import { useEffect, useMemo, useState } from 'react'
import { ScaleIcon } from './Icons.jsx'

/**
 * Interactive risk-tolerance questionnaire, embedded directly in the lesson.
 *
 * This was a standalone tool in the previous version of the site. It belongs in
 * the course instead: the number it produces is meaningless without the lesson
 * around it explaining what tolerance is, how it differs from capacity, and why
 * the honest answer is the one you give before a crash rather than during one.
 *
 * Answers persist to LocalStorage so a reader can come back and see whether
 * their answers changed after living through a bad month.
 */
const STORAGE_KEY = 'stockguide:riskprofile:v1'

const QUESTIONS = [
  {
    id: 'horizon',
    prompt: 'When are you most likely to need this money back?',
    options: [
      { label: 'Within 2 years', points: 0 },
      { label: '2 to 5 years', points: 1 },
      { label: '5 to 10 years', points: 3 },
      { label: 'More than 10 years', points: 4 },
    ],
  },
  {
    id: 'drawdown',
    prompt: 'Your portfolio falls 30% over four months. Honestly, what do you do?',
    options: [
      { label: 'Sell everything to stop the bleeding', points: 0 },
      { label: 'Sell some of it and wait', points: 1 },
      { label: 'Do nothing and stop checking', points: 3 },
      { label: 'Keep buying on schedule', points: 4 },
    ],
  },
  {
    id: 'emergency',
    prompt: 'If your phone died tomorrow and you had to replace it, where would the money come from?',
    options: [
      { label: 'I would have to sell investments', points: 0 },
      { label: 'Borrowing, or asking family', points: 1 },
      { label: 'Savings, but it would hurt', points: 3 },
      { label: 'A cash cushion I keep for exactly this', points: 4 },
    ],
  },
  {
    id: 'income',
    prompt: 'Can you keep adding money regularly over the next few years?',
    options: [
      { label: 'No, this is all I will have', points: 0 },
      { label: 'Occasionally, if something is left over', points: 2 },
      { label: 'Yes, a small amount on a schedule', points: 3 },
      { label: 'Yes, reliably and increasing', points: 4 },
    ],
  },
  {
    id: 'goal',
    prompt: 'What is this money mainly for?',
    options: [
      { label: 'Protecting what I already have', points: 0 },
      { label: 'Beating inflation, modestly', points: 2 },
      { label: 'Growing meaningfully over decades', points: 3 },
      { label: 'Maximum long-run growth, volatility accepted', points: 4 },
    ],
  },
  {
    id: 'experience',
    prompt: 'How much investing have you actually done?',
    options: [
      { label: 'None yet', points: 0 },
      { label: 'A little, less than a year', points: 1 },
      { label: 'A few years, through at least one bad stretch', points: 3 },
      { label: 'Years, including a real crash I held through', points: 4 },
    ],
  },
  {
    id: 'choice',
    prompt: 'Pick the one-year range you would rather sign up for.',
    options: [
      { label: 'Between +4% and -2%', points: 0 },
      { label: 'Between +12% and -10%', points: 2 },
      { label: 'Between +25% and -20%', points: 3 },
      { label: 'Between +45% and -35%', points: 4 },
    ],
  },
]

const MAX = QUESTIONS.reduce((s, q) => s + Math.max(...q.options.map((o) => o.points)), 0)

const BANDS = [
  {
    min: 0,
    label: 'Conservative',
    tone: 'border-sky-300 bg-sky-50 dark:border-sky-500/40 dark:bg-sky-500/10',
    text: 'text-sky-800 dark:text-sky-300',
    summary:
      'Your answers point to a short horizon, a thin cushion, or a strong reaction to losses. Any of those three on its own is a good reason to keep most of this money out of the stock market entirely.',
    implication:
      'The usual reading is a large majority in cash and broad, defensive holdings, with a small equity position at most. Money you might need within a couple of years generally should not be in stocks at all, regardless of how you feel about risk.',
  },
  {
    min: 9,
    label: 'Balanced',
    tone: 'border-emerald-300 bg-emerald-50 dark:border-emerald-500/40 dark:bg-emerald-500/10',
    text: 'text-emerald-800 dark:text-emerald-300',
    summary:
      'You have some tolerance for a bad year but not an unlimited one, and your horizon is real without being indefinite.',
    implication:
      'This profile is usually read as a broad, diversified core doing nearly all the work, with very little in anything speculative. The core is the point; the exciting part is a rounding error by design.',
  },
  {
    min: 16,
    label: 'Growth',
    tone: 'border-amber-300 bg-amber-50 dark:border-amber-500/40 dark:bg-amber-500/10',
    text: 'text-amber-800 dark:text-amber-300',
    summary:
      'A long horizon, a genuine cushion, and a stated willingness to sit through a serious drop without selling.',
    implication:
      'Commonly read as a heavy allocation to broad equity index funds, with a small, deliberately sized sleeve for individual companies or speculation. The Hard track calls this the 90/10 shape and examines it in detail.',
  },
  {
    min: 22,
    label: 'Aggressive',
    tone: 'border-rose-300 bg-rose-50 dark:border-rose-500/40 dark:bg-rose-500/10',
    text: 'text-rose-800 dark:text-rose-300',
    summary:
      'Everything in your answers points one way: decades of horizon, reliable income, cash set aside, and no fear of a large drawdown.',
    implication:
      'Worth being suspicious of your own score here. Almost everyone rates themselves aggressive in a calm market, and the questionnaire cannot tell the difference between real tolerance and never having been tested. If you have not held through a 30% fall, treat this as a hypothesis rather than a finding.',
  },
]

function bandFor(score) {
  return [...BANDS].reverse().find((b) => score >= b.min) ?? BANDS[0]
}

export default function RiskProfile() {
  const [answers, setAnswers] = useState({})

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) setAnswers(JSON.parse(saved) ?? {})
    } catch {
      /* storage unavailable; the questionnaire still works this session */
    }
  }, [])

  useEffect(() => {
    if (!Object.keys(answers).length) return
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(answers))
    } catch {
      /* ignore */
    }
  }, [answers])

  const answered = Object.keys(answers).length
  const done = answered === QUESTIONS.length
  const score = useMemo(() => Object.values(answers).reduce((s, p) => s + p, 0), [answers])
  const band = done ? bandFor(score) : null

  return (
    <section className="my-9 rounded-2xl border border-ink-200 bg-white p-5 dark:border-ink-700 dark:bg-ink-900 sm:p-6">
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-ink-500 dark:text-ink-400">
        <ScaleIcon className="h-4 w-4" />
        Risk profile assessment
      </div>
      <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">
        Seven questions. Answer how you would actually behave, not how you would like to.
      </p>

      <ol className="mt-6 space-y-6">
        {QUESTIONS.map((q, qi) => (
          <li key={q.id}>
            <p className="flex gap-2.5 font-semibold text-ink-900 dark:text-ink-100">
              <span className="shrink-0 tabular-nums text-ink-400 dark:text-ink-500">{qi + 1}.</span>
              <span>{q.prompt}</span>
            </p>
            <div className="mt-2.5 grid gap-2 pl-7 sm:grid-cols-2">
              {q.options.map((o) => {
                const selected = answers[q.id] === o.points
                return (
                  <button
                    key={o.label}
                    type="button"
                    onClick={() => setAnswers((a) => ({ ...a, [q.id]: o.points }))}
                    className={`rounded-lg border px-3.5 py-2.5 text-left text-[0.9rem] transition ${
                      selected
                        ? 'border-emerald-500 bg-emerald-50 font-medium text-emerald-900 dark:bg-emerald-500/15 dark:text-emerald-200'
                        : 'border-ink-200 hover:border-ink-400 dark:border-ink-700 dark:hover:border-ink-500'
                    }`}
                  >
                    {o.label}
                  </button>
                )
              })}
            </div>
          </li>
        ))}
      </ol>

      {!done && (
        <p className="mt-6 text-sm text-ink-500 dark:text-ink-400">
          {answered} of {QUESTIONS.length} answered.
        </p>
      )}

      {done && band && (
        <div className={`mt-7 rounded-xl border p-5 ${band.tone}`}>
          <div className="flex flex-wrap items-baseline justify-between gap-3">
            <p className={`text-xl font-bold ${band.text}`}>{band.label}</p>
            <p className="text-sm tabular-nums text-ink-600 dark:text-ink-300">
              {score} out of {MAX}
            </p>
          </div>
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-white/60 dark:bg-ink-900/60">
            <div className="h-full rounded-full bg-current opacity-60" style={{ width: `${(score / MAX) * 100}%` }} />
          </div>
          <p className="mt-4 text-[0.95rem] leading-relaxed text-ink-700 dark:text-ink-200">{band.summary}</p>
          <p className="mt-3 text-[0.95rem] leading-relaxed text-ink-700 dark:text-ink-200">{band.implication}</p>

          <div className="mt-5 flex flex-wrap gap-3">
            <button type="button" onClick={() => setAnswers({})} className="btn-secondary">
              Start over
            </button>
          </div>

          <p className="mt-4 text-xs leading-relaxed text-ink-500 dark:text-ink-400">
            This is a teaching exercise, not financial advice or a recommendation. It knows nothing about
            your taxes, debts, country or circumstances, and a seven-question quiz cannot substitute for
            either real experience or a licensed professional.
          </p>
        </div>
      )}
    </section>
  )
}
