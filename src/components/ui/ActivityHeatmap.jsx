import { useMemo, useState } from 'react'
import { dayKey } from '../../context/ProgressContext.jsx'

/**
 * A year of daily activity as a contribution grid.
 *
 * One column per week, one square per day, ending on the current week. A day
 * counts as active when the reader changed a lesson status or finished a quiz,
 * so the graph reflects work done rather than pages opened.
 */
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const WEEKS = 53

const LEVELS = [
  'bg-ink-100 dark:bg-ink-800',
  'bg-emerald-200 dark:bg-emerald-900',
  'bg-emerald-300 dark:bg-emerald-700',
  'bg-emerald-500 dark:bg-emerald-600',
  'bg-emerald-600 dark:bg-emerald-400',
]

function levelFor(count) {
  if (!count) return 0
  if (count === 1) return 1
  if (count <= 3) return 2
  if (count <= 6) return 3
  return 4
}

function buildWeeks() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // Finish on the Saturday of the current week so the last column is complete.
  const end = new Date(today)
  end.setDate(today.getDate() + (6 - today.getDay()))

  const start = new Date(end)
  start.setDate(end.getDate() - (WEEKS * 7 - 1))

  const weeks = []
  const cursor = new Date(start)
  for (let w = 0; w < WEEKS; w++) {
    const week = []
    for (let d = 0; d < 7; d++) {
      week.push(new Date(cursor))
      cursor.setDate(cursor.getDate() + 1)
    }
    weeks.push(week)
  }
  return { weeks, today }
}

export default function ActivityHeatmap({ activity = {} }) {
  const { weeks, today } = useMemo(buildWeeks, [])
  const [hovered, setHovered] = useState(null)

  // Label a column when its month differs from the previous column's month.
  const labels = useMemo(() => {
    let last = -1
    return weeks.map((week) => {
      const m = week[0].getMonth()
      if (m !== last) {
        last = m
        return MONTHS[m]
      }
      return ''
    })
  }, [weeks])

  const totalActive = Object.values(activity).filter((n) => n > 0).length
  const totalActions = Object.values(activity).reduce((s, n) => s + n, 0)

  return (
    <div className="rounded-2xl border border-ink-200 bg-white p-5 dark:border-ink-800 dark:bg-ink-900/40 sm:p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <div className="min-w-0 flex-1 overflow-x-auto pb-1">
          <div className="inline-block">
            {/* Month labels, one slot per week column */}
            <div className="mb-1.5 flex gap-[3px]">
              {labels.map((label, i) => (
                <span
                  key={i}
                  className="w-[11px] shrink-0 whitespace-nowrap text-[11px] leading-none text-ink-400 dark:text-ink-500"
                >
                  {label}
                </span>
              ))}
            </div>

            <div className="flex gap-[3px]">
              {weeks.map((week, wi) => (
                <div key={wi} className="flex flex-col gap-[3px]">
                  {week.map((date) => {
                    const key = dayKey(date)
                    const count = activity[key] ?? 0
                    const future = date > today
                    return (
                      <button
                        key={key}
                        type="button"
                        aria-label={`${count} on ${key}`}
                        onMouseEnter={() => !future && setHovered({ key, count, date })}
                        onFocus={() => !future && setHovered({ key, count, date })}
                        onMouseLeave={() => setHovered(null)}
                        onBlur={() => setHovered(null)}
                        className={`h-[11px] w-[11px] rounded-[2px] transition ${
                          future ? 'bg-transparent' : LEVELS[levelFor(count)]
                        } ${hovered?.key === key ? 'ring-2 ring-ink-500' : ''}`}
                      />
                    )
                  })}
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="mt-3 flex items-center gap-1.5 text-[11px] text-ink-400 dark:text-ink-500">
              <span>Less</span>
              {LEVELS.map((c) => (
                <span key={c} className={`h-[11px] w-[11px] rounded-[2px] ${c}`} />
              ))}
              <span>More</span>
            </div>
          </div>
        </div>

        <div className="shrink-0 lg:w-64">
          {hovered ? (
            <div>
              <p className="text-sm font-semibold text-ink-900 dark:text-white">
                {hovered.date.toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
              <p className="mt-1 text-sm text-ink-500 dark:text-ink-400">
                {hovered.count === 0
                  ? 'Nothing recorded on this day.'
                  : `${hovered.count} ${hovered.count === 1 ? 'thing' : 'things'} done: lessons updated or quizzes finished.`}
              </p>
            </div>
          ) : (
            <div>
              <p className="text-sm text-ink-500 dark:text-ink-400">
                Hover over a square to see that day.
              </p>
              <p className="mt-3 text-sm text-ink-600 dark:text-ink-300">
                <strong className="font-semibold text-ink-900 dark:text-white">{totalActions}</strong>{' '}
                {totalActions === 1 ? 'thing' : 'things'} done across{' '}
                <strong className="font-semibold text-ink-900 dark:text-white">{totalActive}</strong>{' '}
                {totalActive === 1 ? 'day' : 'days'}.
              </p>
            </div>
          )}
        </div>
      </div>

      <p className="mt-4 border-t border-ink-100 pt-3 text-xs text-ink-400 dark:border-ink-800 dark:text-ink-500">
        A square fills in when you change a lesson status or finish a quiz. All of it is stored in this
        browser and nowhere else.
      </p>
    </div>
  )
}
