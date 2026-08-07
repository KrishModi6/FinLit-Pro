/**
 * The whole course, in order.
 *
 * This file is the single source of truth for navigation, the sidebar, progress
 * maths and routing. Lesson *content* lives in `src/content/<track>/<File>.jsx`
 * and is wired up in `src/content/index.js` by module id.
 *
 * Tailwind class strings are written out in full rather than composed at
 * runtime (`bg-${color}-500`), because the JIT compiler only sees literal
 * strings and would otherwise purge them out of the build.
 */

const THEMES = {
  beginner: {
    label: 'text-emerald-700 dark:text-emerald-400',
    dot: 'bg-emerald-500',
    bar: 'bg-emerald-500',
    soft: 'bg-emerald-50 dark:bg-emerald-500/10',
    softText: 'text-emerald-800 dark:text-emerald-300',
    border: 'border-emerald-200 dark:border-emerald-500/30',
    hover: 'hover:border-emerald-400 dark:hover:border-emerald-500/50',
    gradient: 'from-emerald-500 to-teal-600',
    activeNav: 'bg-emerald-50 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300',
  },
  intermediate: {
    label: 'text-sky-700 dark:text-sky-400',
    dot: 'bg-sky-500',
    bar: 'bg-sky-500',
    soft: 'bg-sky-50 dark:bg-sky-500/10',
    softText: 'text-sky-800 dark:text-sky-300',
    border: 'border-sky-200 dark:border-sky-500/30',
    hover: 'hover:border-sky-400 dark:hover:border-sky-500/50',
    gradient: 'from-sky-500 to-indigo-600',
    activeNav: 'bg-sky-50 text-sky-800 dark:bg-sky-500/10 dark:text-sky-300',
  },
  examples: {
    label: 'text-violet-700 dark:text-violet-400',
    dot: 'bg-violet-500',
    bar: 'bg-violet-500',
    soft: 'bg-violet-50 dark:bg-violet-500/10',
    softText: 'text-violet-800 dark:text-violet-300',
    border: 'border-violet-200 dark:border-violet-500/30',
    hover: 'hover:border-violet-400 dark:hover:border-violet-500/50',
    gradient: 'from-violet-500 to-purple-600',
    activeNav: 'bg-violet-50 text-violet-800 dark:bg-violet-500/10 dark:text-violet-300',
  },
  hard: {
    label: 'text-amber-700 dark:text-amber-400',
    dot: 'bg-amber-500',
    bar: 'bg-amber-500',
    soft: 'bg-amber-50 dark:bg-amber-500/10',
    softText: 'text-amber-800 dark:text-amber-300',
    border: 'border-amber-200 dark:border-amber-500/30',
    hover: 'hover:border-amber-400 dark:hover:border-amber-500/50',
    gradient: 'from-amber-500 to-orange-600',
    activeNav: 'bg-amber-50 text-amber-800 dark:bg-amber-500/10 dark:text-amber-300',
  },
}

const RAW_TRACKS = [
  {
    slug: 'beginner',
    name: 'Beginner',
    title: 'How Stocks Actually Work',
    tagline: 'Start here. Zero prior knowledge assumed.',
    description:
      "Everything that people assume you already know but nobody ever actually teaches you: what a share is, where it's traded, why the price moves, and how you'd buy one.",
    outcomes: [
      'Explain what owning a share actually gets you',
      'Read a stock quote without Googling every number',
      'Tell the difference between an index, an exchange and a broker',
      'Work out your own risk tolerance and risk capacity',
      'Walk through a first purchase end to end',
    ],
    modules: [
      {
        slug: 'what-is-a-stock',
        title: 'What Is a Stock?',
        blurb: 'Ownership, share counts, and why a company would hand over a slice of itself.',
        minutes: 9,
      },
      {
        slug: 'how-the-market-works',
        title: 'The Stock Market: NYSE, NASDAQ and Who You Trade With',
        blurb: 'Exchanges, the order book, and what really happens in the two seconds after you tap Buy.',
        minutes: 9,
      },
      {
        slug: 'why-prices-move',
        title: 'Why Prices Move: Supply, Demand and Sentiment',
        blurb: 'Price is not value. It is the last number two people agreed on.',
        minutes: 8,
      },
      {
        slug: 'brokerages-and-quotes',
        title: 'Brokerages and Reading a Stock Quote',
        blurb: 'Robinhood vs Fidelity vs Schwab, and how to decode price, volume and market cap.',
        minutes: 10,
      },
      {
        slug: 'indices-and-market-cycles',
        title: 'Indices, Bull Markets and Bear Markets',
        blurb: 'The S&P 500, the Dow, the NASDAQ Composite, and what "the market is down" means.',
        minutes: 9,
      },
      {
        slug: 'dividends-and-time-horizon',
        title: 'Dividends and the Long Game',
        blurb: 'Getting paid to hold, compounding, and why your time horizon changes everything.',
        minutes: 9,
      },
      {
        slug: 'know-your-risk-profile',
        title: 'Know Your Risk Profile',
        blurb: 'Risk tolerance versus risk capacity, and a seven-question assessment that tells you how much volatility to build in.',
        minutes: 10,
      },
      {
        slug: 'your-first-share',
        title: 'Walkthrough: Buying Your First Share',
        blurb: 'A complete, click-by-click run through one share of Apple and one share of VOO.',
        minutes: 11,
      },
      {
        slug: 'recap',
        title: 'Recap: What You Now Know',
        blurb: 'Everything the Beginner track covered, in one page, and what the Intermediate track does with it.',
        minutes: 6,
      },
    ],
  },
  {
    slug: 'intermediate',
    name: 'Intermediate',
    title: 'Stable vs Unstable Stocks',
    tagline: 'Learn to tell a boring compounder from a coin flip.',
    description:
      'How to categorise a stock before you buy it: what makes something stable, what makes something volatile, the numbers that tell you which is which, and why a portion of your money should always sit in the boring half.',
    outcomes: [
      'Classify a stock as stable or speculative using real metrics',
      'Read a P/E ratio, EPS, beta and debt-to-equity',
      'Explain why an index fund is lower risk than one great stock',
      'Design a portfolio with a deliberate stable core',
    ],
    modules: [
      {
        slug: 'stable-vs-unstable',
        title: 'What Makes a Stock Stable or Unstable',
        blurb: 'Blue chips, dividend aristocrats, small caps and speculative names, and the traits that separate them.',
        minutes: 12,
      },
      {
        slug: 'beta-and-volatility',
        title: 'Beta: Reading the Volatility Number',
        blurb: 'What beta measures, what it definitely does not measure, and where to find it.',
        minutes: 9,
      },
      {
        slug: 'fundamental-analysis',
        title: 'Fundamental Analysis: P/E, EPS, Growth and Debt',
        blurb: 'The four numbers that tell you what a business actually earns and what you are paying for it.',
        minutes: 12,
      },
      {
        slug: 'technical-analysis',
        title: 'Technical Analysis: Candlesticks, Moving Averages and RSI',
        blurb: 'Reading a chart honestly: what these tools show, and what they cannot tell you.',
        minutes: 11,
      },
      {
        slug: 'etfs-and-diversification',
        title: 'ETFs, Index Funds and Sector Diversification',
        blurb: 'Buying hundreds of companies in one order, and why one industry should never be your whole portfolio.',
        minutes: 11,
      },
      {
        slug: 'the-stable-core',
        title: 'Why You Always Keep a Stable Core',
        blurb: 'Two students, the same starting money, one very different 2022. The maths of drawdown recovery.',
        minutes: 10,
      },
      {
        slug: 'case-study-and-tools',
        title: 'Case Study: GameStop vs Boring, and Your Research Toolkit',
        blurb: 'GME in 2021 next to J&J and VOO over a decade, plus how to look all of this up yourself.',
        minutes: 12,
      },
      {
        slug: 'recap',
        title: 'Recap: Sorting Stocks by Risk',
        blurb: 'The Intermediate track in one page, and why the next track puts real charts in front of you.',
        minutes: 6,
      },
    ],
  },
  {
    slug: 'examples',
    name: 'Examples',
    title: 'Real Charts, Real Lessons',
    tagline: 'Live data, not hypotheticals. Four charts that argue with each other.',
    description:
      'Everything so far has been explained with invented numbers so the arithmetic stays clean. This track does the opposite: real companies, real price history pulled live, and the uncomfortable patterns that only show up when you look at an actual decade.',
    outcomes: [
      'Read a five-year chart and describe what actually happened',
      'Explain why a stock can rise 400% and still lose you money',
      'Recognise the shape of a crowd-driven move versus a business-driven one',
      'Say what "knowing when to get out" concretely means',
    ],
    modules: [
      {
        slug: 'roblox-the-round-trip',
        title: 'Roblox: The Round Trip',
        blurb: 'A stock that went up enormously and gave almost all of it back. What that does to somebody who never decided when to stop.',
        minutes: 11,
      },
      {
        slug: 'gamestop-after-the-crowd',
        title: 'GameStop: After the Crowd Left',
        blurb: 'Not the squeeze itself, but the five years that followed it, which almost nobody posts about.',
        minutes: 10,
      },
      {
        slug: 'the-boring-chart',
        title: 'The Boring Chart That Beat Both',
        blurb: 'A broad index fund and a healthcare giant over the same five years, next to the two above.',
        minutes: 10,
      },
      {
        slug: 'recap',
        title: 'Recap: What the Charts Showed',
        blurb: 'What four real price histories agree on, and what the Hard track does with that.',
        minutes: 6,
      },
    ],
  },
  {
    slug: 'hard',
    name: 'Hard',
    title: 'Risky Bets: When to Take Them, When to Walk Away',
    tagline: 'The honest version. Upside and wipeout, side by side.',
    description:
      'High-risk investing explained without the hype: what the instruments actually are, how position sizing decides whether a loss is survivable, when a speculative bet is defensible, and the psychology that makes people get this wrong.',
    outcomes: [
      'Explain calls, puts, strikes and expiration in plain language',
      'Size a speculative position so a total loss is survivable',
      'Recognise FOMO, loss aversion and overconfidence in yourself',
      'Walk through a real options trade in both directions',
    ],
    modules: [
      {
        slug: 'what-high-risk-means',
        title: 'What High-Risk Investing Actually Is',
        blurb: 'Penny stocks, options, leveraged ETFs, meme stocks and crypto-adjacent plays, defined properly.',
        minutes: 11,
      },
      {
        slug: 'options-basics',
        title: 'Options Basics: Calls, Puts, Strikes and Expiration',
        blurb: 'A contract, not a lottery ticket. What each part means and why time is working against you.',
        minutes: 14,
      },
      {
        slug: 'risk-reward-and-sizing',
        title: 'Risk, Reward and Position Sizing',
        blurb: 'Why a 50% loss needs a 100% gain to break even, and where the 1–2% rule comes from.',
        minutes: 11,
      },
      {
        slug: 'when-a-bet-makes-sense',
        title: 'When a Risky Bet Can Make Sense',
        blurb: 'Asymmetric upside, genuine conviction, and an allocation small enough to be wrong.',
        minutes: 10,
      },
      {
        slug: 'when-bets-go-bad',
        title: 'When It Goes Wrong: GameStop and Enron',
        blurb: 'Two failures, two different lessons: one about timing, one about trusting the story.',
        minutes: 12,
      },
      {
        slug: 'investor-psychology',
        title: 'The Psychology of Investing',
        blurb: 'FOMO, loss aversion, overconfidence and the reason your brain is bad at this.',
        minutes: 11,
      },
      {
        slug: 'building-your-risk-sleeve',
        title: 'Building a Risky Sleeve, and Researching a Play',
        blurb: 'The 90/10 structure, plus catalysts, earnings dates and short interest.',
        minutes: 12,
      },
      {
        slug: 'options-trade-walkthrough',
        title: 'Walkthrough: One Options Trade, Both Endings',
        blurb: 'The same hypothetical trade run to a win and to a total loss, with the numbers shown.',
        minutes: 12,
      },
      {
        slug: 'recap',
        title: 'Recap: The Whole Course in One Page',
        blurb: 'What all four tracks were actually arguing, and the short list worth remembering.',
        minutes: 7,
      },
    ],
  },
]

/** Tracks with derived fields (`id`, `theme`, `path`) filled in. */
export const TRACKS = RAW_TRACKS.map((track, trackIndex) => ({
  ...track,
  index: trackIndex,
  theme: THEMES[track.slug],
  path: `/${track.slug}`,
  modules: track.modules.map((mod, modIndex) => ({
    ...mod,
    // Global, stable id, also the LocalStorage key for progress.
    id: `${track.slug}/${mod.slug}`,
    number: modIndex + 1,
    trackSlug: track.slug,
    trackName: track.name,
    path: `/${track.slug}/${mod.slug}`,
  })),
}))

/** Every module across every track, in the recommended learning order. */
export const ALL_MODULES = TRACKS.flatMap((t) => t.modules)

export const TOTAL_MINUTES = ALL_MODULES.reduce((sum, m) => sum + m.minutes, 0)

export function getTrack(slug) {
  return TRACKS.find((t) => t.slug === slug) ?? null
}

export function getModule(trackSlug, moduleSlug) {
  return getTrack(trackSlug)?.modules.find((m) => m.slug === moduleSlug) ?? null
}

/**
 * Previous/next module in global course order, so "Next lesson" rolls naturally
 * from the last Beginner module into the first Intermediate one.
 */
export function getNeighbours(moduleId) {
  const i = ALL_MODULES.findIndex((m) => m.id === moduleId)
  if (i === -1) return { prev: null, next: null }
  return {
    prev: i > 0 ? ALL_MODULES[i - 1] : null,
    next: i < ALL_MODULES.length - 1 ? ALL_MODULES[i + 1] : null,
  }
}
