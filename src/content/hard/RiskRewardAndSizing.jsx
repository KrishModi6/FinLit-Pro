import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A bet pays +$10 nine times out of ten and loses $100 the other time. What is its expected value per bet?',
    options: [
      'Positive, about $9 per bet',
      'Positive, about $1 per bet',
      'Negative, about $1 per bet',
      'Zero, because a 90% win rate exactly offsets the large loss',
    ],
    answer: 2,
    explanation: 'The two legs are 0.9 × $10 = +$9 and 0.1 × −$100 = −$10, so the expected value is −$1. The +$9 answer is tempting because it counts only the wins, but a 90% win rate is meaningless once the single loss is ten times the size of a win.',
  },
  {
    prompt: 'A strategy that wins nine times out of ten is, by that fact alone, a profitable strategy.',
    type: 'tf',
    answer: false,
    explanation: 'Win rate is one of two inputs and is useless on its own. A 90% winner with tiny wins and one catastrophic loss loses money; a 10% winner with one huge payoff can make money. Only the full payoff distribution tells you which you are holding.',
  },
  {
    prompt: 'You put $500 of a $10,000 portfolio into a single out-of-the-money call option that can plausibly expire worthless. Under the 1–2% rule, how much are you risking?',
    options: [
      'About $100, since you would exit if it dropped 20%',
      'The full $500, because total loss is a realistic outcome for that position',
      'Nothing until expiry, since the loss is not locked in yet',
      '2% of $500, which is $10',
    ],
    answer: 1,
    explanation: 'Risk means the money you would actually lose in your realistic downside scenario. For a stock you would exit at −20%, that is a fifth of the position. For an option that can go to zero, the realistic downside is the entire premium, so the whole $500 counts, which is 5% of a $10,000 account and already breaks the rule.',
  },
  {
    prompt: 'You hold five speculative positions, each risking 2% of your portfolio, and all five are in the same sector and tend to move together. What are you actually risking on that theme?',
    options: [
      '2%, since that is the size of each individual position',
      'About 10%, because positions that move together behave like one larger position',
      'Less than 2%, because holding five names is diversification',
      'It cannot be estimated without each company’s exact beta',
    ],
    answer: 1,
    explanation: 'Correlated positions add up. If one piece of sector news moves all five the same way, the bad case hits every position at once, so five 2% risks are one 10% risk wearing a disguise. Owning five tickers is only diversification if they do not share the thing that can go wrong.',
  },
  {
    prompt: 'If you risk 2% of your portfolio per idea, ten losses in a row would cut your account roughly in half.',
    type: 'tf',
    answer: false,
    explanation: 'Each loss takes 2% of what remains, so ten of them leave 0.98 to the tenth power, about 0.82, or roughly 82% of the account. That is an 18% hole needing about a 22% gain to fill. Painful, survivable, and nothing like the 50% loss that would need a 100% gain.',
  },
]

export default function RiskRewardAndSizing({ moduleId }) {
  return (
    <>
      <p className="lead">Two students buy the same stock on the same morning at the same price. A year later one has doubled their money and the other has almost nothing left. The company did exactly one thing in that year, and it did the same thing for both of them. The difference was never the pick; it was how much of the account was standing behind it.</p>

      <h2>“High risk, high reward” is a mistranslation</h2>

      <p>The phrase gets repeated until people hear it as a promise: accept more risk, receive more reward. That is not what it means, and the promise version is expensive.</p>

      <p>Stated properly, a higher <strong>expected</strong> return is compensation for accepting a wider distribution of outcomes. Risk does not produce reward. Risk is the price of admission to a payoff you might not get. A speculative biotech has to offer the possibility of a large gain because otherwise nobody would tolerate the possibility of losing everything; a Treasury bill offers almost nothing because almost nothing can go wrong.</p>

      <p>So plenty of high-risk positions deliver only the risk. That is not the system malfunctioning. That is the system working exactly as described, and you happened to land on the wrong side of the distribution. Once you internalise that, the interesting question stops being “how much can this make?” and becomes “what am I being paid to accept, and can I survive the bad half?”</p>

      <h2>Expected value: the number that actually matters</h2>

      <p>Expected value is the average outcome if you could run the same situation thousands of times. You compute it by multiplying each outcome by its probability and adding the results. It is arithmetic, not opinion, and it settles arguments that feel unsettlable.</p>

      <Callout variant="example">
        <p>Bet A wins $10 with 90% probability and loses $100 with 10% probability. The winning leg contributes 0.9 × $10 = +$9. The losing leg contributes 0.1 × $100 = −$10. Expected value: −$1 per bet.</p>
        <p>Bet B wins $200 with 10% probability and loses $10 with 90% probability. Winning leg: 0.1 × $200 = +$20. Losing leg: 0.9 × $10 = −$9. Expected value: +$11 per bet.</p>
      </Callout>

      <p>Bet A wins nine times out of ten and loses money. Bet B loses nine times out of ten and makes money. Take the second one seriously for a moment: you would be wrong almost every time you played it, you would feel like an idiot for weeks, and you would still be doing the right thing. That mismatch between what is correct and what feels correct is where most bad investing decisions live.</p>

      <p>The practical conclusion is blunt. Win rate tells you nothing on its own. When somebody says “I was right nine times out of ten”, they have given you half of one input and none of the other, and it is not evidence of anything yet. A structurally sound <Term k="asymmetric bet">asymmetric bet</Term> is one where the payoff on the good outcome is large relative to the loss on the bad one, which is the only reason a low win rate can ever be acceptable.</p>

      <h2>Risk of ruin: the arithmetic that ends accounts</h2>

      <p>Expected value assumes you are still playing. If a losing streak removes you from the game, the long-run average never arrives. That is risk of ruin, and it is entirely a function of how much you stake, not how good your ideas are.</p>

      <p>Suppose you start with $1,000 and risk 50% of the account on each idea, which is roughly what a “this one is a sure thing” trade looks like in practice, especially with <Term k="leverage">borrowed money or leveraged products</Term> involved.</p>

      <ol>
        <li>Start: $1,000.</li>
        <li>One loss: $500 left.</li>
        <li>Two losses: $250 left, a quarter of where you began.</li>
        <li>To get back to $1,000 from $250 you now need a 300% gain.</li>
      </ol>

      <p>Two bad calls. Not ten, not a crash, not fraud. Two. And the required recovery is something most professional investors never achieve in a decade.</p>

      <p>Now risk 2% instead. Ten consecutive losses leave you with 0.98 to the tenth power of the account, which is about 0.817, or roughly $817 of the original $1,000. You need about a 22% gain to be whole. Ten losses in a row is a genuinely brutal streak, and the 2% version of you is still trading, still solvent, still able to be right later.</p>

      <Callout variant="did-you-know">
        <p>GameStop went from under $20 at the start of January 2021 to an intraday high near $483 on 28 January 2021, then fell roughly 90% within weeks. A 90% loss requires a 900% gain to recover. Someone who sized that position at 2% of their portfolio has an interesting story; someone who sized it at 40% has a different kind of story.</p>
      </Callout>

      <h2>The 1–2% rule</h2>

      <KeyTerm term="Position Sizing" />

      <p>The rule is simple to state and constantly violated: risk no more than 1–2% of your total portfolio value on any single idea. <Term k="position sizing">Position sizing</Term> is the decision of how much, and it is a separate decision from what to buy. Most people collapse the two and decide the amount based on how confident they feel, which means their largest position is always the one they are most emotionally attached to.</p>

      <h3>Deployed is not the same as risked</h3>

      <p>The word “risk” in the rule means the money you would actually lose in your realistic downside scenario, not the money you put in. Those are different numbers, and confusing them is the most common way people think they are following the rule while breaking it.</p>

      <p>A $500 stock position where you have genuinely decided to exit at a 20% loss risks $100. A $500 options position where expiring worthless is a real, ordinary outcome risks $500. Same cash deployed, five times the risk.</p>

      <Callout variant="warning">
        <p>The stock version only risks $100 if you actually exit. An exit plan you abandon at the moment of pain is not a plan, it is a hope, and the honest risk number for a position you know you will not sell is closer to the full amount.</p>
        <p>For options and leveraged products, assume total loss is the realistic downside unless you can explain clearly why it is not. Options are often described as cheap because the ticket price is small. The relevant number is not the ticket price, it is the probability that the ticket is worth zero at expiry, and for out-of-the-money contracts that probability is frequently the most likely single outcome.</p>
      </Callout>

      <h3>What the rule looks like on a real account</h3>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Portfolio</th>
              <th>1% max risk</th>
              <th>2% max risk</th>
              <th>What the 2% figure actually buys</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>$1,000</td>
              <td>$10</td>
              <td>$20</td>
              <td>A $100 stock position you would exit 20% down. No standard option contract costs this little.</td>
            </tr>
            <tr>
              <td>$5,000</td>
              <td>$50</td>
              <td>$100</td>
              <td>A $500 stock position with a 20% exit, or one option contract priced at $1.00 per share.</td>
            </tr>
            <tr>
              <td>$10,000</td>
              <td>$100</td>
              <td>$200</td>
              <td>A $1,000 stock position with a 20% exit, or one contract at $2.00 per share of premium.</td>
            </tr>
            <tr>
              <td>$25,000</td>
              <td>$250</td>
              <td>$500</td>
              <td>A $2,500 stock position with a 20% exit, or a small multi-contract options position.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Read the top row carefully, because it is the one that applies to most students. On a $500 account, 2% is $10, and a single option contract covering 100 shares will cost more than that at almost any premium worth trading. The rule is telling you something true: at that account size, options positions cannot be sized responsibly. That is real information about what your capital can and cannot do yet, not a reason to decide the rule does not apply to you.</p>

      <TryIt moduleId={moduleId} placeholder="Portfolio value: $___. 1% = $___. 2% = $___. My idea risks $___ in the realistic bad case, which is ___% of the portfolio. Passes / fails, and what I would change.">
        <p>Take your real portfolio value, or a realistic number you expect to have within a year, and write down your 1% and 2% figures in dollars. Then take your most recent speculative idea, or the one you are most tempted by right now, and open its actual page on Yahoo Finance or your broker. Work out what the position would cost and what you would genuinely lose in the bad case: the full premium for an option, the distance to your exit for a stock. Compare that number to your 1% and 2% figures and write one sentence saying whether it passes, and if it fails, what size would make it pass.</p>
      </TryIt>

      <h2>Why sizing dominates selection</h2>

      <KeyTerm term="Drawdown" />

      <p>The recovery table from the earlier lesson is the reason sizing matters more than picking. A 20% <Term k="drawdown">drawdown</Term> needs a 25% gain to undo. A 50% loss needs 100%. A 75% loss needs 300%. The damage compounds against you faster than the recovery compounds for you, and there is no cleverness that repeals this.</p>

      <p>Which means the question “was I right about this company?” is much less important than the question “how much did it cost me to be wrong?” You will be wrong regularly. Everyone is. Analysts with access to management, models and full-time hours are wrong constantly. The people who last are not the ones who are wrong less often, they are the ones who are wrong smaller.</p>

      <h3>Correlation, or five positions pretending to be five</h3>

      <p>Here is how the rule gets broken by people who believe they are following it. You hold five speculative names, each risking a tidy 2%. It looks disciplined. But all five are semiconductor companies, and semiconductors move together on the same news about demand, supply chains and rates. The bad case does not arrive one position at a time. It arrives once and hits all five.</p>

      <p>That is a 10% risk in five costumes. Real <Term k="diversification">diversification</Term> is not about the number of tickers, it is about whether the things that can go wrong are different things. Before you add a position, ask what single headline would damage everything you already own, and whether the new name shares it.</p>

      <h2>The formal answer you probably cannot use</h2>

      <p>There is a mathematically optimal bet size. The Kelly criterion computes the fraction of capital that maximises long-run growth, given your edge and your odds. It is elegant and it is correct. It is also close to unusable for a retail investor, because it requires you to know your true probability of being right and your true payoff ratio, and you do not know either. You have estimates, and overconfident ones. Kelly is extremely sensitive to those inputs: overestimate your edge slightly and it tells you to bet an amount that will eventually ruin you. Professionals who use it routinely trade a half or a quarter of the Kelly size for exactly that reason. Treat it as evidence that a right answer exists and that it is smaller than your instinct, not as a formula to plug numbers into.</p>

      <h2>What to carry forward</h2>

      <p>One idea, and it is the whole lesson: you cannot control whether you are right, and you can always control how much it costs to be wrong. Selection is a guess dressed up in research. Sizing is arithmetic you perform before the market has any say in it.</p>

      <Callout variant="real-talk">
        <p>Position sizing is the only part of investing you fully control. Not the earnings report, not the Fed, not the guy on a forum who moved the stock 8% with a screenshot. The size of the position is yours, entirely, decided by you before anything happens, and it is the single input that determines whether a bad year is a setback or an ending.</p>
      </Callout>

      <p>Every number in this lesson rests on one honest estimate: your realistic downside. Get that wrong and the 2% rule quietly becomes the 15% rule while you congratulate yourself on your discipline. That is what comes next: how to decide in advance what your exit actually is, and why the exit has to be defined before the entry rather than negotiated with yourself while you are losing money.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
