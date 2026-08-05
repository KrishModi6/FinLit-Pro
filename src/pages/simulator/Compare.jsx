import { useMemo, useState } from 'react'
import { DataTable, Flag, LessonLink, Panel, Td, num, pct } from '../../components/ui/SimUI.jsx'
import { MetricInputs, ScoreParts } from './StockAnalyzer.jsx'
import { BLANK, analyse } from '../../data/analyze.js'
import { getTool } from '../../data/simulator.js'

const A0 = { ...BLANK, ticker: 'Company A', marketCapB: 400, pe: 26, eps: 6.2, beta: 0.85, divYield: 2.4, debtToEquity: 0.5, revGrowth: 6 }
const B0 = { ...BLANK, ticker: 'Company B', marketCapB: 3, pe: 0, eps: -1.4, beta: 2.3, divYield: 0, debtToEquity: 2.6, revGrowth: 45 }

/** One row of the side-by-side table, with a plain-English read of the gap. */
function Row({ label, a, b, format = (x) => num(x), better }) {
  const verdict = better ? better(a, b) : null
  return (
    <tr>
      <Td className="font-medium text-ink-900 dark:text-white">{label}</Td>
      <Td>{Number.isFinite(a) ? format(a) : 'n/a'}</Td>
      <Td>{Number.isFinite(b) ? format(b) : 'n/a'}</Td>
      <Td className="text-ink-500 dark:text-ink-400">{verdict}</Td>
    </tr>
  )
}

export default function Compare() {
  const tool = getTool('compare')
  const [a, setA] = useState(A0)
  const [b, setB] = useState(B0)

  const ra = useMemo(() => analyse(a), [a])
  const rb = useMemo(() => analyse(b), [b])

  const nameA = a.ticker || 'Company A'
  const nameB = b.ticker || 'Company B'

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <Panel title={nameA}>
          <MetricInputs v={a} set={(patch) => setA((s) => ({ ...s, ...patch }))} />
        </Panel>
        <Panel title={nameB}>
          <MetricInputs v={b} set={(patch) => setB((s) => ({ ...s, ...patch }))} />
        </Panel>
      </div>

      <Panel title="Side by side" className="mt-6">
        <DataTable head={['Metric', nameA, nameB, 'What the gap means']}>
          <Row
            label="Market cap"
            a={a.marketCapB}
            b={b.marketCapB}
            format={(x) => `$${num(x, 1)}B`}
            better={(x, y) =>
              Math.max(x, y) / Math.max(1e-9, Math.min(x, y)) > 3
                ? `${x > y ? nameA : nameB} is far larger, so it has more cushion`
                : 'Comparable size'
            }
          />
          <Row
            label="P/E ratio"
            a={a.pe}
            b={b.pe}
            format={(x) => (x > 0 ? num(x, 1) : 'no earnings')}
            better={(x, y) => {
              if (x <= 0 || y <= 0) return 'P/E is meaningless without profits'
              return `${x < y ? nameA : nameB} is cheaper per $1 of profit, which may mean value or expected decline`
            }}
          />
          <Row label="EPS" a={a.eps} b={b.eps} format={(x) => `$${num(x)}`} better={(x, y) => (x > 0 && y > 0 ? 'Both profitable' : x > 0 ? `Only ${nameA} makes money` : y > 0 ? `Only ${nameB} makes money` : 'Neither is profitable')} />
          <Row
            label="Beta"
            a={a.beta}
            b={b.beta}
            better={(x, y) => `${x < y ? nameA : nameB} has been the steadier of the two`}
          />
          <Row
            label="Dividend yield"
            a={a.divYield}
            b={b.divYield}
            format={(x) => pct(x, 2)}
            better={(x, y) => (x === 0 && y === 0 ? 'Neither pays a dividend' : `${x > y ? nameA : nameB} returns more cash to holders`)}
          />
          <Row
            label="Debt to equity"
            a={a.debtToEquity}
            b={b.debtToEquity}
            better={(x, y) => `${x < y ? nameA : nameB} carries less leverage, so it is less fragile`}
          />
          <Row
            label="Revenue growth"
            a={a.revGrowth}
            b={b.revGrowth}
            format={(x) => pct(x)}
            better={(x, y) => `${x > y ? nameA : nameB} is growing faster`}
          />
          <Row
            label="Stability score"
            a={ra.score}
            b={rb.score}
            format={(x) => `${x}/100`}
            better={() => `${ra.score > rb.score ? nameA : nameB} sits nearer the stable end`}
          />
        </DataTable>
      </Panel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Panel title={`${nameA}: ${ra.band.label}`}>
          <ScoreParts parts={ra.parts} />
        </Panel>
        <Panel title={`${nameB}: ${rb.band.label}`}>
          <ScoreParts parts={rb.parts} />
        </Panel>
      </div>

      <Panel title="Reading this honestly" className="mt-6">
        <ul className="space-y-2.5">
          <Flag level="info" title="A higher score is not a buy signal">
            These two companies may not even be trying to do the same thing. A profitable mega cap and an
            unprofitable fast grower have different jobs in a portfolio, and the right answer is often that
            one belongs in the core and the other belongs in a small speculative sleeve, if at all.
          </Flag>
          {Math.abs(ra.score - rb.score) > 35 && (
            <Flag level="warn" title="These are not really peers">
              A gap of {Math.abs(ra.score - rb.score)} points means you are comparing different categories of
              risk. Sizing them identically would be the mistake, regardless of which story you find more
              convincing.
            </Flag>
          )}
          {a.pe > 0 && b.pe > 0 && Math.abs(a.pe - b.pe) > 15 && (
            <Flag level="info" title="A large P/E gap is a question, not an answer">
              The market is pricing very different futures into these two. Your job is to work out what it
              expects and whether you disagree, not to assume the lower number is the better deal.
            </Flag>
          )}
        </ul>
        <LessonLink to={tool.lesson} name={tool.lessonName} />
      </Panel>
    </div>
  )
}
