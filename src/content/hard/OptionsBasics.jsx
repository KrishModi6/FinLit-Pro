import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A call is quoted at $2.35. Ignoring fees, what does one standard contract cost?',
    options: ['$2.35', '$23.50', '$235', '$2,350'],
    answer: 2,
    explanation: 'Option prices are quoted per share, and one standard US equity contract covers 100 shares, so $2.35 × 100 = $235. Reading the quote as the total cost is the classic beginner error, and it understates your real size by a factor of 100.',
  },
  {
    prompt: 'A stock trades at $48. You buy a $50 strike call for a $3.00 premium. At expiration, what stock price leaves you exactly even?',
    options: ['$47', '$50', '$53', '$55'],
    answer: 2,
    explanation: 'Break-even for a long call is strike plus premium: $50 + $3 = $53. At $50 the option is worthless and you have lost the whole $3; at $52 you recover $2 of the $3 and are still down. Being above the strike is not the same as being profitable.',
  },
  {
    prompt: 'If you buy a call and the stock rises at all by expiration, you make money.',
    type: 'tf',
    answer: false,
    explanation: 'You need the stock above strike plus premium, not merely above where it started. A stock that drifts from $48 to $49.50 has gone up, and your $50 call still expires worthless. Direction alone is not enough; magnitude and timing have to cooperate too.',
  },
  {
    prompt: 'A stock trades at $107. A call with a $100 strike is trading at $9.50. How much of that price is extrinsic (time) value?',
    options: ['$0', '$2.50', '$7.00', '$9.50'],
    answer: 1,
    explanation: 'Intrinsic value is $107 − $100 = $7.00, so the remaining $2.50 is extrinsic value. That $2.50 is the part that theta decay eats away as expiration approaches, and at expiration it is worth exactly zero.',
  },
  {
    prompt: 'The most a call buyer can lose is the premium paid, while a seller of an uncovered call has no fixed cap on losses.',
    type: 'tf',
    answer: true,
    explanation: 'The buyer paid a fixed amount and can walk away, so the loss is capped at 100% of the premium. The uncovered seller must deliver shares at the strike no matter how high the stock goes, and there is no ceiling on how high that can be. Capped loss and unlimited loss are not the same risk.',
  },
]

export default function OptionsBasics({ moduleId }) {
  return (
    <>
      <p className="lead">Someone offers you a deal on their used car. You hand them $500 today, and in return you get the right, but not the obligation, to buy that car for $8,000 any time in the next three months. The $500 is theirs to keep no matter what happens. What you bought with it is a choice, and that choice is the entire idea behind every option contract ever traded.</p>

      <h2>A deal on a used car</h2>

      <p>Play it forward. Three weeks later that model gets a cult following and the going rate jumps to $11,000. You use your right, pay the agreed $8,000, and own an $11,000 car. Your gain is $3,000 minus the $500 you paid for the right, so $2,500. Now play it the other way: the model gets recalled and the market value drops to $6,000. You do nothing. The deal expires, you never bought the car, and your loss is exactly $500. Not $2,000. Not the price of the car. Five hundred dollars, which was known and capped from the moment you agreed.</p>

      <p>Every piece of that scenario has a name in the market:</p>

      <ul>
        <li>The car is the <strong>underlying</strong>, the thing the contract is written on.</li>
        <li>The $8,000 is the <strong>strike price</strong>, the agreed price you may transact at.</li>
        <li>The three months is the <strong>expiration</strong>, and after that date the right stops existing.</li>
        <li>The $500 is the <strong>premium</strong>, what you paid the seller for the right itself.</li>
        <li>Choosing to buy the car at $8,000 is <strong>exercising</strong>. Walking away is letting it expire worthless.</li>
      </ul>

      <p>The analogy is unusually good, which is why I like it. But it breaks in one place, and that one place is where most beginners lose their money.</p>

      <Callout variant="note">
        <p>A used car does not become less valuable to you simply because a week went by. An option does. The right to buy at $8,000 for three more months is worth more than the same right with three days left, because there is more remaining time in which something good could happen. That built-in bleed has a name, and we will spend a whole section on it.</p>
      </Callout>

      <h2>The four things every contract specifies</h2>

      <KeyTerm term="Option" />

      <p>An <Term k="option">option</Term> quote is fully described by four numbers and one word. The underlying tells you which stock. The <Term k="strike">strike price</Term> tells you the price at which you may transact. The expiration date tells you when the right dies. The <Term k="premium">premium</Term> tells you what the right costs right now. And the word is either “call” or “put”, which tells you whether the right is to buy or to sell.</p>

      <KeyTerm term="Premium" />

      <p>Then there is the multiplier, and it deserves its own paragraph because it is where beginners misjudge their size by a factor of one hundred. One standard US equity option contract covers 100 shares. Premiums are quoted per share. So a call quoted at $3.20 does not cost $3.20; it costs $320 for one contract. Ten contracts is not a $32 position, it is a $3,200 position controlling 1,000 shares. That control-a-lot-with-a-little property is <Term k="leverage">leverage</Term>, and leverage is symmetric: it magnifies the good outcome and the bad one equally.</p>

      <Callout variant="warning" title="Check your size before you check your thesis">
        <p>Every quoted premium is per share. Multiply by 100 to get the cost of one contract, then multiply by the number of contracts. Before you place any options order, say the total dollar amount out loud. If that number would ruin your week, the position is too big, regardless of how confident you feel.</p>
      </Callout>

      <h2>Calls and puts</h2>

      <h3>Calls: the right to buy</h3>

      <p>A <Term k="call">call</Term> gives the holder the right to buy 100 shares at the strike, any time before expiration. You want the stock to go up, and up by enough.</p>

      <p>Work it through. Suppose a stock trades at $48 and you buy one call with a $50 strike expiring in three months for a premium of $3.00 per share. Your cost is $300 and that is your maximum loss. The break-even is strike plus premium: $50 + $3 = $53.</p>

      <ol>
        <li>Stock at $58 at expiration: the contract is worth $8 per share, or $800. You paid $300, so you profit $500, a 167% gain on a stock that rose about 21%.</li>
        <li>Stock at $53: worth $300. You get your money back and have made nothing.</li>
        <li>Stock at $49.50: worth nothing. The stock went up and you lost 100% of the $300.</li>
        <li>Stock at $40: worth nothing. You lost the same $300 you lost at $49.50. The floor does not get lower.</li>
      </ol>

      <p>Look hard at lines three and four. The loss is capped, which is genuinely useful. But between $50 and $53 you are still losing money while being directionally correct, and below $50 you lose everything.</p>

      <h3>Puts: the right to sell</h3>

      <p>A <Term k="put">put</Term> is the mirror image: the right to sell 100 shares at the strike. You profit when the stock falls below strike minus premium.</p>

      <p>Suppose a stock trades at $100 and a $95 strike put costs $4.00, so $400 for the contract. Break-even is $95 − $4 = $91. If the stock drops to $85, the put is worth $10 per share, or $1,000, for a $600 profit. If the stock sits at $95 or anywhere above it, the put expires worthless and you lose the full $400.</p>

      <p>Puts have a second use that is not speculation at all. If you already own 100 shares bought at $100 and you buy that same $95 put, you have set a floor: no matter how far the stock falls, you can always sell at $95. Counting the $4 you paid, your worst realistic outcome on the package is about $91 per share. That is a protective put, and it is insurance in the ordinary sense: you pay a premium, you hope you never need it, and the cost is real whether or not disaster arrives.</p>

      <h3>Where the stock sits relative to the strike</h3>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Where the stock is</th>
              <th>A call is</th>
              <th>A put is</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Above the strike</td>
              <td>In the money</td>
              <td>Out of the money</td>
            </tr>
            <tr>
              <td>At or very near the strike</td>
              <td>At the money</td>
              <td>At the money</td>
            </tr>
            <tr>
              <td>Below the strike</td>
              <td>Out of the money</td>
              <td>In the money</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>In the money means the contract would be worth something if it expired right now. Out of the money means it would be worth zero. Cheap contracts are usually cheap because they are far out of the money, which is another way of saying the market thinks they will probably expire at zero.</p>

      <h2>Time value and theta decay</h2>

      <h3>Splitting the premium in two</h3>

      <p>Any premium is the sum of two pieces. Intrinsic value is what the contract would pay if it expired this second. Extrinsic value, also called time value, is everything else: what buyers are paying for the possibility that things get better before expiration.</p>

      <p>Concretely: a stock trades at $107 and a call with a $100 strike is trading at $9.50. Intrinsic value is $107 − $100 = $7.00. Extrinsic value is the remaining $2.50. At the moment of expiration, extrinsic value is zero by definition, because there is no time left for anything to happen. That $2.50 must go somewhere, and where it goes is away.</p>

      <KeyTerm term="Theta Decay" />

      <h3>Right about direction, wrong anyway</h3>

      <p><Term k="theta decay">Theta decay</Term> is the daily erosion of extrinsic value, and it accelerates as expiration approaches. A contract with 90 days left loses time value slowly; the same contract in its final two weeks bleeds noticeably every single day, including days the market is closed.</p>

      <Callout variant="example" title="Correct and still down $200">
        <p>You buy that $100 strike call for $9.50 with 30 days left, while the stock sits at $107. Over the next month the stock does exactly what you predicted: it goes up. It closes at $107.50 on expiration day.</p>
        <p>Your contract is now worth its intrinsic value only: $7.50 per share, or $750. You paid $950. You were right about the direction, right that the company was fine, right that nothing bad would happen, and you still lost $200. The stock did not move enough, soon enough, to outrun the $2.50 of time value you bought.</p>
      </Callout>

      <p>This is the single most important sentence in the lesson: with options you can be right and still lose everything. A shareholder who is right eventually gets paid. An option holder who is right too slowly gets nothing, because the contract simply ceases to exist.</p>

      <h2>The other Greeks, and implied volatility</h2>

      <p>Theta is one of a family of sensitivity measures with Greek-letter names. You do not need to compute them, but the vocabulary should not feel like a wall. Delta is roughly how much the option price moves for a $1 move in the stock. Gamma is how fast delta itself changes as the stock moves. Vega is how much the option price responds to changes in expected future movement.</p>

      <p>That last one leads somewhere useful. Implied volatility, or IV, is the market’s expectation of how much the stock will swing between now and expiration. More expected movement means more chance of a big payoff, so options on a jumpy stock cost more than options on a placid one, all else equal. IV is not a forecast of direction; it is a forecast of size.</p>

      <Callout variant="real-talk" title="The earnings trap">
        <p>Before an earnings announcement, implied volatility rises because a known, dated event could move the stock hard. Options get expensive. Then the announcement happens, the uncertainty resolves, and IV collapses within minutes.</p>
        <p>So a trader buys a $50 call for $4.00 the day before earnings. The company beats, the stock rises to $52. They were right. But the elevated IV they paid for has evaporated, and the contract is now marked at $2.50. They called the event correctly and lost 38% of their money. This is IV crush, and it catches people every single earnings season.</p>
      </Callout>

      <h2>Buying versus selling, and three ways to be wrong</h2>

      <p>Everything so far has been from the buyer’s seat. Someone sold you those contracts, and their risk profile is upside down relative to yours. As a buyer, your loss is capped at the premium and your potential gain is large. As a seller, you collect the premium up front (that is your maximum gain) and you take on the obligation.</p>

      <p>How bad can the obligation get? Sell an uncovered $50 call for $3.00 and collect $300. The stock is taken over and jumps to $90. You must deliver 100 shares at $50 while they are worth $90, a $4,000 hit against the $300 you collected, for a net loss of $3,700 on a trade whose best case was $300. There is no theoretical ceiling on how high a stock can go, so there is no theoretical ceiling on that loss. Selling naked options is not a beginner activity, and most brokers will not approve you for it early on. Two more conservative structures, covered calls and cash-secured puts, exist and are worth learning later; both involve already owning the shares or the cash to back the obligation.</p>

      <p>Now the statistics, stated carefully because this is an area where confident-sounding numbers get invented. It is well established that a large share of option contracts expire worthless. The exact percentage depends on the year, the venue and how you count contracts that were closed early rather than held to expiry, so treat any single quoted figure with suspicion. The structural reason matters more than the number. To profit as a buyer you must be right about direction, right about magnitude, and right about timing, all at once. Miss any one and the position can go to zero. That is three independent ways to be wrong on a single trade, where a shareholder has essentially one.</p>

      <Callout variant="warning" title="Total loss here means total">
        <p>Options are the fastest way for a beginner to lose 100% of a position, and the loss is final in a way stock losses are not. If you buy shares of a real company and they fall 60%, you still own something; you can wait, and the company can recover. If your contract expires out of the money, there is nothing to hold. The position is not down; it is gone, deleted, with no recovery scenario at any point in the future.</p>
        <p>Never put money into an option that you cannot afford to see reach exactly zero, and assume that outcome is the base case rather than the tail case.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Ticker, strike, expiration, premium per share, total cost for one contract, break-even price, and one sentence on what would have to happen for that to be reached.">
        <p>Open any real option chain: your broker’s trading screen, or the “Options” tab on a Yahoo Finance quote page. Pick one large, familiar company and choose a single call contract with an expiration a month or two out. Write down five things: the strike price, the expiration date, the premium per share, the total cost of one contract, and the exact stock price at which you would break even at expiration. Then look up where the stock is trading today and write one sentence about how far it would have to move, and by when, for that break-even to be reached. Do not place a trade. The point is to feel how far away that number usually is.</p>
      </TryIt>

      <h2>The one thing to remember</h2>

      <p>An option is a dated, expiring contract on a price, not a piece of a business. That single distinction generates everything else in this lesson. Because it is dated, time works against the buyer. Because it expires, being right slowly is identical to being wrong. Because one contract covers 100 shares, small-looking premiums are large-looking positions.</p>

      <p>None of this makes options illegitimate. They are genuinely useful instruments: a protective put on shares you already own is a rational way to buy downside insurance, and understanding how they are priced makes you a sharper reader of the market as a whole. What they are not is a shortcut. The leverage that turns a 21% stock move into a 167% gain turns a 3% miss into a complete loss, and the second outcome happens far more often than the first.</p>

      <p>Which raises the question this lesson has deliberately left hanging: if a position can plausibly go to zero, how much of your money should ever be in one? That is the next lesson: sizing, and the arithmetic of what a total loss actually does to a portfolio.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
