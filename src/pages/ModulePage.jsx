import { Suspense, useCallback, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getModule, getNeighbours, getTrack } from '../data/curriculum.js'
import { getContent } from '../content/index.jsx'
import { useProgress } from '../context/ProgressContext.jsx'
import { getStatusMeta } from '../data/statuses.js'
import StatusSelect from '../components/ui/StatusSelect.jsx'
import TableOfContents, { HeadingIndexer } from '../components/ui/TableOfContents.jsx'
import NotFound from './NotFound.jsx'
import { ArrowLeftIcon, ArrowRightIcon, CheckIcon, ClockIcon } from '../components/ui/Icons.jsx'

/**
 * The template every lesson renders inside.
 *
 * Responsibilities: header + metadata + status control, the `.lesson`
 * typography wrapper, the auto-generated table of contents, and previous/next
 * navigation. The lesson body and its quiz come from
 * `src/content/<track>/<Module>.jsx`.
 */
export default function ModulePage() {
  const { trackSlug, moduleSlug } = useParams()
  const track = getTrack(trackSlug)
  const mod = getModule(trackSlug, moduleSlug)
  const { getStatus, setStatus, isComplete, toggleComplete, getQuiz } = useProgress()

  const articleRef = useRef(null)
  const [headings, setHeadings] = useState([])
  // Stable identity so HeadingIndexer's effect doesn't re-run every render.
  const onIndex = useCallback((list) => setHeadings(list), [])

  if (!track || !mod) return <NotFound />

  const Content = getContent(mod.id)
  const { prev, next } = getNeighbours(mod.id)
  const status = getStatus(mod.id)
  const statusMeta = getStatusMeta(status)
  const done = isComplete(mod.id)
  const quiz = getQuiz(mod.id)

  return (
    <div className="px-4 py-8 sm:px-8 sm:py-12 lg:px-12">
      <div className="mx-auto flex max-w-[76rem] items-start gap-12">
        {/* ---------------------------- Article ---------------------------- */}
        <div className="mx-auto w-full min-w-0 max-w-prose xl:mx-0">
          {/* --- Header ------------------------------------------------- */}
          <div className="flex flex-wrap items-start justify-between gap-4">
            <nav aria-label="Breadcrumb" className="text-sm">
              <Link to={track.path} className={`font-semibold ${track.theme.label} transition hover:underline`}>
                {track.name}
              </Link>
              <span className="mx-2 text-ink-300 dark:text-ink-600">/</span>
              <span className="text-ink-500 dark:text-ink-400">
                Lesson {mod.number} of {track.modules.length}
              </span>
            </nav>

            <StatusSelect moduleId={mod.id} />
          </div>

          <h1 className="mt-5 text-3xl font-extrabold leading-tight tracking-tight text-ink-900 dark:text-white sm:text-[2.5rem]">
            {mod.title}
          </h1>

          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-ink-500 dark:text-ink-400">
            <span>
              Author: <span className="font-medium text-ink-700 dark:text-ink-300">Krish Modi</span>
            </span>
            <span aria-hidden="true" className="text-ink-300 dark:text-ink-700">
              ·
            </span>
            <span className="inline-flex items-center gap-1.5">
              <ClockIcon className="h-4 w-4" />
              {mod.minutes} min read
            </span>
            {status !== 'not-started' && (
              <>
                <span aria-hidden="true" className="text-ink-300 dark:text-ink-700">
                  ·
                </span>
                <span className={`inline-flex items-center gap-1.5 font-semibold ${statusMeta.text}`}>
                  <span className={`h-2 w-2 rounded-full ${statusMeta.dot}`} />
                  {statusMeta.label}
                </span>
              </>
            )}
            {quiz && (
              <>
                <span aria-hidden="true" className="text-ink-300 dark:text-ink-700">
                  ·
                </span>
                <span className="tabular-nums">
                  Quiz {quiz.correct}/{quiz.total}
                </span>
              </>
            )}
          </div>

          <p className="mt-4 text-lg leading-relaxed text-ink-500 dark:text-ink-400">{mod.blurb}</p>

          <hr className="mt-8 border-ink-200 dark:border-ink-800" />

          {/* Contents, inline, the right rail is hidden on narrower screens. */}
          {headings.length > 1 && (
            <details className="mt-8 rounded-xl border border-ink-200 px-4 py-3 dark:border-ink-800 xl:hidden">
              <summary className="cursor-pointer text-sm font-semibold text-ink-700 dark:text-ink-200">
                On this page
              </summary>
              <ul className="mt-3 space-y-1.5">
                {headings.map((h) => (
                  <li key={h.id}>
                    <a
                      href={`#${h.id}`}
                      className="text-sm text-ink-500 hover:text-ink-900 dark:text-ink-400 dark:hover:text-white"
                    >
                      {h.text}
                    </a>
                  </li>
                ))}
              </ul>
            </details>
          )}

          {/* --- Lesson body -------------------------------------------- */}
          <article ref={articleRef} className="lesson mt-8">
            <Suspense
              fallback={
                <div className="animate-pulse space-y-4 py-8" aria-label="Loading lesson">
                  <div className="h-4 w-3/4 rounded bg-ink-200 dark:bg-ink-800" />
                  <div className="h-4 w-full rounded bg-ink-200 dark:bg-ink-800" />
                  <div className="h-4 w-5/6 rounded bg-ink-200 dark:bg-ink-800" />
                </div>
              }
            >
              <Content moduleId={mod.id} />
              {/* Mounts only after the lazy lesson has committed to the DOM. */}
              <HeadingIndexer containerRef={articleRef} moduleId={mod.id} onIndex={onIndex} />
            </Suspense>
          </article>

          {/* --- Finish the lesson --------------------------------------- */}
          <div
            className={`mt-12 flex flex-wrap items-center justify-between gap-4 rounded-xl border p-5 transition ${
              done
                ? 'border-emerald-300 bg-emerald-50 dark:border-emerald-500/40 dark:bg-emerald-500/10'
                : 'border-ink-200 bg-ink-50 dark:border-ink-800 dark:bg-ink-900/40'
            }`}
          >
            <div>
              <p className="font-semibold text-ink-900 dark:text-white">
                {done ? 'Marked as complete' : 'Finished this lesson?'}
              </p>
              <p className="mt-0.5 text-sm text-ink-500 dark:text-ink-400">
                {done
                  ? 'It shows as complete in the sidebar and on your dashboard.'
                  : 'Update the status so the sidebar and your dashboard stay accurate.'}
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {!done && status !== 'skipped' && (
                <button
                  type="button"
                  onClick={() => setStatus(mod.id, 'skipped')}
                  className="btn-secondary"
                >
                  Skip this one
                </button>
              )}
              <button
                type="button"
                onClick={() => toggleComplete(mod.id)}
                className={done ? 'btn-secondary' : 'btn-primary'}
              >
                {done ? (
                  'Mark as not done'
                ) : (
                  <>
                    <CheckIcon className="h-4 w-4" />
                    Mark complete
                  </>
                )}
              </button>
            </div>
          </div>

          {/* --- Previous / next ---------------------------------------- */}
          <nav aria-label="Lesson navigation" className="mt-8 grid gap-3 sm:grid-cols-2">
            {prev ? (
              <Link to={prev.path} className="card flex flex-col p-4 hover:border-ink-400 dark:hover:border-ink-600">
                <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-ink-400 dark:text-ink-500">
                  <ArrowLeftIcon className="h-3.5 w-3.5" />
                  Previous
                </span>
                <span className="mt-1.5 font-semibold leading-snug text-ink-800 dark:text-ink-100">
                  {prev.title}
                </span>
              </Link>
            ) : (
              <div className="hidden sm:block" />
            )}

            {next && (
              <Link
                to={next.path}
                className="card flex flex-col p-4 text-right hover:border-ink-400 dark:hover:border-ink-600"
              >
                <span className="inline-flex items-center justify-end gap-1.5 text-xs font-semibold uppercase tracking-wider text-ink-400 dark:text-ink-500">
                  Next
                  <ArrowRightIcon className="h-3.5 w-3.5" />
                </span>
                <span className="mt-1.5 font-semibold leading-snug text-ink-800 dark:text-ink-100">
                  {next.title}
                </span>
              </Link>
            )}
          </nav>
        </div>

        {/* --------------------------- TOC rail --------------------------- */}
        <aside className="hidden w-56 shrink-0 pt-24 xl:block">
          <TableOfContents headings={headings} />
        </aside>
      </div>
    </div>
  )
}
