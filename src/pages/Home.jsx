import { Link } from 'react-router-dom'
import { ALL_MODULES, TOTAL_MINUTES, TRACKS } from '../data/curriculum.js'
import { GLOSSARY_LIST } from '../data/glossary.js'
import { useProgress } from '../context/ProgressContext.jsx'
import ProgressBar from '../components/ui/ProgressBar.jsx'
import Wordmark from '../components/layout/Wordmark.jsx'
import { ArrowRightIcon, BookIcon, ChartIcon, ClockIcon, ScaleIcon } from '../components/ui/Icons.jsx'

/** Short pitch shown on each track card on the homepage. */
const TRACK_PITCH = {
  beginner:
    'What a share actually is, where it trades, why the price moves, and how you would buy your first one. No jargon assumed.',
  intermediate:
    'How to tell a boring compounder from a coin flip: beta, P/E, ETFs, diversification, and why part of your money should always be somewhere dull.',
  examples:
    'Real companies, real five-year charts pulled live. A stock that gave back everything it gained, the years after the GameStop squeeze, and two deliberately boring charts next to them.',
  hard:
    'Options, leverage and speculation, explained honestly. What the upside really looks like, what a total loss really looks like, and how to size a bet you can survive.',
}

export default function Home() {
  const { stats, nextModule } = useProgress()
  const started = stats.overall.done > 0

  return (
    <>
      {/* ================= HERO ================= */}
      <section className="relative overflow-hidden border-b border-ink-200 dark:border-ink-800">
        {/* Soft market-green wash behind the hero. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(60rem_30rem_at_50%_-10rem,theme(colors.emerald.100),transparent)] dark:bg-[radial-gradient(60rem_30rem_at_50%_-10rem,theme(colors.emerald.500/0.15),transparent)]"
        />

        <div className="relative mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 sm:py-28">
          <h1 className="text-5xl font-extrabold leading-[1.05] tracking-tight sm:text-7xl">
            <Wordmark />
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-ink-600 dark:text-ink-300 sm:text-2xl sm:leading-relaxed">
            A free collection of{' '}
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              structured, honest lessons
            </span>{' '}
            to take you from your first share to understanding real risk.
          </p>

          {/* The two mission quotes, front and centre. */}
          <div className="mx-auto mt-10 max-w-2xl space-y-4 text-left">
            <blockquote className="rounded-xl border-l-4 border-emerald-500 bg-white/70 px-5 py-4 text-[1.0625rem] italic leading-relaxed text-ink-700 shadow-sm backdrop-blur dark:bg-ink-900/60 dark:text-ink-200">
              “I made this course to help my fellow classmates and other students across the world learn about
              stocks.”
            </blockquote>
            <blockquote className="rounded-xl border-l-4 border-emerald-500 bg-white/70 px-5 py-4 text-[1.0625rem] italic leading-relaxed text-ink-700 shadow-sm backdrop-blur dark:bg-ink-900/60 dark:text-ink-200">
              “This website I created has the potential to help you learn what I’ve learned in my time and
              more.”
            </blockquote>
          </div>

          <p className="mt-6 text-sm font-medium text-ink-500 dark:text-ink-400">
            Made by <span className="font-bold text-ink-800 dark:text-ink-200">Krish Modi</span>, a student,
            as an IB CAS project. Free, with no sign-up.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link to="/beginner" className="btn-primary px-6 py-3 text-base">
              Start Learning
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
            {started && (
              <Link to="/dashboard" className="btn-secondary px-6 py-3 text-base">
                See my progress
              </Link>
            )}
          </div>

          {/* Course-at-a-glance stats */}
          <dl className="mx-auto mt-12 flex max-w-lg flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-ink-500 dark:text-ink-400">
            <div className="inline-flex items-center gap-2">
              <BookIcon className="h-4 w-4" />
              <dt className="sr-only">Lessons</dt>
              <dd>
                <strong className="font-bold text-ink-800 dark:text-ink-100">{ALL_MODULES.length}</strong>{' '}
                lessons
              </dd>
            </div>
            <div className="inline-flex items-center gap-2">
              <ClockIcon className="h-4 w-4" />
              <dt className="sr-only">Reading time</dt>
              <dd>
                <strong className="font-bold text-ink-800 dark:text-ink-100">
                  ~{Math.round(TOTAL_MINUTES / 60)}
                </strong>{' '}
                hours of reading
              </dd>
            </div>
            <div className="inline-flex items-center gap-2">
              <ScaleIcon className="h-4 w-4" />
              <dt className="sr-only">Glossary</dt>
              <dd>
                <strong className="font-bold text-ink-800 dark:text-ink-100">{GLOSSARY_LIST.length}</strong>{' '}
                terms defined
              </dd>
            </div>
          </dl>
        </div>
      </section>

      {/* ============== PROGRESS (only once started) ============== */}
      {started && (
        <section className="border-b border-ink-200 bg-ink-50/70 dark:border-ink-800 dark:bg-ink-900/30">
          <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-ink-900 dark:text-white">
                  You’re {stats.overall.percent}% through the course
                </p>
                <p className="mt-0.5 text-sm text-ink-500 dark:text-ink-400">
                  {stats.overall.done} of {stats.overall.total} lessons marked complete
                  {nextModule && ` · up next: ${nextModule.title}`}
                </p>
              </div>
              {nextModule && (
                <Link to={nextModule.path} className="btn-primary">
                  Continue
                  <ArrowRightIcon className="h-4 w-4" />
                </Link>
              )}
            </div>
            <ProgressBar percent={stats.overall.percent} className="mt-4" label="Overall course progress" />
          </div>
        </section>
      )}

      {/* ================= TRACKS ================= */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
            Four tracks, one path
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-ink-600 dark:text-ink-300">
            Work through them in order if you’re starting from zero, or jump straight to whatever you
            actually need. Nothing is locked. The order is a recommendation, not a gate.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
          {TRACKS.map((track) => {
            const s = stats.byTrack[track.slug]
            return (
              <Link
                key={track.slug}
                to={track.path}
                className={`card group flex flex-col p-6 hover:shadow-lg ${track.theme.hover}`}
              >
                <div className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 ${track.theme.soft}`}>
                  <span className={`h-2 w-2 rounded-full ${track.theme.dot}`} />
                  <span className={`text-xs font-bold uppercase tracking-wider ${track.theme.softText}`}>
                    {track.name}
                  </span>
                </div>

                <h3 className="mt-4 text-xl font-bold leading-snug text-ink-900 dark:text-white">
                  {track.title}
                </h3>

                <p className="mt-3 flex-1 text-[0.95rem] leading-relaxed text-ink-600 dark:text-ink-400">
                  {TRACK_PITCH[track.slug]}
                </p>

                <div className="mt-6">
                  <div className="flex items-baseline justify-between text-xs text-ink-500 dark:text-ink-400">
                    <span>{track.modules.length} lessons</span>
                    <span className="tabular-nums">
                      {s.done}/{s.total} done
                    </span>
                  </div>
                  <ProgressBar
                    percent={s.percent}
                    bar={track.theme.bar}
                    className="mt-2"
                    label={`${track.name} progress`}
                  />
                </div>

                <span
                  className={`mt-5 inline-flex items-center gap-1.5 text-sm font-semibold ${track.theme.label}`}
                >
                  {s.done > 0 ? 'Continue track' : 'Open track'}
                  <ArrowRightIcon className="h-4 w-4 transition group-hover:translate-x-0.5" />
                </span>
              </Link>
            )
          })}
        </div>
      </section>

      {/* ================= HOW IT WORKS ================= */}
      <section className="border-t border-ink-200 bg-ink-50/70 dark:border-ink-800 dark:bg-ink-900/30">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20">
          <h2 className="text-center text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white">
            How the lessons work
          </h2>

          <div className="mt-12 grid gap-8 sm:grid-cols-3">
            {[
              {
                Icon: BookIcon,
                title: 'Read the concept',
                body: 'Every lesson is written to be read once, properly: real definitions, real numbers, and a worked example rather than a vague summary.',
              },
              {
                Icon: ChartIcon,
                title: 'Try it on a real stock',
                body: 'Each lesson has a hands-on prompt: look up a P/E ratio, find a beta, check a dividend yield. Your answers save in your browser.',
              },
              {
                Icon: ScaleIcon,
                title: 'Check yourself',
                body: 'A short quiz at the bottom of every lesson tells you instantly whether it landed, and explains why the right answer is right.',
              },
            ].map(({ Icon, title, body }) => (
              <div key={title}>
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-white text-emerald-600 shadow-sm ring-1 ring-ink-200 dark:bg-ink-900 dark:text-emerald-400 dark:ring-ink-700">
                  <Icon className="h-5 w-5" />
                </span>
                <h3 className="mt-4 font-bold text-ink-900 dark:text-white">{title}</h3>
                <p className="mt-2 text-[0.95rem] leading-relaxed text-ink-600 dark:text-ink-400">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= CLOSING CTA ================= */}
      <section className="mx-auto max-w-3xl px-4 py-20 text-center sm:px-6">
        <h2 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white">
          Start with the thing nobody explains
        </h2>
        <p className="mt-4 text-lg leading-relaxed text-ink-600 dark:text-ink-300">
          Most people’s first exposure to investing is a screenshot of somebody’s gains. That’s a terrible
          place to start. Begin with what a share actually is. It takes nine minutes.
        </p>
        <Link to="/beginner/what-is-a-stock" className="btn-primary mt-8 px-6 py-3 text-base">
          Lesson 1: What Is a Stock?
          <ArrowRightIcon className="h-4 w-4" />
        </Link>
      </section>
    </>
  )
}
