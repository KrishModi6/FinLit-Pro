import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A portfolio falls 75%. What gain is needed on the remaining balance to get back to the starting value?',
    options: ['+75%', '+150%', '+300%', '+400%'],
    answer: 2,
    explanation: '$100 falling 75% leaves $25. To get from $25 back to $100 you need to quadruple it, which is a gain of $75 on a $25 base, or +300%. The tempting answer is +75%, because people assume the percentage that took you down is the percentage that brings you back. It is not, because the gain is calculated on a much smaller base.',
  },
  {
    prompt: 'Student A puts all $1,000 into speculative names; Student B puts $850 into a broad index fund and $150 into the same speculative names. In a year where the speculative names rise 150% and the index rises 12%, which statement is accurate?',
    options: [
      'Student B ends the year with more money, because diversification always wins.',
      'Student A ends the year with more money, and that is a real cost of holding a stable core.',
      'Both end with the same amount, because the maths cancels out.',
      'Student A ends with more money only if the index falls that year.',
    ],
    answer: 1,
    explanation: 'Student A ends near $2,500 and Student B near $1,327. Concentration genuinely wins in good years, and pretending otherwise would be dishonest. The point of a stable core is not that it maximises returns; it is that it caps how bad the bad years get so you still have capital to invest afterwards.',
  },
  {
    prompt: 'A stable core exists mainly to increase your expected return over the long run.',
    type: 'tf',
    answer: false,
    explanation: 'A stable core is a survival mechanism, not a return-maximiser. Its job is to keep your losses recoverable and your behaviour steady so you get more attempts. Over some periods a concentrated bet will beat a diversified portfolio, which is exactly why the argument for a core rests on the distribution of outcomes rather than on any single year.',
  },
  {
    prompt: 'Two investors earn the same average annual return over ten years, but one suffers the worst loss in year one and the other in year ten, while both add money from income along the way. What does this illustrate?',
    options: [
      'Nothing, because equal averages always produce equal ending balances.',
      'Sequence-of-returns risk: the order in which gains and losses arrive changes the outcome once money moves in or out.',
      'That averages are always misleading and should be ignored.',
      'That losses early in life are mathematically impossible to recover from.',
    ],
    answer: 1,
    explanation: 'With no deposits or withdrawals, order does not change the ending balance. Once you are contributing or spending, it does, because each return applies to a different amount of money. An early crash for someone still adding money can even help, since later contributions buy in cheaply; the same crash for someone withdrawing is far more damaging.',
  },
  {
    prompt: 'The most common way people destroy their own stable core is by selling the boring holdings to add money to a losing speculative position.',
    type: 'tf',
    answer: true,
    explanation: 'This is the classic failure. The speculative position drops, it feels underpriced, and the only available cash is sitting in the index fund. Selling the core to fund the bet converts a diversified portfolio into a concentrated one at exactly the moment conviction is running ahead of evidence, and it removes the buffer that made the loss survivable in the first place.',
  },
]

export default function TheStableCore({ moduleId }) {
  return (
    <>
      <p className="lead">Lose half your money and you need to double what is left just to get back where you started. That single asymmetry is the entire argument for holding a boring, stable core, and it is arithmetic rather than opinion. Everything else in this lesson is a consequence of it.</p>

      <h2>The recovery maths is not symmetric</h2>
      <p>A <Term k="drawdown">drawdown</Term> is the peak-to-trough decline in your portfolio value. People instinctively treat a 30% loss and a 30% gain as opposites that cancel out. They do not, because a loss shrinks the base that the next gain is calculated on. Lose 30% of $100 and you hold $70; a 30% gain on $70 returns $91, not $100.</p>

      <p>Here is the full picture. The recovery figure is what the surviving balance has to gain to reach the original amount.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Loss</th>
              <th>$100 becomes</th>
              <th>Gain needed to recover</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>10%</td>
              <td>$90</td>
              <td>+11.1%</td>
            </tr>
            <tr>
              <td>20%</td>
              <td>$80</td>
              <td>+25%</td>
            </tr>
            <tr>
              <td>30%</td>
              <td>$70</td>
              <td>+42.9%</td>
            </tr>
            <tr>
              <td>50%</td>
              <td>$50</td>
              <td>+100%</td>
            </tr>
            <tr>
              <td>75%</td>
              <td>$25</td>
              <td>+300%</td>
            </tr>
            <tr>
              <td>90%</td>
              <td>$10</td>
              <td>+900%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Notice how gentle the top of the table is and how violent the bottom is. Small losses are almost free to undo. Past roughly 50% the required recovery goes near-vertical. The implication is blunt: avoiding catastrophic losses matters more than capturing spectacular gains, because you can compound your way out of a 20% hole in a couple of ordinary years and you cannot realistically compound your way out of a 90% hole at all.</p>

      <KeyTerm term="drawdown" />

      <h2>Two students, same $1,000</h2>
      <p>Meet Student A and Student B. They are illustrations, not real people, and the numbers below are hypothetical figures chosen to make the arithmetic clean. Both start with $1,000. Both are equally interested in the market and equally convinced they have found something good.</p>

      <p>Student A puts the whole $1,000 into two heavily hyped, highly speculative positions. Student B puts $850 into a broad <Term k="index fund">index fund</Term> and $150 into the exact same two speculative ideas. Same research, same enthusiasm, different <Term k="position sizing">position sizing</Term>.</p>

      <h3>The bad year</h3>
      <p>Suppose the speculative names fall about 70% and the broad index falls about 18%.</p>
      <ol>
        <li>Student A: $1,000 down 70% leaves $300.</li>
        <li>Student B, core: $850 down 18% leaves $697.</li>
        <li>Student B, speculative sleeve: $150 down 70% leaves $45.</li>
        <li>Student B total: $697 plus $45 is $742.</li>
      </ol>

      <p>Now run the recovery. Student A needs a gain of about 233% to get back to $1,000, since $300 has to more than triple. Student B needs about 35%. Historically, a broad US index has produced gains in the 30% range in a strong year and has done so more than once. A 233% gain is not something you plan around; it is something you hope for.</p>

      <p>Play the next three years forward at a plain 9% a year, with nothing added. Student B goes from $742 to roughly $961 and is nearly whole. Student A goes from $300 to roughly $389 and is still down more than 60% from where they began. The gap did not open up because Student B picked better. It opened up because Student B lost less.</p>

      <h3>The good year, told honestly</h3>
      <p>Now flip it. The speculative names rise 150% and the index rises 12%.</p>
      <ol>
        <li>Student A: $1,000 up 150% is $2,500.</li>
        <li>Student B, core: $850 up 12% is $952.</li>
        <li>Student B, speculative sleeve: $150 up 150% is $375.</li>
        <li>Student B total: $1,327.</li>
      </ol>

      <p>Student A wins that year, and wins by a lot. Almost $1,200 more. Anyone who tells you a diversified portfolio always beats a concentrated one is selling you something. Concentration is how large fortunes get built, and in a year when the bet pays, the person who sized it small watches from the sidelines with a perfectly respectable 33% and a slightly sour expression.</p>

      <Callout variant="real-talk">
        <p>If speculation never worked, nobody would do it, and this lesson would be unnecessary. It works often enough to stay tempting. The question is not whether concentration can win. It is what happens to you in the years it does not.</p>
      </Callout>

      <h2>The point that actually lands</h2>
      <p>Line up all four outcomes. In the good year Student A is at $2,500 and Student B is at $1,327. In the bad year Student A is at $300 and Student B is at $742. Student A wins one scenario decisively and is functionally out of the game in the other.</p>

      <p>Student B is still in the game in every scenario. That is the whole thing. A stable core is not there to maximise your return; it is there to guarantee you get more attempts. If you make one concentrated bet a year for ten years, Student A needs an early win to still have capital by year four. Student B can be wrong repeatedly and keep showing up, and showing up is most of how compounding works.</p>

      <Callout variant="did-you-know">
        <p>This is why professional risk managers care more about the size of the worst plausible loss than about the size of the best plausible gain. A fund that returns 40% a year and then loses 95% once has, over its life, returned nothing to anyone who was there for the whole ride.</p>
      </Callout>

      <h2>When the losses happen matters</h2>
      <p>Averages hide something important. If you never add or withdraw money, the order of your annual returns makes no difference to your final balance; multiplication does not care about sequence. The moment you start contributing from a job, or withdrawing to pay for something, order starts to matter enormously. This is called sequence-of-returns risk.</p>

      <p>Consider two people who both average the same return over ten years. One takes their worst year first, the other takes it last. If both are adding $200 a month from income, the person who crashed early was buying at low prices for years afterwards and often comes out ahead. The person who crashed at the end took the hit on a much larger balance, so the same percentage loss destroyed far more dollars.</p>

      <p>For a student with decades ahead and income to add, an early bear market is genuinely not the disaster it feels like, provided you are still holding something and still buying. That proviso is doing a lot of work. It only holds if the crash did not wipe you out first.</p>

      <h2>The core is mostly a behavioural device</h2>
      <p>The most underrated function of a stable core has nothing to do with arithmetic. When the market falls hard, the difference between a portfolio down 22% and a portfolio down 70% is not just financial, it is emotional. At down 22% you feel bad. At down 70% you start believing you were fundamentally wrong about everything, and that is the state of mind in which people sell everything at the bottom and never come back.</p>

      <p>A core made of broad, diversified holdings gives you something to look at that is merely unpleasant rather than catastrophic. <Term k="diversification">Diversification</Term> does not stop losses; it stops them from being correlated enough to break you. The Hard track lesson on trading psychology goes much deeper into why the bottom of a decline is precisely when your judgement is worst.</p>

      <Callout variant="warning" title="The most common self-inflicted wound">
        <p>A stable core only works if you actually leave it alone. The classic sequence: the speculative position drops 60%, you become more convinced rather than less, and the only money available to average down is sitting in the index fund. So you sell the boring half to feed the exciting half.</p>
        <p>You have now converted a diversified portfolio into a concentrated one at the exact moment your conviction has outrun your evidence, and you have deleted the buffer that made the original loss survivable. If you take one operational rule from this lesson, make it this one: the core is not a funding source for the speculative sleeve.</p>
      </Callout>

      <h2>What “stable” actually means</h2>
      <p>Stable does not mean safe, and it certainly does not mean flat. For a young investor with a long horizon, the stable part of a portfolio usually looks like some combination of three things: broad index funds tracking a wide market, large diversified companies with real earnings and multiple product lines, and plain cash for anything you will need within the next few years.</p>

      <p>That last category matters more than people expect. Money you need for university fees in eighteen months does not belong in equities at all, whatever the expected return, because you do not get to choose when the market is down.</p>

      <p>Be honest about what the first two categories do. A total-market index fund still falls in a bear market. In the 2008 crisis broad US indices lost roughly half their value peak to trough. Stable is a statement about <Term k="volatility">volatility</Term> relative to a single speculative position, not a promise of protection. Falling 40% and recovering over several years is a completely acceptable outcome if your horizon is measured in decades. It is a disaster if your horizon is measured in months.</p>

      <Callout variant="note">
        <p>Broad index funds are also where costs bite least. Widely held funds tracking the S and P 500, such as VOO, carry expense ratios in the region of 0.03%. Look up the current figure for anything you are studying rather than trusting a number in a lesson.</p>
      </Callout>

      <h2>How to think about the split</h2>
      <p>No website can tell you the right proportion, and any that claims to is guessing about your life. What a lesson can do is hand you the three questions that actually drive the number.</p>

      <p>First, your time horizon. Money you will not touch for twenty years can tolerate deep drawdowns; money you need in two years cannot. Second, whether you can add money from income. Someone contributing every month has a recovery engine that someone with a fixed lump sum does not, and can reasonably carry more risk. Third, and most revealing, how you actually behaved the last time your portfolio dropped. Not how you think you would behave. What you did. If you sold in a panic at down 15%, your real risk tolerance is lower than your imagined one, and the honest response is to build a larger core rather than to promise yourself you will be braver next time.</p>

      <p>A frame you will hear discussed is the 90/10 idea, where roughly ninety percent sits in broad diversified holdings and ten percent is available for concentrated bets. Treat it as a conversation starter, not a prescription. The Hard track examines where that number comes from and where it breaks down.</p>

      <TryIt moduleId={moduleId} placeholder="e.g. 60% broad index fund, 25% individual large companies, 15% speculative. If the speculative part fell 70% tomorrow I would…">
        <p>Write down the percentage of your portfolio, real or imagined, that sits in broad and boring holdings. Use your brokerage account, a paper portfolio, or a watchlist you have been tracking on Yahoo Finance.</p>
        <p>Then answer the second question honestly, because it is the one that matters: if the speculative part fell 70% tomorrow, what would you actually do? Sell it, hold it, add to it, or sell the boring holdings to add to it? Write the real answer, not the admirable one.</p>
      </TryIt>

      <h2>The one thing to remember</h2>
      <p>Losses and gains are not mirror images. A 50% loss demands a 100% gain, a 90% loss demands a 900% gain, and no realistic strategy reliably delivers the second number. The stable core exists to keep your worst year inside the range that ordinary market returns can undo.</p>

      <p>It will cost you in the good years. Student A took home $2,500 while Student B took home $1,327, and that gap is real, not a rhetorical trick. What you are buying with that gap is the certainty that you are still investing in year five, and year ten, and year thirty. Survival is not a consolation prize in investing. It is the mechanism by which compounding does anything at all.</p>

      <p>Next up: how to actually build the core, including how a handful of broad funds can cover most of a global market, and what to check before you assume two holdings are diversifying each other when they may in fact own the same twenty companies.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
