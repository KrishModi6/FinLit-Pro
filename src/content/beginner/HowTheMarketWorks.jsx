import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'You buy 10 shares of Coca-Cola through your brokerage app. Where does your money go?',
    options: [
      'To Coca-Cola, which uses it to fund operations',
      'To the investor who sold you those shares',
      'To the NYSE, which holds it on the company’s behalf',
      'It is split between the company and the exchange',
    ],
    answer: 1,
    explanation:
      'Coca-Cola collected money from its shares when it first sold them to the public and at any later offering. Everything since then is a secondhand trade between investors, so your cash goes to the seller and the company is not a party to it.',
  },
  {
    prompt: 'A stock’s best bid is $50.04 and its best ask is $50.10. You buy at the ask and instantly sell at the bid. What happens?',
    options: [
      'You break even, since the price never moved',
      'You lose about 6 cents per share, which is the spread',
      'You gain about 6 cents per share',
      'The trade is rejected because the price did not change',
    ],
    answer: 1,
    explanation:
      'You buy at the ask and sell at the bid, so the round trip costs you the spread even though nothing moved. Six cents on a $50 stock is 0.12% and barely registers, but the same six-cent gap on a $2 stock is 3%.',
  },
  {
    prompt: 'A market order guarantees you the price you saw on your screen when you tapped Buy.',
    type: 'tf',
    answer: false,
    explanation:
      'A market order guarantees execution, not price. It walks up the order book until your quantity is filled, so on a thinly traded stock it can fill several percent above the last quoted price. A limit order is the mirror image: it guarantees price, not execution.',
  },
  {
    prompt: 'Which statement about the NYSE and NASDAQ is accurate?',
    options: [
      'NASDAQ lists riskier companies, so a NASDAQ listing is a warning sign',
      'The NYSE assigns each stock a Designated Market Maker who is obliged to maintain an orderly market, while NASDAQ relies on multiple competing market makers',
      'The NYSE is entirely floor-based and NASDAQ is entirely electronic',
      'Only NASDAQ-listed companies must file audited financials with the SEC',
    ],
    answer: 1,
    explanation:
      'The NYSE grew up as an auction market with assigned DMMs who carry real obligations; NASDAQ has always been a dealer market with market makers quoting against each other. The third option is the tempting one, but the vast majority of NYSE volume is matched electronically today, and both exchanges impose genuine listing and disclosure standards.',
  },
  {
    prompt: 'If the S&P 500 falls 7% during the trading day, US markets close for the rest of the session.',
    type: 'tf',
    answer: false,
    explanation:
      'A 7% decline trips the Level 1 circuit breaker, which is a 15-minute halt, and only before 3:25pm ET. The full-day close is the Level 3 breaker at a 20% decline. Level 1 halts fired four separate times in March 2020 and trading resumed within fifteen minutes each time.',
  },
]

export default function HowTheMarketWorks({ moduleId }) {
  return (
    <>
      <p className="lead">The first time you buy a share of Apple, Apple does not receive a cent of your money. Another investor, someone you will never meet who decided that morning they would rather hold cash, sold you that share and your money went to them. Once that clicks, the rest of the machinery stops looking mysterious.</p>

      <h2>You are buying from another investor, not from the company</h2>

      <p>A company collects money from its own stock on only a handful of occasions: at its IPO, when it sells shares to the public for the first time, and at later offerings when it issues new ones. After that, the shares simply circulate. Coca-Cola has been publicly traded since 1919. Every Coca-Cola share that changes hands today is a used share moving from one owner to the next, and the company is a bystander to the transaction.</p>

      <p>So what is the “stock market”? Strip away the trading-floor footage and it is a matching service. It takes millions of people who want to buy and millions who want to sell, and pairs them at a price both sides accept. That is the entire product. The market never decides what a company is worth. It reports, second by second, the price at which the most recent buyer and the most recent seller happened to agree.</p>

      <h2>An exchange is a matching service with rules</h2>

      <p>An <Term k="exchange">exchange</Term> is the regulated venue where that matching happens. It controls who may trade on it, enforces the order in which orders get filled (best price first, and among equal prices, whoever arrived first), publishes the resulting prices for everyone to see, and sets the standards a company must meet to be listed there at all.</p>

      <KeyTerm term="Exchange" />

      <h3>NYSE: an auction market with a floor</h3>

      <p>The New York Stock Exchange traces its origins to 1792 and still runs the model it grew up with, an auction. Every listed stock is assigned to a Designated Market Maker: a firm that carries an obligation, not merely an opportunity. The DMM must quote continuously in its assigned names, commit its own capital when buyers and sellers are badly mismatched, and run the opening and closing auctions that set the day’s first and last prices. The floor at 11 Wall Street is real and still staffed, but the overwhelming majority of NYSE volume is matched electronically. The humans are there for the moments when a machine alone would do a worse job.</p>

      <h3>NASDAQ: a dealer market, electronic from the start</h3>

      <p>NASDAQ opened in 1971 as the first electronic quotation system of its kind and has never had a floor. Its model is a dealer market. Instead of one assigned specialist per stock, multiple market makers compete, each posting the prices at which they will buy and sell. They hold inventory, take the other side of your order, and earn the difference between their buying and selling prices. Competition among those dealers is what is supposed to keep the prices honest.</p>

      <h3>Which exchange a stock lists on tells you almost nothing</h3>

      <p>This is where beginners over-read the signal. Listing venue is mostly history, fees and preference. NASDAQ courted technology companies early and cheaply, which is why Apple, Microsoft and Amazon sit there, while the NYSE holds a great many older industrial and consumer names such as Coca-Cola, Johnson and Johnson, and Walmart. Companies occasionally switch. Both exchanges answer to the SEC and both enforce real listing standards. Venue is not a quality rating.</p>

      <Callout variant="did-you-know">
        <p>For most of the twentieth century you could guess a stock’s home exchange from the length of its <Term k="ticker">ticker</Term>. NYSE symbols ran one to three letters, like F for Ford and KO for Coca-Cola, while NASDAQ used four, like AAPL and MSFT.</p>
        <p>That tell has broken down. NASDAQ now hosts plenty of short symbols, so symbol length is trivia rather than information.</p>
      </Callout>

      <h2>Listing standards are a filter, and outside them there are none</h2>

      <p>To list on a major exchange, a company must clear a bar and keep clearing it: a minimum share price, a minimum number of public shareholders and publicly held shares, a minimum market value, audited financial statements, independent directors on its audit committee, and continuing filings with the SEC. That means an annual 10-K, quarterly 10-Qs, and 8-Ks when something material happens. Slip below the standards and the company gets a deficiency notice, a window to fix the problem, and eventually delisting.</p>

      <p>None of that guarantees a company is good. Enron satisfied every listing standard right up until it did not, and its stock fell from around $90 in mid-2000 to near zero when it filed for bankruptcy in December 2001. What listing standards guarantee is information: you can read the filings and see what management is claiming, with legal penalties attached to lying.</p>

      <p>Outside the exchanges sit the over-the-counter markets, where securities are quoted through dealer networks rather than listed venues. Disclosure there ranges from adequate down to nothing at all, and the lowest tiers carry companies that have not published current financials in years. Most penny stocks live in that world, and the Hard track devotes a full lesson to it.</p>

      <Callout variant="note">
        <p>Delisting does not make shares vanish. They usually keep trading over the counter, where far fewer buyers show up, the gap between what buyers offer and what sellers want widens sharply, and getting out at anything close to the price you see becomes genuinely difficult.</p>
      </Callout>

      <h2>The order book: where the price actually comes from</h2>

      <p>At any given moment a stock has two crowds standing behind it. Buyers have posted bids, meaning a price they are willing to pay and a number of shares they want. Sellers have posted asks, also called offers, with their own price and quantity. Stack all of them by price and you have the order book.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Price</th>
              <th>Shares bid (buyers)</th>
              <th>Shares offered (sellers)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>$50.15</td>
              <td>n/a</td>
              <td>900</td>
            </tr>
            <tr>
              <td>$50.12</td>
              <td>n/a</td>
              <td>400</td>
            </tr>
            <tr>
              <td>$50.10</td>
              <td>n/a</td>
              <td>250</td>
            </tr>
            <tr>
              <td>$50.04</td>
              <td>300</td>
              <td>n/a</td>
            </tr>
            <tr>
              <td>$50.02</td>
              <td>700</td>
              <td>n/a</td>
            </tr>
            <tr>
              <td>$49.98</td>
              <td>1,200</td>
              <td>n/a</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>The best bid is the highest price any buyer is currently offering, $50.04. The best ask is the lowest price any seller will accept, $50.10. Nothing trades between those two numbers, because nobody has agreed to meet there. That six-cent gap is the <Term k="spread">bid-ask spread</Term>.</p>

      <KeyTerm term="Spread" />

      <p>The gap is a real cost, not an abstraction. Buy at the ask and sell instantly at the bid and you are down six cents a share before the price has moved at all. On a $50 stock that is 0.12%, which is nothing. The identical six-cent gap on a $2 stock is 3%, and thin stocks routinely carry spreads much wider than that.</p>

      <p>What sets the width? <Term k="liquidity">Liquidity</Term>, meaning how easily you can turn shares into cash without moving the price yourself. Liquidity comes from participation. Heavy <Term k="volume">volume</Term> means many resting orders at many price levels, which gives you a tight spread and real size at each rung of the ladder. A stock that trades 4,000 shares on an average day has a shallow book, and your order is a large fraction of it.</p>

      <h2>Market orders and limit orders</h2>

      <p>A market order says: fill me now, at whatever prices are available, walking up or down the book until my quantity is complete. It guarantees execution and promises nothing about price. A limit order says: this is the worst price I will accept, $50.12 or better on a buy, and otherwise I wait. It guarantees price and promises nothing about execution.</p>

      <p>On a stock with a penny-wide spread and millions of shares trading daily, that distinction barely matters. On a thin one it matters enormously. Suppose a small company last traded at $20.10 and the sell side of its book looks like this:</p>

      <ol>
        <li>50 shares offered at $20.10</li>
        <li>100 shares at $20.90</li>
        <li>150 shares at $22.00</li>
        <li>200 shares at $23.50</li>
      </ol>

      <p>You send a market order for 400 shares. It sweeps all 50 at $20.10 for $1,005, all 100 at $20.90 for $2,090, all 150 at $22.00 for $3,300, and 100 at $23.50 for $2,350. Total spent: $8,745 for 400 shares, an average of $21.86. You paid roughly 8.8% above the price on your screen, and you did it to yourself. A limit order at $20.50 would have taken the 50 cheap shares and left the rest resting until sellers came down to you.</p>

      <Callout variant="warning">
        <p>Make limit orders your default habit for anything that is not enormously liquid, and be particularly careful in the first few minutes after the open, when spreads are wide even in large, familiar names.</p>
        <p>The cost of a limit order is that it might not fill. The cost of a careless market order is a price you did not choose and cannot undo.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Stock 1: bid / ask / spread in cents / spread as % of price / average volume …">
        <p>Open Yahoo Finance or your broker and pull up two companies: one household-name giant, and one company with a market value under a billion dollars. For each, write down the bid, the ask, the spread in cents, the spread as a percentage of the share price, and the average daily volume. Then answer in one sentence: which one would make you nervous about sending a market order for 500 shares, and which number in your notes says so? Check during regular trading hours, since bids and asks only exist while the market is open, and remember that free quotes are often delayed by about fifteen minutes.</p>
      </TryIt>

      <h2>What happens in the two seconds after you tap Buy</h2>

      <ol>
        <li>Your broker checks the order: do you have the cash or the shares, is the size sane, is the market open.</li>
        <li>The broker routes it. It may go to an exchange, or, very commonly for retail orders, to a wholesale market maker that fills it away from an exchange.</li>
        <li>It is matched against a resting order or against the market maker’s own inventory, and it executes.</li>
        <li>You get a fill confirmation showing price, quantity and time. That confirmation is the trade.</li>
        <li>Settlement follows one business day later. US equity trades have settled T+1 since May 2024, so a Monday purchase becomes legally yours on Tuesday.</li>
      </ol>

      <p>Step two is the interesting one, because it answers a question most people never think to ask: if your broker charges no commission, who is paying for all this?</p>

      <Callout variant="real-talk">
        <p>Payment for order flow is how most “commission free” brokers get paid. A wholesale market maker hands your broker a small amount, often a fraction of a cent per share, for the right to fill its customers’ orders, and then earns the spread on the other side of those trades.</p>
        <p>It is legal, and brokers must publish their routing arrangements in quarterly disclosures. Defenders note that retail orders frequently fill slightly inside the quoted spread, which is real money in your favor. Critics note that your broker is being paid by the firm taking the other side of your trade, which is a conflict of interest however carefully it is managed. Both of those are true, and several other countries have banned the practice outright.</p>
      </Callout>

      <h2>9:30 to 4:00, and the thin edges around it</h2>

      <p>The US regular session runs from 9:30am to 4:00pm Eastern, Monday through Friday, minus market holidays. Most brokers also offer a pre-market session in the hours before the open and an after-hours session that typically runs until 8:00pm ET.</p>

      <p>Extended hours are not the regular market with the lights dimmed. Far fewer participants are quoting, so books are thin, spreads widen, and a modest order can shove the price several percent. This is precisely the trap that catches beginners. A company reports earnings at 4:05pm, the stock lurches 9% on a few thousand shares, and that lurch feels like information. By 10:00am the next morning, once the whole market is quoting again, the move has often partly or entirely reversed.</p>

      <Callout variant="warning">
        <p>Many brokers require limit orders during extended hours, and the ones that do are protecting you. A market order sent into a nearly empty book is how people end up with fills they cannot believe the next morning.</p>
      </Callout>

      <h2>Circuit breakers: the plumbing that stops a freefall</h2>

      <p>Markets have automatic pause buttons. Market-wide circuit breakers key off the S&amp;P 500’s decline from the previous close. A 7% drop (Level 1) and a 13% drop (Level 2) each trigger a 15-minute halt across US equity markets, once per day each and only before 3:25pm ET. A 20% decline (Level 3) at any point in the session closes the market for the rest of the day.</p>

      <p>Individual stocks have their own version. Under the Limit Up-Limit Down rules, a stock that tries to trade outside a price band around its recent average is paused for five minutes so the book can rebuild.</p>

      <p>The purpose is not to prevent losses. A halt does not change what a company is worth. The purpose is to interrupt the feedback loop in which falling prices trigger forced selling that drives prices lower still. In March 2020, Level 1 halts fired four separate times in a single month, and each time trading resumed a quarter of an hour later.</p>

      <h2>What to remember</h2>

      <p>One idea carries this whole lesson: there is no single price. There is a highest price somebody will pay and a lowest price somebody will accept, and every trade is a negotiation between those two numbers. Your order type decides whether you take whatever the book is offering or name your terms and wait.</p>

      <p>Everything else here is plumbing, and the plumbing exists for a reason: exchanges to match orders under enforceable rules, listing standards to compel disclosure, settlement to make ownership legally real, circuit breakers to stop a bad hour from becoming a catastrophic one. You do not have to memorise the mechanics. You do need to know the machine is there and where its sharp edges are, which is to say thin stocks, thin hours, and the market order that never asks permission.</p>

      <p>Next up is the brokerage account itself: what a broker actually does with your money, how a cash account differs from a margin account, what SIPC protection covers and the much bigger thing it does not, and how to read a fill confirmation line by line.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
