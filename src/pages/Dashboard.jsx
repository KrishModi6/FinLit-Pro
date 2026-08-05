import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ALL_MODULES, TRACKS } from '../data/curriculum.js'
import { getStatusMeta } from '../data/statuses.js'
import { useProgress } from '../context/ProgressContext.jsx'
import ProgressBar, { ProgressRing } from '../components/ui/ProgressBar.jsx'
import ActivityHeatmap from '../components/ui/ActivityHeatmap.jsx'
import StatCard from '../components/ui/StatCard.jsx'
import { ArrowRightIcon } from '../components/ui/Icons.jsx'

/** Everything the site knows about you, and that is only what is in this browser. */
export default function Dashboard() {
  const { stats, quizStats, streak, activity, nextModule, getStatus, getQuiz, resetAll } = useProgress()
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

        <div className="min-w-0 rounded-2xl border border-ink-200 p-6 dark:border-ink-800">
          <p className="text-2xl font-bold text-ink-900 dark:text-white">
            {stats.overall.done} of {stats.overall.total} lessons complete
          </p>

          {quizzesTaken.length > 0 && (
            <p className="mt-2 text-ink-600 dark:text-ink-400">
              Quiz score across {quizzesTaken.length} {quizzesTaken.length === 1 ? 'quiz' : 'quizzes'}:{' '}
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
                {nextModule.trackName} track, {nextModule.minutes} min
              </p>
            </div>
          ) : (
            <p className="mt-6 rounded-lg bg-emerald-50 px-4 py-3 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300">
              Every lesson is settled. Go back through the Hard track once more before you put real money
              anywhere near a speculative position.
            </p>
          )}
        </div>
      </div>

      {/* --- Activity -------------------------------------------------- */}
      <h2 className="mt-14 text-2xl font-extrabold tracking-tight text-ink-900 dark:text-white">Activity</h2>
      <div className="mt-5">
        <ActivityHeatmap activity={activity} />
      </div>

      {/* --- Statistics ------------------------------------------------ */}
      <h2 className="mt-14 text-2xl font-extrabold tracking-tight text-ink-900 dark:text-white">
        Statistics
      </h2>

      <div className="mt-5 grid gap-6 lg:grid-cols-2">
        <StatCard
          title="Lesson Progress, all tracks"
          total={stats.overall.total}
          items={[
            {
              label: 'Completed',
              value: stats.overall.counts.complete,
              disc: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
              bar: 'bg-emerald-500',
            },
            {
              label: 'In progress',
              value: stats.overall.inProgress,
              disc: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300',
              bar: 'bg-amber-500',
            },
            {
              label: 'Skipped',
              value: stats.overall.counts.skipped,
              disc: 'bg-sky-100 text-sky-700 dark:bg-sky-500/20 dark:text-sky-300',
              bar: 'bg-sky-500',
            },
            {
              label: 'Not started',
              value: stats.overall.counts['not-started'],
              disc: 'bg-ink-100 text-ink-700 dark:bg-ink-800 dark:text-ink-300',
              bar: 'bg-ink-300 dark:bg-ink-600',
            },
          ]}
        />

        <StatCard
          title="Quiz Progress, all tracks"
          total={quizStats.total}
          items={[
            {
              label: 'Passed',
              value: quizStats.passed,
              disc: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
              bar: 'bg-emerald-500',
            },
            {
              label: 'Attempted',
              value: quizStats.attempted,
              disc: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300',
              bar: 'bg-amber-500',
            },
            {
              label: 'Skipped',
              value: quizStats.skipped,
              disc: 'bg-sky-100 text-sky-700 dark:bg-sky-500/20 dark:text-sky-300',
              bar: 'bg-sky-500',
            },
            {
              label: 'Not started',
              value: quizStats.notStarted,
              disc: 'bg-ink-100 text-ink-700 dark:bg-ink-800 dark:text-ink-300',
              bar: 'bg-ink-300 dark:bg-ink-600',
            },
          ]}
        />
      </div>

      {/* --- Streak ---------------------------------------------------- */}
      <div className="mt-6 rounded-2xl border border-ink-200 bg-white p-6 text-center dark:border-ink-800 dark:bg-ink-900/40">
        <p className="text-lg font-bold text-ink-900 dark:text-white">
          <span aria-hidden="true">🔥</span> {streak.current} day streak
          {streak.current > 1 ? ': keep it going' : ''}
        </p>
        <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">
          {streak.current <= 1
            ? 'Come back tomorrow to start a streak. Consistency matters far more here than intensity.'
            : `You have opened this guide ${streak.current} days in a row.`}
          {streak.longest > streak.current && ` Your longest run so far is ${streak.longest} days.`}
        </p>
        <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">
          Twenty minutes a day for a month will teach you more than one panicked afternoon before you buy
          something.
        </p>
      </div>

      {/* --- Per-track breakdown -------------------------------------- */}
      <h2 className="mt-14 text-2xl font-extrabold tracking-tight text-ink-900 dark:text-white">By track</h2>
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
          Clears every lesson status, quiz score and activity square from this browser. Your saved notes in
          the "Try it" boxes are kept.
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

      <p className="mt-10 text-center text-sm text-ink-400 dark:text-ink-500">
        Stock Guide is made by Krish Modi.
      </p>
    </div>
  )
}
