import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'You have $500 saved, and also $1,800 sitting on a credit card charging 24% interest. What does the honest version of Step 0 say you should do?',
    options: [
      'Buy the ETF anyway, since stocks have historically returned more than the interest costs',
      'Pay down the card first: avoiding 24% interest is a guaranteed return the market cannot promise',
      'Buy a single company instead, because it can grow faster and catch you up',
      'Split the $500 evenly between the card and the ETF so you do not miss out',
    ],
    answer: 1,
    explanation: 'Paying off a 24% balance is a certain 24% saved. A stock might return 10% or might fall 30%; nothing in the market is guaranteed. The tempting answer is the first one, which compares an average long-run return to a certain cost. That is not a fair comparison.',
  },
  {
    prompt: 'A stock shows $190.40. You place a limit buy for one share at $190.50, and before your order reaches the exchange the price jumps to $193. What happens?',
    options: [
      'You are filled at exactly $190.50 because that is the price you named',
      'Nothing fills: you pay no more than $190.50, so at $193 the order simply sits unfilled',
      'The order automatically converts to a market order and fills at $193',
      'Your broker fills it at whatever price it chooses and bills you the difference',
    ],
    answer: 1,
    explanation: 'A limit price is a ceiling, not a target. Above it, you do not buy at all, which is the whole point. Option one is the common misread: the limit says “never more than this”, not “exactly this”.',
  },
  {
    prompt: 'Buying one share of a broad S&P 500 index ETF means a single company going bankrupt cannot wipe out your position.',
    type: 'tf',
    answer: true,
    explanation: 'True, and it is the strongest argument for a diversified first purchase. But do not over-read it: the fund still falls when the whole market falls, and in 2008 that was roughly a 50% drawdown. Spreading across 500 companies removes single-company risk, not market risk.',
  },
  {
    prompt: 'You buy a share on a Tuesday. Under the T+1 rules in effect since May 2024, when does the trade settle?',
    options: [
      'Instantly, at the moment the order fills',
      'Wednesday, one business day after the trade',
      'Friday, three business days after the trade',
      'The following Tuesday, one week later',
    ],
    answer: 1,
    explanation: 'T+1 means settlement one business day after the trade date. Your price and your ownership are locked in at the fill; settlement is the back-office plumbing that moves cash and shares.',
  },
  {
    prompt: 'A broad index fund charges an expense ratio of 0.03%. On a $2,000 position, roughly what does that cost you per year?',
    options: ['About $0.60', 'About $6', 'About $60', 'Nothing: index funds do not charge fees'],
    answer: 0,
    explanation: '0.03% of $2,000 is $0.60, taken quietly out of the fund’s assets rather than billed to you. Compare a fund charging 1%: that is $20 a year on the same position, and the gap compounds over decades.',
  },
]

export default function YourFirstShare({ moduleId }) {
  return (
    <>
      <p className="lead">You already know what a share is, what an exchange does, and why fees matter more than they look. This is the lesson where all of that turns into a button you actually press. Every price below is invented so the arithmetic is easy to follow. The real numbers move every second, and you will look them up yourself.</p>

      <h2>Step 0: Three things that have to be true first</h2>
      <p>Before any of the fun parts, three conditions. This is the most valuable paragraph in the lesson, so read it slowly.</p>
      <p>First, the money has to be money you will not need for at least five years. Not next semester’s laptop, not car insurance in March. A broad market can fall 20% and stay down for a year or two, and if you are forced to sell during that stretch, a paper loss turns into a real one.</p>
      <p>Second, no high-interest debt. If you are carrying a credit card balance at 24%, paying it off is a guaranteed 24% return. There is nothing in the stock market that comes with the word “guaranteed” attached to it.</p>
      <p>Third, a small emergency cushion, even a few hundred dollars in a plain savings account. Its entire job is to absorb the flat tyre and the surprise bill so that you never have to liquidate an investment at the worst possible moment.</p>
      <p>If any one of those three is not true, the correct move is to not buy stock yet. That is not a consolation prize. Clearing a 24% card and building a cushion is the highest-certainty financial move available to almost anyone, and unlike a good year in the market, it is available today.</p>

      <Callout variant="warning">
        <p>Only invest money you can genuinely leave alone. The most common way beginners lose is not picking the wrong stock; it is being forced to sell a perfectly reasonable one at a bad price because rent was due. Money with a job in the next few years does not belong in the market.</p>
      </Callout>

      <h2>Step 1: Open the account, then fund it</h2>
      <p>You buy shares through a <Term k="brokerage">brokerage</Term>, which is the licensed intermediary that routes your order to an exchange. If you are under 18 in the US you cannot open one in your own name. What you need is a custodial account: a parent or guardian opens it and controls it, the assets are legally yours, and control transfers to you at the age of majority in your state.</p>
      <p>Funding is a bank transfer, and it is slower than you expect. Give it a few business days, since many brokers also hold new deposits briefly before the cash is available to trade. Start the transfer on a Monday and be mildly annoyed on Wednesday, rather than starting it in a hurry the instant you have decided what to buy.</p>
      <p>Use the waiting time for Step 2. That ordering is deliberate: money moves first, the decision gets made calmly second.</p>

      <h2>Step 2: Decide what before you decide how</h2>
      <p>Two beginner-shaped paths, presented as illustrations of two categories rather than as suggestions. Path A is one share of a single company, say Apple, whose <Term k="ticker">ticker</Term> is AAPL. Path B is one share of a broad index fund, say VOO, which tracks the S&amp;P 500.</p>

      <KeyTerm term="etf" />

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Question</th>
              <th>Path A: one share of AAPL</th>
              <th>Path B: one share of VOO</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>What you actually own</td>
              <td>A sliver of one company’s equity</td>
              <td>A sliver of a fund that holds roughly 500 companies</td>
            </tr>
            <tr>
              <td>How many businesses</td>
              <td>One</td>
              <td>About 500, weighted by size</td>
            </tr>
            <tr>
              <td>What can wipe you out</td>
              <td>That one company failing, or a product cycle going badly</td>
              <td>A broad market decline: no single bankruptcy can do it</td>
            </tr>
            <tr>
              <td>Ongoing fee</td>
              <td>None on the share itself</td>
              <td>An expense ratio, roughly 0.03% for funds like this (check the current figure)</td>
            </tr>
            <tr>
              <td>Homework required</td>
              <td>Real: the business, its competitors, its numbers</td>
              <td>Modest: what the index holds and what the fund charges</td>
            </tr>
            <tr>
              <td>Typical bumpiness</td>
              <td>Higher: one company’s news moves all of it</td>
              <td>Lower: good and bad news across 500 names partly cancel</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Here is the reasoning, not a recommendation. A single company can go to zero: Enron traded around $90 in mid-2000 and was essentially worthless when it filed for bankruptcy in December 2001. Roughly 500 large companies cannot all go to zero at the same time. That does not promise Path B goes up; index funds fall hard in bad years too. It is a claim about which kind of failure you can survive and keep investing through, which is why the maths tends to favour the diversified option for a first purchase.</p>
      <p>Path A still has a genuine use: owning one share of a company you find interesting makes you read its earnings reports in a way that no assignment ever will. Just be clear with yourself that you are paying tuition for attention, not making a bet you have researched.</p>

      <h2>Step 3: Two minutes of homework</h2>
      <p>Open the quote page on Yahoo Finance or inside your broker, and look at four things before you buy anything.</p>
      <ul>
        <li>Price, so the arithmetic in the next step is real rather than imagined.</li>
        <li><Term k="market cap">Market cap</Term>, which tells you the size of what you are buying into: a company worth $2 trillion and one worth $200 million are different species.</li>
        <li>Average daily volume, a rough proxy for how easily you can get in and out without moving the price.</li>
        <li>For a fund: the <Term k="expense ratio">expense ratio</Term> and the list of top holdings, so you know both what it costs and what it actually owns.</li>
      </ul>

      <Callout variant="did-you-know">
        <p>An expense ratio of 0.03% costs about $3 a year per $10,000 invested. A fund charging 1% costs about $100 a year on the same money. Neither number sounds like much on the day you buy, and over thirty years the difference between them is the price of a car.</p>
      </Callout>

      <h2>Step 4: The order ticket, field by field</h2>
      <p>The ticket looks intimidating for about ninety seconds. It has four fields that matter. <strong>Symbol</strong>: type the ticker and confirm the company name that autocompletes, because near-identical tickers exist and the market will happily sell you the wrong one. <strong>Action</strong>: buy. <strong>Quantity</strong>: a number of shares, or a dollar amount if your broker supports fractional buying. <strong>Order type</strong>: market or limit.</p>

      <h3>Use a limit order, for the habit</h3>
      <Callout variant="example">
        <p>Suppose AAPL shows $190.40. A market order says “get me a share at whatever the next available price is”. A limit order at $190.50 says “get me a share, but never pay more than $190.50”.</p>
        <p>If the price stays near $190.40, you fill around there and the limit cost you nothing. If a headline lands and the price runs to $193 before your order reaches the exchange, the order simply does not fill. You did not buy. That is the feature, not a malfunction.</p>
        <p>Your maximum cost is 1 × $190.50 = $190.50. For three shares it is 3 × $190.50 = $571.50, and the preview screen will show that estimate before you confirm.</p>
      </Callout>
      <p>On one share of a heavily traded stock, the difference between a market and a limit order is pennies. The reason to build the habit now is that the same reflex saves real money later, when the amounts are larger or when you are trading something thin where the gap between the buying and selling price is wide.</p>

      <h3>Time in force, in one sentence</h3>
      <p>“Day” means the order expires unfilled at the 4:00pm ET close, and “GTC”, good till cancelled, keeps it alive for weeks. For a first purchase choose day, so that if it does not fill you get to decide again tomorrow with a clear head.</p>

      <h3>You do not need $190</h3>
      <p>Many brokers now sell fractional shares, which means $10 buys you about one nineteenth of a $190 share, with proportional dividends and proportional gains. This quietly changed who is allowed to participate at all: a high-schooler with $25 a month is no longer locked out of owning part of a large company.</p>

      <KeyTerm term="dollar cost averaging" />

      <h2>Step 5: Submit, settle, and then the hard part</h2>
      <p>The review screen shows symbol, action, quantity, order type, limit price, time in force, estimated total, and any commission. Read it properly. The classic beginner disaster at this stage is not a bad thesis, it is typing 100 in the quantity box instead of 1.</p>
      <p>Once you submit and the order fills, the confirmation shows the executed price, the time, and the total. That price is yours from the instant of the fill. Settlement follows one business day later under the T+1 standard that took effect in May 2024, which is the plumbing moving cash one way and shares the other.</p>

      <Callout variant="note">
        <p>Settled versus unsettled cash matters mostly if you sell and immediately want to buy something else. In a cash account, using proceeds before they settle can trigger a good-faith violation and a restriction on the account. Check your broker’s rules once, and then you will never think about it again.</p>
      </Callout>

      <h3>The first week means nothing</h3>
      <p>Your position will move one or two percent a day and your brain will insist that each wiggle is information. It is not. A week of price movement on a large company tells you almost nothing about whether the business is doing well, and treating it as feedback is how people learn the wrong lesson quickly.</p>

      <Callout variant="real-talk">
        <p>Your first loss will feel roughly twice as bad as your first equal-sized gain feels good. That asymmetry is measured, it has a name, and it is the single most reliable way ordinary investors are talked into selling low. We take it apart properly under <Term k="loss aversion">loss aversion</Term> in the Hard track. For now, just know the feeling is coming and that it is a bias, not a signal.</p>
      </Callout>

      <p>So build two habits on day one. Check the position monthly, not hourly, and turn off price notifications entirely. And write down, the day you buy, why you bought it and what would make you change your mind. In a year, future-you gets to audit past-you’s reasoning against what actually happened, which is the only way anyone gets better at this.</p>

      <h3>What not to do in the first month</h3>
      <ol>
        <li>Do not buy more after a drop purely because it dropped. Adding to a position needs a reason about the business; “it is cheaper than it was” is a fact about the price, not an argument.</li>
        <li>Do not sell on a red week. If a 6% move over five days changes your plan, the position was too large for your temperament. That is a sizing problem, not a market problem.</li>
        <li>Do not add a second position before you can explain the first one out loud, including what would make you wrong.</li>
      </ol>

      <TryIt moduleId={moduleId} placeholder="What it is, why you would own it, and the specific thing that would make you change your mind…">
        <p>Before you spend anything, write your own one-paragraph investment thesis for something you might buy. Pull up its real quote page first. Cover three things: what it actually is, in your own words; why you want to own a piece of it for five years; and the specific development that would tell you the reasoning was wrong. If you cannot fill in the third part, you do not have a thesis yet: you have an urge, and that is worth knowing before the money moves.</p>
      </TryIt>

      <h2>Where you go from here</h2>
      <p>The one idea to carry out of this lesson: the quality of a purchase is decided before you ever open the order ticket. Step 0 and Step 2 are where the money is made or lost. The clicking part takes ninety seconds and is almost impossible to get badly wrong once you have read the review screen.</p>
      <p>That covers the Beginner track. You can now open an account, tell the difference between owning one business and owning five hundred, place an order without guessing, and sit still afterwards.</p>
      <p>The Intermediate track picks up the obvious next question: now that you can buy something, which things are reasonably stable and which are coin flips dressed up as opportunities? We start reading the numbers a company reports about itself, look at what makes a business durable rather than merely popular, and use measures like volatility and beta to compare two holdings honestly instead of by vibe.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
