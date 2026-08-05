import { useMemo, useState } from 'react'
import {
  DataTable,
  Flag,
  LessonLink,
  NumberField,
  Panel,
  Stat,
  Td,
  money,
  pct,
} from '../../components/ui/SimUI.jsx'
import { getTool } from '../../data/simulator.js'

/**
 * Monte Carlo projection.
 *
 * Deliberately NOT called a predictor. It draws thousands of random return
 * paths from a normal distribution around the return and volatility you supply,
 * then shows the spread. The point it exists to make is that a single "average
 * return" number hides an enormous range of real outcomes.
 *
 * Seeded so the same inputs always give the same picture, rather than the
 * numbers twitching on every keystroke.
 */
function mulberry32(seed) {
  return function () {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Box-Muller transform: two uniforms in, one standard normal out. */
function normal(rand) {
  let u = 0
  let v = 0
  while (u === 0) u = rand()
  while (v === 0) v = rand()
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
}

const RUNS = 2000

function simulate({ start, annual, mean, vol, years }) {
  const rand = mulberry32(20260805)
  const finals = []
  let everBelowStart = 0
  let worstDrawdownRun = 0

  for (let i = 0; i < RUNS; i++) {
    let bal = start
    let peak = start
    let maxDd = 0
    for (let y = 0; y < years; y++) {
      const r = mean / 100 + (vol / 100) * normal(rand)
      bal = bal * (1 + r) + annual
      if (bal > peak) peak = bal
      const dd = (peak - bal) / peak
      if (dd > maxDd) maxDd = dd
    }
    finals.push(bal)
    if (bal < start + annual * years) everBelowStart++
    worstDrawdownRun += maxDd
  }

  finals.sort((a, b) => a - b)
  const at = (p) => finals[Math.min(finals.length - 1, Math.floor((p / 100) * finals.length))]

  return {
    contributed: start + annual * years,
    p5: at(5),
    p10: at(10),
    p25: at(25),
    p50: at(50),
    p75: at(75),
    p90: at(90),
    worst: finals[0],
    best: finals[finals.length - 1],
    lossOdds: (everBelowStart / RUNS) * 100,
    avgMaxDrawdown: (worstDrawdownRun / RUNS) * 100,
    finals,
  }
}

export default function ScenarioProjector() {
  const tool = getTool('scenarios')
  const [start, setStart] = useState(5000)
  const [annual, setAnnual] = useState(2400)
  const [mean, setMean] = useState(8)
  const [vol, setVol] = useState(16)
  const [years, setYears] = useState(20)

  const valid =
    [start, annual, mean, vol, years].every(Number.isFinite) && years >= 1 && years <= 50 && vol >= 0

  const sim = useMemo(() => (valid ? simulate({ start, annual, mean, vol, years }) : null), [
    valid,
    start,
    annual,
    mean,
    vol,
    years,
  ])

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <div className="mt-10 grid gap-6 lg:grid-cols-[22rem,1fr] lg:items-start">
        <Panel title="Assumptions">
          <div className="space-y-4">
            <NumberField label="Starting value" prefix="$" value={start} onChange={setStart} step={500} min={0} />
            <NumberField label="Added each year" prefix="$" value={annual} onChange={setAnnual} step={100} min={0} />
            <NumberField label="Average annual return" suffix="%" value={mean} onChange={setMean} step={0.5} />
            <NumberField
              label="Volatility"
              suffix="%"
              value={vol}
              onChange={setVol}
              step={1}
              min={0}
              hint="Standard deviation of annual returns. Broad stock indices have historically run near 15 to 20."
            />
            <NumberField label="Years" value={years} onChange={setYears} step={1} min={1} max={50} />
          </div>
          <p className="mt-4 text-xs text-ink-400 dark:text-ink-500">
            {RUNS.toLocaleString()} randomised runs, drawn from a normal distribution. Real markets have
            fatter tails than this model, so treat the bad end as optimistic.
          </p>
        </Panel>

        {/* min-w-0: grid children default to min-width:auto, which stops the
            tables' overflow-x-auto wrapper from shrinking on narrow screens. */}
        <div className="min-w-0 space-y-6">
          {!valid && (
            <Panel>
              <p className="text-ink-500 dark:text-ink-400">
                Fill in every field, with 1 to 50 years and a volatility of zero or more.
              </p>
            </Panel>
          )}

          {valid && sim && (
            <>
              <div className="grid gap-4 sm:grid-cols-3">
                <Stat label="Median outcome" value={money(sim.p50)} sub="Half of runs finished above this" />
                <Stat label="Bad case (10th percentile)" value={money(sim.p10)} sub="1 run in 10 did worse" tone="bad" />
                <Stat label="Good case (90th percentile)" value={money(sim.p90)} sub="1 run in 10 did better" tone="good" />
              </div>

              <Panel title="The full spread">
                <DataTable head={['Percentile', 'Ending value', 'vs money you put in']}>
                  {[
                    ['Worst run', sim.worst],
                    ['5th', sim.p5],
                    ['10th', sim.p10],
                    ['25th', sim.p25],
                    ['50th (median)', sim.p50],
                    ['75th', sim.p75],
                    ['90th', sim.p90],
                    ['Best run', sim.best],
                  ].map(([label, value]) => {
                    const multiple = value / sim.contributed
                    return (
                      <tr key={label}>
                        <Td className="font-medium text-ink-900 dark:text-white">{label}</Td>
                        <Td>{money(value)}</Td>
                        <Td className={multiple >= 1 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}>
                          {multiple.toFixed(2)}x
                        </Td>
                      </tr>
                    )
                  })}
                </DataTable>
                <p className="mt-4 text-sm text-ink-500 dark:text-ink-400">
                  You would contribute {money(sim.contributed)} across {years} years. The gap between the
                  10th and 90th percentile is {money(sim.p90 - sim.p10)}, and every one of those futures came
                  from the same assumptions.
                </p>
              </Panel>

              <Panel title="What this actually shows">
                <ul className="space-y-2.5">
                  <Flag level="warn" title={`In ${pct(sim.lossOdds, 0)} of runs you ended with less than you put in`}>
                    Same average return, same contributions. The difference is purely the order in which good
                    and bad years arrived, which is the thing nobody can control or predict.
                  </Flag>
                  <Flag level="info" title={`The average run's worst drawdown was ${pct(sim.avgMaxDrawdown, 0)}`}>
                    That is the peak-to-trough fall you would have had to sit through without selling. The
                    plan only works if you can actually tolerate that, which is a question about you rather
                    than about the maths.
                  </Flag>
                  <Flag level="info" title="A single average return is a bad way to plan">
                    A calculator that returns one tidy number is showing you roughly the median line of this
                    distribution and hiding everything either side of it. The spread is the real answer.
                  </Flag>
                  <Flag level="bad" title="This model is friendlier than reality">
                    Normal distributions understate how often extreme years happen. Real markets crash harder
                    and more often than this simulation will show you, and it assumes you never panic-sell,
                    never lose income, and never need the money early.
                  </Flag>
                </ul>
              </Panel>

              <LessonLink to={tool.lesson} name={tool.lessonName} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
