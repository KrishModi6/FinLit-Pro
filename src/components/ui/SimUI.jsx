import { Link } from 'react-router-dom'
import { formatMoney } from '../../data/market.js'

/**
 * Shared building blocks for the Simulator tools, so six tools look like one
 * product instead of six weekend projects.
 */

/** Labelled numeric input with an optional prefix/suffix and helper line. */
export function NumberField({ label, value, onChange, prefix, suffix, step = 1, min, max, hint, id }) {
  const fieldId = id ?? `f-${label.replace(/\s+/g, '-').toLowerCase()}`
  return (
    <div>
      <label htmlFor={fieldId} className="block text-sm font-medium text-ink-700 dark:text-ink-300">
        {label}
      </label>
      <div className="relative mt-1.5">
        {prefix && (
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-ink-400">
            {prefix}
          </span>
        )}
        <input
          id={fieldId}
          type="number"
          inputMode="decimal"
          step={step}
          min={min}
          max={max}
          value={Number.isFinite(value) ? value : ''}
          onChange={(e) => onChange(e.target.value === '' ? NaN : Number(e.target.value))}
          className={`w-full rounded-lg border border-ink-200 bg-white py-2.5 text-ink-900 tabular-nums focus:border-emerald-500 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100 ${
            prefix ? 'pl-7' : 'pl-3'
          } ${suffix ? 'pr-9' : 'pr-3'}`}
        />
        {suffix && (
          <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm text-ink-400">
            {suffix}
          </span>
        )}
      </div>
      {hint && <p className="mt-1 text-xs text-ink-400 dark:text-ink-500">{hint}</p>}
    </div>
  )
}

/** Labelled text input. */
export function TextField({ label, value, onChange, placeholder, id }) {
  const fieldId = id ?? `t-${label.replace(/\s+/g, '-').toLowerCase()}`
  return (
    <div>
      <label htmlFor={fieldId} className="block text-sm font-medium text-ink-700 dark:text-ink-300">
        {label}
      </label>
      <input
        id={fieldId}
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1.5 w-full rounded-lg border border-ink-200 bg-white px-3 py-2.5 text-ink-900 placeholder:text-ink-400 focus:border-emerald-500 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
      />
    </div>
  )
}

/** Labelled select. */
export function SelectField({ label, value, onChange, options, id }) {
  const fieldId = id ?? `s-${label.replace(/\s+/g, '-').toLowerCase()}`
  return (
    <div>
      <label htmlFor={fieldId} className="block text-sm font-medium text-ink-700 dark:text-ink-300">
        {label}
      </label>
      <select
        id={fieldId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1.5 w-full rounded-lg border border-ink-200 bg-white px-3 py-2.5 text-ink-900 focus:border-emerald-500 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  )
}

/** Big headline figure. `tone` colours it for good/bad outcomes. */
export function Stat({ label, value, sub, tone = 'neutral' }) {
  const tones = {
    neutral: 'text-ink-900 dark:text-white',
    good: 'text-emerald-600 dark:text-emerald-400',
    bad: 'text-rose-600 dark:text-rose-400',
    warn: 'text-amber-600 dark:text-amber-400',
  }
  return (
    <div className="rounded-xl border border-ink-200 p-4 dark:border-ink-800">
      <p className="text-xs font-semibold uppercase tracking-wider text-ink-400 dark:text-ink-500">{label}</p>
      <p className={`mt-1.5 text-2xl font-bold tabular-nums ${tones[tone]}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-ink-500 dark:text-ink-400">{sub}</p>}
    </div>
  )
}

/**
 * A single interpreted finding about the reader's inputs.
 * `level` drives the colour and the icon glyph.
 */
export function Flag({ level = 'info', title, children }) {
  const styles = {
    good: 'border-emerald-300 bg-emerald-50 dark:border-emerald-500/40 dark:bg-emerald-500/10',
    warn: 'border-amber-300 bg-amber-50 dark:border-amber-500/40 dark:bg-amber-500/10',
    bad: 'border-rose-300 bg-rose-50 dark:border-rose-500/40 dark:bg-rose-500/10',
    info: 'border-ink-200 bg-ink-50 dark:border-ink-700 dark:bg-ink-800/50',
  }
  const dots = {
    good: 'bg-emerald-500',
    warn: 'bg-amber-500',
    bad: 'bg-rose-500',
    info: 'bg-ink-400',
  }
  return (
    <li className={`flex gap-3 rounded-lg border px-4 py-3 ${styles[level]}`}>
      <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${dots[level]}`} />
      <div className="min-w-0 flex-1 text-sm">
        <p className="font-semibold text-ink-900 dark:text-white">{title}</p>
        <p className="mt-0.5 leading-relaxed text-ink-600 dark:text-ink-300">{children}</p>
      </div>
    </li>
  )
}

/** Panel wrapper used for the inputs column and the results column. */
export function Panel({ title, children, className = '' }) {
  return (
    <section className={`rounded-2xl border border-ink-200 p-5 dark:border-ink-800 sm:p-6 ${className}`}>
      {title && <h2 className="mb-5 text-lg font-bold text-ink-900 dark:text-white">{title}</h2>}
      {children}
    </section>
  )
}

/** Pointer back to the lesson that explains whatever the tool just computed. */
export function LessonLink({ to, name }) {
  return (
    <p className="mt-6 rounded-lg bg-ink-50 px-4 py-3 text-sm text-ink-600 dark:bg-ink-900/50 dark:text-ink-400">
      The reasoning behind these numbers is in{' '}
      <Link to={to} className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400">
        {name}
      </Link>
      .
    </p>
  )
}

/** Horizontally scrollable table shell (tools live outside `.lesson`). */
export function DataTable({ head, children }) {
  return (
    <div className="-mx-5 mt-5 overflow-x-auto px-5 sm:mx-0 sm:px-0">
      <table className="w-full min-w-[30rem] border-collapse text-left text-sm">
        <thead>
          <tr>
            {head.map((h) => (
              <th
                key={h}
                className="border-b border-ink-200 pb-2 pr-4 text-xs font-semibold uppercase tracking-wide text-ink-500 dark:border-ink-700 dark:text-ink-400"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  )
}

export const Td = ({ children, className = '' }) => (
  <td className={`border-b border-ink-100 py-2.5 pr-4 tabular-nums dark:border-ink-800/70 ${className}`}>
    {children}
  </td>
)

/* ------------------------------ formatters ------------------------------ */

/**
 * Most of the simulator deals in dollars the reader typed in, so USD is the
 * default. Pass a currency for anything priced by an exchange instead, or a
 * London or Mumbai listing gets labelled with a dollar sign.
 */
export const money = (n, dp = 0, currency = 'USD') => formatMoney(n, { currency, dp })

export const pct = (n, dp = 1) => (Number.isFinite(n) ? `${n.toFixed(dp)}%` : 'n/a')

export const num = (n, dp = 2) => (Number.isFinite(n) ? n.toFixed(dp) : 'n/a')
