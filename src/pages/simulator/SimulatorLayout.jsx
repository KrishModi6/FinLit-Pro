import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import Navbar from '../../components/layout/Navbar.jsx'
import Footer from '../../components/layout/Footer.jsx'
import { TOOLS } from '../../data/simulator.js'

/**
 * The Simulator lives outside the course: its own sub-nav, no lesson sidebar,
 * no progress tracking. It is a workshop you visit, not a path you follow.
 *
 * Laying out nine tool tabs takes some care, because a label cut off mid-word
 * reads as a broken page rather than as something you can scroll to:
 *
 *   1. The strip matches the navbar's width (110rem) rather than the narrower
 *      page column. A sub-nav indented from the nav above it looks unmoored,
 *      and the extra room is what lets all nine tabs sit on one row on a
 *      desktop instead of overflowing.
 *   2. From `md` up it wraps instead of scrolling, so a tab that does not fit
 *      moves to a second row and stays readable. Nothing is ever half-cut on
 *      a screen big enough to show rows.
 *   3. Below `md` it scrolls sideways, which is what a phone expects and which
 *      avoids a four-row sticky header. Two things make that legible: the
 *      active tab is scrolled into view on navigation (otherwise the strip
 *      loads at scrollLeft 0 and the current tool can sit off the right edge,
 *      so the nav looks like it has no active item), and the edge fades hint
 *      that more exists past the edge, since the scrollbar is hidden.
 */
export default function SimulatorLayout() {
  const stripRef = useRef(null)
  const [edges, setEdges] = useState({ left: false, right: false })
  const { pathname } = useLocation()

  /** Show a fade only on a side that actually has content hidden past it. */
  const updateEdges = useCallback(() => {
    const el = stripRef.current
    if (!el) return
    const max = el.scrollWidth - el.clientWidth
    // 1px of slack: fractional layout widths otherwise leave a fade stuck on.
    setEdges({ left: el.scrollLeft > 1, right: el.scrollLeft < max - 1 })
  }, [])

  /** Put the active tab on screen, then refresh the fades to match. */
  const syncStrip = useCallback(
    (smooth) => {
      const el = stripRef.current
      if (!el) return
      const active = el.querySelector('[aria-current="page"]')
      if (active) {
        // Set scrollLeft directly rather than calling scrollIntoView, which also
        // scrolls ancestor containers and can shift the whole page.
        const target = active.offsetLeft - (el.clientWidth - active.offsetWidth) / 2
        const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
        el.scrollTo({ left: Math.max(0, target), behavior: smooth && !reduced ? 'smooth' : 'auto' })
      }
      updateEdges()
    },
    [updateEdges]
  )

  // Bring the active tab into view whenever the route changes.
  useEffect(() => {
    syncStrip(true)
  }, [pathname, syncStrip])

  // Inter is fetched asynchronously, so on a cold load the tabs are first laid
  // out in the fallback font and the strip measures narrower than it ends up.
  // It can measure as not overflowing at all, in which case the active tab is
  // never scrolled into view and both fades stay off, leaving a half-cut label
  // with no hint that it scrolls. The ResizeObserver below cannot catch the
  // swap, because it is the content that reflows and the container keeps its
  // width. Re-sync once the font is actually in.
  useEffect(() => {
    let cancelled = false
    document.fonts?.ready.then(() => {
      if (!cancelled) syncStrip(false)
    })
    return () => {
      cancelled = true
    }
  }, [syncStrip])

  // Recheck on resize, and on mount before any scrolling happens.
  useEffect(() => {
    const el = stripRef.current
    if (!el) return
    updateEdges()
    const ro = new ResizeObserver(updateEdges)
    ro.observe(el)
    return () => ro.disconnect()
  }, [updateEdges])

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      {/* Sub-nav strip that makes it obvious you have left the course. */}
      <div className="sticky top-16 z-30 border-b border-ink-200 bg-ink-50/90 backdrop-blur dark:border-ink-800 dark:bg-ink-900/80">
        <div className="relative mx-auto max-w-[110rem]">
          {/* One flat flex container, not a prefix plus a nested <nav>. A nested
              nav is a single flex item, so when it does not fit it wraps as one
              block and strands "Simulator /" alone on the first line. Flat, the
              tabs flow around the prefix and fill each row. */}
          <nav
            ref={stripRef}
            onScroll={updateEdges}
            aria-label="Simulator tools"
            className="relative flex items-center gap-x-1 gap-y-1 overflow-x-auto px-4 py-2.5 no-scrollbar sm:px-6 md:flex-wrap md:overflow-visible"
          >
            <Link
              to="/simulator"
              className="shrink-0 text-sm font-extrabold tracking-tight text-ink-900 dark:text-white"
            >
              Simulator
            </Link>
            <span aria-hidden="true" className="mx-3 shrink-0 text-ink-300 dark:text-ink-700">
              /
            </span>
            {TOOLS.map((tool) => (
              <NavLink
                key={tool.slug}
                to={`/simulator/${tool.slug}`}
                className={({ isActive }) =>
                  `shrink-0 whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                    isActive
                      ? 'bg-white text-ink-900 shadow-sm dark:bg-ink-800 dark:text-white'
                      : 'text-ink-500 hover:text-ink-900 dark:text-ink-400 dark:hover:text-white'
                  }`
                }
              >
                {tool.name}
              </NavLink>
            ))}
          </nav>

          {/* Edge fades: the only signal that the strip scrolls, since the
              scrollbar is hidden. Non-interactive and hidden from readers. */}
          <div
            aria-hidden="true"
            className={`pointer-events-none absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-ink-50 to-transparent transition-opacity duration-200 dark:from-ink-900 md:hidden ${
              edges.left ? 'opacity-100' : 'opacity-0'
            }`}
          />
          <div
            aria-hidden="true"
            className={`pointer-events-none absolute inset-y-0 right-0 w-10 bg-gradient-to-l from-ink-50 to-transparent transition-opacity duration-200 dark:from-ink-900 md:hidden ${
              edges.right ? 'opacity-100' : 'opacity-0'
            }`}
          />
        </div>
      </div>

      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
