import { useEffect, useRef, useState } from 'react'
import { CheckIcon } from './Icons.jsx'
import { STATUS_ORDER, getStatusMeta } from '../../data/statuses.js'
import { useProgress } from '../../context/ProgressContext.jsx'

/**
 * The module status control, modelled on USACO Guide's.
 *
 * A single dropdown at the top of each lesson that records where the reader
 * actually is — Not Started, Reading, Practicing, Complete or Skipped — rather
 * than a binary checkbox. The chosen state colours the dot in the sidebar so
 * the whole course tree is legible at a glance.
 */
export default function StatusSelect({ moduleId }) {
  const { getStatus, setStatus } = useProgress()
  const [open, setOpen] = useState(false)
  const wrapRef = useRef(null)

  const current = getStatus(moduleId)
  const meta = getStatusMeta(current)

  // Close on outside click or Escape.
  useEffect(() => {
    if (!open) return
    const onPointerDown = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false)
    }
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onPointerDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div ref={wrapRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`Module status: ${meta.label}. Change it.`}
        className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold transition hover:brightness-95 dark:hover:brightness-110 ${meta.chip}`}
      >
        <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${meta.dot}`} />
        {meta.label}
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          className={`h-3.5 w-3.5 transition ${open ? 'rotate-180' : ''}`}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      {open && (
        <ul
          role="listbox"
          aria-label="Module status"
          className="absolute right-0 z-30 mt-2 w-48 overflow-hidden rounded-xl border border-ink-200 bg-white py-1 shadow-xl dark:border-ink-700 dark:bg-ink-900"
        >
          {STATUS_ORDER.map((id) => {
            const s = getStatusMeta(id)
            const selected = id === current
            return (
              <li key={id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selected}
                  onClick={() => {
                    setStatus(moduleId, id)
                    setOpen(false)
                  }}
                  className="flex w-full items-center gap-2.5 px-3 py-2 text-left text-sm text-ink-700 transition hover:bg-ink-100 dark:text-ink-200 dark:hover:bg-ink-800"
                >
                  <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${s.dot}`} />
                  <span className="flex-1">{s.label}</span>
                  {selected && <CheckIcon className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />}
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
