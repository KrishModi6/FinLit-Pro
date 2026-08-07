import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'SIPC protection at a US brokerage covers which of the following?',
    options: [
      'Any losses if the stocks you bought fall in value',
      'Up to $500,000 per customer, including $250,000 in cash, if the brokerage firm itself fails',
      'Unlimited protection on every asset held in the account',
      'Trading mistakes, if you report them within 30 days',
    ],
    answer: 1,
    explanation:
      'SIPC exists for one scenario: the broker goes under and your assets need to be recovered or transferred. The tempting wrong answer is the first one; plenty of people assume SIPC is insurance against a bad investment. It is not. If you buy a stock and it drops 60%, that loss is entirely yours.',
  },
  {
    prompt: 'A stock trading at $600 a share must be a larger company than one trading at $12 a share.',
    type: 'tf',
    answer: false,
    explanation:
      'Share price on its own tells you nothing about company size, because a company chooses how many shares to slice itself into. Size is price multiplied by shares outstanding, which is market cap. A $600 stock with 20 million shares is a $12 billion company; a $12 stock with 5 billion shares is a $60 billion company.',
  },
  {
    prompt: 'A quote shows a bid of $4.10 and an ask of $4.35. What does that mostly tell you?',
    options: [
      'The stock is undervalued by 25 cents',
      'The company is about to report earnings',
      'The stock is thinly traded, so buying and selling it carries a real hidden cost',
      'A dividend of 25 cents is about to be paid',
    ],
    answer: 2,
    explanation:
      'The gap between bid and ask is the spread, and a wide spread is a liquidity signal. Here you would buy at $4.35 and could only sell instantly at $4.10, down about 5.7% the moment you own it. Nothing about the spread says the stock is cheap or expensive; it says the stock is hard to get in and out of.',
  },
  {
    prompt: 'Today a stock trades 9 million shares against an average volume of 1.2 million. The most reasonable reading is:',
    options: [
      'The stock is going up, because heavy volume means buying',
      'Something happened (news, earnings or an index change) and unusual attention is on the stock',
      'The company has issued 7.8 million new shares',
      'The market cap has increased roughly sevenfold',
    ],
    answer: 1,
    explanation:
      'Volume measures activity, not direction. Every share bought was also sold by somebody, so a huge volume day is equally consistent with a crash or a surge. What it reliably signals is that the stock has become interesting to a lot of people at once.',
  },
  {
    prompt: 'Robinhood, Fidelity and Charles Schwab all charge a per-trade commission on ordinary US stock trades.',
    type: 'tf',
    answer: false,
    explanation:
      'All three offer commission-free US stock trading, which is why commissions are no longer the thing that separates them. The real differences are account types, research tools, fractional-share support and how easily you can reach a human being.',
  },
]

export default function BrokeragesAndQuotes({ moduleId }) {
  return (
    <>
      <p className="lead">You cannot walk into the New York Stock Exchange, hand someone forty dollars and walk out owning a share. Exchanges only transact with member firms. So every trade you will ever place begins the same way: you tell a middleman what you want, and the middleman goes to the market on your behalf.</p>

      <h2>What a brokerage is for</h2>
      <p>A <Term k="brokerage">brokerage</Term> is a licensed firm that holds your cash and your securities, routes your orders to an exchange or a market maker, and keeps the records that prove what you own. It also handles the plumbing you never see: settlement, tax forms, dividend payments landing in your account, corporate actions like stock splits.</p>
      <p>That is the whole job. A broker is not a fund manager and not your advisor. It is closer to a bank with a trading window attached, and like a bank, the interesting questions are about safety, cost and access rather than about excitement.</p>

      <h2>Three brokers as three archetypes</h2>
      <p>It helps to look at real firms, not because you should pick one of them, but because they illustrate the trade-offs.</p>
      <p><strong>Robinhood</strong> is the mobile-first archetype. It launched with a deliberately stripped-down phone interface, popularised commission-free trading in the US, and built its revenue model substantially on payment for order flow: market makers pay the broker to send them customer orders to execute. Onboarding is fast and the app is easy to use, which is both the selling point and, as you will see below, the thing to watch.</p>
      <p><strong>Fidelity</strong> and <strong>Charles Schwab</strong> are the full-service archetype. Both are very large, long-established firms with decades of track record. They offer retirement accounts, custodial accounts, their own index funds, substantial research and screening tools, physical branch offices you can walk into, and phone support with actual humans. The interfaces are denser, because they are built for someone who may hold a dozen account types over forty years.</p>
      <p>All three offer commission-free US stock trading. For a beginner buying a broad index fund once a month, the practical difference between them is small, smaller than most online arguments suggest.</p>

      <Callout variant="real-talk">
        <p>I am not going to tell you which one to open, and you should be a little suspicious of anyone who does without asking about your situation first. Brokers pay referral bounties, and a startling amount of “best broker” content on the internet is affiliate marketing wearing a lab coat.</p>
        <p>What you can do instead is compare on things that actually differ.</p>
      </Callout>

      <h2>The checklist</h2>
      <p>Six questions, answerable in about fifteen minutes on each broker’s own website.</p>
      <ol>
        <li><strong>Fractional shares.</strong> Can you buy $25 of a stock trading at $300, or must you buy whole shares? If you are investing small amounts regularly, this matters more than anything else on the list.</li>
        <li><strong>Account minimums.</strong> Some accounts require an opening deposit. Many now require nothing. Check rather than assume.</li>
        <li><strong>Account types.</strong> Does the broker support the specific account you need: a taxable account, a retirement account, a custodial account for a minor? A broker that does not offer the account type you need is disqualified regardless of how good the app looks.</li>
        <li><strong>Research tools.</strong> Screeners, analyst reports, fund comparison tools, historical financials. Full-service brokers generally win here; whether you will use any of it is a fair question to ask yourself honestly.</li>
        <li><strong>Getting a human.</strong> Find the support page before you need it. Is there a phone number, a chat, a branch? When something goes wrong with an account holding your money, response time stops being an abstraction.</li>
        <li><strong>SIPC membership.</strong> Non-negotiable for a US broker, and it should be stated plainly at the bottom of the homepage.</li>
      </ol>

      <Callout variant="warning" title="What SIPC does and does not do">
        <p>SIPC covers up to $500,000 per brokerage customer, including up to $250,000 in cash. It protects you if the brokerage firm fails and your assets go missing or need to be transferred to another firm.</p>
        <p>It does not protect you against your investments losing value. If you put $10,000 into a stock and it falls to $3,000, SIPC owes you nothing; the system worked exactly as designed. This distinction is widely misunderstood, and misunderstanding it makes people feel safer than they are.</p>
      </Callout>

      <Callout variant="warning" title="On confetti and streaks">
        <p>Some apps celebrate a trade with animation, track daily login streaks, and put buying one tap away from the home screen. These are product decisions, and their measurable effect is to increase how often people trade.</p>
        <p>That direction is the wrong one. Research on individual investors has consistently found that the most active traders tend to underperform less active ones once costs are counted, and the gap is not small. You do not need to be scandalised by a nice interface. Just notice when an app is nudging you toward frequency, and treat frequency as a cost.</p>
      </Callout>

      <Callout variant="note" title="If you are under 18">
        <p>In the US, a minor generally cannot open a brokerage account alone. The normal route is a custodial account opened by a parent or guardian, who controls it until you reach the age of transfer set by your state. Some brokers also offer teen-branded accounts with a linked adult.</p>
        <p>Rules differ by country: minimum age, account types, and the tax treatment of everything inside them. Check the rules where you actually live rather than assuming the US version applies.</p>
      </Callout>

      <h2>Reading a quote, field by field</h2>
      <p>Open any quote page and you get a wall of numbers. Most people read exactly one of them. Here is a hypothetical company, Northwind Logistics, trading under the <Term k="ticker">ticker</Term> NWL, with every standard field laid out. The figures are invented and internally consistent so you can check the arithmetic yourself.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Field</th>
              <th>Example</th>
              <th>What it actually tells you</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Last price</td>
              <td>$42.04</td>
              <td>The price of the most recent completed trade. It is history, not a promise. The next trade can happen anywhere.</td>
            </tr>
            <tr>
              <td>Change / % change</td>
              <td>−0.86 (−2.0%)</td>
              <td>Movement since the previous close. The percentage is the useful half; the dollar figure means nothing without knowing the price it moved from.</td>
            </tr>
            <tr>
              <td>Day’s range</td>
              <td>41.60 – 43.15</td>
              <td>The low and high so far today. A wide range on ordinary news is a hint that the stock moves violently.</td>
            </tr>
            <tr>
              <td>52-week range</td>
              <td>28.40 – 51.90</td>
              <td>The past year’s extremes. Useful for context, misleading as a signal: “near the low” is not the same as “cheap”, and plenty of stocks set new lows all the way down.</td>
            </tr>
            <tr>
              <td>Open / previous close</td>
              <td>42.85 / 42.90</td>
              <td>Where today started and where yesterday ended. A large gap between them means the news arrived while the market was shut.</td>
            </tr>
            <tr>
              <td>Bid and ask, with size</td>
              <td>41.98 x 300 / 42.04 x 500</td>
              <td>The best price someone will currently pay, the best price someone will currently sell at, and how many shares are available at each. You buy at the ask and sell at the bid.</td>
            </tr>
            <tr>
              <td>Volume</td>
              <td>2.1 million</td>
              <td>Shares traded so far today. Activity, not direction: every buy was also a sell.</td>
            </tr>
            <tr>
              <td>Average volume</td>
              <td>1.4 million</td>
              <td>The typical day, usually over three months. Today against average is the comparison that carries information.</td>
            </tr>
            <tr>
              <td>Market cap</td>
              <td>$6.3 billion</td>
              <td>Price multiplied by shares outstanding: here, $42.04 across about 150 million shares. This is the company’s size in the market’s eyes.</td>
            </tr>
            <tr>
              <td>P/E ratio</td>
              <td>18.5</td>
              <td>Price divided by earnings per share. A rough gauge of how much you pay per dollar of profit. Full treatment comes in the Intermediate track.</td>
            </tr>
            <tr>
              <td>EPS</td>
              <td>$2.27</td>
              <td>Annual profit attributable to each share. Note that 42.04 divided by 2.27 gives the 18.5 above; the two fields are locked together.</td>
            </tr>
            <tr>
              <td>Dividend and yield</td>
              <td>$0.96 (2.3%)</td>
              <td>Cash paid per share per year, and that amount as a percentage of the price. Yield rises automatically when the price falls, which is why a very high yield is often a warning rather than a gift.</td>
            </tr>
            <tr>
              <td>Beta</td>
              <td>1.15</td>
              <td>How much the stock has historically moved relative to the whole market. Above 1 means it has swung harder than the index. More on this later in the course.</td>
            </tr>
            <tr>
              <td>Earnings date</td>
              <td>4 November (estimated)</td>
              <td>When the company next reports results. Prices frequently move sharply on this date, in either direction.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>Price is not size</h3>
      <KeyTerm term="Market Capitalisation">The total market value of a company’s shares: current share price multiplied by the number of shares outstanding. It is the standard measure of company size, and the reason a $12 stock can be a far bigger business than a $600 one.</KeyTerm>
      <p>This is the single most common beginner error, so it is worth repeating in a different shape. A company decides how many shares to divide itself into. Slice a $6.3 billion company into 150 million shares and each is worth about $42; slice the same company into 6.3 billion shares and each is worth a dollar. Nothing about the business changed. Compare market caps, never share prices.</p>

      <h3>Volume is a liquidity signal</h3>
      <KeyTerm term="Volume" />
      <p>Volume is how you judge <Term k="liquidity">liquidity</Term>, how easily you can convert between shares and cash without moving the price against yourself. The visible cost of poor liquidity is the <Term k="spread">spread</Term>, the gap between bid and ask.</p>

      <Callout variant="example">
        <p>Northwind trades 1.4 million shares on a typical day, bid 41.98 and ask 42.04. Buy 100 shares at the ask for $4,204. If you changed your mind one second later and sold at the bid, you would receive $4,198. The 6-cent spread cost you $6, or about 0.14% of the position.</p>
        <p>Now take a thinly traded stock quoted 4.10 bid, 4.35 ask. Buy 1,000 shares for $4,350; sell immediately for $4,100. You are down $250, or roughly 5.7%, before the market has moved at all. Same mechanism, forty times the cost, and the only thing that changed was liquidity.</p>
      </Callout>

      <Callout variant="did-you-know">
        <p>The <Term k="dividend yield">dividend yield</Term> on a quote page may be calculated from the trailing twelve months of payments, or annualised from the most recently declared one, and the page does not always say which. Either way, if a company cut its dividend last week, the yield you are looking at may describe money that is no longer being paid. The dividend history page, not the summary quote, is where the truth lives.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Company and ticker, then the five fields with their values and one sentence on what each one told you…">
        <p>Pick any company you already know something about and open its quote page on Yahoo Finance, Google Finance or your broker. Find and write down five specific fields: market cap, average daily volume, the 52-week range, the dividend yield if there is one, and the next earnings date. Then answer in two sentences: based on average volume and the bid-ask spread, would this stock be easy or expensive to get out of quickly, and how did you decide?</p>
      </TryIt>

      <h2>The one thing to carry forward</h2>
      <p>A broker is infrastructure. Choose it on account types, fractional shares, support and SIPC membership, then stop thinking about it. The choice matters far less than what you do afterwards, and the app that makes trading feel most fun is not automatically the one that serves you best.</p>
      <p>On the quote screen, the number everyone stares at is the one that carries the least information. Last price tells you what somebody paid a moment ago. Market cap tells you how big the company is. Volume and the spread tell you what it will cost you to change your mind. Read those three before the price, and you are already reading a quote better than most people who have been doing it for years.</p>
      <p>Next up: actually placing the order. Market orders versus limit orders, what happens between clicking buy and owning the share, and why the price you see is not always the price you get.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
