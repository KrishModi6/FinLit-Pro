import { lazy } from 'react'

/**
 * Module id → lesson component.
 *
 * Every lesson is code-split with React.lazy so the first page load only ships
 * the shell, not 20-odd essays. ModulePage renders these inside a <Suspense>.
 *
 * Each lesson component receives a single `moduleId` prop, which it forwards to
 * <Quiz> and <TryIt> so their saved state is scoped to that lesson.
 */
const registry = {
  // ---- Beginner: How Stocks Actually Work -----------------------------
  'beginner/what-is-a-stock': lazy(() => import('./beginner/WhatIsAStock.jsx')),
  'beginner/how-the-market-works': lazy(() => import('./beginner/HowTheMarketWorks.jsx')),
  'beginner/why-prices-move': lazy(() => import('./beginner/WhyPricesMove.jsx')),
  'beginner/brokerages-and-quotes': lazy(() => import('./beginner/BrokeragesAndQuotes.jsx')),
  'beginner/indices-and-market-cycles': lazy(() => import('./beginner/IndicesAndMarketCycles.jsx')),
  'beginner/dividends-and-time-horizon': lazy(() => import('./beginner/DividendsAndTimeHorizon.jsx')),
  'beginner/know-your-risk-profile': lazy(() => import('./beginner/KnowYourRiskProfile.jsx')),
  'beginner/your-first-share': lazy(() => import('./beginner/YourFirstShare.jsx')),

  // ---- Intermediate: Stable vs Unstable Stocks ------------------------
  'intermediate/stable-vs-unstable': lazy(() => import('./intermediate/StableVsUnstable.jsx')),
  'intermediate/beta-and-volatility': lazy(() => import('./intermediate/BetaAndVolatility.jsx')),
  'intermediate/fundamental-analysis': lazy(() => import('./intermediate/FundamentalAnalysis.jsx')),
  'intermediate/technical-analysis': lazy(() => import('./intermediate/TechnicalAnalysis.jsx')),
  'intermediate/etfs-and-diversification': lazy(() => import('./intermediate/EtfsAndDiversification.jsx')),
  'intermediate/the-stable-core': lazy(() => import('./intermediate/TheStableCore.jsx')),
  'intermediate/case-study-and-tools': lazy(() => import('./intermediate/CaseStudyAndTools.jsx')),

  // ---- Hard: Risky Bets ------------------------------------------------
  'hard/what-high-risk-means': lazy(() => import('./hard/WhatHighRiskMeans.jsx')),
  'hard/options-basics': lazy(() => import('./hard/OptionsBasics.jsx')),
  'hard/risk-reward-and-sizing': lazy(() => import('./hard/RiskRewardAndSizing.jsx')),
  'hard/when-a-bet-makes-sense': lazy(() => import('./hard/WhenABetMakesSense.jsx')),
  'hard/when-bets-go-bad': lazy(() => import('./hard/WhenBetsGoBad.jsx')),
  'hard/investor-psychology': lazy(() => import('./hard/InvestorPsychology.jsx')),
  'hard/building-your-risk-sleeve': lazy(() => import('./hard/BuildingYourRiskSleeve.jsx')),
  'hard/options-trade-walkthrough': lazy(() => import('./hard/OptionsTradeWalkthrough.jsx')),
}

/** Shown if a module exists in the curriculum but has no content file yet. */
function MissingContent() {
  return (
    <p>
      This lesson’s content could not be loaded. Please pick another lesson from the sidebar. The rest of
      the course is unaffected.
    </p>
  )
}

export function getContent(moduleId) {
  return registry[moduleId] ?? MissingContent
}
