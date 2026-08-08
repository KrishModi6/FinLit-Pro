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
 * Compound growth with regular contributions, plus the fee drag comparison.
 *
 * Compounds monthly at the effective monthly rate derived from the annual rate,
 * (1 + r)^(1/12) - 1, rather than the naive r/12. Contributions are added at
 * the end of each month.
 */
function project({ initial, monthly, annualReturn, years, fee }) {
  const netAnnual = (annualReturn - fee) / 100
  const monthlyRate = Math.pow(1 + netAnnual, 1 / 12) - 1

  let balance = initial
  let contributed = initial
  const rows = []

  for (let m = 1; m <= years * 12; m++) {
    balance = balance * (1 + monthlyRate) + monthly
    contributed += monthly
    if (m % 12 === 0) {
      rows.push({ year: m / 12, balance, contributed, growth: balance - contributed })
    }
  }

  return { final: balance, contributed, growth: balance - contributed, rows }
}

export default function GrowthCalculator() {
  const tool = getTool('growth')
  const [initial, setInitial] = useState(1000)
  const [monthly, setMonthly] = useState(100)
  const [annualReturn, setAnnualReturn] = useState(8)
  const [years, setYears] = useState(30)
  const [fee, setFee] = useState(0.03)

  // The net return has to stay above -100%. Below that, compounding it into a
  // monthly rate takes the twelfth root of a negative number, which is NaN,
  // and the NaN then spreads silently into every figure and the chart.
  // Losing more than everything is not a scenario worth modelling anyway.
  const allNumbers = [initial, monthly, annualReturn, years, fee].every(Number.isFinite)
  const valid = allNumbers && years > 0 && years <= 70 && annualReturn - fee > -100

  // Say which rule was broken. A single catch-all message told a reader who
  // had filled in every field and used a sensible number of years to go and
  // do exactly that, which is no help at all.
  const problem = !allNumbers
    ? 'Fill in every field with a number to see a projection.'
    : years <= 0 || years > 70
      ? 'Use between 1 and 70 years to see a projection.'
      : 'A return of less than -100% after fees would lose more than there is to lose, so there is nothing to project. Raise the return or lower the fee.'

  const result = useMemo(
    () => (valid ? project({ initial, monthly, annualReturn, years, fee }) : null),
    [valid, initial, monthly, annualReturn, years, fee]
  )

  // Same inputs with no fee, to price the fee itself.
  const noFee = useMemo(
    () => (valid ? project({ initial, monthly, annualReturn, years, fee: 0 }) : null),
    [valid, initial, monthly, annualReturn, years]
  )

  const feeCost = result && noFee ? noFee.final - result.final : NaN
  const growthShare = result ? (result.growth / result.final) * 100 : NaN

  // Simple area chart of balance vs money actually put in.
  const chart = useMemo(() => {
    if (!result || !result.rows.length) return null
    const max = result.final
    const pts = (key) =>
      result.rows
        .map((r, i) => `${(i / (result.rows.length - 1 || 1)) * 100},${100 - (r[key] / max) * 100}`)
        .join(' ')
    return { balance: pts('balance'), contributed: pts('contributed') }
  }, [result])

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <div className="mt-10 grid gap-6 lg:grid-cols-[22rem,1fr] lg:items-start">
        <Panel title="Assumptions">
          <div className="space-y-4">
            <NumberField label="Starting amount" prefix="$" value={initial} onChange={setInitial} step={100} min={0} />
            <NumberField
              label="Added every month"
              prefix="$"
              value={monthly}
              onChange={setMonthly}
              step={25}
              min={0}
            />
            <NumberField
              label="Annual return"
              suffix="%"
              value={annualReturn}
              onChange={setAnnualReturn}
              step={0.5}
              hint="A hypothetical average. Real returns are nothing like this smooth."
            />
            <NumberField label="Years invested" value={years} onChange={setYears} step={1} min={1} max={70} />
            <NumberField
              label="Annual fee"
              suffix="%"
              value={fee}
              onChange={setFee}
              step={0.01}
              min={0}
              hint="A broad index fund is often near 0.03%. An active fund can be 0.75% or more."
            />
          </div>
        </Panel>

        {/* min-w-0: grid children default to min-width:auto, which stops the
            tables' overflow-x-auto wrapper from shrinking on narrow screens. */}
        <div className="min-w-0 space-y-6">
          {!valid && (
            <Panel>
              <p className="text-ink-500 dark:text-ink-400">{problem}</p>
            </Panel>
          )}

          {valid && result && (
            <>
              <div className="grid gap-4 sm:grid-cols-3">
                <Stat label="Ending balance" value={money(result.final)} tone="good" />
                <Stat label="You put in" value={money(result.contributed)} sub="Your own money" />
                <Stat
                  label="Growth"
                  value={money(result.growth)}
                  sub={`${pct(growthShare)} of the final balance`}
                  tone="good"
                />
              </div>

              <Panel title="Balance over time">
                {chart && (
                  <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="h-52 w-full" role="img"
                       aria-label={`Balance grows to ${money(result.final)} after ${years} years`}>
                    <polyline
                      points={`0,100 ${chart.balance} 100,100`}
                      className="fill-emerald-500/20 stroke-none"
                    />
                    <polyline points={chart.balance} className="fill-none stroke-emerald-500" strokeWidth="1.5"
                              vectorEffect="non-scaling-stroke" />
                    <polyline points={chart.contributed} className="fill-none stroke-ink-400" strokeWidth="1.5"
                              strokeDasharray="4 3" vectorEffect="non-scaling-stroke" />
                  </svg>
                )}
                <div className="mt-3 flex flex-wrap gap-5 text-xs text-ink-500 dark:text-ink-400">
                  <span className="inline-flex items-center gap-2">
                    <span className="h-0.5 w-5 bg-emerald-500" /> Balance
                  </span>
                  <span className="inline-flex items-center gap-2">
                    <span className="h-0.5 w-5 border-t-2 border-dashed border-ink-400" /> Money you put in
                  </span>
                </div>
              </Panel>

              <Panel title="What the numbers say">
                <ul className="space-y-2.5">
                  {Number.isFinite(feeCost) && feeCost > 1 && (
                    <Flag level={feeCost > result.contributed * 0.5 ? 'bad' : 'warn'} title={`That ${pct(fee, 2)} fee costs you ${money(feeCost)}`}>
                      With no fee at all, the same assumptions end at {money(noFee.final)}. The fee is charged
                      on the whole balance every year, including on growth you would otherwise have kept, so
                      it compounds against you.
                    </Flag>
                  )}
                  {growthShare > 50 && (
                    <Flag level="good" title="Growth is now doing more work than you are">
                      {pct(growthShare)} of the ending balance is growth rather than money you deposited. That
                      crossover is the entire argument for a long time horizon.
                    </Flag>
                  )}
                  {years >= 20 && result.rows.length >= 20 && (
                    <Flag level="info" title="The last decade is the one that matters">
                      Between year {years - 10} and year {years} the balance grows by{' '}
                      {money(result.final - result.rows[result.rows.length - 11].balance)}. Compounding is
                      back-loaded, which is why starting early beats contributing more later.
                    </Flag>
                  )}
                  <Flag level="warn" title="A steady annual return does not exist">
                    This model applies {pct(annualReturn)} every single year. Real markets deliver that as an
                    average across violent up and down years, and the order those years arrive in changes the
                    outcome.
                  </Flag>
                </ul>
              </Panel>

              <Panel title="Year by year">
                <DataTable head={['Year', 'Balance', 'You put in', 'Growth']}>
                  {result.rows
                    .filter((r, i) => result.rows.length <= 15 || r.year % 5 === 0 || i === result.rows.length - 1)
                    .map((r) => (
                      <tr key={r.year}>
                        <Td className="font-semibold text-ink-900 dark:text-white">{r.year}</Td>
                        <Td>{money(r.balance)}</Td>
                        <Td className="text-ink-500 dark:text-ink-400">{money(r.contributed)}</Td>
                        <Td className="text-emerald-600 dark:text-emerald-400">{money(r.growth)}</Td>
                      </tr>
                    ))}
                </DataTable>
              </Panel>
            </>
          )}

          <LessonLink to={tool.lesson} name={tool.lessonName} />
        </div>
      </div>
    </div>
  )
}
