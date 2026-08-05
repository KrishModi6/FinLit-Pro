import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A company reports the highest quarterly profit in its history, and the stock drops 6% the next morning. What is the most likely explanation?',
    options: [
      'The exchange marked the price down because profits were too high',
      'Investors had already expected an even better result, or management’s outlook for the next quarter disappointed',
      'Record profits reliably cause selling, because traders take profits every time',
      'The company decided to lower its share price to attract new buyers',
    ],
    answer: 1,
    explanation: 'Price already reflects what people expect. A record number that falls short of the expected record is a disappointment, and guidance about the future often matters more than the quarter just reported. The “take profits every time” answer is tempting because it sounds like something traders say, but plenty of strong reports are followed by strong rallies — the reaction depends on the gap between result and expectation, not on the result alone.',
  },
  {
    prompt: 'The lowest sell orders on a stock are 200 shares at $50.10, then 300 at $50.15, then 500 at $50.25. Someone buys 1,000 shares at market, filling all three levels. What is the last traded price?',
    options: ['$50.10', '$50.15', '$50.19', '$50.25'],
    answer: 3,
    explanation: 'The last trade happened at $50.25, so that is the price you now see quoted. $50.19 is the average price the buyer paid across all 1,000 shares, which is a useful number for the buyer but is not the market price. Notice that the quote moved 15 cents with no news at all — just an order large enough to clear the cheapest sellers.',
  },
  {
    prompt: 'The company itself decides the price at which its shares trade each day.',
    type: 'tf',
    answer: false,
    explanation: 'A company sets the price of its shares exactly once: at its IPO, with its bankers. After that the price is simply the last price a buyer and a seller agreed on. Management can influence the business, and the business influences what people are willing to pay, but nobody at headquarters types in a number.',
  },
  {
    prompt: 'Interest rates rise sharply. Why might stock prices fall even if company profits have not changed at all?',
    options: [
      'Safer bonds now pay more, so investors demand a better deal from risky stocks, and future profits are worth less in today’s money',
      'Companies are legally required to reduce their share price when rates rise',
      'Exchanges raise trading fees, which is deducted from every share price',
      'Rising rates force companies to stop paying dividends',
    ],
    answer: 0,
    explanation: 'Two effects stack. Stocks compete with bonds for the same money, so when the safe option pays more, the risky option has to get cheaper to stay attractive. And because a dollar of profit arriving in five years is discounted back to today at a higher rate, that same future profit is worth less now.',
  },
  {
    prompt: 'Over a single week, a stock’s price and the true value of the underlying business are essentially the same thing.',
    type: 'tf',
    answer: false,
    explanation: 'Over long horizons price and value tend to converge, because a business that keeps earning more eventually gets repriced. Over a week they can drift far apart on nothing but mood, positioning and headlines. Confusing the two is the single most expensive beginner mistake.',
  },
]

export default function WhyPricesMove({ moduleId }) {
  return (
    <>
      <p className="lead">There is no committee that decides what a stock is worth this morning. No executive types a number into a screen. The price you see is just the last price at which one person agreed to sell and another agreed to buy — and understanding that one fact explains almost every confusing thing the market does.</p>

      <h2>Nobody sets the price</h2>

      <p>A company sets the price of its shares exactly once, at its IPO, together with its bankers. After the first day of trading, that power is gone forever. From then on the price is an outcome, not a decision: it is the record of the most recent handshake between a buyer and a seller.</p>

      <p>This matters more than it sounds. It means the price is not a measurement of what a company is worth, the way a scale measures weight. It is a measurement of what the most motivated buyer and the most motivated seller could agree on, in the last second that anyone traded. Those are different things, and the gap between them is where most of investing lives.</p>

      <h2>The order book, one trade at a time</h2>

      <p>Behind every ticker sits a list of unfilled orders. On one side, buyers state the highest price they are willing to pay. On the other, sellers state the lowest price they will accept. Imagine a fictional company, Harbor Coffee, and the sell side of its book looks like this: 200 shares offered at $50.10, then 300 shares at $50.15, then 500 shares at $50.25. The best buyer is bidding $50.05.</p>

      <KeyTerm term="spread" />

      <p>Now someone decides to buy 1,000 shares immediately. They take the 200 cheapest shares at $50.10, then the next 300 at $50.15, then 500 at $50.25. Their average cost is $50.19, and the last trade printed is $50.25. The quoted price just rose 15 cents. No news happened. No analyst changed a rating. One order was simply bigger than the supply sitting at the front of the queue.</p>

      <p>That is the entire mechanic, repeated thousands of times a day. When there is more eagerness to buy than to sell at the current price, buyers have to reach higher to get filled, and the price rises until enough sellers are tempted. When selling pressure dominates, the reverse happens. Stocks with heavy <Term k="volume">daily trading volume</Term> have deep books that absorb large orders without moving much, while thinly traded ones can jump on a single order.</p>

      <Callout variant="example">
        <p>Two stocks each drop 3% on a Tuesday. In the first, 40 million shares change hands and the drop follows a widely covered announcement. In the second, 8,000 shares trade all day and one seller walked the book down looking for buyers.</p>
        <p>Same percentage, completely different information. The first tells you something about how a large group of people revalued the business. The second mostly tells you that one person wanted out and there was nobody around to take the other side.</p>
      </Callout>

      <h2>News moves prices, but expectations move them more</h2>

      <p>Okay, so imagine Apple launches a phone that everyone actually loves, reviews are glowing, the queues are around the block. Guess what happens to the stock? Half the time, nothing. Sometimes it falls.</p>

      <p>Here is the precise version. The price today already reflects what buyers and sellers collectively expect to happen. If the market spent three months anticipating a great launch, it has been buying on that anticipation the entire time, and the good news is already embedded in the price. What moves the stock on launch day is not whether the news is good. It is whether the news is better or worse than what was already assumed.</p>

      <p>This is what traders mean by <em>buy the rumour, sell the news</em>. Money flows in during the period of anticipation, when the outcome is still uncertain and improving. Once the event actually arrives and the uncertainty resolves, the reason to hold the position is gone, so some holders sell into the very headline that confirmed they were right.</p>

      <Callout variant="did-you-know">
        <p>A company can report the best quarter in its history and watch its stock fall 10% the same morning. It happens constantly, and it is not irrational.</p>
        <p>Suppose analysts collectively expect earnings of $2.00 per share, and the company delivers $2.05 — genuinely a record. But in the same release, management guides next quarter down and mentions softening demand. The $2.05 was already assumed; the guidance was not. Investors are pricing the next twelve months, not the twelve weeks that just ended.</p>
      </Callout>

      <h2>What actually moves a price</h2>

      <p>Price-moving events sort into three rough layers. Company-specific news covers earnings, product launches, guidance, management changes, lawsuits and buybacks. Sector-wide news hits every company in an industry at once: a chip shortage, an oil supply shock, a regulator opening an inquiry into an entire business model. Macro news moves nearly everything together — interest rate decisions, inflation prints, employment data, elections, wars.</p>

      <KeyTerm term="catalyst" />

      <h3>Why interest rates matter so much</h3>

      <p>Rates are the one macro lever worth understanding early, because the link is intuitive once you see it. Money has options. If a safe government bond pays 5%, why accept the uncertainty of a stock unless it offers a meaningfully better expected return? When safe yields rise, investors demand a better deal from risky assets, and the way a stock offers a better deal is by getting cheaper.</p>

      <p>There is a second, quieter effect. A stock is a claim on profits that mostly arrive in the future, and future money is discounted back to today. At a 2% discount rate, $110 arriving next year is worth about $107.84 now. At 5%, that same $110 is worth about $104.76. Nothing about the business changed. The arithmetic of waiting did.</p>

      <h3>Headline versus what matters</h3>

      <p>Financial headlines are written to be read in one second, which means they routinely bury the part that actually explains the move.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>The headline</th>
              <th>What actually matters</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Company beats earnings</td>
              <td>By how much versus what analysts already expected, and what management said about the next quarter</td>
            </tr>
            <tr>
              <td>Record revenue, stock falls 8%</td>
              <td>Revenue grew, but slower than before, or margins shrank while it grew</td>
            </tr>
            <tr>
              <td>Central bank leaves rates unchanged</td>
              <td>Whether that was already priced in, and what the wording implies about the next few meetings</td>
            </tr>
            <tr>
              <td>CEO steps down</td>
              <td>Planned succession or abrupt exit, and how much the business depends on that one person</td>
            </tr>
            <tr>
              <td>Analyst upgrades stock to Buy</td>
              <td>One firm’s opinion, published after the research was done; ask what it claims to know that the market does not</td>
            </tr>
            <tr>
              <td>Stock hits an all-time high</td>
              <td>Nothing on its own. A high price says how it compares with its own past, not whether the business is cheap or expensive</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>Prices move because people expect prices to move</h2>

      <p>There is a loop inside all of this. If enough people believe a stock will rise, they buy, and their buying makes it rise, which convinces more people it will rise. Belief becomes its own evidence for a while. That is <Term k="fomo">the fear of missing out</Term> doing real work on real prices, and it runs in reverse too: falling prices frighten holders into selling, which pushes prices lower.</p>

      <p>GameStop in January 2021 is the cleanest illustration anyone has. The stock went from under $20 at the start of the month to an intraday high near $483 on 28 January, then fell roughly 90% within weeks. The underlying business did not improve 20-fold and then collapse. Positioning, attention and belief did all of it.</p>

      <p>This loop is why short-term price movement carries so much <Term k="volatility">volatility</Term> and so little signal. You are not just forecasting a company. You are forecasting what a few million people will believe about that company, including what they believe everyone else believes.</p>

      <Callout variant="real-talk">
        <p>Nobody reliably predicts short-term price moves. Not your uncle, not the person on your feed with the chart and the confident tone, and not the professionals with expensive data and teams of PhDs. The ones who look right for a stretch are usually the ones you happened to notice, because the ones who were wrong stopped posting.</p>
        <p>You do not need short-term prediction to do well. That is the genuinely good news buried in this lesson.</p>
      </Callout>

      <h2>Price is not value</h2>

      <p>Hold these two ideas separately, because everything in the Intermediate track builds on the distinction. <strong>Price</strong> is what the stock trades at right now: an auction result, sensitive to mood, headlines and who happens to need cash this week. <strong>Value</strong> is what the business is actually worth — the cash it will generate over its life, discounted to today.</p>

      <p>Over long horizons the two are tethered. A company that keeps earning more eventually gets repriced upward, and one whose earnings evaporate eventually gets repriced toward zero. Enron traded around $90 in mid-2000 and reached near zero when it filed for bankruptcy in December 2001, because the value was never there and price finally noticed. Over short horizons the tether is long and slack, and the two can drift absurdly far apart in either direction.</p>

      <Callout variant="warning">
        <p>The most expensive habit a new investor can build is treating a falling price as proof that a business is bad and a rising price as proof that it is good. Price is evidence about what other people currently think. It is not a verdict on the company.</p>
        <p>This cuts both ways. Buying something purely because it has gone up, and panic-selling something purely because it has gone down, are the same mistake wearing different clothes.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Company, reported EPS, expected EPS, what the stock did, and your one-sentence explanation of why">
        <p>Pick any large company you actually use something from. Find its most recent quarterly earnings report on Yahoo Finance or the company’s own investor-relations page, and note three things: the earnings per share it reported, the figure analysts expected, and what the stock did in the day or two afterwards.</p>
        <p>Then write two or three sentences answering this: did the price reaction match the direction of the surprise? If it did not, look at what management said about the coming quarter and see whether that explains the gap.</p>
      </TryIt>

      <h2>The one thing to carry forward</h2>

      <p>Price is an agreement, not a fact about a company. It moves when the balance of eagerness between buyers and sellers shifts, and that balance shifts on the difference between what happens and what was already expected to happen. Once that clicks, the market stops looking random and starts looking like a very loud, very fast argument about the future.</p>

      <p>You will not win that argument by predicting next week. You win it, slowly, by understanding businesses better than the average participant and by being willing to wait for price and value to reconnect.</p>

      <p>Next up: how to read a stock quote properly — bid, ask, last, volume, market cap and the numbers on a broker screen that most people scroll past without knowing what they mean.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
