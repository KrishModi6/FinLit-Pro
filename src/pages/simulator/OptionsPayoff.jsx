import { useMemo, useState } from 'react'
import {
  DataTable,
  Flag,
  LessonLink,
  NumberField,
  Panel,
  SelectField,
  Stat,
  Td,
  money,
  num,
  pct,
} from '../../components/ui/SimUI.jsx'
import { getTool } from '../../data/simulator.js'

/**
 * Payoff of a long call or long put at expiration.
 *
 * Deliberately models expiration only. Pricing a contract before expiry needs
 * Black-Scholes and an implied volatility input, which would give the reader a
 * precision this tool has no business implying. What it does show honestly is
 * the hurdle, the maximum loss, and how the same money in shares compares.
 */
const SHARES_PER_CONTRACT = 100

function payoffAt(price, { type, strike, premium, contracts }) {
  const intrinsic = type === 'Call' ? Math.max(0, price - strike) : Math.max(0, strike - price)
  const value = intrinsic * SHARES_PER_CONTRACT * contracts
  const cost = premium * SHARES_PER_CONTRACT * contracts
  return { intrinsic, value, pnl: value - cost }
}

export default function OptionsPayoff() {
  const tool = getTool('options')
  const [type, setType] = useState('Call')
  const [spot, setSpot] = useState(50)
  const [strike, setStrike] = useState(55)
  const [premium, setPremium] = useState(2)
  const [contracts, setContracts] = useState(1)
  const [exit, setExit] = useState(64)

  const valid =
    [spot, strike, premium, contracts, exit].every(Number.isFinite) &&
    spot > 0 &&
    strike > 0 &&
    premium > 0 &&
    contracts >= 1

  const model = useMemo(() => {
    if (!valid) return null
    const cost = premium * SHARES_PER_CONTRACT * contracts
    const breakEven = type === 'Call' ? strike + premium : strike - premium
    const moveNeeded = ((breakEven - spot) / spot) * 100

    const atExit = payoffAt(exit, { type, strike, premium, contracts })
    // Fractional, deliberately. The comparison is "the same money in shares
    // instead", so flooring to whole shares made it unfair whenever the
    // amounts did not divide evenly, and outright wrong when one contract
    // cost less than one share: that floored to zero shares and reported the
    // stock alternative as making exactly $0, which reads as shares having
    // gone nowhere rather than as not having bought any. Fractional shares
    // are widely available anyway.
    const shares = cost / spot
    const stockPnl = shares * (exit - spot)

    // Payoff ladder spanning roughly 40% either side of spot.
    const lo = Math.max(0, spot * 0.6)
    const hi = spot * 1.4
    const ladder = Array.from({ length: 9 }, (_, i) => {
      const p = lo + ((hi - lo) * i) / 8
      return { price: p, ...payoffAt(p, { type, strike, premium, contracts }), stock: shares * (p - spot) }
    })

    return { cost, breakEven, moveNeeded, atExit, shares, stockPnl, ladder }
  }, [valid, type, spot, strike, premium, contracts, exit])

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <div className="mt-10 grid gap-6 lg:grid-cols-[22rem,1fr] lg:items-start">
        <Panel title="The contract">
          <div className="space-y-4">
            <SelectField label="Type" value={type} onChange={setType} options={['Call', 'Put']} />
            <NumberField label="Stock price now" prefix="$" value={spot} onChange={setSpot} step={1} min={0.01} />
            <NumberField label="Strike price" prefix="$" value={strike} onChange={setStrike} step={1} min={0.01} />
            <NumberField
              label="Premium per share"
              prefix="$"
              value={premium}
              onChange={setPremium}
              step={0.05}
              min={0.01}
              hint="Quoted per share. One contract covers 100 of them."
            />
            <NumberField label="Contracts" value={contracts} onChange={setContracts} step={1} min={1} />
            <NumberField
              label="Stock price at expiration"
              prefix="$"
              value={exit}
              onChange={setExit}
              step={1}
              min={0}
              hint="The scenario you want to test."
            />
          </div>
        </Panel>

        {/* min-w-0: grid children default to min-width:auto, which stops the
            tables' overflow-x-auto wrapper from shrinking on narrow screens. */}
        <div className="min-w-0 space-y-6">
          {!valid && (
            <Panel>
              <p className="text-ink-500 dark:text-ink-400">
                Enter positive numbers for the price, strike, premium and contract count.
              </p>
            </Panel>
          )}

          {valid && model && (
            <>
              <div className="grid gap-4 sm:grid-cols-3">
                <Stat label="Total cost" value={money(model.cost, 2)} sub={`${contracts} contract(s)`} />
                <Stat
                  label="Break-even at expiry"
                  value={money(model.breakEven, 2)}
                  sub={`${model.moveNeeded >= 0 ? 'Needs' : 'Allows'} a ${pct(Math.abs(model.moveNeeded))} move`}
                  tone="warn"
                />
                <Stat label="Maximum loss" value={money(model.cost, 2)} sub="100% of the premium" tone="bad" />
              </div>

              <Panel title={`If the stock finishes at ${money(exit, 2)}`}>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Stat
                    label="Option position"
                    value={`${model.atExit.pnl >= 0 ? '+' : ''}${money(model.atExit.pnl, 2)}`}
                    sub={`Contract worth ${money(model.atExit.value, 2)} · ${pct((model.atExit.pnl / model.cost) * 100)} on the position`}
                    tone={model.atExit.pnl > 0 ? 'good' : 'bad'}
                  />
                  <Stat
                    label={`Same ${money(model.cost, 0)} in shares instead`}
                    value={`${model.stockPnl >= 0 ? '+' : ''}${money(model.stockPnl, 2)}`}
                    sub={`${num(model.shares, 2)} shares at ${money(spot, 2)}`}
                    tone={model.stockPnl > 0 ? 'good' : model.stockPnl < 0 ? 'bad' : 'neutral'}
                  />
                </div>

                <ul className="mt-5 space-y-2.5">
                  {model.atExit.pnl <= -model.cost * 0.999 && (
                    <Flag level="bad" title="This scenario is a total loss">
                      The contract finishes out of the money and expires worthless. There is no holding on and
                      waiting for a recovery: the contract simply stops existing.
                    </Flag>
                  )}
                  {model.stockPnl > 0 && model.atExit.pnl < 0 && (
                    <Flag level="warn" title="Right about direction, still a loss">
                      The stock moved your way and the shares would have made {money(model.stockPnl, 2)}. The
                      option still lost money because the move was smaller than the{' '}
                      {pct(Math.abs(model.moveNeeded))} needed to clear break-even. Direction alone does not
                      pay an option buyer.
                    </Flag>
                  )}
                  {model.atExit.pnl > 0 && model.stockPnl > 0 && (
                    <Flag level="info" title="This is what leverage looks like">
                      The option returned {pct((model.atExit.pnl / model.cost) * 100)} against{' '}
                      {pct((model.stockPnl / model.cost) * 100)} for the shares. The same multiplication runs
                      in reverse when you are wrong, which is why the maximum loss line matters more than this
                      one.
                    </Flag>
                  )}
                  <Flag level="info" title="Expiration only">
                    This models the value at expiry. Before then a contract also carries time value, which
                    bleeds away every day. You can be down heavily on an option while the stock is up.
                  </Flag>
                </ul>
              </Panel>

              <Panel title="Payoff across a range of outcomes">
                <DataTable head={['Stock at expiry', 'Option value', 'Option profit/loss', 'Shares instead']}>
                  {model.ladder.map((r) => (
                    <tr key={r.price}>
                      <Td className="font-semibold text-ink-900 dark:text-white">{money(r.price, 2)}</Td>
                      <Td>{money(r.value, 2)}</Td>
                      <Td className={r.pnl > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}>
                        {r.pnl >= 0 ? '+' : ''}
                        {money(r.pnl, 2)}
                      </Td>
                      <Td className="text-ink-500 dark:text-ink-400">
                        {r.stock >= 0 ? '+' : ''}
                        {money(r.stock, 2)}
                      </Td>
                    </tr>
                  ))}
                </DataTable>
                <p className="mt-4 text-sm text-ink-500 dark:text-ink-400">
                  Notice how much of this table is a flat loss of {money(model.cost, 2)}. That band is every
                  outcome where the contract expires worthless, and for most contracts it is wider than people
                  expect.
                </p>
              </Panel>
            </>
          )}

          <LessonLink to={tool.lesson} name={tool.lessonName} />
        </div>
      </div>
    </div>
  )
}
