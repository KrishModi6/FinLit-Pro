/**
 * Shared definitions.
 *
 * These power two things: the standalone /glossary page, and the inline <Term>
 * component that shows a definition on hover inside a lesson. Keeping them in
 * one place means a term is defined identically everywhere it appears.
 *
 * Keys are lowercase; look them up with `defineTerm()` which is case-insensitive.
 */
export const GLOSSARY = {
  share: {
    term: 'Share',
    short: 'One unit of ownership in a company.',
    long: 'A single unit of ownership in a company. Own one share out of a billion and you own one-billionth of the business — its assets, its profits, and its problems.',
    tags: ['basics'],
  },
  equity: {
    term: 'Equity',
    short: 'Ownership in a company; the collective term for its stock.',
    long: 'Ownership in a company. "Equities" is the formal name for stocks as an asset class, which is why you will see portfolios described as 80% equities, 20% bonds.',
    tags: ['basics'],
  },
  ipo: {
    term: 'IPO',
    short: 'Initial Public Offering — the first sale of a company’s shares to the public.',
    long: 'Initial Public Offering. The first time a private company sells shares to the general public, turning it into a publicly traded company. The company receives the money raised in the IPO itself; after that, shares change hands between investors.',
    tags: ['basics'],
  },
  exchange: {
    term: 'Exchange',
    short: 'The regulated marketplace where buyers and sellers are matched.',
    long: 'A regulated marketplace that matches buy and sell orders. The NYSE and NASDAQ are the two large US exchanges. The exchange does not set prices; it records the price that a buyer and a seller agreed on.',
    tags: ['basics'],
  },
  brokerage: {
    term: 'Brokerage',
    short: 'The company that places your trades on an exchange for you.',
    long: 'A licensed firm that places orders on an exchange on your behalf and holds the shares in your account. You cannot walk up to the NYSE yourself — a broker such as Fidelity, Schwab or Robinhood is the door.',
    tags: ['basics'],
  },
  ticker: {
    term: 'Ticker',
    short: 'The short code that identifies a stock, like AAPL for Apple.',
    long: 'The short symbol that uniquely identifies a security on an exchange — AAPL for Apple, MSFT for Microsoft, VOO for Vanguard’s S&P 500 ETF. Tickers are how orders are routed, so getting one character wrong buys a different company.',
    tags: ['basics'],
  },
  'market cap': {
    term: 'Market Capitalisation',
    short: 'Share price × total shares. The market’s price tag on the whole company.',
    long: 'Share price multiplied by the number of shares outstanding — what the market currently says the entire company is worth. A $10 stock is not "cheaper" than a $500 stock; market cap is the number that lets you compare company sizes.',
    tags: ['basics', 'analysis'],
  },
  volume: {
    term: 'Volume',
    short: 'How many shares changed hands in a period.',
    long: 'The number of shares traded over a period, usually one day. High volume means lots of participants and easier buying and selling; very low volume means you may struggle to sell without pushing the price down.',
    tags: ['basics'],
  },
  liquidity: {
    term: 'Liquidity',
    short: 'How easily you can sell without moving the price.',
    long: 'How quickly an asset can be converted to cash near its quoted price. Apple is extremely liquid — you can sell instantly at roughly the screen price. A thinly traded penny stock is illiquid: your sell order itself can push the price down.',
    tags: ['risk'],
  },
  spread: {
    term: 'Bid-Ask Spread',
    short: 'The gap between the highest bid and the lowest ask.',
    long: 'The difference between the highest price a buyer will pay (the bid) and the lowest price a seller will accept (the ask). It is a real cost: you generally buy at the ask and sell at the bid. Wide spreads are a warning sign about liquidity.',
    tags: ['basics', 'risk'],
  },
  dividend: {
    term: 'Dividend',
    short: 'A cash payment a company makes to shareholders out of profits.',
    long: 'A cash payment made to shareholders, usually quarterly, out of company profits. Dividends are decided by the board and can be cut at any time — they are a signal of confidence, not a guarantee.',
    tags: ['income'],
  },
  'dividend yield': {
    term: 'Dividend Yield',
    short: 'Annual dividend ÷ share price, as a percentage.',
    long: 'Annual dividend per share divided by the share price. A $2 annual dividend on a $50 stock is a 4% yield. Note that yield rises when the price falls, so an unusually high yield often means the market expects a cut.',
    tags: ['income', 'analysis'],
  },
  index: {
    term: 'Index',
    short: 'A measured basket of stocks used to track a market.',
    long: 'A standardised basket of stocks used as a yardstick for a market or segment. The S&P 500 tracks roughly 500 large US companies. You cannot buy an index directly; you buy a fund that copies it.',
    tags: ['basics', 'funds'],
  },
  etf: {
    term: 'ETF',
    short: 'Exchange-Traded Fund — a basket of assets that trades like one stock.',
    long: 'Exchange-Traded Fund. A fund holding many underlying assets that itself trades on an exchange like a single stock. One share of VOO gives you a slice of all ~500 companies in the S&P 500.',
    tags: ['funds'],
  },
  'index fund': {
    term: 'Index Fund',
    short: 'A fund that simply copies an index instead of picking stocks.',
    long: 'A fund that mechanically tracks an index rather than employing managers to pick winners. Because there is little to decide, fees are very low — often under 0.05% a year.',
    tags: ['funds'],
  },
  'expense ratio': {
    term: 'Expense Ratio',
    short: 'The annual % fee a fund charges you.',
    long: 'The annual percentage a fund charges to run itself, deducted automatically from the fund’s value. 0.03% means $3 a year on $10,000. It sounds trivial and compounds into real money over decades.',
    tags: ['funds'],
  },
  'blue chip': {
    term: 'Blue Chip',
    short: 'A large, long-established, financially solid company.',
    long: 'An informal label for a large, long-established company with reliable earnings and a strong balance sheet. Blue chips still fall in crashes — they simply tend to fall less and recover more reliably.',
    tags: ['stability'],
  },
  'dividend aristocrat': {
    term: 'Dividend Aristocrat',
    short: 'An S&P 500 company that has raised its dividend 25+ years running.',
    long: 'A company in the S&P 500 that has increased its dividend every year for at least 25 consecutive years. The streak is evidence of durable cash flow across multiple recessions — though past streaks guarantee nothing.',
    tags: ['stability', 'income'],
  },
  volatility: {
    term: 'Volatility',
    short: 'How violently a price swings around, up or down.',
    long: 'A measure of how much and how quickly a price moves in either direction. Volatility is not the same as loss — but high volatility means larger possible losses over any short window.',
    tags: ['risk'],
  },
  beta: {
    term: 'Beta',
    short: 'How much a stock moves relative to the whole market.',
    long: 'A number describing how a stock has historically moved relative to the market. Beta 1.0 means it moved with the market; 1.8 means it tended to swing ~80% harder in both directions; below 1.0 means it was steadier.',
    tags: ['risk', 'analysis'],
  },
  'pe ratio': {
    term: 'P/E Ratio',
    short: 'Price ÷ earnings per share — what you pay per $1 of profit.',
    long: 'Price-to-Earnings ratio: share price divided by earnings per share. A P/E of 25 means you are paying $25 for each $1 of annual profit. High P/E means the market expects growth; it is only meaningful compared with peers in the same industry.',
    tags: ['analysis'],
  },
  eps: {
    term: 'EPS',
    short: 'Earnings per share — company profit split across all shares.',
    long: 'Earnings Per Share: net profit divided by shares outstanding. It is the per-share slice of profit, and the denominator of the P/E ratio. Rising EPS over years is one of the cleanest signs of a healthy business.',
    tags: ['analysis'],
  },
  'debt to equity': {
    term: 'Debt-to-Equity',
    short: 'Total debt ÷ shareholder equity. How leveraged a company is.',
    long: 'Total debt divided by shareholder equity — how much of the business is funded by borrowing. Heavy debt magnifies both good and bad years, and makes a company far more fragile when interest rates rise.',
    tags: ['analysis', 'risk'],
  },
  'moving average': {
    term: 'Moving Average',
    short: 'The average closing price over the last N days, plotted as a line.',
    long: 'The average closing price over a rolling window — the 50-day and 200-day are the common ones. It smooths daily noise so a trend is visible. It is descriptive, not predictive.',
    tags: ['technical'],
  },
  rsi: {
    term: 'RSI',
    short: 'A 0–100 momentum gauge; above 70 "overbought", below 30 "oversold".',
    long: 'Relative Strength Index. A momentum indicator scaled 0–100 comparing recent gains to recent losses. Above 70 is conventionally called overbought and below 30 oversold — but a strong stock can sit above 70 for months.',
    tags: ['technical'],
  },
  candlestick: {
    term: 'Candlestick',
    short: 'A chart mark showing open, high, low and close for one period.',
    long: 'A chart element encoding four numbers for one period: open, high, low and close. The thick body spans open to close; the thin wicks show the extremes reached during the period.',
    tags: ['technical'],
  },
  diversification: {
    term: 'Diversification',
    short: 'Spreading money across assets so no single failure ruins you.',
    long: 'Spreading capital across different companies, industries and asset types so that one failure cannot take out the portfolio. It reduces the damage from being wrong; it does not eliminate market-wide losses.',
    tags: ['risk', 'strategy'],
  },
  drawdown: {
    term: 'Drawdown',
    short: 'The fall from a portfolio’s peak to its trough.',
    long: 'The percentage decline from a peak value to the following trough. Drawdown matters more than average return because recovery is asymmetric: a 50% drawdown requires a 100% gain to get back to even.',
    tags: ['risk'],
  },
  'bull market': {
    term: 'Bull Market',
    short: 'A sustained rise, conventionally 20%+ off a low.',
    long: 'A sustained period of rising prices, conventionally marked once a major index is 20% above a recent low. Bull markets historically last years, which is why time in the market tends to beat timing it.',
    tags: ['cycles'],
  },
  'bear market': {
    term: 'Bear Market',
    short: 'A sustained fall of 20%+ from a recent high.',
    long: 'A decline of 20% or more from a recent high in a major index. Bear markets are shorter than bull markets on average but far more emotionally intense, which is when most permanent mistakes get made.',
    tags: ['cycles'],
  },
  correction: {
    term: 'Correction',
    short: 'A drop of 10–20% from a recent high.',
    long: 'A decline of 10% to 20% from a recent high. Corrections happen roughly once a year on average and are a normal feature of markets rather than a sign something has broken.',
    tags: ['cycles'],
  },
  option: {
    term: 'Option',
    short: 'A contract giving the right — not the obligation — to trade at a set price.',
    long: 'A contract giving the buyer the right, but not the obligation, to buy (call) or sell (put) 100 shares at a set strike price before an expiration date. Buyers pay a premium; if the option expires worthless, the entire premium is lost.',
    tags: ['options', 'risk'],
  },
  call: {
    term: 'Call Option',
    short: 'The right to BUY 100 shares at the strike price.',
    long: 'An option giving the right to buy 100 shares at the strike price before expiration. Buyers of calls profit if the stock rises meaningfully above the strike plus the premium paid.',
    tags: ['options'],
  },
  put: {
    term: 'Put Option',
    short: 'The right to SELL 100 shares at the strike price.',
    long: 'An option giving the right to sell 100 shares at the strike price before expiration. Puts gain value when the stock falls, which is why they are used both to speculate on declines and to insure existing holdings.',
    tags: ['options'],
  },
  strike: {
    term: 'Strike Price',
    short: 'The fixed price an option lets you buy or sell at.',
    long: 'The fixed price at which an option holder may buy (call) or sell (put) the underlying shares. The relationship between the strike and the current price determines whether an option is in or out of the money.',
    tags: ['options'],
  },
  premium: {
    term: 'Premium',
    short: 'The price paid for an option contract — the maximum a buyer can lose.',
    long: 'The price paid to buy an option, quoted per share but sold in contracts of 100. A $2.50 premium costs $250 per contract, and that $250 is the entire amount a buyer can lose.',
    tags: ['options'],
  },
  'theta decay': {
    term: 'Theta Decay',
    short: 'The daily loss of an option’s value as expiration approaches.',
    long: 'The erosion of an option’s value as time passes, accelerating near expiration. It is why an option buyer can be right about direction and still lose money — the stock has to move enough, and soon enough.',
    tags: ['options', 'risk'],
  },
  leverage: {
    term: 'Leverage',
    short: 'Using borrowed money or derivatives to amplify exposure.',
    long: 'Amplifying exposure using borrowed money or derivatives, so gains and losses are both multiplied. Leverage does not change whether you are right — it changes whether you survive being wrong.',
    tags: ['risk'],
  },
  'short interest': {
    term: 'Short Interest',
    short: 'The % of a company’s shares currently sold short.',
    long: 'The percentage of a company’s tradable shares that have been borrowed and sold short by investors betting on a decline. Unusually high short interest can set up a short squeeze, but it is a description of positioning, not a prediction.',
    tags: ['risk', 'advanced'],
  },
  'short squeeze': {
    term: 'Short Squeeze',
    short: 'A price spike caused by short sellers being forced to buy back.',
    long: 'A rapid price rise driven by short sellers buying shares to close losing positions, which pushes the price higher and forces still more buying. Squeezes are violent, self-limiting, and impossible to time reliably.',
    tags: ['risk', 'advanced'],
  },
  'penny stock': {
    term: 'Penny Stock',
    short: 'A very low-priced, thinly traded, often unlisted stock.',
    long: 'A stock trading at a very low price, typically under $5 and often off the main exchanges. Low prices come with minimal disclosure requirements, terrible liquidity and a long history of manipulation.',
    tags: ['risk'],
  },
  'catalyst': {
    term: 'Catalyst',
    short: 'A specific dated event expected to move a stock.',
    long: 'A specific, usually scheduled event that could re-rate a stock: an earnings release, a regulatory decision, a product launch, a court ruling. Speculative theses without a catalyst are just hoping.',
    tags: ['advanced', 'strategy'],
  },
  'asymmetric bet': {
    term: 'Asymmetric Bet',
    short: 'A position where the possible upside far outweighs the capped downside.',
    long: 'A position where the realistic upside is several times larger than the maximum downside. Buying an option is structurally asymmetric — you can lose 100% of a small premium, or make several times it — which is only useful if the position is genuinely small.',
    tags: ['strategy', 'risk'],
  },
  fomo: {
    term: 'FOMO',
    short: 'Fear of missing out — buying because something already went up.',
    long: 'Fear Of Missing Out: the urge to buy because a price has already risen sharply and others are profiting. It reliably produces buying near tops, because the feeling is strongest exactly when a move is most extended.',
    tags: ['psychology'],
  },
  'loss aversion': {
    term: 'Loss Aversion',
    short: 'Losses hurt roughly twice as much as equivalent gains feel good.',
    long: 'The well-documented finding that a loss is felt roughly twice as intensely as a gain of the same size. It causes people to hold losers hoping to break even and to sell winners too early.',
    tags: ['psychology'],
  },
  'dollar cost averaging': {
    term: 'Dollar-Cost Averaging',
    short: 'Investing a fixed amount on a fixed schedule regardless of price.',
    long: 'Investing a fixed sum at regular intervals regardless of price, so you buy more shares when prices are low and fewer when high. Its real benefit is behavioural: it removes the decision that people most often get wrong.',
    tags: ['strategy'],
  },
  'position sizing': {
    term: 'Position Sizing',
    short: 'Deciding how much to risk on one idea.',
    long: 'Deciding how much capital to commit to a single position. It is the single most important risk control available to an individual investor, and the one beginners skip: being wrong is survivable, being wrong and oversized is not.',
    tags: ['risk', 'strategy'],
  },
  'compound interest': {
    term: 'Compound Interest',
    short: 'Returns earning returns on themselves over time.',
    long: 'Growth that accrues on both the original amount and on previously earned returns, so gains accelerate over long periods. Compounding is the entire mathematical argument for starting early, and it needs decades to be dramatic.',
    tags: ['basics', 'strategy'],
  },
}

/**
 * Secondary index by display name, so a lookup works whether the caller passes
 * the storage key ("market cap") or the term as it reads on the page
 * ("Market Capitalisation"). Without this, <KeyTerm term="P/E Ratio" /> would
 * silently render a heading with no definition under it.
 */
const BY_DISPLAY_NAME = Object.fromEntries(
  Object.values(GLOSSARY).map((entry) => [entry.term.toLowerCase(), entry])
)

/** Case-insensitive lookup used by <Term> and <KeyTerm>. */
export function defineTerm(key) {
  const k = String(key).trim().toLowerCase()
  return GLOSSARY[k] ?? BY_DISPLAY_NAME[k] ?? null
}

/** Alphabetical list for the /glossary page. */
export const GLOSSARY_LIST = Object.entries(GLOSSARY)
  .map(([key, value]) => ({ key, ...value }))
  .sort((a, b) => a.term.localeCompare(b.term))
