import { Link } from 'react-router-dom'
import { TRACKS } from '../../data/curriculum.js'
import Wordmark from './Wordmark.jsx'

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-ink-200 bg-ink-50/60 dark:border-ink-800 dark:bg-ink-900/30">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-3">
          <div className="sm:col-span-1">
            <Wordmark className="block text-sm font-extrabold tracking-tight" />
            <p className="mt-2 text-sm leading-relaxed text-ink-500 dark:text-ink-400">
              A free stock market course written by a student, for students. No sign-up, no paywall, no
              newsletter.
            </p>
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-ink-400 dark:text-ink-500">Tracks</p>
            <ul className="mt-3 space-y-2">
              {TRACKS.map((t) => (
                <li key={t.slug}>
                  <Link
                    to={t.path}
                    className="text-sm text-ink-600 transition hover:text-ink-900 dark:text-ink-400 dark:hover:text-white"
                  >
                    {t.name}: {t.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-ink-400 dark:text-ink-500">Site</p>
            <ul className="mt-3 space-y-2">
              <li>
                <Link
                  to="/dashboard"
                  className="text-sm text-ink-600 transition hover:text-ink-900 dark:text-ink-400 dark:hover:text-white"
                >
                  My progress
                </Link>
              </li>
              <li>
                <Link
                  to="/glossary"
                  className="text-sm text-ink-600 transition hover:text-ink-900 dark:text-ink-400 dark:hover:text-white"
                >
                  Glossary
                </Link>
              </li>
              <li>
                <Link
                  to="/simulator"
                  className="text-sm text-ink-600 transition hover:text-ink-900 dark:text-ink-400 dark:hover:text-white"
                >
                  Simulator
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* This has to be unmissable on a site that talks about options and
            speculative bets. It is not boilerplate. It is the point. */}
        <div className="mt-10 rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 dark:border-amber-500/30 dark:bg-amber-500/10">
          <p className="text-[0.8125rem] leading-relaxed text-amber-900 dark:text-amber-200">
            <strong className="font-bold">This is education, not financial advice.</strong> Nothing here is a
            recommendation to buy or sell any security. Company and ticker names appear only as real-world
            examples of concepts. Investing involves risk, including the permanent loss of your money. Do your
            own research, and talk to a licensed financial professional before you invest.
          </p>
        </div>

        <p className="mt-8 text-xs text-ink-400 dark:text-ink-600">
          Built as an IB CAS project by Krish Modi. Progress is stored in your browser only, nothing is
          uploaded anywhere.
        </p>
      </div>
    </footer>
  )
}
