import { useEffect, useMemo, useState } from 'react'
import {
  DataTable,
  Flag,
  LessonLink,
  Panel,
  Stat,
  Td,
  money,
  num,
  pct,
} from '../../components/ui/SimUI.jsx'
import { SECTORS, getTool } from '../../data/simulator.js'
import { CloseIcon } from '../../components/ui/Icons.jsx'

const STORAGE_KEY = 'stockguide:sim:portfolio:v1'

const STARTER = [
  { id: 1, name: 'Broad index fund', amount: 6000, sector: 'Broad Index Fund', beta: 1 },
  { id: 2, name: 'Large tech company', amount: 2500, sector: 'Technology', beta: 1.3 },
  { id: 3, name: 'Speculative small cap', amount: 1500, sector: 'Technology', beta: 2.4 },
]

export default function PortfolioBuilder() {
  const tool = getTool('portfolio')
  const [rows, setRows] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed) && parsed.length) return parsed
      }
    } catch {
      /* fall through to the starter portfolio */
    }
    return STARTER
  })

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(rows))
    } catch {
      /* storage blocked; the tool still works for this session */
    }
  }, [rows])

  const update = (id, patch) => setRows((rs) => rs.map((r) => (r.id === id ? { ...r, ...patch } : r)))
  const remove = (id) => setRows((rs) => rs.filter((r) => r.id !== id))
  const add = () =>
    setRows((rs) => [
      ...rs,
      { id: Math.max(0, ...rs.map((r) => r.id)) + 1, name: '', amount: 1000, sector: 'Other', beta: 1 },
    ])

  const analysis = useMemo(() => {
    const valid = rows.filter((r) => Number.isFinite(r.amount) && r.amount > 0)
    const total = valid.reduce((s, r) => s + r.amount, 0)
    if (!total) return null

    const weighted = valid.map((r) => ({ ...r, weight: (r.amount / total) * 100 }))
    const portfolioBeta = weighted.reduce(
      (s, r) => s + (Number.isFinite(r.beta) ? r.beta : 1) * (r.weight / 100),
      0
    )

    const bySector = {}
    for (const r of weighted) bySector[r.sector] = (bySector[r.sector] ?? 0) + r.weight
    const sectors = Object.entries(bySector).sort((a, b) => b[1] - a[1])

    const largest = weighted.reduce((a, b) => (a.weight > b.weight ? a : b))
    const stableWeight = weighted
      .filter((r) => r.sector === 'Broad Index Fund' || r.sector === 'Bonds / Cash')
      .reduce((s, r) => s + r.weight, 0)

    return { total, weighted, portfolioBeta, sectors, largest, stableWeight, count: valid.length }
  }, [rows])

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <Panel title="Your holdings" className="mt-10">
        <div className="space-y-3">
          {rows.map((r) => (
            <div key={r.id} className="grid grid-cols-2 gap-3 rounded-lg border border-ink-200 p-3 dark:border-ink-800 sm:grid-cols-[1fr,7rem,11rem,5.5rem,2.5rem]">
              <input
                type="text"
                value={r.name}
                placeholder="Holding name"
                onChange={(e) => update(r.id, { name: e.target.value })}
                className="col-span-2 rounded-lg border border-ink-200 px-3 py-2 text-sm dark:border-ink-700 dark:bg-ink-900 sm:col-span-1"
              />
              <input
                type="number"
                value={Number.isFinite(r.amount) ? r.amount : ''}
                onChange={(e) => update(r.id, { amount: e.target.value === '' ? NaN : Number(e.target.value) })}
                className="rounded-lg border border-ink-200 px-3 py-2 text-sm tabular-nums dark:border-ink-700 dark:bg-ink-900"
                aria-label="Amount in dollars"
              />
              <select
                value={r.sector}
                onChange={(e) => update(r.id, { sector: e.target.value })}
                className="rounded-lg border border-ink-200 px-2 py-2 text-sm dark:border-ink-700 dark:bg-ink-900"
                aria-label="Sector"
              >
                {SECTORS.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
              <input
                type="number"
                step="0.1"
                value={Number.isFinite(r.beta) ? r.beta : ''}
                onChange={(e) => update(r.id, { beta: e.target.value === '' ? NaN : Number(e.target.value) })}
                className="rounded-lg border border-ink-200 px-3 py-2 text-sm tabular-nums dark:border-ink-700 dark:bg-ink-900"
                aria-label="Beta"
                placeholder="Beta"
              />
              <button
                type="button"
                onClick={() => remove(r.id)}
                aria-label={`Remove ${r.name || 'holding'}`}
                className="justify-self-end rounded-lg p-2 text-ink-400 hover:bg-ink-100 hover:text-rose-600 dark:hover:bg-ink-800"
              >
                <CloseIcon className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <button type="button" onClick={add} className="btn-secondary">
            Add a holding
          </button>
          <button type="button" onClick={() => setRows(STARTER)} className="btn-secondary">
            Reset to example
          </button>
        </div>
        <p className="mt-3 text-xs text-ink-400 dark:text-ink-500">
          Columns are name, amount in dollars, sector and beta. Look beta up on a quote page; leave it at 1.0
          if you do not know it.
        </p>
      </Panel>

      {analysis && (
        <div className="mt-6 space-y-6">
          <div className="grid gap-4 sm:grid-cols-4">
            <Stat label="Total value" value={money(analysis.total)} />
            <Stat
              label="Weighted beta"
              value={num(analysis.portfolioBeta)}
              sub={analysis.portfolioBeta > 1 ? 'Swings harder than the market' : 'Steadier than the market'}
              tone={analysis.portfolioBeta > 1.3 ? 'warn' : 'neutral'}
            />
            <Stat
              label="Largest position"
              value={pct(analysis.largest.weight)}
              sub={analysis.largest.name || 'Unnamed holding'}
              tone={analysis.largest.weight > 25 ? 'warn' : 'neutral'}
            />
            <Stat
              label="In stable assets"
              value={pct(analysis.stableWeight)}
              sub="Index funds, bonds and cash"
              tone={analysis.stableWeight < 40 ? 'warn' : 'good'}
            />
          </div>

          <Panel title="Allocation">
            <DataTable head={['Holding', 'Sector', 'Amount', 'Weight', 'Beta']}>
              {analysis.weighted
                .slice()
                .sort((a, b) => b.weight - a.weight)
                .map((r) => (
                  <tr key={r.id}>
                    <Td className="font-medium text-ink-900 dark:text-white">{r.name || 'Unnamed'}</Td>
                    <Td className="text-ink-500 dark:text-ink-400">{r.sector}</Td>
                    <Td>{money(r.amount)}</Td>
                    <Td>{pct(r.weight)}</Td>
                    <Td>{num(r.beta)}</Td>
                  </tr>
                ))}
            </DataTable>
          </Panel>

          <Panel title="Concentration by sector">
            <DataTable head={['Sector', 'Weight', '']}>
              {analysis.sectors.map(([sector, weight]) => (
                <tr key={sector}>
                  <Td className="font-medium text-ink-900 dark:text-white">{sector}</Td>
                  <Td>{pct(weight)}</Td>
                  <Td className="w-1/2">
                    <span className="block h-2 w-full rounded-full bg-ink-100 dark:bg-ink-800">
                      <span
                        className={`block h-2 rounded-full ${weight > 40 ? 'bg-amber-500' : 'bg-sky-500'}`}
                        style={{ width: `${Math.min(100, weight)}%` }}
                      />
                    </span>
                  </Td>
                </tr>
              ))}
            </DataTable>
          </Panel>

          <Panel title="What stands out">
            <ul className="space-y-2.5">
              {analysis.largest.weight > 25 && (
                <Flag level={analysis.largest.weight > 40 ? 'bad' : 'warn'} title={`${analysis.largest.name || 'One holding'} is ${pct(analysis.largest.weight)} of the portfolio`}>
                  A single position this large means one company's bad year is your bad year. If it fell 50%
                  tomorrow the whole portfolio would drop {pct(analysis.largest.weight / 2)}.
                </Flag>
              )}
              {analysis.sectors[0] && analysis.sectors[0][1] > 40 && analysis.sectors[0][0] !== 'Broad Index Fund' && (
                <Flag level="warn" title={`${pct(analysis.sectors[0][1])} sits in ${analysis.sectors[0][0]}`}>
                  Companies in one sector tend to fall together, so several holdings here behave closer to one
                  large position than to real diversification.
                </Flag>
              )}
              {analysis.stableWeight < 40 && (
                <Flag level={analysis.stableWeight < 20 ? 'bad' : 'warn'} title={`Only ${pct(analysis.stableWeight)} is in broad or defensive assets`}>
                  The stable core is what keeps you solvent and calm through a bad year. With this little of
                  it, a market-wide drop hits almost the entire portfolio at once.
                </Flag>
              )}
              {analysis.portfolioBeta > 1.3 && (
                <Flag level="warn" title={`A weighted beta of ${num(analysis.portfolioBeta)} is an aggressive portfolio`}>
                  Historically this mix would have moved about {pct((analysis.portfolioBeta - 1) * 100, 0)} more
                  than the market in both directions. In a 30% market drop that implies roughly{' '}
                  {pct(30 * analysis.portfolioBeta)}.
                </Flag>
              )}
              {analysis.count < 4 && (
                <Flag level="info" title="Only a few holdings">
                  With {analysis.count} position(s), one bad outcome is a large share of the result. A single
                  broad index fund is itself hundreds of companies, so it counts for more than its row suggests.
                </Flag>
              )}
              {analysis.largest.weight <= 25 && analysis.stableWeight >= 40 && analysis.portfolioBeta <= 1.3 && (
                <Flag level="good" title="This is a structurally sound shape">
                  No single position dominates, there is a real stable core, and the weighted beta is close to
                  the market. That does not make it a good portfolio, but it is not a fragile one.
                </Flag>
              )}
            </ul>
          </Panel>

          <LessonLink to={tool.lesson} name={tool.lessonName} />
        </div>
      )}
    </div>
  )
}
