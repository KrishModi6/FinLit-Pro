import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ALL_MODULES, TRACKS } from '../data/curriculum.js'
import { STATUS_ORDER, getStatusMeta } from '../data/statuses.js'
import { useProgress } from '../context/ProgressContext.jsx'
import ProgressBar, { ProgressRing } from '../components/ui/ProgressBar.jsx'
import { ArrowRightIcon } from '../components/ui/Icons.jsx'

/** Everything the site knows about you, and that is only what’s in this browser. */
export default function Dashboard() {
  const { stats, nextModule, getStatus, getQuiz, resetAll } = useProgress()
  const [confirmingReset, setConfirmingReset] = useState(false)

  const quizzesTaken = ALL_MODULES.map((m) => ({ mod: m, quiz: getQuiz(m.id) })).filter((r) => r.quiz)
  const quizCorrect = quizzesTaken.reduce((n, r) => n + r.quiz.correct, 0)
  const quizTotal = quizzesTaken.reduce((n, r) => n + r.quiz.total, 0)

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        Your progress
      </h1>
      <p className="mt-3 text-ink-600 dark:text-ink-400">
        Saved in this browser only. Clearing your browser data or opening the site elsewhere starts you
        fresh.
      </p>

      {/* --- Overview ------------------------------------------------- */}
      <div className="mt-8 grid gap-6 sm:grid-cols-[auto,1fr]">
        <div className="flex items-center justify-center rounded-2xl border border-ink-200 p-6 dark:border-ink-800">
          <ProgressRing percent={stats.overall.percent} />
        </div>

        <div className="rounded-2xl border border-ink-200 p-6 dark:border-ink-800">
          <p className="text-2xl font-bold text-ink-900 dark:text-white">
            {stats.overall.done} of {stats.overall.total} lessons complete
          </p>

          {quizzesTaken.length > 0 && (
            <p className="mt-2 text-ink-600 dark:text-ink-400">
              Quiz score across {quizzesTaken.length}{' '}
              {quizzesTaken.length === 1 ? 'quiz' : 'quizzes'}:{' '}
              <strong className="font-bold text-ink-900 dark:text-white">
                {quizCorrect}/{quizTotal}
              </strong>{' '}
              ({Math.round((quizCorrect / quizTotal) * 100)}%)
            </p>
          )}

          {nextModule ? (
            <div className="mt-6">
              <p className="text-xs font-bold uppercase tracking-wider text-ink-400 dark:text-ink-500">
                Recommended next
              </p>
              <Link
                to={nextModule.path}
                className="mt-2 inline-flex items-baseline gap-2 text-lg font-semibold text-emerald-700 hover:underline dark:text-emerald-400"
              >
                {nextModule.title}
                <ArrowRightIcon className="h-4 w-4 self-center" />
              </Link>
              <p className="mt-1 text-sm text-ink-500 dark:text-ink-400">
                {nextModule.trackName} track · {nextModule.minutes} min
              </p>
            </div>
          ) : (
            <p className="mt-6 rounded-lg bg-emerald-50 px-4 py-3 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300">
              Every lesson is marked complete. Go back through the Hard track once more before you put real
              money anywhere near a speculative position.
            </p>
          )}
        </div>
      </div>

      {/* --- Status legend --------------------------------------------- */}
      <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 rounded-xl border border-ink-200 px-5 py-4 dark:border-ink-800">
        {STATUS_ORDER.map((id) => {
          const meta = getStatusMeta(id)
          return (
            <span key={id} className="inline-flex items-center gap-2 text-sm">
              <span className={`h-2.5 w-2.5 rounded-full ${meta.dot}`} />
              <span className="text-ink-600 dark:text-ink-400">{meta.label}</span>
              <span className="font-semibold tabular-nums text-ink-900 dark:text-white">
                {stats.overall.counts[id]}
              </span>
            </span>
          )
        })}
      </div>

      {/* --- Per-track breakdown -------------------------------------- */}
      <h2 className="mt-14 text-xl font-bold text-ink-900 dark:text-white">By track</h2>
      <div className="mt-5 space-y-8">
        {TRACKS.map((track) => {
          const s = stats.byTrack[track.slug]
          return (
            <section key={track.slug}>
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <Link
                  to={track.path}
                  className={`text-sm font-bold uppercase tracking-wider ${track.theme.label} hover:underline`}
                >
                  {track.name}: {track.title}
                </Link>
                <span className="text-sm tabular-nums text-ink-500 dark:text-ink-400">
                  {s.done}/{s.total} · {s.percent}%
                </span>
              </div>

              <ProgressBar
                percent={s.percent}
                bar={track.theme.bar}
                className="mt-2.5"
                label={`${track.name} progress`}
              />

              <ul className="mt-4 grid gap-2 sm:grid-cols-2">
                {track.modules.map((mod) => {
                  const meta = getStatusMeta(getStatus(mod.id))
                  const settled = meta.id === 'complete' || meta.id === 'skipped'
                  const quiz = getQuiz(mod.id)
                  return (
                    <li key={mod.id}>
                      <Link
                        to={mod.path}
                        className="flex items-start gap-2.5 rounded-lg px-2.5 py-2 text-sm transition hover:bg-ink-100 dark:hover:bg-ink-800/60"
                      >
                        <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${meta.dot}`} title={meta.label} />
                        <span className="sr-only">{meta.label}: </span>
                        <span
                          className={`flex-1 ${settled ? 'text-ink-500 dark:text-ink-500' : 'text-ink-700 dark:text-ink-300'}`}
                        >
                          {mod.title}
                        </span>
                        {quiz && (
                          <span className="shrink-0 font-mono text-xs tabular-nums text-ink-400 dark:text-ink-500">
                            {quiz.correct}/{quiz.total}
                          </span>
                        )}
                      </Link>
                    </li>
                  )
                })}
              </ul>
            </section>
          )
        })}
      </div>

      {/* --- Reset ---------------------------------------------------- */}
      <div className="mt-14 rounded-xl border border-ink-200 p-5 dark:border-ink-800">
        <p className="font-semibold text-ink-900 dark:text-white">Reset progress</p>
        <p className="mt-1 text-sm text-ink-500 dark:text-ink-400">
          Clears every completed lesson and quiz score from this browser. Your saved “Try it” notes are kept.
        </p>

        {confirmingReset ? (
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => {
                resetAll()
                setConfirmingReset(false)
              }}
              className="btn bg-rose-600 text-white hover:bg-rose-500"
            >
              Yes, reset everything
            </button>
            <button type="button" onClick={() => setConfirmingReset(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        ) : (
          <button type="button" onClick={() => setConfirmingReset(true)} className="btn-secondary mt-4">
            Reset my progress
          </button>
        )}
      </div>
    </div>
  )
}
