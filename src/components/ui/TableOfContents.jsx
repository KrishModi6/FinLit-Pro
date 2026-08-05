import { useEffect, useState } from 'react'

function slugify(text) {
  return (
    text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
      .slice(0, 60) || 'section'
  )
}

/**
 * Renders nothing, it walks the lesson DOM once it exists, gives every <h2> a
 * stable id, and hands the list back to the page.
 *
 * This lives INSIDE the <Suspense> boundary and after <Content />, so by the
 * time its effect runs the lazily-loaded lesson has committed to the DOM.
 * Doing it this way means none of the 22 lesson files has to hand-maintain a
 * table of contents.
 */
export function HeadingIndexer({ containerRef, moduleId, onIndex }) {
  useEffect(() => {
    const root = containerRef.current
    if (!root) return

    const seen = new Set()
    const found = []

    for (const el of root.querySelectorAll('h2')) {
      const text = el.textContent?.trim()
      if (!text) continue

      if (!el.id) {
        let id = slugify(text)
        // Two sections can legitimately share a heading; keep ids unique.
        let n = 2
        while (seen.has(id)) id = `${slugify(text)}-${n++}`
        el.id = id
      }
      seen.add(el.id)
      found.push({ id: el.id, text })
    }

    onIndex(found)
  }, [containerRef, moduleId, onIndex])

  return null
}

/** Sticky right-rail contents list with scroll-spy highlighting. */
export default function TableOfContents({ headings }) {
  const [active, setActive] = useState(null)

  useEffect(() => {
    if (!headings.length) return

    const observer = new IntersectionObserver(
      (entries) => {
        // Highlight the heading nearest the top of the reading area. Only
        // consider entries currently inside the observation band.
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible.length) setActive(visible[0].target.id)
      },
      // Band runs from just under the sticky header to ~35% down the viewport.
      { rootMargin: '-88px 0px -65% 0px', threshold: 0 }
    )

    for (const h of headings) {
      const el = document.getElementById(h.id)
      if (el) observer.observe(el)
    }
    return () => observer.disconnect()
  }, [headings])

  if (headings.length < 2) return null

  return (
    <nav aria-label="On this page" className="sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto no-scrollbar">
      <p className="text-xs font-bold uppercase tracking-wider text-ink-400 dark:text-ink-500">
        On this page
      </p>
      <ul className="mt-3 space-y-1 border-l border-ink-200 dark:border-ink-800">
        {headings.map((h) => (
          <li key={h.id}>
            <a
              href={`#${h.id}`}
              className={`-ml-px block border-l-2 py-1 pl-3 text-[0.8125rem] leading-snug transition ${
                active === h.id
                  ? 'border-emerald-500 font-semibold text-emerald-700 dark:text-emerald-400'
                  : 'border-transparent text-ink-500 hover:border-ink-300 hover:text-ink-800 dark:text-ink-400 dark:hover:text-ink-100'
              }`}
            >
              {h.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}
