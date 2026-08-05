import { BookIcon } from './Icons.jsx'
import { defineTerm } from '../../data/glossary.js'

/**
 * A key-term definition card, dropped inline in a lesson the first time a piece
 * of jargon appears.
 *
 * Pass children to write a bespoke definition, or omit them and the shared
 * glossary definition is used, so a term reads identically everywhere.
 *
 *   <KeyTerm term="Beta" />                        // uses glossary.js
 *   <KeyTerm term="Beta">Custom wording here</KeyTerm>
 */
export default function KeyTerm({ term, children }) {
  const entry = defineTerm(term)
  const heading = entry?.term ?? term
  const body = children ?? entry?.long ?? null

  return (
    <div className="my-7 overflow-hidden rounded-xl border border-ink-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
      <div className="flex items-center gap-2 border-b border-ink-100 bg-ink-50 px-5 py-2.5 dark:border-ink-800 dark:bg-ink-800/60">
        <BookIcon className="h-4 w-4 shrink-0 text-ink-400 dark:text-ink-500" />
        <span className="text-xs font-bold uppercase tracking-wider text-ink-500 dark:text-ink-400">
          Key term
        </span>
      </div>
      <div className="px-5 py-4">
        <dl>
          <dt className="text-base font-bold text-ink-900 dark:text-white">{heading}</dt>
          <dd className="mt-1.5 text-[1rem] leading-relaxed text-ink-700 dark:text-ink-300 [&>p:first-child]:mt-0">
            {body}
          </dd>
        </dl>
      </div>
    </div>
  )
}
