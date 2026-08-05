/**
 * The Simulator: a set of hands-on tools that sit alongside the course rather
 * than inside it.
 *
 * Design rule: every tool runs entirely in the browser on numbers the reader
 * supplies. Nothing here fetches a live price. That is deliberate. The course
 * teaches you where to look each number up (Yahoo Finance, Finviz, your broker),
 * and the simulator is where you find out what those numbers actually imply.
 * It also means no API key, no backend, and nothing that can silently break.
 */

export const TOOLS = [
  {
    slug: 'growth',
    name: 'Growth Calculator',
    blurb:
      'Project an investment forward with regular contributions, and see exactly how much a fee costs you over decades.',
    tag: 'Planning',
    accent: 'from-emerald-500 to-teal-600',
    lesson: '/beginner/dividends-and-time-horizon',
    lessonName: 'Dividends and the Long Game',
  },
  {
    slug: 'portfolio',
    name: 'Portfolio Builder',
    blurb:
      'Enter your holdings and get weights, weighted beta, sector concentration and an honest list of what is over-exposed.',
    tag: 'Risk',
    accent: 'from-sky-500 to-indigo-600',
    lesson: '/intermediate/etfs-and-diversification',
    lessonName: 'ETFs, Index Funds and Sector Diversification',
  },
  {
    slug: 'analyzer',
    name: 'Stock Analyzer',
    blurb:
      'Type in the numbers from a quote page and get a structured read on where that company sits between stable and speculative.',
    tag: 'Analysis',
    accent: 'from-violet-500 to-purple-600',
    lesson: '/intermediate/stable-vs-unstable',
    lessonName: 'What Makes a Stock Stable or Unstable',
  },
  {
    slug: 'compare',
    name: 'Compare',
    blurb:
      'Two companies, the same metrics, side by side, with a plain-English read on what each difference actually means.',
    tag: 'Analysis',
    accent: 'from-cyan-500 to-blue-600',
    lesson: '/intermediate/fundamental-analysis',
    lessonName: 'Fundamental Analysis',
  },
  {
    slug: 'options',
    name: 'Options Payoff',
    blurb:
      'Price out a hypothetical call or put: break-even, maximum loss, and the payoff at every exit price next to just buying the stock.',
    tag: 'Advanced',
    accent: 'from-amber-500 to-orange-600',
    lesson: '/hard/options-basics',
    lessonName: 'Options Basics',
  },
  {
    slug: 'scenarios',
    name: 'Scenario Projector',
    blurb:
      'Run thousands of randomised futures for a portfolio and see the spread of outcomes instead of a single tidy number.',
    tag: 'Risk',
    accent: 'from-rose-500 to-pink-600',
    lesson: '/hard/risk-reward-and-sizing',
    lessonName: 'Risk, Reward and Position Sizing',
  },
]

export function getTool(slug) {
  return TOOLS.find((t) => t.slug === slug) ?? null
}

/** Sectors offered in the portfolio builder, matching the GICS list the course uses. */
export const SECTORS = [
  'Technology',
  'Healthcare',
  'Financials',
  'Consumer Staples',
  'Consumer Discretionary',
  'Energy',
  'Industrials',
  'Utilities',
  'Materials',
  'Real Estate',
  'Communication Services',
  'Broad Index Fund',
  'Bonds / Cash',
  'Crypto',
  'Other',
]
