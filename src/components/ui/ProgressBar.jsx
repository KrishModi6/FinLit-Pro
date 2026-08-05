/** Thin horizontal completion bar. `bar` is a Tailwind background class. */
export default function ProgressBar({ percent, bar = 'bg-emerald-500', className = '', label }) {
  const safe = Math.max(0, Math.min(100, percent || 0))

  return (
    <div
      className={`h-1.5 w-full overflow-hidden rounded-full bg-ink-200 dark:bg-ink-800 ${className}`}
      role="progressbar"
      aria-valuenow={safe}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label ?? 'Progress'}
    >
      <div className={`h-full rounded-full transition-[width] duration-500 ${bar}`} style={{ width: `${safe}%` }} />
    </div>
  )
}

/** Circular variant used on the dashboard hero. */
export function ProgressRing({ percent, size = 116, stroke = 9, className = '' }) {
  const safe = Math.max(0, Math.min(100, percent || 0))
  const r = (size - stroke) / 2
  const circumference = 2 * Math.PI * r

  return (
    <svg width={size} height={size} className={className} role="img" aria-label={`${safe}% of the course complete`}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        strokeWidth={stroke}
        className="stroke-ink-200 dark:stroke-ink-800"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={circumference * (1 - safe / 100)}
        className="stroke-emerald-500 transition-[stroke-dashoffset] duration-700"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="50%"
        dominantBaseline="central"
        textAnchor="middle"
        className="fill-ink-900 text-xl font-bold tabular-nums dark:fill-white"
      >
        {safe}%
      </text>
    </svg>
  )
}
