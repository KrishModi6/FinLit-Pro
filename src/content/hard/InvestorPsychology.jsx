import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'You bought a stock at $80. It now trades at $40, and the company has since lost its largest customer and cut guidance twice. You tell yourself “it was $80, so at $40 it’s cheap.” Which bias is doing the most work in that sentence?',
    options: [
      'Recency bias: you are extrapolating the last few months forever',
      'Anchoring: you are treating the old price as a measure of value',
      'Herding: you are following what other investors are doing',
      'Overconfidence: you are overrating your own stock-picking skill',
    ],
    answer: 1,
    explanation: 'Anchoring is fixating on a reference number (your purchase price or a past high) as if the market knows or cares about it. The $80 tells you nothing about the business today; the lost customer and cut guidance do. Recency bias is tempting here, but recency would be extrapolating the recent decline forward, which is roughly the opposite of what this investor is doing.',
  },
  {
    prompt: 'Knowing about a cognitive bias is generally enough to stop it from affecting your decisions.',
    type: 'tf',
    answer: false,
    explanation: 'Recognising a bias in a calm classroom moment and resisting it at 2am with money on the line are different skills. Biases operate below the level you can introspect on, which is why the fix is process (written rules, waiting periods, decision journals) rather than awareness. Believing that awareness alone protects you is itself a form of overconfidence.',
  },
  {
    prompt: 'A trader has made money on six of her last seven trades during a period when the broad market rose about 25%. What is the most defensible conclusion?',
    options: [
      'She has demonstrated genuine skill and should increase her position sizes',
      'The sample is far too small and too market-dependent to separate skill from a rising tide',
      'Her method is proven, since seven trades is a reasonable sample',
      'She got lucky, and her approach is therefore worthless',
    ],
    answer: 1,
    explanation: 'In a strong bull market almost everyone looks brilliant, because the market is doing the work. Over short periods, decision quality and outcome quality are only loosely coupled, so seven outcomes cannot tell you which one you are observing. The honest answer is not “she is skilled” or “she is lucky”; it is that you do not yet have enough evidence to say, which is exactly what a decision journal is designed to fix.',
  },
  {
    prompt: 'The disposition effect describes which pattern?',
    options: [
      'Buying more of whatever has risen fastest in the last month',
      'Selling winners early to lock in a gain while holding losers to avoid realising a loss',
      'Refusing to invest at all after a single bad experience',
      'Trading more often as account size increases',
    ],
    answer: 1,
    explanation: 'The disposition effect falls out of loss aversion: a realised gain feels good now, while a realised loss feels roughly twice as bad, so people cash the first and postpone the second. The practical damage is that it systematically shortens your winners and lengthens your losers, which is the reverse of what a portfolio needs.',
  },
  {
    prompt: 'Averaging down into a position whose original thesis has broken is risky mainly because it increases the size of the position at the moment your conviction should be shrinking.',
    type: 'tf',
    answer: true,
    explanation: 'Adding to a loser is often framed as “improving my average price,” which sounds like arithmetic rather than a decision. But each addition makes the position a larger share of your portfolio precisely as the evidence for it weakens, so it quietly overrides whatever position-sizing limits you set. Averaging down can be defensible when the thesis genuinely still holds and the size was planned in advance. The failure mode is doing it to avoid admitting the first purchase was wrong.',
  },
]

export default function InvestorPsychology({ moduleId }) {
  return (
    <>
      <p className="lead">Two people can read the same earnings report, hold the same stock, and pay the same commission, and one of them will still lose money the other keeps. The difference usually is not information. It is what happens in the four seconds between feeling something and tapping the button.</p>

      <h2>Your brain is not broken, it is just in the wrong environment</h2>

      <p>It is tempting to read a list of cognitive biases as a list of ways people are stupid. That framing is both unkind and wrong, and it will make you worse at spotting these in yourself, because nobody thinks they are the stupid one.</p>

      <p>Every bias in this lesson is a well-adapted instinct running in an environment it was never built for. Reacting hard to loss is excellent design when the loss is your food supply for the winter. Copying the crowd is excellent design when the crowd is running from something you have not seen yet. Trusting a pattern after a few successes is how you learn anything at all.</p>

      <p>Markets take those instincts and invert their payoff. Here, the loss is a temporary price quote on a screen, the crowd is often most confident at exactly the wrong moment, and three good outcomes prove almost nothing about your process. The instincts fire the same way regardless. That mismatch (good hardware, wrong environment) is the whole subject.</p>

      <h2>FOMO: urgency peaks when the move is most extended</h2>

      <KeyTerm term="FOMO" />

      <p><Term k="fomo">Fear of missing out</Term> is not really about the stock. It is about the gap between where you are and where you imagine you would be if you had acted earlier. Two inputs create it: a rising price, and social proof (a friend who is up 40%, a screenshot in a group chat, a subreddit that will not stop talking about one ticker).</p>

      <p>Here is the mechanism that makes it expensive. Both inputs get stronger as a move extends. A stock that has doubled generates more excitement than one that has risen 5%, and it generates the most excitement of all right at the point where the crowd is largest and the price is furthest from where it started. So the moment your urgency peaks is, on average, the worst available entry point. FOMO does not just make you buy; it makes you buy near local tops with unusual reliability.</p>

      <p>The symptom to watch for is subtle and very diagnostic: <em>you notice you are researching after you have already decided to buy.</em> If you are reading to find reasons rather than to reach a conclusion, the decision was made emotionally and the analysis is decoration.</p>

      <Callout variant="example">
        <p>In January 2021, GameStop went from under $20 at the start of the month to an intraday high near $483 on 28 January (all pre-split figures: GME did a 4-for-1 split in July 2022). The coverage, the memes and the social proof were most intense in the last few days of that run. Within weeks the stock had fallen roughly 90% from that peak.</p>
        <p>Most of the people who bought at the loudest moment were not being irrational by their own lights. They were responding to overwhelming social evidence. That is precisely the problem: the evidence was loudest at the top.</p>
      </Callout>

      <p><strong>Countermeasure.</strong> Put mandatory time between the impulse and the order: 24 hours is a common choice, and the exact number matters less than the fact that it is decided in advance. Second, write the thesis down <em>before</em> you open the brokerage app: what the company does, why you think the price is wrong, and what would prove you wrong. If you cannot fill in the third one, you do not have a thesis, you have an urge.</p>

      <h2>Loss aversion: the money is already gone</h2>

      <KeyTerm term="Loss Aversion" />

      <p><Term k="loss aversion">The pain of a loss</Term> runs roughly twice as intense as the pleasure of an equivalent gain. Losing $500 does not feel like the mirror image of making $500; it feels considerably worse. That asymmetry is well documented in behavioural research, and it produces one of the most consistent patterns in retail investing: the disposition effect.</p>

      <p>The disposition effect is selling your winners early to lock in a good feeling, while holding your losers indefinitely to avoid making the loss real. Notice that both halves are emotionally sensible and financially backwards. You end up with a portfolio of your worst ideas, having sold your best ones at the point where they were just getting started.</p>

      <p>Underneath it sits the single most persistent piece of bad reasoning in investing: “it is only a loss if I sell.” This is exactly inverted. If you bought at $80 and the stock trades at $40, your position is worth $40. That is not an opinion or a threat; it is the amount of money you have. The loss already happened. What selling decides is not whether you lost the money but <em>where the remaining money sits</em>: in this company, or in something else. Refusing to sell is not avoiding the loss, it is choosing to keep betting on the same idea.</p>

      <Callout variant="warning" title="The arithmetic of holding on">
        <p>Losses and the gains needed to undo them are not symmetric. A 20% <Term k="drawdown">decline</Term> needs a 25% gain to break even. A 50% loss needs a 100% gain. An 80% loss needs a 400% gain.</p>
        <p>This is why “I will sell when it gets back to what I paid” is such an expensive rule. The deeper the hole, the more heroic the recovery has to be, and the more of your capital sits idle waiting for it rather than working somewhere with a better forward case.</p>
      </Callout>

      <p><strong>Countermeasure.</strong> Decide your exit before you enter (a price, a thesis condition, or both) and write it next to the thesis. Then use the reframing question that strips out your purchase price entirely: <em>would I buy this today, at this price, knowing what I know now?</em> If the answer is no, you are holding it only because you already own it, which is not a reason.</p>

      <h2>Overconfidence: a rising tide reads as skill</h2>

      <p>Suppose you make four trades in a year when the broad market rises 20%, and three of them work. It feels like evidence about you. Statistically, it is mostly evidence about the market.</p>

      <p>The feedback loop here is genuinely deceptive, and it is worth being precise about why. Over short periods, decision quality and outcome quality are only loosely coupled. A well-reasoned position can lose to bad luck; a reckless one can win because the whole market rose. Since you experience the outcome vividly and the process only faintly, your brain files good outcomes as proof of good judgement. In a strong bull market, that means nearly everyone gets a stream of confirmation that they are unusually skilled, and the ones who conclude they should trade bigger and more often are set up badly for the first real <Term k="drawdown">drawdown</Term>.</p>

      <p><strong>Countermeasure.</strong> Keep a decision journal, and understand that the timing is the entire point. Before you act, record: what you are doing, the thesis in two or three sentences, your confidence as a percentage, and what would falsify it. Then leave it alone. Months later, audit: not just whether you were right, but whether your stated reason was the reason it moved. You will find cases where you made money for reasons you never mentioned. Those are the ones that teach you something, and they are invisible without the written record, because memory quietly rewrites your old thesis to match the outcome.</p>

      <h2>Confirmation bias: everyone agrees with me, so I must be right</h2>

      <p>The moment you take a position, your reading habits change without your permission. You start clicking the analyst who likes your company. You linger on the bullish thread and scroll past the bearish one. You follow three more accounts that already agree with you.</p>

      <p>The failure is that each new agreement <em>feels</em> like fresh evidence when it is mostly an echo. Ten posts making the same argument are one argument, repeated. Meanwhile the disconfirming information, the reason the position might be wrong, is the only information that could actually change your decision, and it is exactly what you have filtered out.</p>

      <p><strong>Countermeasure.</strong> Go find the strongest bear case, not the dumbest one, and hold yourself to a real standard: can you state it well enough that someone who believes it would say you represented them fairly? If you cannot, you do not understand your own position yet; you only understand the flattering half of it.</p>

      <Callout variant="did-you-know">
        <p>Professional investment committees sometimes assign someone to argue the opposite side of a proposal on purpose, and rotate who does it. The point is not that the assigned sceptic is right. It is that a group which only hears agreement mistakes volume for evidence, and building the objection into the process is the only reliable way to get it said out loud.</p>
      </Callout>

      <h2>Anchoring, recency and herding</h2>

      <p>Anchoring is fixating on a number that feels meaningful and letting it stand in for analysis. Usually it is your purchase price. Sometimes it is a past high: “it traded at $80 last year, so $40 is half price.” The market has no record of what you paid and no obligation to return to any previous level. A stock at $40 that was $80 might be a bargain or might be a business in decline that is still too expensive. The old price does not distinguish those cases; only the current facts do.</p>

      <p>Recency bias is taking the last few months and extending them forever. After a strong run, permanence feels obvious. After a sharp fall, recovery feels impossible. Both feelings are the recent past being mistaken for the shape of the future.</p>

      <p>Herding is drawing comfort from the fact that lots of people agree with you. The uncomfortable structural point is that crowd agreement is most complete near extremes: at a top, nearly everyone who was going to buy already has, and at a bottom, nearly everyone who was going to sell already has. The consensus feels most reassuring at the moment it is least useful.</p>

      <h2>Sunk cost: how averaging down breaks your sizing</h2>

      <p>You bought at $80. It is now $40. Buying more brings your average cost to $60, and $60 sounds better than $80, so the action feels like progress.</p>

      <p>Watch what actually changed. Your average cost is an accounting fact about your own history. It has no effect on the company, and the only thing that genuinely changed is that you now own twice as many shares of something whose price move you have not explained. If the market is telling you something true about the business, you just doubled your exposure to being wrong.</p>

      <p>The quiet damage is to <Term k="position sizing">position sizing</Term>. Suppose you set a sensible limit of 5% of your portfolio per idea. You buy at $80 at exactly 5%. It falls by half, so the position is now around 2.6% of a portfolio that has also shrunk a bit. You buy the same number of shares again, which now costs half as many dollars, and you are back near 5%, but with double the shares, and a thesis that is weaker than it was on day one. Do it twice more and a single deteriorating idea is your largest holding. Nobody makes that decision consciously. It arrives one reasonable-sounding step at a time.</p>

      <p>Averaging down is not automatically wrong. It is defensible when the thesis genuinely still holds, when you can name what changed and why it is temporary, and when the additional purchase was planned before the fall, which is what <Term k="dollar cost averaging">dollar cost averaging</Term> into a broad index fund on a fixed schedule actually is. The failure mode is different: adding because selling would mean admitting the first purchase was a mistake.</p>

      <h2>The table you can actually use mid-decision</h2>

      <p>Names of biases are useless in the moment. What you need is the interior sensation, because that is the only part you have access to while it is happening.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Bias</th>
              <th>What it feels like from the inside</th>
              <th>What it makes you do</th>
              <th>Countermeasure</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>FOMO</td>
              <td>“I need to get in before it runs away.” Physical urgency; checking the price repeatedly; researching after deciding.</td>
              <td>Buy near local tops, oversized, with no exit plan.</td>
              <td>24-hour waiting rule; thesis written down before the app opens.</td>
            </tr>
            <tr>
              <td>Loss aversion</td>
              <td>“It is only a loss if I sell.” Relief when you take a small gain; dread when you open the losing position.</td>
              <td>Sell winners early, hold losers indefinitely.</td>
              <td>Pre-committed exit rules; ask “would I buy this today at this price?”</td>
            </tr>
            <tr>
              <td>Overconfidence</td>
              <td>“I am actually good at this.” Wanting to size up; finding your process slow and unnecessary.</td>
              <td>Trade bigger and more often right before conditions change.</td>
              <td>Decision journal written before outcomes, audited later.</td>
            </tr>
            <tr>
              <td>Confirmation bias</td>
              <td>Reading feels satisfying rather than uncomfortable. Everything you find agrees with you.</td>
              <td>Hold through real deterioration because you filtered out the warning.</td>
              <td>State the strongest bear case convincingly, out loud or in writing.</td>
            </tr>
            <tr>
              <td>Anchoring</td>
              <td>“It was $80, so $40 is cheap.” The old number keeps appearing in your reasoning.</td>
              <td>Buy declines that deserved to decline; refuse to sell below cost.</td>
              <td>Evaluate from today’s facts as if you held no position.</td>
            </tr>
            <tr>
              <td>Recency bias</td>
              <td>The current trend feels like a permanent condition rather than a period.</td>
              <td>Chase after runs; abandon a sound plan after a bad quarter.</td>
              <td>Look at longer history; write down what would end the trend.</td>
            </tr>
            <tr>
              <td>Herding</td>
              <td>Comfort. Everyone you follow is positioned the same way you are.</td>
              <td>Crowd into consensus trades near their extremes.</td>
              <td>Ask who is on the other side of this trade, and why.</td>
            </tr>
            <tr>
              <td>Sunk cost</td>
              <td>“I just need to lower my average.” Focus on your entry price rather than the business.</td>
              <td>Average down into deterioration until it dominates the portfolio.</td>
              <td>Hard per-idea size cap that additions are counted against.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>The structural fix: let your calm self vote</h2>

      <p>Notice that every countermeasure above is the same shape. None of them is “try harder to be rational.” Each one is a rule written down in advance, when nothing is at stake.</p>

      <p>That is the entire technique, and the reasoning behind it is simple. You are not one decision-maker; you are at least two. One of you reads slowly on a quiet afternoon, weighs both sides, and can hold a number like “a 50% loss needs a 100% gain” without flinching. The other one is awake at 2am watching a position gap down. The second one is going to show up eventually; you cannot train that away. A written rule is how the first one gets a vote in a meeting they are not present for.</p>

      <p>Keep the rules few and specific enough to be checkable. Maximum size per idea. A waiting period before any unplanned buy. An exit condition recorded at entry. A journal entry before the trade, not after. Vague intentions like “stay disciplined” do nothing, because at 2am you will feel disciplined and be wrong.</p>

      <Callout variant="real-talk">
        <p>Every person who reads this comes away thinking it describes other people. That reaction is not a sign that you are unusually self-aware; it is the overconfidence bias, arriving right on schedule, in a lesson about the overconfidence bias.</p>
        <p>Here is the part that is genuinely hard to accept: knowing about a bias does not remove it. Researchers have found these effects persist in people who study them for a living. Awareness gets you the vocabulary to name the mistake afterwards. Only process changes what you do while it is happening. If you finish this lesson with insight and no written rules, you have gained nothing that will survive contact with a real position.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="1. The decision: … 2. The bias I think was most active, and the specific feeling that gives it away: … 3. The one rule that would have slowed me down: …">
        <p>Think of the last financial decision you made quickly; it does not have to be a stock. A purchase you talked yourself into, a subscription, a bet with a friend, moving money because of something you saw online.</p>
        <p>Write three things. First, what you did and how much time passed between the impulse and the action. Second, which bias from the table was most active, and quote the sentence you actually said to yourself at the time. That sentence is your personal signature for this bias, and it is what you will recognise next time. Third, write the single rule that would have slowed you down enough to change the outcome. Make it specific and checkable: “wait 24 hours before any unplanned buy,” not “be more careful.”</p>
      </TryIt>

      <h2>What to carry out of this</h2>

      <p>If one idea survives from this lesson, make it this: your emotions are not a bug to be suppressed, they are a signal you have to route around, and the routing is done in writing when you are calm. Discipline is not a personality trait some people were issued. It is a set of decisions made in advance by someone who happened to be you on a better day.</p>

      <p>Start small. One rule about size, one about waiting, one about exits, plus a decision journal that takes ninety seconds per entry. Four honest sentences before a trade will do more for your results over the next decade than any indicator you could learn.</p>

      <p>The next lesson turns this inward-facing work outward, into risk management as a system: how much of your capital any single idea is allowed to touch, how to size a position so that being wrong is survivable rather than catastrophic, and why the investors who last are the ones who spent most of their attention on not losing.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
