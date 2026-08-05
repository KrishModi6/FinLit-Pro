import { Link } from 'react-router-dom'
import { TOOLS } from '../../data/simulator.js'
import { ArrowRightIcon } from '../../components/ui/Icons.jsx'

export default function SimulatorHome() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-20">
      <div className="max-w-2xl">
        <p className="text-sm font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-400">
          Simulator
        </p>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-5xl">
          Run the numbers yourself
        </h1>
        <p className="mt-5 text-lg leading-relaxed text-ink-600 dark:text-ink-300">
          The course explains the ideas. This is where you test them on real figures. Every tool works on
          numbers you type in, so you can model a portfolio you actually hold, a trade you are actually
          considering, or a company you just looked up.
        </p>
      </div>

      <div className="mt-10 rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 dark:border-amber-500/30 dark:bg-amber-500/10">
        <p className="text-sm leading-relaxed text-amber-900 dark:text-amber-200">
          <strong className="font-bold">These are models, not predictions.</strong> Nothing here fetches a
          live price or tells you what to buy. A model is only as good as the assumptions you feed it, and
          the future is not obliged to match any of them.
        </p>
      </div>

      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {TOOLS.map((tool) => (
          <Link
            key={tool.slug}
            to={`/simulator/${tool.slug}`}
            className="card group flex flex-col p-6 hover:border-ink-400 hover:shadow-lg dark:hover:border-ink-600"
          >
            <span
              className={`inline-flex w-fit rounded-full bg-gradient-to-r px-3 py-1 text-xs font-bold uppercase tracking-wider text-white ${tool.accent}`}
            >
              {tool.tag}
            </span>
            <h2 className="mt-4 text-lg font-bold text-ink-900 dark:text-white">{tool.name}</h2>
            <p className="mt-2 flex-1 text-[0.9375rem] leading-relaxed text-ink-600 dark:text-ink-400">
              {tool.blurb}
            </p>
            <span className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700 dark:text-emerald-400">
              Open tool
              <ArrowRightIcon className="h-4 w-4 transition group-hover:translate-x-0.5" />
            </span>
          </Link>
        ))}
      </div>

      <p className="mt-12 text-sm text-ink-500 dark:text-ink-400">
        Looking for the risk tolerance questionnaire? It moved into the course, where it belongs, as{' '}
        <Link
          to="/beginner/know-your-risk-profile"
          className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400"
        >
          Know Your Risk Profile
        </Link>
        .
      </p>
    </div>
  )
}
