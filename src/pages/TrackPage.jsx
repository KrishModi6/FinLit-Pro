import { Link, useParams } from 'react-router-dom'
import { getTrack } from '../data/curriculum.js'
import { getStatusMeta } from '../data/statuses.js'
import { useProgress } from '../context/ProgressContext.jsx'
import ProgressBar from '../components/ui/ProgressBar.jsx'
import NotFound from './NotFound.jsx'
import { ArrowRightIcon, CheckCircleIcon, ClockIcon } from '../components/ui/Icons.jsx'

/** Track overview: what the track covers, and the ordered list of its lessons. */
export default function TrackPage() {
  const { trackSlug } = useParams()
  const track = getTrack(trackSlug)
  const { getStatus, stats } = useProgress()

  if (!track) return <NotFound />

  const s = stats.byTrack[track.slug]
  const minutes = track.modules.reduce((sum, m) => sum + m.minutes, 0)
  const settled = new Set(['complete', 'skipped'])
  const firstUnfinished =
    track.modules.find((m) => !settled.has(getStatus(m.id))) ?? track.modules[0]

  return (
    <div className="px-4 py-10 sm:px-8 sm:py-14 lg:px-14">
      <div className="mx-auto max-w-3xl">
        <p className={`text-sm font-bold uppercase tracking-widest ${track.theme.label}`}>
          {track.name} track
        </p>

        <h1 className="mt-3 text-3xl font-extrabold leading-tight tracking-tight text-ink-900 dark:text-white sm:text-[2.75rem]">
          {track.title}
        </h1>

        <p className="mt-4 text-lg leading-relaxed text-ink-600 dark:text-ink-300">{track.description}</p>

        {/* Progress summary */}
        <div className="mt-8 rounded-xl border border-ink-200 p-5 dark:border-ink-800">
          <div className="flex items-baseline justify-between gap-4">
            <span className="text-sm font-semibold text-ink-700 dark:text-ink-200">Your progress</span>
            <span className="text-sm tabular-nums text-ink-500 dark:text-ink-400">
              {s.done} of {s.total} lessons · {minutes} min total
            </span>
          </div>
          <ProgressBar
            percent={s.percent}
            bar={track.theme.bar}
            className="mt-3"
            label={`${track.name} track progress`}
          />
          <Link to={firstUnfinished.path} className="btn-primary mt-5">
            {s.done === 0 ? 'Start the track' : s.done === s.total ? 'Review the track' : 'Continue where you left off'}
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>

        {/* What you'll be able to do */}
        <h2 className="mt-12 text-lg font-bold text-ink-900 dark:text-white">
          By the end of this track you should be able to
        </h2>
        <ul className="mt-4 space-y-2.5">
          {track.outcomes.map((outcome) => (
            <li key={outcome} className="flex gap-3 text-ink-700 dark:text-ink-300">
              <CheckCircleIcon className={`mt-0.5 h-5 w-5 shrink-0 ${track.theme.label}`} />
              <span>{outcome}</span>
            </li>
          ))}
        </ul>

        {/* Lesson list */}
        <h2 className="mt-12 text-lg font-bold text-ink-900 dark:text-white">Lessons</h2>
        <ol className="mt-4 space-y-3">
          {track.modules.map((mod) => {
            const meta = getStatusMeta(getStatus(mod.id))
            return (
              <li key={mod.id}>
                <Link
                  to={mod.path}
                  className={`card flex gap-4 p-5 ${track.theme.hover} hover:shadow-sm`}
                >
                  <span className="mt-1.5 shrink-0" title={meta.label}>
                    <span className={`block h-3 w-3 rounded-full ${meta.dot}`} />
                    <span className="sr-only">{meta.label}</span>
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      <span className="font-semibold text-ink-900 dark:text-white">
                        {mod.number}. {mod.title}
                      </span>
                      <span className="inline-flex items-center gap-1 text-xs text-ink-400 dark:text-ink-500">
                        <ClockIcon className="h-3.5 w-3.5" />
                        {mod.minutes} min
                      </span>
                      {meta.id !== 'not-started' && (
                        <span className={`text-xs font-semibold ${meta.text}`}>{meta.label}</span>
                      )}
                    </span>
                    <span className="mt-1.5 block text-sm leading-relaxed text-ink-500 dark:text-ink-400">
                      {mod.blurb}
                    </span>
                  </span>
                </Link>
              </li>
            )
          })}
        </ol>
      </div>
    </div>
  )
}
