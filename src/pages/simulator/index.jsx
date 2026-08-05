import { Suspense, lazy } from 'react'
import { useParams } from 'react-router-dom'
import NotFound from '../NotFound.jsx'

/** Tool slug to component. Code-split so the course never pays for the simulator. */
const REGISTRY = {
  growth: lazy(() => import('./GrowthCalculator.jsx')),
  portfolio: lazy(() => import('./PortfolioBuilder.jsx')),
  analyzer: lazy(() => import('./StockAnalyzer.jsx')),
  compare: lazy(() => import('./Compare.jsx')),
  options: lazy(() => import('./OptionsPayoff.jsx')),
  scenarios: lazy(() => import('./ScenarioProjector.jsx')),
}

export default function SimulatorTool() {
  const { toolSlug } = useParams()
  const Tool = REGISTRY[toolSlug]

  if (!Tool) return <NotFound />

  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-6xl animate-pulse px-4 py-16 sm:px-6" aria-label="Loading tool">
          <div className="h-9 w-64 rounded bg-ink-200 dark:bg-ink-800" />
          <div className="mt-4 h-4 w-96 max-w-full rounded bg-ink-200 dark:bg-ink-800" />
          <div className="mt-10 h-72 rounded-2xl bg-ink-100 dark:bg-ink-900" />
        </div>
      }
    >
      <Tool />
    </Suspense>
  )
}
