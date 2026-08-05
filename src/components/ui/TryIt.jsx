import { useEffect, useState } from 'react'
import { WrenchIcon } from './Icons.jsx'

/**
 * A hands-on exercise or reflection prompt.
 *
 * Whatever the reader types is saved to LocalStorage under the module id, so
 * their notes survive a refresh and they can come back to compare answers
 * later. Nothing is sent anywhere — this is a notebook, not a submission.
 */
export default function TryIt({ moduleId, id = 'default', title = 'Try it yourself', children, placeholder }) {
  const storageKey = `stockguide:tryit:${moduleId}:${id}`
  const [value, setValue] = useState('')
  const [saved, setSaved] = useState(false)

  // Load any previously written answer when the module mounts.
  useEffect(() => {
    try {
      setValue(localStorage.getItem(storageKey) ?? '')
    } catch {
      /* storage unavailable — the box still works, it just won't persist */
    }
  }, [storageKey])

  // Debounce writes so we aren't hitting storage on every keystroke.
  useEffect(() => {
    if (value === '') return
    const t = setTimeout(() => {
      try {
        localStorage.setItem(storageKey, value)
        setSaved(true)
        setTimeout(() => setSaved(false), 1600)
      } catch {
        /* ignore */
      }
    }, 600)
    return () => clearTimeout(t)
  }, [value, storageKey])

  return (
    <section className="my-8 rounded-xl border-2 border-dashed border-emerald-300 bg-emerald-50/50 p-5 dark:border-emerald-500/40 dark:bg-emerald-500/5">
      <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
        <WrenchIcon className="h-4 w-4 shrink-0" />
        <span>{title}</span>
      </div>

      <div className="text-[1rem] leading-relaxed text-ink-700 dark:text-ink-200 [&>p:first-child]:mt-0">
        {children}
      </div>

      <label className="sr-only" htmlFor={storageKey}>
        Your answer
      </label>
      <textarea
        id={storageKey}
        rows={3}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder ?? 'Write your answer here — it saves automatically.'}
        className="mt-4 w-full resize-y rounded-lg border border-emerald-200 bg-white px-3.5 py-2.5 text-[0.95rem] text-ink-800 placeholder:text-ink-400 focus:border-emerald-500 dark:border-emerald-500/30 dark:bg-ink-900 dark:text-ink-100 dark:placeholder:text-ink-500"
      />

      <p className="mt-2 h-4 text-xs text-emerald-700 dark:text-emerald-400">
        {saved ? 'Saved to this browser' : ' '}
      </p>
    </section>
  )
}
