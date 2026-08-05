import { AlertIcon, ChartIcon, LightbulbIcon, ScaleIcon, WrenchIcon } from './Icons.jsx'

/**
 * Highlighted aside inside a lesson.
 *
 * Five deliberately distinct voices:
 *  - `did-you-know` — a surprising but true fact
 *  - `real-talk`    — the honest, slightly uncomfortable version
 *  - `warning`      — something that can genuinely cost you money
 *  - `example`      — a worked number or scenario
 *  - `note`         — a clarification or footnote
 *
 * Each variant carries an icon and a label as well as a colour, so the meaning
 * survives for colour-blind readers and in printouts.
 */
const VARIANTS = {
  'did-you-know': {
    label: 'Did you know?',
    Icon: LightbulbIcon,
    wrap: 'border-sky-200 bg-sky-50 dark:border-sky-500/30 dark:bg-sky-500/10',
    accent: 'text-sky-700 dark:text-sky-300',
  },
  'real-talk': {
    label: 'Real talk',
    Icon: ScaleIcon,
    wrap: 'border-violet-200 bg-violet-50 dark:border-violet-500/30 dark:bg-violet-500/10',
    accent: 'text-violet-700 dark:text-violet-300',
  },
  warning: {
    label: 'Careful',
    Icon: AlertIcon,
    wrap: 'border-rose-200 bg-rose-50 dark:border-rose-500/30 dark:bg-rose-500/10',
    accent: 'text-rose-700 dark:text-rose-300',
  },
  example: {
    label: 'Worked example',
    Icon: ChartIcon,
    wrap: 'border-emerald-200 bg-emerald-50 dark:border-emerald-500/30 dark:bg-emerald-500/10',
    accent: 'text-emerald-700 dark:text-emerald-300',
  },
  note: {
    label: 'Note',
    Icon: WrenchIcon,
    wrap: 'border-ink-200 bg-ink-50 dark:border-ink-700 dark:bg-ink-800/50',
    accent: 'text-ink-600 dark:text-ink-300',
  },
}

export default function Callout({ variant = 'note', title, children }) {
  const v = VARIANTS[variant] ?? VARIANTS.note
  const { Icon } = v

  return (
    <aside className={`my-7 rounded-xl border px-5 py-4 ${v.wrap}`}>
      <div className={`mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${v.accent}`}>
        <Icon className="h-4 w-4 shrink-0" />
        <span>{title ?? v.label}</span>
      </div>
      {/* `[&>p:first-child]:mt-0` keeps the first paragraph tight to the label
          while still letting `.lesson p` spacing apply to the rest. */}
      <div className="text-[1rem] leading-relaxed text-ink-700 dark:text-ink-200 [&>p:first-child]:mt-0">
        {children}
      </div>
    </aside>
  )
}
