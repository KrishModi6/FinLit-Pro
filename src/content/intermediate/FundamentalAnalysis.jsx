import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A company earns $200 million in net income and has 50 million shares outstanding. Its stock trades at $60. What is its trailing P/E?',
    options: ['3', '15', '20', '60'],
    answer: 1,
    explanation: 'EPS is $200m ÷ 50m shares = $4.00. P/E is $60 ÷ $4.00 = 15. The tempting wrong answer is 20, which comes from dividing price by something other than per-share earnings. Always reduce net income to a per-share figure first, because price is a per-share number too.',
  },
  {
    prompt: 'A company buys back 10% of its shares and net income stays exactly flat. What happens to EPS?',
    options: [
      'It falls, because cash left the business',
      'It stays the same, because profit did not change',
      'It rises by roughly 11%, because the same profit is split across fewer shares',
      'It becomes undefined',
    ],
    answer: 2,
    explanation: 'Dividing the same numerator by a smaller denominator raises the result: 1 ÷ 0.9 is about 1.11, so EPS climbs roughly 11%. Answer B is the classic trap: the business genuinely did not earn a cent more, but EPS still went up, which is exactly why you check whether earnings growth came from operations or from share count.',
  },
  {
    prompt: 'A stock with a P/E of 7 is cheaper, and therefore a better value, than one with a P/E of 34.',
    type: 'tf',
    answer: false,
    explanation: 'A low P/E often means the market expects earnings to shrink, not that the market has made a mistake. That is the value trap. A high P/E means growth is already priced in, which is its own risk. Neither number means anything until you compare it with the same company’s history and with direct competitors in the same industry.',
  },
  {
    prompt: 'Which comparison of debt-to-equity ratios is actually informative?',
    options: [
      'A regional bank at 4.0 versus a software company at 0.1',
      'Two mid-sized utilities in the same country, one at 1.2 and one at 2.4',
      'A retailer today versus an airline in 1995',
      'Any two companies, since lower debt is always better',
    ],
    answer: 1,
    explanation: 'Capital structure is an industry norm before it is a company choice. Utilities and banks carry heavy debt by design; software firms usually carry almost none. Comparing across those industries tells you about the industries, not the companies. Two utilities in the same market, though, are running the same playbook, so the gap is a real signal worth investigating.',
  },
  {
    prompt: 'Free cash flow is generally harder for management to massage than reported earnings.',
    type: 'tf',
    answer: true,
    explanation: 'Earnings involve judgement calls: how fast to depreciate assets, when to recognise revenue, which costs to label one-off. Free cash flow tracks money that actually moved, so there are fewer levers. It is not tamper-proof, but it is a useful cross-check when reported profit and cash generation start telling different stories.',
  },
]

export default function FundamentalAnalysis({ moduleId }) {
  return (
    <>
      <p className="lead">Two companies make the same product, in the same country, for the same customers. One trades at $40 a share, the other at $95. Which is more expensive? You cannot answer that yet, and neither can anyone who only knows the prices. Fundamental analysis is the discipline of asking a better question: what does this business actually earn, and what am I paying for each dollar of it?</p>

      <h2>Earnings per share: the number everything else is built on</h2>
      <p>Price on its own is meaningless because share counts are arbitrary. A company can split its stock ten-for-one tomorrow and every share price falls by 90% while the business is completely unchanged. So the first move in fundamental analysis is always to reduce the business to a per-share figure.</p>

      <KeyTerm term="EPS" />

      <p><Term k="eps">Earnings per share</Term> is net income divided by shares outstanding. Suppose a coffee chain reports $480 million of net income for the year and has 320 million shares. That is $480m ÷ 320m = $1.50 of profit per share. If you own one share, the business earned $1.50 on your behalf. You do not receive that $1.50 (most of it stays inside the company or comes back as buybacks), but it is your claim on it.</p>

      <h3>Trailing, forward, and the difference that matters</h3>
      <p>Trailing EPS uses the last four reported quarters. It is a fact: the money was earned, audited, and filed. Forward EPS uses analyst estimates for the next twelve months. It is a forecast, and forecasts drift. When a site shows you an EPS figure without saying which one it is, assume trailing and go check.</p>

      <p>There is a second split that trips people up more often. GAAP EPS follows standard accounting rules. Adjusted EPS, sometimes called non-GAAP or “core” earnings, is GAAP with certain costs removed: restructuring charges, stock-based compensation, acquisition expenses. Sometimes those exclusions are reasonable, because a one-time legal settlement really does not tell you about next year. Sometimes a company excludes the same “one-time” cost five years running.</p>

      <Callout variant="real-talk">
        <p>Management chooses what goes into adjusted EPS. Nobody outside the company votes on it. When adjusted EPS is dramatically higher than GAAP EPS year after year, that gap is not noise: it is the company telling you which costs it would prefer you ignore. Read the reconciliation table in the earnings release and decide for yourself whether you agree.</p>
      </Callout>

      <h3>The buyback subtlety</h3>
      <p>Here is a genuinely important mechanic that most beginners miss. EPS can rise without the business earning one extra dollar. Take that coffee chain: $480m of net income, 320m shares, $1.50 EPS. Now the company spends cash buying back 32 million of its own shares, leaving 288 million. Net income is still $480m. EPS is now $480m ÷ 288m = $1.67. That is an 11% increase in “earnings growth” produced entirely by arithmetic.</p>

      <p>Buybacks are not a scam: reducing the share count genuinely increases each remaining owner’s slice. But when a headline says earnings grew 11%, you want to know how much came from selling more coffee and how much came from shrinking the denominator. Revenue growth, which we get to shortly, is one way to check.</p>

      <h2>The P/E ratio: what you pay for a dollar of profit</h2>

      <KeyTerm term="P/E Ratio" />

      <p>The <Term k="pe ratio">price-to-earnings ratio</Term> is share price divided by EPS. Our coffee chain at $1.50 EPS, trading at $37.50, has a P/E of 25. Say that out loud in plain English: you are paying $25 for each $1 of annual profit. At that rate, holding earnings flat, it takes 25 years of profit to equal your purchase price.</p>

      <p>That framing does most of the work. It also explains why P/E travels with expectations. Nobody pays 25 years of current profit for a business they expect to stagnate; they pay it because they expect year 5 to earn far more than year 1. Trailing P/E uses trailing EPS, forward P/E uses estimated EPS, and forward P/E is almost always the lower of the two for a growing company, because the denominator is bigger.</p>

      <h3>High is not expensive and low is not cheap</h3>
      <p>This is where most people go wrong, and it is worth slowing down for. A P/E of 40 does not mean the stock is overpriced. It means the market is pricing in substantial future growth, and that the stock will fall hard if the growth does not show up. A P/E of 6 does not mean bargain. It usually means the market expects earnings to decline, and the market is often right.</p>

      <Callout variant="warning" title="The value trap">
        <p>A value trap is a stock that looks statistically cheap and keeps getting cheaper because the business is genuinely deteriorating. Newspaper publishers in the 2000s traded at single-digit P/Es for years, and the earnings kept shrinking underneath them, so the ratio never actually improved for the people who bought.</p>
        <p>Before you conclude the market has mispriced something, write down what you think the market is missing and why you would know it when thousands of professionals do not. If you cannot answer, the low P/E is probably information, not opportunity.</p>
      </Callout>

      <p>P/E only carries meaning in two comparisons: against the same company’s own history, and against direct competitors in the same industry. Normal ranges differ enormously by sector: capital-intensive, slow-growth industries typically trade at low multiples while fast-growing software businesses trade at high ones, and that difference reflects structure, not mispricing. Comparing a utility’s P/E to a software company’s P/E is like comparing a marathon time to a sprint time.</p>

      <p>One more limit: if a company has no profit, P/E is undefined or negative, and either way useless. Plenty of young companies fall in this bucket. You need different tools for them (price-to-sales, cash burn, the path to profitability), which is a topic of its own.</p>

      <h2>Revenue growth: the top line and its flattery</h2>
      <p>Revenue is total sales before any costs. It sits at the top of the income statement, which is why people call it the top line. Growth here matters because earnings growth without revenue growth eventually runs out of road: you can only cut costs and retire shares for so long.</p>

      <p>But revenue growth flatters easily. Three ways it can look better than it is. First, discounting: sell at 30% off and volume jumps, revenue rises, and profitability quietly erodes. Second, acquisitions: buy a company with $500m of sales and your revenue grows $500m, which tells you nothing about whether the business you already owned is healthy. Look for the phrase “organic growth”, which strips acquisitions out. Third, one-off demand spikes that never repeat.</p>

      <p>The quickest quality check is gross margin (revenue minus the direct cost of producing what you sold, as a percentage of revenue), because rising sales alongside falling gross margin usually means growth was bought with price cuts.</p>

      <h2>Debt-to-equity: how fragile is this business?</h2>
      <p><Term k="debt to equity">Debt-to-equity</Term> is total debt divided by shareholders’ equity. Suppose a manufacturer carries $600 million of debt and $400 million of equity. That is 600 ÷ 400 = 1.5, meaning $1.50 of borrowed money for every $1.00 of owner money.</p>

      <p><Term k="leverage">Leverage</Term> magnifies outcomes in both directions, and the second direction is the one to sit with. Imagine two companies, each earning $100m on $1,000m of assets. The unlevered one funded those assets entirely with equity. The levered one funded $700m with debt at 6%, costing $42m a year in interest. In a good year the levered company’s owners do better, because the same profit is spread over a much smaller equity base. In a year when operating profit falls to $40m, the unlevered company has a mediocre year and the levered one cannot cover its interest.</p>

      <Callout variant="note">
        <p>Interest costs also reset. When a company refinances debt taken out at 3% into an environment where it must pay 7%, nothing about the business changed, but the annual cash cost of the same debt more than doubled. This is why rising rates hurt heavily indebted companies first and hardest.</p>
      </Callout>

      <p>Crucially, “normal” D/E varies enormously by industry. Utilities borrow heavily because their revenue is regulated and predictable, which makes debt safe to carry. Banks are leveraged by the nature of what they do. Mature software companies often carry almost no debt at all. A D/E of 2.0 could be conservative for one and alarming for another, so cross-industry comparison is not just imprecise; it is meaningless.</p>

      <h2>Putting the four together</h2>
      <p>Here are two entirely hypothetical companies in the same industry. Neither exists; the numbers are invented to make a point.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Northline Corp</th>
              <th>Grayvale Inc</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>EPS (trailing)</td>
              <td>$2.40</td>
              <td>$3.10</td>
            </tr>
            <tr>
              <td>Share price</td>
              <td>$72.00</td>
              <td>$27.90</td>
            </tr>
            <tr>
              <td>P/E</td>
              <td>30</td>
              <td>9</td>
            </tr>
            <tr>
              <td>Revenue growth (yr/yr)</td>
              <td>18%</td>
              <td>-4%</td>
            </tr>
            <tr>
              <td>Debt-to-equity</td>
              <td>0.4</td>
              <td>2.1</td>
            </tr>
            <tr>
              <td>One-line read</td>
              <td>Priced for growth it must keep delivering</td>
              <td>Statistically cheap, shrinking, and levered</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Look at P/E alone and Grayvale is the obvious pick at a third the multiple. Add revenue growth and the picture inverts: Grayvale is shrinking, so its earnings base is likely to erode and that P/E of 9 may be 14 next year without the price moving at all. Add debt and the risk sharpens: a shrinking business with $2.10 of debt per $1.00 of equity has very little room for a bad quarter.</p>

      <p>Northline is not therefore “the good one”. A P/E of 30 means the market has already paid for years of that 18% growth. If growth slows to 6%, the stock can fall sharply even though the company is still profitable and still growing. Four numbers do not produce a verdict. They produce a much sharper question for each company: for Northline, is the growth durable? For Grayvale, is the decline permanent?</p>

      <Callout variant="did-you-know">
        <p>Two metrics worth knowing by name so they do not blindside you later. Free cash flow is cash from operations minus capital expenditure: actual money left over after keeping the business running. It is harder to massage than earnings, because it tracks money that genuinely moved rather than accounting judgements. Return on equity is net income divided by shareholders’ equity, and it answers how efficiently the company turns owner capital into profit. One caution: heavy debt shrinks the equity denominator and inflates ROE, so always read it next to D/E.</p>
      </Callout>

      <Callout variant="warning" title="No ratio is a buy signal">
        <p>There is no P/E threshold that means buy and no D/E level that means sell. Every one of these numbers is backward-looking, industry-dependent, and knowable by everyone with an internet connection, which means it is already reflected in the price.</p>
        <p>What ratios do is narrow the question. A low P/E tells you to go find out what the market expects to go wrong. A high D/E tells you to check the debt maturity schedule and interest coverage. They tell you what to investigate. They never tell you what to do.</p>
      </Callout>

      <h2>Where to get the real numbers</h2>
      <p>All of this is free, and the primary sources are better than the summaries. Every US-listed company runs an investor-relations page carrying its quarterly and annual reports. The annual report is the 10-K and the quarterly is the 10-Q, both filed with the SEC and searchable on the EDGAR database. These are the documents the company is legally accountable for, and the notes buried in the back are where the interesting detail lives: debt maturities, segment breakdowns, what exactly got excluded from adjusted earnings.</p>

      <p>Aggregator sites like Yahoo Finance or your broker’s research tab are convenient and fine for a first pass. Just remember they are secondhand: they make choices about trailing versus forward, GAAP versus adjusted, and which twelve months count. When two sites disagree about a company’s P/E, the filing is the tiebreaker.</p>

      <TryIt moduleId={moduleId} placeholder="Company A: P/E ___, EPS ___ · Company B: P/E ___, EPS ___ · What the gap might mean: …">
        <p>Pick any company you already know something about. Find its trailing P/E and trailing EPS, then find the same two numbers for one direct competitor in the same industry. Note which source you used and whether the EPS figure is GAAP or adjusted.</p>
        <p>Then write one sentence on what the gap might mean. Not what you would buy, but what the difference in multiple suggests the market believes about each company’s future. If the P/Es are nearly identical, say that, and say what would have to change for them to diverge.</p>
      </TryIt>

      <h2>The one thing to carry forward</h2>
      <p>Fundamental analysis is not a scoring system that ranks companies from best to worst. It is a way of turning a vague feeling about a business into a specific, checkable claim about earnings, price, growth and risk: a claim that can be proven wrong, which is the only kind worth holding.</p>

      <p>If you remember one sentence from this lesson, make it this: every ratio is a comparison, and a ratio without a comparison is just a number. P/E compared with the company’s own history and its direct competitors. Growth compared with the industry and with the company’s own margin trend. Debt compared with what is normal for that type of business. Strip away the comparison and you have arithmetic, not analysis.</p>

      <p>Next up: reading a company’s financial statements directly (the income statement, balance sheet and cash flow statement), and how the four numbers from this lesson are assembled out of them.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
