import { Link } from 'react-router-dom'
import { TRACKS } from '../data/curriculum.js'

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <p className="font-mono text-sm font-bold uppercase tracking-widest text-ink-400 dark:text-ink-500">
        404
      </p>
      <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white">
        That page isn’t here
      </h1>
      <p className="mt-3 text-ink-600 dark:text-ink-400">
        The link may be old, or the lesson may have been renamed. Everything on the site is reachable from
        one of the four tracks below.
      </p>

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        {TRACKS.map((t) => (
          <Link key={t.slug} to={t.path} className="btn-secondary">
            <span className={`h-2 w-2 rounded-full ${t.theme.dot}`} />
            {t.name}
          </Link>
        ))}
      </div>

      <Link to="/" className="mt-6 inline-block text-sm font-medium text-emerald-700 hover:underline dark:text-emerald-400">
        Back to the homepage
      </Link>
    </div>
  )
}
