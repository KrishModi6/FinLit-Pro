import { NavLink } from 'react-router-dom'
import { CloseIcon } from '../ui/Icons.jsx'
import ProgressBar from '../ui/ProgressBar.jsx'
import { TRACKS } from '../../data/curriculum.js'
import { getStatusMeta } from '../../data/statuses.js'
import { useProgress } from '../../context/ProgressContext.jsx'

/**
 * Full course tree.
 *
 * Every module is always reachable, nothing is gated behind completing
 * something else. The recommended order is conveyed by numbering and layout,
 * not by locking doors.
 */
function Tree({ onNavigate }) {
  const { getStatus, stats } = useProgress()

  return (
    <nav aria-label="Course contents" className="space-y-8 pb-16">
      {TRACKS.map((track) => {
        const s = stats.byTrack[track.slug]

        return (
          <div key={track.slug}>
            <NavLink
              to={track.path}
              onClick={onNavigate}
              className={({ isActive }) =>
                `group flex items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 ${
                  isActive ? track.theme.activeNav : 'hover:bg-ink-100 dark:hover:bg-ink-800/60'
                }`
              }
            >
              <span className="text-[0.8125rem] font-bold uppercase tracking-wider">{track.name}</span>
              <span className="shrink-0 text-xs tabular-nums text-ink-400 dark:text-ink-500">
                {s.done}/{s.total}
              </span>
            </NavLink>

            <ProgressBar
              percent={s.percent}
              bar={track.theme.bar}
              className="mx-2 mt-1.5 !h-1"
              label={`${track.name} track progress`}
            />

            <ul className="mt-2.5 space-y-0.5">
              {track.modules.map((mod) => {
                const status = getStatus(mod.id)
                const meta = getStatusMeta(status)
                const settled = status === 'complete' || status === 'skipped'
                return (
                  <li key={mod.id}>
                    <NavLink
                      to={mod.path}
                      onClick={onNavigate}
                      className={({ isActive }) =>
                        `flex gap-2.5 rounded-lg px-2 py-1.5 text-[0.8125rem] leading-snug transition ${
                          isActive
                            ? `font-semibold ${track.theme.activeNav}`
                            : 'text-ink-600 hover:bg-ink-100 hover:text-ink-900 dark:text-ink-400 dark:hover:bg-ink-800/60 dark:hover:text-ink-100'
                        }`
                      }
                    >
                      {/* Status dot, colour carries the state, the title
                          attribute carries it for screen readers and hover. */}
                      <span
                        className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${meta.dot}`}
                        title={meta.label}
                      />
                      <span className="sr-only">{meta.label}: </span>
                      <span className={settled ? 'text-ink-400 dark:text-ink-500' : ''}>{mod.title}</span>
                    </NavLink>
                  </li>
                )
              })}
            </ul>
          </div>
        )
      })}
    </nav>
  )
}

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Desktop: pinned column that scrolls independently of the article. */}
      <aside className="sticky top-16 hidden h-[calc(100vh-4rem)] w-72 shrink-0 overflow-y-auto border-r border-ink-200 px-4 py-6 no-scrollbar dark:border-ink-800 lg:block">
        <Tree />
      </aside>

      {/* Mobile: slide-over drawer. */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-ink-950/50 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden="true"
          />
          <div className="absolute inset-y-0 left-0 flex w-[19rem] max-w-[85vw] flex-col bg-white shadow-2xl dark:bg-ink-950">
            <div className="flex h-16 shrink-0 items-center justify-between border-b border-ink-200 px-4 dark:border-ink-800">
              <span className="text-sm font-bold text-ink-900 dark:text-white">Course contents</span>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close navigation"
                className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:hover:bg-ink-800"
              >
                <CloseIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-5">
              <Tree onNavigate={onClose} />
            </div>
          </div>
        </div>
      )}
    </>
  )
}
