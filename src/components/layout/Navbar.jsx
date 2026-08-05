import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { ChartIcon, CloseIcon, MenuIcon, MoonIcon, SunIcon } from '../ui/Icons.jsx'
import { TRACKS } from '../../data/curriculum.js'
import { useProgress } from '../../context/ProgressContext.jsx'
import { useTheme } from '../../context/ThemeContext.jsx'

const linkBase =
  'rounded-lg px-3 py-2 text-sm font-medium transition hover:bg-ink-100 dark:hover:bg-ink-800'
const linkActive = 'text-ink-900 dark:text-white'
const linkIdle = 'text-ink-600 dark:text-ink-400'

/**
 * Sticky top bar.
 *
 * `onMenuClick` is only supplied by CourseLayout — on pages with no sidebar the
 * hamburger opens this component's own nav dropdown instead.
 */
export default function Navbar({ onMenuClick }) {
  const { theme, toggleTheme } = useTheme()
  const { stats } = useProgress()
  const [navOpen, setNavOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-ink-200 bg-white/85 backdrop-blur-md dark:border-ink-800 dark:bg-ink-950/85">
      <div className="mx-auto flex h-16 max-w-[110rem] items-center gap-3 px-4 sm:px-6">
        {/* Sidebar toggle — course pages only, phones/tablets only */}
        {onMenuClick && (
          <button
            type="button"
            onClick={onMenuClick}
            aria-label="Open lesson navigation"
            className="-ml-1 rounded-lg p-2 text-ink-600 hover:bg-ink-100 dark:text-ink-400 dark:hover:bg-ink-800 lg:hidden"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
        )}

        <Link to="/" className="flex shrink-0 items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-sm">
            <ChartIcon className="h-[18px] w-[18px]" />
          </span>
          <span className="text-[1.0625rem] font-extrabold tracking-tight text-ink-900 dark:text-white">
            Stock Guide
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="ml-4 hidden items-center gap-1 md:flex">
          {TRACKS.map((track) => (
            <NavLink
              key={track.slug}
              to={track.path}
              className={({ isActive }) => `${linkBase} ${isActive ? linkActive : linkIdle}`}
            >
              <span className={`mr-1.5 inline-block h-1.5 w-1.5 rounded-full align-middle ${track.theme.dot}`} />
              {track.name}
            </NavLink>
          ))}
          <NavLink to="/glossary" className={({ isActive }) => `${linkBase} ${isActive ? linkActive : linkIdle}`}>
            Glossary
          </NavLink>
        </nav>

        <div className="ml-auto flex items-center gap-1.5">
          <Link
            to="/dashboard"
            className="hidden items-center gap-2 rounded-lg border border-ink-200 px-3 py-1.5 text-sm font-medium text-ink-700 transition hover:border-ink-300 hover:bg-ink-50 dark:border-ink-700 dark:text-ink-300 dark:hover:bg-ink-800 sm:flex"
          >
            <span className="tabular-nums">
              {stats.overall.done}/{stats.overall.total}
            </span>
            <span className="text-ink-400 dark:text-ink-500">done</span>
          </Link>

          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            className="rounded-lg p-2 text-ink-600 transition hover:bg-ink-100 dark:text-ink-400 dark:hover:bg-ink-800"
          >
            {theme === 'dark' ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
          </button>

          {/* Top-level nav dropdown for small screens */}
          <button
            type="button"
            onClick={() => setNavOpen((o) => !o)}
            aria-label="Menu"
            aria-expanded={navOpen}
            className="rounded-lg p-2 text-ink-600 hover:bg-ink-100 dark:text-ink-400 dark:hover:bg-ink-800 md:hidden"
          >
            {navOpen ? <CloseIcon className="h-5 w-5" /> : <MenuIcon className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {navOpen && (
        <nav className="border-t border-ink-200 bg-white px-4 py-3 dark:border-ink-800 dark:bg-ink-950 md:hidden">
          {TRACKS.map((track) => (
            <NavLink
              key={track.slug}
              to={track.path}
              onClick={() => setNavOpen(false)}
              className="flex items-center gap-2.5 rounded-lg px-2 py-2.5 text-sm font-medium text-ink-700 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
            >
              <span className={`h-1.5 w-1.5 rounded-full ${track.theme.dot}`} />
              {track.name} — {track.title}
            </NavLink>
          ))}
          <NavLink
            to="/glossary"
            onClick={() => setNavOpen(false)}
            className="block rounded-lg px-2 py-2.5 text-sm font-medium text-ink-700 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
          >
            Glossary
          </NavLink>
          <NavLink
            to="/dashboard"
            onClick={() => setNavOpen(false)}
            className="block rounded-lg px-2 py-2.5 text-sm font-medium text-ink-700 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
          >
            My progress
          </NavLink>
        </nav>
      )}
    </header>
  )
}
