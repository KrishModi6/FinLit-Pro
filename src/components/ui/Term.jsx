import { useId, useState } from 'react'
import { defineTerm } from '../../data/glossary.js'

/**
 * Inline glossary term with a hover/focus definition — the Grammarly-style
 * "what does that word mean" pattern, without leaving the sentence.
 *
 *   You are buying <Term k="equity">a slice of the business</Term>.
 *
 * `k` is the glossary key; children are the words shown in the prose (defaults
 * to the term's own name). Works on touch too: the underlined word is a real
 * <button>, so tapping toggles the popover and it is reachable by keyboard.
 */
export default function Term({ k, children }) {
  const entry = defineTerm(k)
  const [open, setOpen] = useState(false)
  const id = useId()

  // Unknown key — render the text plainly rather than a broken tooltip.
  if (!entry) return <>{children ?? k}</>

  return (
    <span className="relative inline-block">
      <button
        type="button"
        aria-describedby={open ? id : undefined}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        className="cursor-help rounded-sm border-b-2 border-dotted border-emerald-400 font-medium text-inherit transition hover:border-emerald-600 hover:text-emerald-700 dark:border-emerald-500/60 dark:hover:text-emerald-300"
      >
        {children ?? entry.term}
      </button>

      {open && (
        <span
          id={id}
          role="tooltip"
          className="absolute bottom-full left-1/2 z-40 mb-2 w-64 -translate-x-1/2 animate-fade-up rounded-lg bg-ink-900 px-3.5 py-2.5 text-left text-[0.8125rem] font-normal leading-snug text-ink-100 shadow-xl ring-1 ring-black/10 dark:bg-ink-800 dark:ring-white/10 sm:w-72"
        >
          <span className="mb-0.5 block font-bold text-white">{entry.term}</span>
          <span className="block">{entry.short}</span>
        </span>
      )}
    </span>
  )
}
