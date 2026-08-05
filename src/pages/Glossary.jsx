import { useMemo, useState } from 'react'
import { GLOSSARY_LIST } from '../data/glossary.js'
import { SearchIcon } from '../components/ui/Icons.jsx'

/**
 * Every key term on the site in one searchable list.
 *
 * The same definitions power the inline hover popovers inside lessons, so
 * nothing can drift out of sync between here and the course.
 */
export default function Glossary() {
  const [query, setQuery] = useState('')

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return GLOSSARY_LIST
    return GLOSSARY_LIST.filter(
      (e) =>
        e.term.toLowerCase().includes(q) ||
        e.short.toLowerCase().includes(q) ||
        e.long.toLowerCase().includes(q) ||
        e.tags.some((t) => t.includes(q))
    )
  }, [query])

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        Glossary
      </h1>
      <p className="mt-3 text-lg text-ink-600 dark:text-ink-300">
        Every term the course uses, defined in plain English. Finance vocabulary is mostly a gatekeeping
        problem — once you know the words, the ideas underneath are not that complicated.
      </p>

      <div className="relative mt-8">
        <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-ink-400" />
        <label className="sr-only" htmlFor="glossary-search">
          Search the glossary
        </label>
        <input
          id="glossary-search"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search terms — try “beta”, “options”, “risk”…"
          className="w-full rounded-xl border border-ink-200 bg-white py-3.5 pl-12 pr-4 text-ink-800 placeholder:text-ink-400 focus:border-emerald-500 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
        />
      </div>

      <p className="mt-4 text-sm text-ink-500 dark:text-ink-400">
        {results.length} {results.length === 1 ? 'term' : 'terms'}
      </p>

      <dl className="mt-4 divide-y divide-ink-200 dark:divide-ink-800">
        {results.map((entry) => (
          <div key={entry.key} className="py-5">
            <dt className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <span className="text-lg font-bold text-ink-900 dark:text-white">{entry.term}</span>
              {entry.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-ink-100 px-2.5 py-0.5 text-[0.6875rem] font-semibold uppercase tracking-wide text-ink-500 dark:bg-ink-800 dark:text-ink-400"
                >
                  {tag}
                </span>
              ))}
            </dt>
            <dd className="mt-2 leading-relaxed text-ink-600 dark:text-ink-300">{entry.long}</dd>
          </div>
        ))}
      </dl>

      {results.length === 0 && (
        <p className="rounded-xl border border-dashed border-ink-300 px-5 py-10 text-center text-ink-500 dark:border-ink-700 dark:text-ink-400">
          No term matches “{query}”. Try a shorter word.
        </p>
      )}
    </div>
  )
}
