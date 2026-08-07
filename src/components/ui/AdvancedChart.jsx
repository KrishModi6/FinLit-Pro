import { useCallback, useMemo, useRef, useState } from 'react'
import { bollinger, formatMoney, rsi, sma } from '../../data/market.js'

/**
 * Candlestick chart with the indicator stack the old Streamlit app had:
 * SMA 20 and 50, Bollinger Bands, a volume panel and an RSI panel, plus
 * drag-to-zoom and scroll-to-zoom.
 *
 * Drawn as one inline SVG rather than a charting library. That keeps the
 * bundle small, means nothing external can fail to load, and lets the whole
 * thing inherit the site's palette in both light and dark themes.
 *
 * Indicators are computed over the FULL series and only then sliced to the
 * visible window. Computing them after slicing would make the leftmost values
 * wrong, because a 50-period average needs 50 prior bars whether or not you
 * are currently looking at them.
 */

const DAY_MS = 86_400_000

// viewBox units. Three stacked panels sharing one x axis.
const W = 1000
const M = { left: 56, right: 12, top: 10 }
const PRICE_H = 330
const VOL_TOP = 366
const VOL_H = 84
const RSI_TOP = 484
const RSI_H = 92
const H = RSI_TOP + RSI_H + 30

const SERIES = [
  { key: 'price', label: 'Price', swatch: 'bg-gradient-to-r from-emerald-500 to-rose-500' },
  { key: 'sma20', label: 'SMA 20', swatch: 'bg-sky-400' },
  { key: 'sma50', label: 'SMA 50', swatch: 'bg-violet-400' },
  { key: 'bb', label: 'Bollinger', swatch: 'bg-indigo-300' },
  { key: 'volume', label: 'Volume', swatch: 'bg-emerald-500/60' },
  { key: 'rsi', label: 'RSI', swatch: 'bg-pink-500' },
]

export default function AdvancedChart({ points, currency = 'USD' }) {
  const svgRef = useRef(null)
  const [range, setRange] = useState(null) // [start, end] or null for all
  const [drag, setDrag] = useState(null) // { from, to } in index space
  const [hover, setHover] = useState(null)
  const [on, setOn] = useState({
    price: true,
    sma20: true,
    sma50: true,
    bb: true,
    volume: true,
    rsi: true,
  })

  // Indicators over the whole series, computed once.
  const full = useMemo(() => {
    const closes = points.map((p) => p.c)
    return {
      closes,
      sma20: sma(closes, 20),
      sma50: sma(closes, 50),
      bb: bollinger(closes, 20, 2),
      rsi: rsi(closes, 14),
    }
  }, [points])

  // How far apart the bars are, taken as the median gap so a weekend or a
  // holiday does not skew it. This drives the axis labels: five-minute bars
  // want clock times, monthly bars want years. Deriving it from the spacing
  // rather than the total span means zooming in does not suddenly start
  // labelling daily bars with times they do not have.
  const barMs = useMemo(() => {
    if (points.length < 2) return DAY_MS
    const gaps = []
    for (let i = 1; i < Math.min(points.length, 60); i++) gaps.push(points[i].t - points[i - 1].t)
    gaps.sort((a, b) => a - b)
    return gaps[Math.floor(gaps.length / 2)] || DAY_MS
  }, [points])
  const intradayBars = barMs < DAY_MS

  const [lo, hi] = range ?? [0, points.length - 1]
  const view = useMemo(() => {
    const slice = (a) => a.slice(lo, hi + 1)
    return {
      pts: points.slice(lo, hi + 1),
      sma20: slice(full.sma20),
      sma50: slice(full.sma50),
      bbUpper: slice(full.bb.upper),
      bbLower: slice(full.bb.lower),
      rsi: slice(full.rsi),
    }
  }, [points, full, lo, hi])

  const scale = useMemo(() => {
    const n = view.pts.length
    if (!n) return null

    const plotW = W - M.left - M.right
    const band = plotW / n
    const x = (i) => M.left + band * (i + 0.5)

    // Price extent must include whatever overlays are switched on, or a line
    // can leave the panel.
    let min = Infinity
    let max = -Infinity
    view.pts.forEach((p) => {
      if (p.l < min) min = p.l
      if (p.h > max) max = p.h
    })
    const consider = (arr) =>
      arr.forEach((v) => {
        if (v == null) return
        if (v < min) min = v
        if (v > max) max = v
      })
    if (on.sma20) consider(view.sma20)
    if (on.sma50) consider(view.sma50)
    if (on.bb) {
      consider(view.bbUpper)
      consider(view.bbLower)
    }
    const pad = (max - min) * 0.06 || 1
    min -= pad
    max += pad

    const y = (v) => M.top + (1 - (v - min) / (max - min)) * PRICE_H
    const maxVol = Math.max(1, ...view.pts.map((p) => p.v ?? 0))
    const vy = (v) => VOL_TOP + VOL_H - (v / maxVol) * VOL_H
    const ry = (v) => RSI_TOP + (1 - v / 100) * RSI_H

    return { x, y, vy, ry, band, min, max, maxVol, n }
  }, [view, on])

  // Axis ticks drop the cents on anything above 10, because three whole
  // numbers up the side read faster than three with decimals.
  const fmt = useCallback((v) => formatMoney(v, { currency, dp: 'auto' }), [currency])

  // The OHLC readout always keeps the cents. A five-minute bar often moves
  // less than a dollar, so rounding collapses open, high, low and close into
  // the same number and the readout says nothing.
  const fmtExact = useCallback((v) => formatMoney(v, { currency, dp: 2 }), [currency])

  /** Pointer x in viewBox units to an index in the visible window. */
  const idxFromEvent = useCallback(
    (e) => {
      const rect = svgRef.current?.getBoundingClientRect()
      if (!rect || !scale) return null
      const vx = ((e.clientX - rect.left) / rect.width) * W
      const i = Math.round((vx - M.left) / scale.band - 0.5)
      return Math.max(0, Math.min(scale.n - 1, i))
    },
    [scale]
  )

  const onDown = (e) => {
    const i = idxFromEvent(e)
    if (i != null) setDrag({ from: i, to: i })
  }
  const onMove = (e) => {
    const i = idxFromEvent(e)
    if (i == null) return
    setHover(i)
    if (drag) setDrag((d) => ({ ...d, to: i }))
  }
  const onUp = () => {
    if (drag) {
      const a = Math.min(drag.from, drag.to)
      const b = Math.max(drag.from, drag.to)
      // Ignore an accidental click; require a few bars of selection.
      if (b - a >= 4) setRange([lo + a, lo + b])
      setDrag(null)
    }
  }
  const onWheel = (e) => {
    if (!scale) return
    e.preventDefault()
    const i = idxFromEvent(e)
    if (i == null) return
    const anchor = lo + i
    const span = hi - lo
    const next = Math.round(span * (e.deltaY > 0 ? 1.25 : 0.8))
    const clamped = Math.max(20, Math.min(points.length - 1, next))
    const frac = span > 0 ? (anchor - lo) / span : 0.5
    let nLo = Math.round(anchor - clamped * frac)
    let nHi = nLo + clamped
    if (nLo < 0) {
      nLo = 0
      nHi = clamped
    }
    if (nHi > points.length - 1) {
      nHi = points.length - 1
      nLo = Math.max(0, nHi - clamped)
    }
    setRange(nLo === 0 && nHi === points.length - 1 ? null : [nLo, nHi])
  }

  if (!scale) return null

  const path = (arr) => {
    let d = ''
    let started = false
    arr.forEach((v, i) => {
      if (v == null || !Number.isFinite(v)) {
        started = false
        return
      }
      d += `${started ? 'L' : 'M'}${scale.x(i).toFixed(1)},${scale.y(v).toFixed(1)} `
      started = true
    })
    return d.trim()
  }

  // Bollinger band as one filled shape: upper left-to-right, lower back.
  const bbBand = (() => {
    const up = []
    const dn = []
    view.bbUpper.forEach((v, i) => {
      if (v == null || view.bbLower[i] == null) return
      up.push(`${scale.x(i).toFixed(1)},${scale.y(v).toFixed(1)}`)
      dn.unshift(`${scale.x(i).toFixed(1)},${scale.y(view.bbLower[i]).toFixed(1)}`)
    })
    return up.length ? `M${up.join('L')}L${dn.join('L')}Z` : ''
  })()

  const priceTicks = [scale.min, (scale.min + scale.max) / 2, scale.max].map((v) => ({
    v,
    y: scale.y(v),
  }))

  // Label format follows the bar size and how much time is on screen. Times
  // for a single intraday session, dates once it spans days, years once it
  // spans a long stretch, so the four labels never all read the same.
  const visibleSpan = scale.n > 1 ? view.pts[scale.n - 1].t - view.pts[0].t : 0
  const labelFmt = intradayBars
    ? visibleSpan <= 1.5 * DAY_MS
      ? { hour: 'numeric', minute: '2-digit' }
      : { month: 'short', day: 'numeric' }
    : visibleSpan < 75 * DAY_MS
      ? { month: 'short', day: 'numeric' }
      : { month: 'short', year: '2-digit' }

  const dateLabels = [0, Math.floor(scale.n / 3), Math.floor((2 * scale.n) / 3), scale.n - 1]
    .filter((i, k, a) => a.indexOf(i) === k)
    .map((i) => ({ i, text: new Date(view.pts[i].t).toLocaleString('en-US', labelFmt) }))

  const candleW = Math.max(1, Math.min(9, scale.band * 0.65))
  const hovered = hover != null && hover < view.pts.length ? view.pts[hover] : null
  const zoomed = range != null

  return (
    <div>
      {/* Legend, doubling as visibility toggles */}
      <div className="mb-2 flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
        {SERIES.map((s) => (
          <button
            key={s.key}
            type="button"
            onClick={() => setOn((o) => ({ ...o, [s.key]: !o[s.key] }))}
            aria-pressed={on[s.key]}
            className={`inline-flex items-center gap-1.5 text-xs transition ${
              on[s.key] ? 'text-ink-700 dark:text-ink-200' : 'text-ink-300 dark:text-ink-600'
            }`}
          >
            <span className={`h-2 w-4 rounded-sm ${s.swatch} ${on[s.key] ? '' : 'opacity-30'}`} />
            {s.label}
          </button>
        ))}
      </div>

      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        className="w-full cursor-crosshair select-none"
        onMouseDown={onDown}
        onMouseMove={onMove}
        onMouseUp={onUp}
        onMouseLeave={() => {
          setHover(null)
          setDrag(null)
        }}
        onWheel={onWheel}
        role="img"
        aria-label={`Candlestick chart with moving averages, volume and RSI, showing ${scale.n} periods`}
      >
        {/* ---- price panel ---- */}
        {priceTicks.map((t) => (
          <g key={`p${t.v}`}>
            <line
              x1={M.left}
              x2={W - M.right}
              y1={t.y}
              y2={t.y}
              className="stroke-ink-200 dark:stroke-ink-800"
              strokeWidth="1"
            />
            <text
              x={M.left - 6}
              y={t.y + 3.5}
              textAnchor="end"
              className="fill-ink-400 text-[10px] tabular-nums dark:fill-ink-500"
            >
              {fmt(t.v)}
            </text>
          </g>
        ))}

        {on.bb && bbBand && (
          <path d={bbBand} className="fill-indigo-400/10 stroke-indigo-300/60 dark:stroke-indigo-400/40" strokeWidth="1" />
        )}

        {on.price &&
          view.pts.map((p, i) => {
            const up = p.c >= p.o
            const cls = up ? 'stroke-emerald-500 fill-emerald-500' : 'stroke-rose-500 fill-rose-500'
            const yO = scale.y(p.o)
            const yC = scale.y(p.c)
            const top = Math.min(yO, yC)
            const h = Math.max(1, Math.abs(yC - yO))
            return (
              <g key={p.t} className={cls}>
                <line
                  x1={scale.x(i)}
                  x2={scale.x(i)}
                  y1={scale.y(p.h)}
                  y2={scale.y(p.l)}
                  strokeWidth="1"
                />
                <rect x={scale.x(i) - candleW / 2} y={top} width={candleW} height={h} />
              </g>
            )
          })}

        {on.sma20 && <path d={path(view.sma20)} className="fill-none stroke-sky-400" strokeWidth="1.6" />}
        {on.sma50 && <path d={path(view.sma50)} className="fill-none stroke-violet-400" strokeWidth="1.6" />}

        {/* ---- volume panel ---- */}
        {on.volume &&
          view.pts.map((p, i) => {
            if (!p.v) return null
            const up = p.c >= p.o
            return (
              <rect
                key={`v${p.t}`}
                x={scale.x(i) - candleW / 2}
                y={scale.vy(p.v)}
                width={candleW}
                height={VOL_TOP + VOL_H - scale.vy(p.v)}
                className={up ? 'fill-emerald-500/60' : 'fill-rose-500/60'}
              />
            )
          })}
        <text
          x={M.left - 6}
          y={VOL_TOP + 10}
          textAnchor="end"
          className="fill-ink-400 text-[10px] dark:fill-ink-500"
        >
          Vol
        </text>

        {/* ---- RSI panel ---- */}
        {on.rsi && (
          <>
            {[70, 30].map((lvl) => (
              <line
                key={lvl}
                x1={M.left}
                x2={W - M.right}
                y1={scale.ry(lvl)}
                y2={scale.ry(lvl)}
                className={lvl === 70 ? 'stroke-rose-400/60' : 'stroke-emerald-400/60'}
                strokeWidth="1"
                strokeDasharray="5 4"
              />
            ))}
            <path
              d={(() => {
                let d = ''
                let started = false
                view.rsi.forEach((v, i) => {
                  if (v == null) {
                    started = false
                    return
                  }
                  d += `${started ? 'L' : 'M'}${scale.x(i).toFixed(1)},${scale.ry(v).toFixed(1)} `
                  started = true
                })
                return d.trim()
              })()}
              className="fill-none stroke-pink-500"
              strokeWidth="1.5"
            />
            {[70, 30].map((lvl) => (
              <text
                key={`t${lvl}`}
                x={M.left - 6}
                y={scale.ry(lvl) + 3.5}
                textAnchor="end"
                className="fill-ink-400 text-[10px] tabular-nums dark:fill-ink-500"
              >
                {lvl}
              </text>
            ))}
          </>
        )}

        {/* ---- date axis ---- */}
        {dateLabels.map((d) => (
          <text
            key={d.i}
            x={scale.x(d.i)}
            y={H - 8}
            textAnchor="middle"
            className="fill-ink-400 text-[10px] dark:fill-ink-500"
          >
            {d.text}
          </text>
        ))}

        {/* ---- drag selection ---- */}
        {drag && Math.abs(drag.to - drag.from) >= 1 && (
          <rect
            x={scale.x(Math.min(drag.from, drag.to)) - scale.band / 2}
            y={M.top}
            width={Math.abs(drag.to - drag.from) * scale.band}
            height={RSI_TOP + RSI_H - M.top}
            className="fill-sky-500/15 stroke-sky-500/50"
            strokeWidth="1"
          />
        )}

        {/* ---- crosshair ---- */}
        {hovered && !drag && (
          <line
            x1={scale.x(hover)}
            x2={scale.x(hover)}
            y1={M.top}
            y2={RSI_TOP + RSI_H}
            className="stroke-ink-400 dark:stroke-ink-500"
            strokeWidth="1"
            strokeDasharray="3 3"
          />
        )}
      </svg>

      <div className="mt-2 flex flex-wrap items-center justify-between gap-x-6 gap-y-2 text-xs text-ink-500 dark:text-ink-400">
        <span>
          {zoomed ? (
            <button
              type="button"
              onClick={() => setRange(null)}
              className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400"
            >
              Reset zoom
            </button>
          ) : (
            'Drag across the chart to zoom, or scroll on it'
          )}
        </span>
        <span className="tabular-nums">
          {hovered
            ? `${new Date(hovered.t).toLocaleString(
                'en-US',
                intradayBars
                  ? { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
                  : { month: 'short', day: 'numeric', year: 'numeric' }
              )}  O ${fmtExact(hovered.o)}  H ${fmtExact(hovered.h)}  L ${fmtExact(hovered.l)}  C ${fmtExact(hovered.c)}`
            : `${scale.n} periods shown`}
        </span>
      </div>
    </div>
  )
}
