import { Link, NavLink, Outlet } from 'react-router-dom'
import Navbar from '../../components/layout/Navbar.jsx'
import Footer from '../../components/layout/Footer.jsx'
import { TOOLS } from '../../data/simulator.js'

/**
 * The Simulator lives outside the course: its own sub-nav, no lesson sidebar,
 * no progress tracking. It is a workshop you visit, not a path you follow.
 */
export default function SimulatorLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      {/* Sub-nav strip that makes it obvious you have left the course. */}
      <div className="sticky top-16 z-30 border-b border-ink-200 bg-ink-50/90 backdrop-blur dark:border-ink-800 dark:bg-ink-900/80">
        <div className="mx-auto flex max-w-6xl items-center gap-4 overflow-x-auto px-4 py-2.5 no-scrollbar sm:px-6">
          <Link
            to="/simulator"
            className="shrink-0 text-sm font-extrabold tracking-tight text-ink-900 dark:text-white"
          >
            Simulator
          </Link>
          <span aria-hidden="true" className="shrink-0 text-ink-300 dark:text-ink-700">
            /
          </span>
          <nav className="flex items-center gap-1">
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
        </div>
      </div>

      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
