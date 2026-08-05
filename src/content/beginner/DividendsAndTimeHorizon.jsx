import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'To receive the next dividend payment, when must you own the shares?',
    options: [
      'Any time before the payment date',
      'Before the ex-dividend date',
      'On the declaration date',
      'For at least one full quarter',
    ],
    answer: 1,
    explanation: 'Ownership has to be established before the ex-dividend date. Buying on or after the ex-date means the seller keeps the payment, no matter that the cash has not gone out yet. The payment date is just when the money moves.',
  },
  {
    prompt: 'A share trades at $50 and pays a quarterly dividend of $0.25. What is the dividend yield?',
    options: ['0.5%', '2%', '4%', '5%'],
    answer: 1,
    explanation: 'Annualise first: $0.25 x 4 = $1.00 a year. Then $1.00 ÷ $50 = 0.02, so 2%. The common mistake is dividing the quarterly figure by the price and reporting 0.5%.',
  },
  {
    prompt: 'A stock whose dividend yield jumps from 3% to 11% has become a better deal, because you are now paid more for the same company.',
    type: 'tf',
    answer: false,
    explanation: 'Yield is dividend ÷ price, so it usually spikes because the price collapsed, not because the payout grew. A yield far above a company’s peers is often the market forecasting a dividend cut. That is the yield trap.',
  },
  {
    prompt: 'In the $2,000 at a hypothetical 8% table, which stretch of time adds the most dollars?',
    options: ['Years 1 to 10', 'Years 10 to 20', 'Years 20 to 30', 'Years 30 to 40'],
    answer: 3,
    explanation: 'Years 30 to 40 add roughly $23,300, which is more than the first thirty years produced in total. Growth compounds on a larger and larger base, which is the whole argument for starting early rather than investing more later.',
  },
  {
    prompt: 'Dollar-cost averaging works mainly because buying on a fixed schedule is mathematically guaranteed to beat investing a lump sum.',
    type: 'tf',
    answer: false,
    explanation: 'It carries no mathematical guarantee, and historically lump sums have often come out ahead simply because markets rise more often than they fall. Its real value is behavioural: it removes the timing decision that people most reliably get wrong.',
  },
]

export default function DividendsAndTimeHorizon({ moduleId }) {
  return (
    <>
      <p className="lead">Own a share of a company like Coca-Cola and a little cash appears in your brokerage account four times a year, without you lifting a finger. That is a <Term k="dividend">dividend</Term>, and it is the closest thing the stock market has to a paycheck. It is also misunderstood more often than almost anything else here, starting with the fact that it is not free money.</p>

      <h2>Cash out of profits</h2>

      <p>A company that earns more than it needs to run itself has a decision to make. It can reinvest the surplus, buy back its own shares, sit on the cash, or hand some of it to the people who own the business. That last option is the dividend: a cash payment, declared by the board of directors, usually paid quarterly in the United States.</p>

      <KeyTerm term="Dividend" />

      <p>Three things about that definition matter more than they look. It is declared, which means a human committee votes on it every quarter and can vote differently next quarter. It is not interest, so nobody owes it to you and no contract enforces it. And it can be cut, suspended, or eliminated at any time. In the spring of 2020, when travel collapsed, a long list of well-known companies cut or suspended dividends within weeks. Shareholders had no recourse, because there was nothing to enforce.</p>

      <p>Companies still hate cutting. A cut is read as an admission of trouble and the share price usually falls hard on the news, so boards defend the payment for as long as they plausibly can. That reluctance is why a long unbroken record of increases carries weight. A <Term k="dividend aristocrat">Dividend Aristocrat</Term> is an S&amp;P 500 member that has raised its dividend for 25 consecutive years or more, which means it kept raising through 2008 and through 2020. That is a real signal about how the business is run. It is still not a guarantee about the future.</p>

      <h2>The four dates, explained properly</h2>

      <p>Every dividend runs through the same four-date sequence, and the sequence trips up nearly everyone the first time.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>What happens</th>
              <th>Why you care</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Declaration date</td>
              <td>The board announces the amount and the other three dates</td>
              <td>Nothing is owed to anyone before this</td>
            </tr>
            <tr>
              <td>Ex-dividend date</td>
              <td>Shares begin trading without the right to this payment</td>
              <td>You must already own the shares before this day</td>
            </tr>
            <tr>
              <td>Record date</td>
              <td>The company checks its books to see who the holders are</td>
              <td>Set by the company; the ex-date is derived from it</td>
            </tr>
            <tr>
              <td>Payment date</td>
              <td>Cash actually lands in your account</td>
              <td>Typically a few weeks after the record date</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>The ex-dividend date is the one that decides everything. Buy on or after it and the seller keeps the payment even though the cash has not moved yet. Before May 2024 the ex-date sat one business day ahead of the record date, because US trades took two days to settle. Since US equities moved to T+1 settlement, the ex-date and the record date usually fall on the same day.</p>

      <h3>Why the price drops on the ex-date</h3>

      <p>Here is the fact that surprises people. On the morning of the ex-dividend date, the share price typically opens lower by roughly the dividend amount. If a company pays $0.80 a share, the stock starts the day about $0.80 cheaper, before any normal trading noise moves it around.</p>

      <p>That is not a glitch. The cash is leaving the company and going into shareholders’ accounts, so the company is worth exactly that much less than it was the day before. You did not gain anything; you converted part of your holding into cash.</p>

      <Callout variant="did-you-know">
        <p>This kills a strategy that sounds clever and gets reinvented constantly: buy the day before the ex-date, collect the dividend, sell the next day. You receive $0.80 and the share you sell is worth about $0.80 less. You have earned nothing, paid any spread and commission twice, and possibly created a taxable event. The market is not leaving a free quarterly payout lying on the floor.</p>
      </Callout>

      <h2>Yield is a ratio, not a reward</h2>

      <KeyTerm term="Dividend Yield" />

      <p><Term k="dividend yield">Dividend yield</Term> is the annual dividend divided by the current share price. Suppose a stock trades at $40 and pays $0.30 per share each quarter. Annualise the payment first: $0.30 x 4 = $1.20 a year. Then $1.20 ÷ $40 = 0.03, so the yield is 3%. Forgetting to annualise is the single most common error in this calculation.</p>

      <p>Now watch what happens to that ratio when the business gets into trouble. The dividend stays at $1.20 for the moment, but bad news drags the price from $40 down to $12. The yield is now $1.20 ÷ $12, or 10%. Nothing improved. The company got worse and the arithmetic made it look generous.</p>

      <Callout variant="warning" title="The yield trap">
        <p>An unusually high yield is usually a forecast, not a bargain. When a stock yields far more than its industry peers, the market is typically pricing in a dividend cut that has not been announced yet. If the cut comes, you lose the income and hold a share that has already fallen: losses on both sides of the ratio.</p>
        <p>Yield alone tells you almost nothing. Before treating a number as attractive, look at whether earnings and free cash flow actually cover the payment, and why the price fell in the first place.</p>
      </Callout>

      <h2>Why some excellent companies pay nothing</h2>

      <p>Plenty of outstanding businesses have never paid a cent in dividends, and that is a deliberate choice rather than a failure. If a company can put $1 back into new stores, research, or capacity and turn it into more than $1 of future value, shareholders are better off leaving the money inside. Handing it back would be the wasteful option.</p>

      <p>So the pattern tends to follow the stage of the business. A young company with more opportunities than cash reinvests everything. A mature company with a dominant position and limited room to expand generates more cash than it can sensibly deploy, and starts returning it. Amazon paid no dividend for its first three decades as a public company while it built out the business. Johnson &amp; Johnson, operating in a slower and more settled market, has paid and raised one for many years.</p>

      <p>Neither model is superior. They are different points on the same lifecycle, and total return (price change plus dividends) is what actually lands in your account.</p>

      <h3>Reinvesting what you receive</h3>

      <p>Most brokers offer a dividend reinvestment plan, or DRIP, which automatically uses each payment to buy more shares of the same company instead of leaving cash idle. Those extra shares then pay dividends of their own, which buy more shares again.</p>

      <Callout variant="example">
        <p>Say you hold 100 shares of a stock priced at $50 with a 3% yield, and the price and payout both stay flat. Year one pays $150, which buys 3 more shares. Year two you hold 103 shares, so the payment is about $154.50. It is small at first and almost boring. Left alone for thirty years, that quiet loop is responsible for a large share of the total return of dividend-paying stocks.</p>
      </Callout>

      <h2>The long game</h2>

      <p><Term k="compound interest">Compound interest</Term> means your returns start earning returns. It sounds mild stated that way, so put numbers on it. Here is $2,000 invested once and left alone, at a hypothetical 8% a year.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Years</th>
              <th>Value</th>
              <th>Total gained</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>5</td><td>$2,939</td><td>$939</td></tr>
            <tr><td>10</td><td>$4,318</td><td>$2,318</td></tr>
            <tr><td>20</td><td>$9,322</td><td>$7,322</td></tr>
            <tr><td>30</td><td>$20,125</td><td>$18,125</td></tr>
            <tr><td>40</td><td>$43,449</td><td>$41,449</td></tr>
          </tbody>
        </table>
      </div>

      <p>Look at the last row against the one above it. Years 30 to 40 add about $23,300, while the entire first thirty years added $18,125. The final decade out-earns the first three combined, using the same money and the same rate. That is the whole argument for starting early: the last decade is the valuable one, and you only get it by having started.</p>

      <Callout variant="note">
        <p>The 8% here is an illustration, not a promise. Real returns swing enormously from year to year: some years are up 25%, some are down 35%, and almost none land on the average. Long-run US stock market returns are commonly cited near 10% a year before inflation, but that is a historical average over a very long window, not a rate anyone is entitled to going forward.</p>
      </Callout>

      <h2>What actually changes over decades</h2>

      <p>Here is the part worth internalising: the stock does not behave differently for a long-term investor. What changes is your relationship to <Term k="volatility">volatility</Term>. Over a single day, price movement is mostly noise: a headline, a nervous fund manager, an algorithm rebalancing. Over decades, that noise averages out and what dominates is whether the underlying businesses actually grew earnings.</p>

      <p>The concrete implication is unglamorous and important. Money you will need within the next few years (tuition, a deposit, anything with a date attached) should not be in stocks at all. Not because stocks are bad, but because a 30% drawdown in the wrong eighteen months forces you to sell at the worst possible moment. Time horizon is not a preference. It is the thing that decides whether an asset is appropriate for you.</p>

      <h2>Buying on a schedule</h2>

      <p><Term k="dollar cost averaging">Dollar-cost averaging</Term> means investing a fixed amount at fixed intervals (say $100 on the first of every month) regardless of price. When prices are low your $100 buys more units; when prices are high it buys fewer.</p>

      <Callout variant="real-talk">
        <p>You will see this sold as a mathematical edge. It is not one. Historically, investing a lump sum immediately has often beaten spreading it out, for the boring reason that markets rise more often than they fall.</p>
        <p>What dollar-cost averaging actually does is remove the decision people get wrong most reliably: when to buy. Left to judgement, investors buy after good news and freeze after bad news, which is precisely backwards. A schedule takes the judgement out. That is a behavioural tool, and it is worth a great deal. Just be honest about which kind of tool it is.</p>
      </Callout>

      <p>Taxes and fees are real, and they differ enormously by country. Dividends may be taxed as ordinary income or at a lower rate, tax-advantaged accounts change the picture completely, and some countries withhold tax on foreign dividends before the money ever reaches you. This lesson does not cover any of that, deliberately, because getting it wrong for your jurisdiction would be worse than not stating it. Check your local rules, or ask someone qualified in your country.</p>

      <TryIt moduleId={moduleId} placeholder="Company and ticker, the four dates, the quarterly amount, the annual amount, the price you used, and the yield you calculated.">
        <p>Pick a company you already know that pays a dividend, then go to its investor relations page or a site like Yahoo Finance and find the dividend history. Write down all four dates for the most recent payment and the amount per share. Then annualise it, look up the current price yourself, and calculate the yield to one decimal place. Finish with one sentence: does that yield look ordinary for the industry, or high enough that you would want to know why?</p>
      </TryIt>

      <h2>What to carry forward</h2>

      <p>If one idea survives from this lesson, make it this: a dividend is a transfer, not a gift. The cash comes out of the company you own, which is why the price adjusts on the ex-date, why chasing the payment for its own sake achieves nothing, and why a spectacular yield usually means a falling price rather than a generous board.</p>

      <p>The second idea is that time does the work you cannot. Nobody controls next year’s return. You do control how early you start, whether the money you invest is money you can leave alone, and whether you keep buying on a schedule when the news is bad. Those three choices explain more real-world outcomes than any stock-picking skill.</p>

      <p>Next up is portfolio construction: how <Term k="diversification">diversification</Term> works, why owning thirty stocks in the same industry is not diversified, and how index funds solve most of this problem in one purchase.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
