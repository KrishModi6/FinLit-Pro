import { useMemo, useState } from 'react'

/**
 * Line chart for a price series, with optional overlay lines (moving averages)
 * and a hover readout.
 *
 * Drawn as inline SVG rather than pulling in a charting library: it keeps the
 * bundle small and there is nothing external that can fail to load.
 */
const W = 760
const H = 260
const PAD = { top: 12, right: 8, bottom: 22, left: 46 }

export default function PriceChart({ points, overlays = [], currency = 'USD' }) {
  const [hover, setHover] = useState(null)

  const model = useMemo(() => {
    if (!points?.length) return null
    const closes = points.map((p) => p.c)
    const overlayValues = overlays.flatMap((o) => o.values.filter((v) => v != null))
    const lo = Math.min(...closes, ...overlayValues)
    const hi = Math.max(...closes, ...overlayValues)
    const span = hi - lo || 1
    const pad = span * 0.06

    const min = lo - pad
    const max = hi + pad
    const plotW = W - PAD.left - PAD.right
    const plotH = H - PAD.top - PAD.bottom

    const x = (i) => PAD.left + (i / (points.length - 1 || 1)) * plotW
    const y = (v) => PAD.top + (1 - (v - min) / (max - min)) * plotH

    const path = (values) => {
      let d = ''
      let started = false
      values.forEach((v, i) => {
        if (v == null || !Number.isFinite(v)) {
          started = false
          return
        }
        d += `${started ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)} `
        started = true
      })
      return d.trim()
    }

    const ticks = [min + (max - min) * 0.05, (min + max) / 2, max - (max - min) * 0.05]

    return { x, y, min, max, path, ticks, plotW, plotH, closes }
  }, [points, overlays])

  if (!model) return null

  const fmt = (v) =>
    v.toLocaleString('en-US', {
      style: 'currency',
      currency,
      maximumFractionDigits: v < 10 ? 2 : 0,
    })

  const first = points[0].c
  const last = points[points.length - 1].c
  const rising = last >= first
  const stroke = rising ? 'stroke-emerald-500' : 'stroke-rose-500'
  const fill = rising ? 'fill-emerald-500/10' : 'fill-rose-500/10'

  const onMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const rel = ((e.clientX - rect.left) / rect.width) * W
    const i = Math.round(
      ((rel - PAD.left) / (W - PAD.left - PAD.right)) * (points.length - 1)
    )
    if (i >= 0 && i < points.length) setHover(i)
  }

  const areaPath =
    `M${model.x(0).toFixed(1)},${(H - PAD.bottom).toFixed(1)} ` +
    model.path(model.closes).replace(/^M/, 'L') +
    ` L${model.x(points.length - 1).toFixed(1)},${(H - PAD.bottom).toFixed(1)} Z`

  return (
    <div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full touch-none"
        onMouseMove={onMove}
        onMouseLeave={() => setHover(null)}
        role="img"
        aria-label={`Price chart, ${fmt(first)} to ${fmt(last)}`}
      >
        {model.ticks.map((t) => (
          <g key={t}>
            <line
              x1={PAD.left}
              x2={W - PAD.right}
              y1={model.y(t)}
              y2={model.y(t)}
              className="stroke-ink-200 dark:stroke-ink-800"
              strokeWidth="1"
            />
            <text
              x={PAD.left - 6}
              y={model.y(t) + 3.5}
              textAnchor="end"
              className="fill-ink-400 text-[10px] tabular-nums dark:fill-ink-500"
            >
              {fmt(t)}
            </text>
          </g>
        ))}

        <path d={areaPath} className={`${fill} stroke-none`} />
        <path d={model.path(model.closes)} className={`fill-none ${stroke}`} strokeWidth="1.8" />

        {overlays.map((o) => (
          <path
            key={o.label}
            d={model.path(o.values)}
            className={`fill-none ${o.className}`}
            strokeWidth="1.3"
            strokeDasharray={o.dashed ? '5 4' : undefined}
          />
        ))}

        {hover != null && (
          <g>
            <line
              x1={model.x(hover)}
              x2={model.x(hover)}
              y1={PAD.top}
              y2={H - PAD.bottom}
              className="stroke-ink-400 dark:stroke-ink-500"
              strokeWidth="1"
              strokeDasharray="3 3"
            />
            <circle
              cx={model.x(hover)}
              cy={model.y(points[hover].c)}
              r="3.5"
              className="fill-white stroke-ink-900 dark:fill-ink-900 dark:stroke-white"
              strokeWidth="2"
            />
          </g>
        )}
      </svg>

      <div className="mt-2 flex flex-wrap items-center justify-between gap-x-6 gap-y-2 text-xs text-ink-500 dark:text-ink-400">
        <div className="flex flex-wrap items-center gap-4">
          <span className="inline-flex items-center gap-2">
            <span className={`h-0.5 w-5 ${rising ? 'bg-emerald-500' : 'bg-rose-500'}`} /> Close
          </span>
          {overlays.map((o) => (
            <span key={o.label} className="inline-flex items-center gap-2">
              <span
                className={`h-0.5 w-5 ${o.legendClass}`}
                style={o.dashed ? { backgroundImage: 'none' } : undefined}
              />
              {o.label}
            </span>
          ))}
        </div>
        <span className="tabular-nums">
          {hover != null
            ? `${new Date(points[hover].t).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })} · ${fmt(points[hover].c)}`
            : 'Hover the chart for a date'}
        </span>
      </div>
    </div>
  )
}
