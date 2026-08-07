/**
 * The stability read used by both the Stock Analyzer and Compare.
 *
 * The scoring is deliberately simple and fully visible: six criteria the
 * Intermediate track actually teaches, each worth a stated number of points.
 * It is a structured way to organise what you just looked up, not a rating
 * agency. Two companies with the same score can be completely different
 * businesses, and the score says nothing about whether either is worth owning.
 */

export const BLANK = {
  ticker: '',
  price: 100,
  marketCapB: 50,
  pe: 20,
  eps: 5,
  beta: 1,
  divYield: 1.5,
  debtToEquity: 0.6,
  revGrowth: 8,
}

function capBucket(b) {
  if (!Number.isFinite(b)) return { label: 'unknown', points: 0 }
  if (b >= 200) return { label: 'Mega cap', points: 25 }
  if (b >= 10) return { label: 'Large cap', points: 20 }
  if (b >= 2) return { label: 'Mid cap', points: 12 }
  if (b >= 0.3) return { label: 'Small cap', points: 5 }
  return { label: 'Micro cap', points: 0 }
}

function betaPoints(beta) {
  if (!Number.isFinite(beta)) return 0
  if (beta < 0.8) return 20
  if (beta <= 1.2) return 15
  if (beta <= 1.6) return 8
  if (beta <= 2) return 3
  return 0
}

function debtPoints(de) {
  if (!Number.isFinite(de)) return 0
  if (de < 0.5) return 15
  if (de <= 1) return 10
  if (de <= 2) return 5
  return 0
}

export function analyse(input) {
  const { price, marketCapB, pe, eps, beta, divYield, debtToEquity, revGrowth } = input

  // P/E is share price divided by earnings per share, and the form asks for
  // all three separately, so they can disagree. Ignoring the price made it a
  // field that changed nothing while the reader assumed it was being checked.
  // Working out what their own numbers imply turns that into the lesson.
  const impliedPe =
    Number.isFinite(price) && Number.isFinite(eps) && eps > 0 ? price / eps : null

  const cap = capBucket(marketCapB)
  const profitable = Number.isFinite(eps) && eps > 0
  const paysDividend = Number.isFinite(divYield) && divYield > 0
  const growing = Number.isFinite(revGrowth) && revGrowth > 0

  const parts = [
    { label: 'Company size', points: cap.points, max: 25, note: cap.label },
    { label: 'Profitable today', points: profitable ? 20 : 0, max: 20, note: profitable ? 'Positive EPS' : 'Negative or zero EPS' },
    { label: 'Market sensitivity', points: betaPoints(beta), max: 20, note: Number.isFinite(beta) ? `Beta ${beta.toFixed(2)}` : 'Beta unknown' },
    { label: 'Balance sheet', points: debtPoints(debtToEquity), max: 15, note: Number.isFinite(debtToEquity) ? `D/E ${debtToEquity.toFixed(2)}` : 'D/E unknown' },
    { label: 'Pays a dividend', points: paysDividend ? 10 : 0, max: 10, note: paysDividend ? `${divYield.toFixed(2)}% yield` : 'No dividend' },
    { label: 'Revenue growing', points: growing ? 10 : 0, max: 10, note: growing ? `${revGrowth.toFixed(1)}% growth` : 'Flat or shrinking' },
  ]

  const score = parts.reduce((s, p) => s + p.points, 0)

  let band
  if (score >= 75) band = { label: 'Stable end of the spectrum', tone: 'good' }
  else if (score >= 50) band = { label: 'Middle of the spectrum', tone: 'neutral' }
  else if (score >= 25) band = { label: 'Volatile end of the spectrum', tone: 'warn' }
  else band = { label: 'Highly speculative', tone: 'bad' }

  /* ------------------------- interpreted signals ------------------------- */
  const signals = []

  if (!profitable) {
    signals.push({
      level: 'bad',
      title: 'Not profitable today',
      detail:
        'A company funding itself by issuing shares or debt depends on markets staying friendly. If that funding gets expensive, the story can end quickly regardless of how good the product is.',
    })
  }
  if (Number.isFinite(beta) && beta > 1.6) {
    signals.push({
      level: 'warn',
      title: `Beta of ${beta.toFixed(2)} means outsized swings`,
      detail: `Historically this moved about ${((beta - 1) * 100).toFixed(0)}% harder than the market in both directions. In a 30% market fall that shape implies roughly ${(30 * beta).toFixed(0)}%.`,
    })
  }
  if (Number.isFinite(beta) && beta < 0.8) {
    signals.push({
      level: 'info',
      title: 'Low beta is not the same as safe',
      detail:
        'Beta only measures how much this moved with the market. A company facing a single lawsuit, trial result or accounting problem can have low beta and still be a coin flip, because that risk is specific rather than market-wide.',
    })
  }
  if (Number.isFinite(debtToEquity) && debtToEquity > 2) {
    signals.push({
      level: 'warn',
      title: `Debt-to-equity of ${debtToEquity.toFixed(2)} is heavy`,
      detail:
        'Leverage magnifies good years and bad ones, and it makes rising interest rates a direct problem. Normal levels differ sharply by industry, so compare this against direct competitors rather than against the market.',
    })
  }
  if (Number.isFinite(pe) && pe > 40 && profitable) {
    signals.push({
      level: 'warn',
      title: `A P/E of ${pe.toFixed(1)} prices in a lot of growth`,
      detail: `You are paying about $${pe.toFixed(0)} for each $1 of current annual profit. That is only justified if earnings grow substantially, and the price will fall hard if they do not.`,
    })
  }
  if (Number.isFinite(pe) && pe > 0 && pe < 10 && profitable) {
    signals.push({
      level: 'info',
      title: `A P/E of ${pe.toFixed(1)} is unusually low`,
      detail:
        'Cheap is sometimes a bargain and sometimes a warning. Work out which by asking what the market expects to go wrong, because a low multiple usually means somebody is pricing in decline.',
    })
  }
  if (impliedPe != null && Number.isFinite(pe) && pe > 0 && Math.abs(impliedPe - pe) / pe > 0.1) {
    signals.push({
      level: 'info',
      title: `Your own numbers imply a P/E of ${impliedPe.toFixed(1)}, not ${pe.toFixed(1)}`,
      detail: `P/E is the share price divided by earnings per share, so ${price.toFixed(2)} divided by ${eps.toFixed(2)} is ${impliedPe.toFixed(1)}. One of those three figures is stale or mistyped. Companies do report an adjusted EPS that differs from the one behind a quoted P/E, so check which you copied before trusting the rest of this.`,
    })
  }
  if (Number.isFinite(divYield) && divYield > 7) {
    signals.push({
      level: 'warn',
      title: `A ${divYield.toFixed(1)}% yield is high enough to question`,
      detail:
        'Yield rises when price falls. An unusually high yield is often the market forecasting a dividend cut rather than offering you free income. Check whether earnings actually cover the payment.',
    })
  }
  if (Number.isFinite(marketCapB) && marketCapB < 2) {
    signals.push({
      level: 'warn',
      title: `${cap.label} companies have less cushion`,
      detail:
        'Smaller companies are more exposed to a single lost customer, a funding squeeze or one bad quarter, and their shares are usually thinner to trade, which widens the spread you pay.',
    })
  }
  if (Number.isFinite(revGrowth) && revGrowth < 0) {
    signals.push({
      level: 'warn',
      title: 'Revenue is shrinking',
      detail:
        'Declining revenue puts pressure on every other number. Profits can be defended for a while through cost cutting, but not indefinitely.',
    })
  }
  if (score >= 75) {
    signals.push({
      level: 'good',
      title: 'This has the profile of a stable holding',
      detail:
        'Size, profitability, a manageable balance sheet and moderate market sensitivity. That combination tends to fall less in bad years. It does not mean it cannot fall, and it says nothing about the price you are paying.',
    })
  }

  return { score, band, parts, cap, profitable, impliedPe, signals }
}
