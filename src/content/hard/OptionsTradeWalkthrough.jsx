import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'In the walkthrough, the reader pays $2.00 per share for a $55 call on a stock trading at $50. Where is break-even at expiration?',
    options: ['$50.00', '$55.00', '$57.00', '$62.00'],
    answer: 2,
    explanation: 'Break-even is strike plus premium: $55 + $2.00 = $57.00. Picking $55 is the classic mistake. At $55 the contract is worth zero intrinsic value and you are still out the entire $200 you paid.',
  },
  {
    prompt: 'In Ending B the reader was wrong about which way the stock would move.',
    type: 'tf',
    answer: false,
    explanation: 'The reader was right about direction. NWR went from $50 to $53. The trade still lost 100% because the move was smaller than the 14% needed to reach break-even, and the clock ran out. Direction alone does not pay an option holder.',
  },
  {
    prompt: 'At expiration the hypothetical NWR closes at $53. What is the $55 call worth?',
    options: ['$300, because the stock rose $3', '$200, the reader gets the premium back', '$0, it is out of the money and expires worthless', '$100, half of the premium is refunded'],
    answer: 2,
    explanation: 'A call only has value at expiration if the stock is above the strike. At $53 with a $55 strike there is nothing to exercise, so the contract expires at zero. Premium is never refunded: it went to the seller the moment the trade filled.',
  },
  {
    prompt: 'In the middle outcome, NWR finishes at $58 and the contract is worth $300. What did the position actually make?',
    options: ['A loss of $100', 'A gain of $100, or +50% on the position', 'A gain of $300, or +150% on the position', 'Exactly break-even'],
    answer: 1,
    explanation: 'You paid $200 and the contract is worth $300, so the profit is $100. Counting the full $300 as profit is the most common accounting error people make with options: the premium you already spent is part of the cost, not part of the gain.',
  },
  {
    prompt: 'The 100% loss in Ending B was survivable mainly because of a decision made before the trade was placed.',
    type: 'tf',
    answer: true,
    explanation: 'The sizing decision ($200, which is 2% of the portfolio) is what turned a total loss into a 2% dent. Nothing done after the trade was placed could have created that protection. Sizing is the only real risk control that exists in advance.',
  },
]

export default function OptionsTradeWalkthrough({ moduleId }) {
  return (
    <>
      <p className="lead">Every figure below is invented. The company does not exist, the prices are made up, and nothing here is a suggestion to trade anything. What is real is the arithmetic: one hypothetical <Term k="call">call option</Term>, run all the way to two different endings, with every dollar shown and reconciled. Most people only ever see the first ending.</p>

      <h2>The setup, stated precisely</h2>
      <p>Northwind Robotics, ticker NWR, is a company I made up for this lesson. Suppose its stock trades at $50.00. You have a hypothetical $10,000 portfolio, split the way the Intermediate track suggested: $9,000 in a broad index fund you do not touch, and $1,000 in a risky sleeve where you are allowed to be wrong.</p>
      <p>Your thesis is specific. NWR reports earnings in six weeks, and you have read enough about its new product line to believe the results will beat what analysts expect. You want exposure to that specific event, in a defined window, without putting real money at risk beyond a number you chose in advance.</p>
      <p>So you buy one call: <Term k="strike">strike price</Term> $55, expiring in about two months, at a <Term k="premium">premium</Term> of $2.00 per share. One contract covers 100 shares, so the total cost is $200.</p>

      <KeyTerm term="call" />

      <Callout variant="did-you-know">
        <p>A standard US equity <Term k="option">option</Term> contract covers 100 shares. That is why a quote of $2.00 costs you $200 and not two dollars. Every options screen in existence shows the per-share number, and every new trader misreads it at least once.</p>
      </Callout>

      <h3>Checking the size before anything else</h3>
      <p>Run the <Term k="position sizing">sizing</Term> arithmetic before you get attached to the idea. $200 out of a $10,000 portfolio is 2.0%. $200 out of a $1,000 risky sleeve is 20%. The rule from the sizing lesson was 1–2% of total portfolio on any single speculative position, so this trade sits exactly at the top of the allowed range, not comfortably inside it.</p>
      <p>That is worth saying plainly rather than glossing over. A trade at the ceiling of your rule is still inside the rule, but it means you have spent your entire risk allowance on one event. If you want two of these open at once, each one has to be half this size.</p>

      <h3>The number people skip</h3>
      <p>Break-even at expiration is the strike plus the premium: $55.00 + $2.00 = $57.00. NWR is at $50.00. To get to $57.00 the stock has to rise $7.00, which is 14%.</p>
      <p>Read that again, because it reframes the whole trade. You are not betting that NWR goes up. You are betting that NWR goes up more than 14% within about two months. Those are completely different claims, and the second one is much harder.</p>

      <Callout variant="warning" title="The 14% is the actual bet">
        <p>Every option you buy has a hurdle built into it, and the hurdle is invisible on the order screen. Before you place any trade like this, write the break-even price on paper next to the current price and look at the gap. If your honest answer to “can it move that far, that fast?” is a shrug, the trade is a donation.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Strike, premium, break-even price, and the percentage move required…">
        <p>Same hypothetical setup, different contract: NWR at $50.00, but now a $60 strike expiring in two months, quoted at $0.75 per share. Compute the total cost of one contract, the break-even price at expiration, and the percentage move NWR needs from $50.00 to reach it. Then write one sentence on whether the cheaper premium made the trade safer or just moved the hurdle further away.</p>
      </TryIt>

      <h2>Ending A: the thesis lands</h2>
      <p>Earnings come in ahead of expectations. NWR jumps and settles near $64.00 in the days after the report, with about three weeks left before expiration.</p>
      <p>Intrinsic value is $64.00 − $55.00 = $9.00 per share. Because time remains, the contract does not trade at exactly its intrinsic value. Suppose it quotes near $9.80. That extra $0.80 is remaining extrinsic value, the market still charging something for the chance that NWR climbs further before expiry.</p>
      <p>You sell to close at $9.80. That is $980 received against $200 paid: a profit of $780, which is +390% on the position and +7.8% on the entire $10,000 portfolio.</p>

      <h3>What the same $200 in stock would have done</h3>
      <p>$200 buys 4 shares of NWR at $50.00. At $64.00 those 4 shares are worth $256, a gain of $56, or +28%. Same thesis, same stock, same window: $56 instead of $780.</p>
      <p>This is the shape people mean when they call an option an <Term k="asymmetric bet">asymmetric bet</Term>: the contract controlled 100 shares of exposure for the price of 4, so a 28% stock move became a 390% position move. Now state the symmetric fact in the same breath, because it is the same mechanism running backwards. The multiplication does not know which direction it is pointing. The stock holder in a bad outcome is down some percentage; the option holder is frequently down all of it.</p>

      <h3>The exit you wrote down before you needed it</h3>
      <p>The reason Ending A ends at $780 is not that you predicted $64. It is that you decided, before placing the trade, that you would sell into any post-earnings move that took the contract above roughly $8.00. The catalyst had happened. The thesis was fully priced. You closed it.</p>

      <Callout variant="real-talk">
        <p>The far more common version of this story: the contract hits $9.80, you think “this is finally working,” and you hold for more. NWR drifts back to $57 over the next two weeks, the remaining extrinsic value bleeds out, and you close at $2.20 for a gain of $20. You were right about the company, right about the earnings, and you still walked away with almost nothing, because the plan ended where your discipline did.</p>
      </Callout>

      <h2>Ending B: right direction, wrong magnitude</h2>
      <p>Rewind. Same $200, same contract. This time earnings are fine (revenue grows, nothing breaks, management sounds reasonable), but nothing about the report excites anyone. NWR drifts from $50.00 to $53.00 over the six weeks and sits there.</p>
      <p>You were right. The stock went up. And at expiration, with NWR at $53.00 and your strike at $55.00, the call is out of the money and expires worthless. Your loss is $200, which is 100% of the position.</p>
      <p>The stock holder in this identical scenario owns 4 shares worth $212 and is up 6%. You are down everything. Correct direction, insufficient magnitude, and the clock ran out. All three had to go your way, and only one did.</p>

      <h3>The interim path, honestly</h3>
      <p>Losses like this rarely arrive as one clean event at expiration. Three weeks in, NWR is at $51.00 (up a dollar from where you bought) and your contract might be quoted around $1.10. You are down about 45% while the stock is up 2%.</p>
      <p>That gap is <Term k="theta decay">theta decay</Term>. Extrinsic value is the market pricing the time left for something to happen, and time only moves one way. Every day that passes with NWR going nowhere, the contract is worth less, whether or not the stock cooperated.</p>

      <KeyTerm term="theta decay" />

      <p>This is the exact moment where the trade is decided, and it is decided by temperament rather than analysis. One reader panic-sells at $1.10 and recovers $110. Another decides the thesis is intact and buys a second contract, doubling the position to 4% of the portfolio at precisely the moment the evidence got worse. Both of those are real decisions with real consequences, and both should have been made weeks earlier, in writing, when nothing was at stake and your judgment was clean.</p>

      <Callout variant="warning" title="Adding to a losing option is not conviction">
        <p>Doubling down on a decaying contract feels like commitment. Mechanically, it is a decision to increase your risk in response to information that argues for less of it. If your written plan does not already say “I will add here, at this price, up to this size,” then the answer at $1.10 is no.</p>
      </Callout>

      <h2>Both endings on one page</h2>
      <p>Here is every outcome side by side, including a middle case at $58 so you can see the narrow band where the option barely does anything at all. Portfolio impact is measured against the starting $10,000.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Scenario</th>
              <th>NWR at exit</th>
              <th>Option value</th>
              <th>Position P&amp;L</th>
              <th>Portfolio impact</th>
              <th>$200 in stock instead</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Ending B: expires</td>
              <td>$53.00</td>
              <td>$0</td>
              <td>−$200 (−100%)</td>
              <td>−2.0%</td>
              <td>$212 (+$12, +6%)</td>
            </tr>
            <tr>
              <td>Middle: expires</td>
              <td>$58.00</td>
              <td>$300</td>
              <td>+$100 (+50%)</td>
              <td>+1.0%</td>
              <td>$232 (+$32, +16%)</td>
            </tr>
            <tr>
              <td>Ending A: sold early</td>
              <td>$64.00</td>
              <td>$980</td>
              <td>+$780 (+390%)</td>
              <td>+7.8%</td>
              <td>$256 (+$56, +28%)</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Look at the middle row for a moment longer than feels necessary. NWR rose 16%, a genuinely strong two-month result that any stock investor would take, and the option turned $200 into $300. All that leverage, all that hurdle, for $100. Anywhere just above the $57 break-even, the contract is doing almost nothing except charging you for the privilege of being right; it only starts to repay the leverage well beyond it.</p>

      <h2>What the sleeve does next</h2>
      <p>The trade is one decision. What you do with the result is another, and it is the one that compounds.</p>
      <p>In Ending A the sleeve now holds $800 of unspent cash plus $980 from the closed contract: $1,780, up 78%. The rule you set earlier says the sleeve does not get to grow indefinitely, so you harvest the excess into the core. Move $780 into the index fund and reset the sleeve to $1,000. The win becomes permanent instead of becoming the next position.</p>
      <p>In Ending B the sleeve holds $800 and is down 20%. The rule says you do not top it back up. It gets refilled at the next scheduled funding date and not a day earlier. That single constraint is what prevents a bad month from becoming a bad year, because the alternative (refilling from the core to “make it back”) is how a 2% loss teaches itself to become a 20% one.</p>

      <h2>The base rate nobody advertises</h2>
      <p>Of the two endings, the second shape is far more common. Not because the analysis was bad, but because buying an option requires direction, magnitude, and timing to cooperate simultaneously, and the market is not obliged to deliver all three inside your expiration window. Ordinary outcomes (a stock that goes up a bit, or sideways, or up after your contract expires) produce total losses on the contract with routine regularity.</p>
      <p>So apply this test to anything you read from here on. If a framework, a video, or a person shows you Ending A repeatedly and Ending B rarely, they are not teaching you options. They are selling you something, and the product is the feeling you get looking at +390%.</p>

      <TryIt moduleId={moduleId} id="reflect" placeholder="Which ending would you have handled worse, and what specifically would you have done?">
        <p>Be honest with yourself in writing. Which of the two endings would you personally have handled worse: Ending A, where you had a $780 gain on the screen and a plan that said sell, or Ending B, where you were down 45% at three weeks with the stock actually up? Name the specific thing you think you would have done wrong, and then write the one sentence you would put in a written plan to stop yourself from doing it.</p>
      </TryIt>

      <h2>One thing to carry out of here</h2>
      <p>The Hard track only functions because the two tracks under it exist. Nothing in this walkthrough required you to be a better forecaster than anyone else. It required a portfolio that could absorb the bad ending without changing your life, and that portfolio was built by the boring lessons.</p>

      <Callout variant="warning" title="Why the 100% loss did not matter">
        <p>Ending B was a total loss on the position and a 2% dent on the portfolio. Those are the same event described at two altitudes, and the only reason the second description is true is that you sized the trade at $200 before you placed it. There is no decision available after a trade goes wrong that can retroactively make it small. Speculation is survivable only on top of something stable, and if the stable part is not built yet, the speculation is not a strategy; it is just exposure.</p>
      </Callout>

      <p>If you skipped the Intermediate track lesson on building a stable core, go back and actually do it. Not skim it. Do the exercises, open the fund pages, look up the expense ratios yourself. That lesson is the foundation this one has been standing on the entire time.</p>

      <p>And the last honest thing worth saying: the most profitable financial decision most people ever make is not a trade at all. It is starting to invest steadily in something boring in their twenties and leaving it alone for decades. Options are a legitimate tool with legitimate uses, and everything you have learned here about break-even, decay, and sizing is real knowledge. It is just not the part that makes you wealthy. That part was in the first track, and it is still available to you tomorrow morning.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
