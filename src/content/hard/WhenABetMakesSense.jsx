import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'You put 1% of a $10,000 portfolio into a speculative position that could plausibly 5x. If it goes to zero, and if it hits the 5x, what happens to the portfolio in each case?',
    options: [
      'Down 1% if it fails, up 5% if it works',
      'Down 1% if it fails, up 4% if it works',
      'Down 10% if it fails, up 50% if it works',
      'Down 1% if it fails, up 400% if it works',
    ],
    answer: 1,
    explanation: 'You risk $100. Total loss costs you $100, which is 1% of the portfolio. A 5x turns $100 into $500, a gain of $400, which is 4% of the portfolio. Option A is the classic slip: a 5x on the position is a 4x GAIN, not a 5x gain, because your original stake is included in the 5x.',
  },
  {
    prompt: 'Which of these is closest to a real thesis rather than a vibe?',
    options: [
      'Everyone in my group chat is buying it and the chart looks like it is about to run.',
      'It is down 70% from its high, so it has to bounce eventually.',
      'The company makes industrial sensors, the market appears to be pricing in flat revenue, I think the new contract announced last quarter changes that, the next earnings report is the test, and three straight quarters of flat revenue means I am wrong.',
      'A well-known investor bought a large stake, so the work is already done.',
    ],
    answer: 2,
    explanation: 'Only the third one names the business, states what the market currently expects, says what you believe is different, gives a dated test, and defines what would prove you wrong. The others cannot be falsified, so there is nothing to be right or wrong about.',
  },
  {
    prompt: 'A bet that passes all five conditions in this lesson is, by definition, a bet you should expect to make money on.',
    type: 'tf',
    answer: false,
    explanation: 'The conditions control the cost of being wrong; they do not raise your probability of being right. For most speculative positions, the single most likely outcome is still a loss. A defensible bet is a loss you have chosen in advance, not a profit you have earned in advance.',
  },
  {
    prompt: 'What is the sharpest practical test that a speculative position is sized too large?',
    options: [
      'It is more than 1% of your portfolio.',
      'You would be sad if it went to zero.',
      'A total loss of the position would change your sleep, your behaviour, or your other decisions.',
      'It is the largest single holding you own.',
    ],
    answer: 2,
    explanation: 'Sadness is fine and unavoidable. The line is behavioural: if losing it all would make you check the price hourly, skip your regular contribution, or chase the loss back, the position is controlling you rather than the other way around. A fixed percentage is a useful default, but the behavioural test is the one that actually binds.',
  },
  {
    prompt: 'The difference between investing and gambling is that investing involves low risk and gambling involves high risk.',
    type: 'tf',
    answer: false,
    explanation: 'Risk level is not the dividing line — plenty of legitimate investments are extremely volatile. The difference is structural: a reasoned edge, a size you have chosen deliberately, and a plan written before entry, versus an outcome decided by chance and a position taken for the feeling you are hoping to get.',
  },
]

export default function WhenABetMakesSense({ moduleId }) {
  return (
    <>
      <p className="lead">A course that only ever says “don’t” has not taught you anything. You are going to be twenty-two one day, with a brokerage app open and an idea you cannot stop thinking about, and “the lesson said no” will not survive that moment. So let’s ask the question that actually helps: not whether speculation is allowed, but under exactly what conditions it is defensible.</p>

      <p>Defensible is a deliberately cold word. It does not mean smart, and it definitely does not mean likely to work. It means that if the position goes to zero — which is the base case for most speculative bets — you could explain to a clear-headed version of yourself why taking it was a reasonable use of a small, pre-decided amount of money. Five conditions get you there. Miss any one, and what you have is a gamble wearing a thesis as a costume.</p>

      <h2>Condition 1: the shape is genuinely asymmetric</h2>

      <p>The first condition has nothing to do with how good the story is. It is arithmetic. An <Term k="asymmetric bet">asymmetric bet</Term> is one where the downside is capped, small and known in advance, while the plausible upside is several times larger. The key word is plausible. Anyone can imagine a 100x; the question is whether a specific, ordinary chain of events gets you to the upside without requiring a miracle.</p>

      <KeyTerm term="Asymmetric Bet" />

      <p>Work it through with numbers. Suppose you have a $10,000 portfolio and you commit 1% — $100 — to a position you think could plausibly reach five times its current price.</p>

      <ol>
        <li>It fails completely. You lose $100. Your portfolio goes from $10,000 to $9,900, a 1% hit. Annoying, forgettable, invisible in a year.</li>
        <li>It works. Your $100 becomes $500. That is a $400 gain, or 4% of the portfolio.</li>
        <li>The ratio: you risked 1% of your net worth to reach for 4%. Four to one.</li>
      </ol>

      <p>Notice what that means about how often you need to be right. If the shape is four to one, you can be wrong four times out of five and roughly break even. That is the entire case for speculation at small size, and it is a real case. But notice also what it does not say: it does not say the story is good, or that this particular company will do anything at all. The shape is what makes the position defensible. The story is just the reason you picked this one instead of another.</p>

      <Callout variant="warning">
        <p>Asymmetry breaks the instant leverage enters. Borrowed money, margin, and most <Term k="option">option</Term> positions can lose more than you put in, or lose all of it on a schedule you do not control. The moment your downside is no longer capped at the amount you deliberately committed, the entire argument in this lesson stops applying.</p>
      </Callout>

      <h2>Condition 2: a real thesis, not a vibe</h2>

      <p>Here is the test I find most useful, because it is impossible to fake. Write your reasoning down in full sentences before you buy. Then read it back and ask: could this be proven wrong?</p>

      <h3>Two write-ups, side by side</h3>

      <p>The first: “Everyone is talking about this one. The chart looks ready. It has been beaten down for months and the sentiment is turning.” Read that again and try to find the sentence that could turn out to be false. There isn’t one. Sentiment turning is not an observable event with a date. The chart looking ready is a description of your own mood rendered as geometry. This is not a bad thesis; it is not a thesis at all.</p>

      <p>The second: “This company makes cooling systems for data centres. Revenue grew about 30% last year. The stock is priced, as far as I can tell, as though that growth stops. I think it does not stop, because two of its three largest customers publicly announced capacity expansions that ship next year. The test is the Q3 report in October: if orders are flat, my read on the customer expansion is wrong. If the company loses either of those customers, I am wrong immediately and I sell.”</p>

      <p>The second one might still be completely mistaken. That is fine — that is the point. It names the business, states what the market is currently pricing in, identifies what specifically you believe is different, points to a dated <Term k="catalyst">catalyst</Term> that will test it, and defines in advance what would prove you wrong. Falsifiability is the requirement. If no observable event could ever demonstrate your error, you have not made an argument, and you will not be able to tell later whether you were right or lucky.</p>

      <Callout variant="note">
        <p>A useful side effect: writing the thesis down kills maybe half of your ideas before they cost you anything. Plenty of positions feel compelling right up until the moment you have to say, in writing, what the market is missing. If you cannot finish that sentence, the market probably is not missing anything.</p>
      </Callout>

      <h2>Condition 3: an allocation small enough to be wrong</h2>

      <p>You already know the rule from the last lesson on <Term k="position sizing">position sizing</Term>: a speculative position sits at 1–5% of your total portfolio, and the total of all such positions stays inside a slice you decided on in advance. That is a good default. Here is the sharper version, and it is the one that actually binds.</p>

      <p>If a total loss of this position would change your behaviour, your sleep, or any of your other decisions, it is too big. Not “would upset you” — losing money always stings, and pretending otherwise is how people talk themselves into ignoring the feeling. The test is behavioural. Would a zero make you check quotes during class? Would it make you skip a month of your regular contributions? Would it make you put more in to win it back? If yes to any of those, size down until the answer is no, or do not take the position.</p>

      <p>Size is the mechanism that converts a gamble into an experiment. Same idea, same odds, same probability of a zero — but at 1%, a loss is information you paid a small tuition for, and at 25%, a loss is an event that reshapes your finances and your judgement for years. Nothing about the company changed between those two versions. Only the number you typed into the order box.</p>

      <h2>Condition 4: an exit decided before entry</h2>

      <p>Write down two numbers, or two conditions, before you buy. What would make you sell at a loss, and what would make you take profits.</p>

      <p>The sell-at-a-loss trigger should ideally be thesis-based rather than price-based: “I sell if the October report shows flat orders” is better than “I sell if it drops 30%,” because a random 30% move tells you about volatility and a flat quarter tells you that you were wrong. The take-profits trigger is the one almost nobody writes, and it is the one that most often turns a winning speculation into a losing one. Decide now: at a 3x, do you sell it all? Sell half and let the rest run on house money? Both are reasonable. Choosing one at 3am while the price is moving is not.</p>

      <Callout variant="real-talk">
        <p>You will not think clearly once money is moving. Not because you are weak — because that is what happens to everyone. A position up 240% produces a genuine physical response, and so does one down 60%, and in both states the plan you wrote calmly two months ago is smarter than the plan you are inventing right now.</p>
        <p>The written plan is not a rule you obey out of discipline. It is a message from a version of you who had no money on the line and could therefore actually think.</p>
      </Callout>

      <h2>Condition 5: the boring core already exists</h2>

      <p>This is the condition people skip, and skipping it inverts the whole structure. Speculation is what you do with a deliberate slice after the foundation is built — an emergency buffer you can actually reach, a regular contribution into something broad and <Term k="diversification">diversified</Term>, and a plan you would still be running if you never took a single speculative position in your life.</p>

      <p>The reason is not moral. It is that the core is what makes the small bet survivable and, more importantly, what makes it optional. If your speculative position is the only thing standing between you and your goals, you will size it wrong, hold it too long, and refuse to sell at a loss, because you need it to work. Need is the single most expensive input in investing. A person who does not need the bet to work can let it fail, and letting it fail cheaply is the entire skill.</p>

      <h2>Run the checklist</h2>

      <p>Five conditions plus one honesty question. Every row has to pass. This is not a scoring system where four out of six is good enough.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Question</th>
              <th>Pass</th>
              <th>Fail</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Is the downside capped and the plausible upside several times larger?</td>
              <td>Capped at what I put in; a realistic path to 3x or more</td>
              <td>Leverage, margin, or an upside that requires a miracle</td>
            </tr>
            <tr>
              <td>Can I write a thesis that could be proven wrong?</td>
              <td>Named business, stated expectation, dated test, defined failure</td>
              <td>Momentum, sentiment, chart shape, or someone else’s conviction</td>
            </tr>
            <tr>
              <td>Would a total loss change my behaviour or my sleep?</td>
              <td>No — it is a rounding error in my plan</td>
              <td>Yes, or I would have to check the price daily to feel okay</td>
            </tr>
            <tr>
              <td>Have I written my exit before entering?</td>
              <td>Both triggers on paper: sell-at-loss and take-profit</td>
              <td>“I will know when the time comes”</td>
            </tr>
            <tr>
              <td>Is my boring core already in place and funded?</td>
              <td>Buffer exists, regular contributions running</td>
              <td>This bet is the plan, or it is funding the plan</td>
            </tr>
            <tr>
              <td>Am I doing this because of something I read this week?</td>
              <td>The idea is at least a few weeks old and survived the wait</td>
              <td>I found it in a feed and I am worried about missing it</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>That last row is the cheapest filter in investing. Ideas that arrive with urgency attached are almost always ideas someone else is already positioned in. Waiting two weeks costs you nothing on a genuine multi-year thesis and saves you almost everything on a <Term k="fomo">FOMO</Term> trade, because the fear of missing out does not survive two weeks of silence.</p>

      <h2>When it is more defensible than it looks</h2>

      <p>There are real situations where a small speculative position holds up better than the sceptical case suggests, and pretending otherwise would be dishonest.</p>

      <ul>
        <li><strong>A genuinely long horizon.</strong> If you are seventeen and this money has no job for thirty years, a total loss costs you the money and very little else. Time does not improve your odds, but it does absorb the outcome.</li>
        <li><strong>Money that is truly discretionary.</strong> Not rent, not tuition, not the emergency buffer — money whose alternative use was something you would have enjoyed and forgotten.</li>
        <li><strong>A domain you understand unusually well from outside finance.</strong> If you have spent four years deep in a niche — a sport, a game engine, lab equipment, a manufacturing process your family works in — you may genuinely notice a shift before the market prices it. Analysts cannot be experts in everything. This is a real edge, and it is also the one people most often imagine they have. Being a customer of a company is not the same as understanding its economics.</li>
        <li><strong>The education itself.</strong> Having real skin in the game at a tiny size teaches you things no simulator can. You learn how you actually behave when a position is down 40% — and finding that out with $80 at stake at seventeen is enormously cheaper than finding it out with $80,000 at forty.</li>
      </ul>

      <Callout variant="did-you-know" title="The house-money illusion">
        <p>People treat gains from a speculative win as though the money is somehow less real than the money they contributed. That is why so many winning bets get given back: the position doubles, the profit stops feeling like money, and the sizing rules quietly stop applying to it.</p>
        <p>Every dollar in your account is identical regardless of where it came from. Once a bet works, the new balance is simply your balance, and it deserves the same rules as everything else you own.</p>
      </Callout>

      <h2>The counter-case, stated fairly</h2>

      <p>Now the part that keeps this lesson honest. Even when all five conditions hold — clean asymmetry, falsifiable thesis, tiny size, written exits, stable core — the single most likely outcome is still that you lose the money. Most speculative theses are wrong. The four-to-one shape does not make you right more often; it makes being wrong survivable. Those are completely different things, and conflating them is how people end up thinking of speculation as a strategy rather than a cost.</p>

      <p>So: a defensible bet is not a good bet. It is a bet whose cost you have deliberately chosen. You have looked at the likely outcome, priced it, decided it is affordable, and accepted it in advance. If you cannot say that sentence honestly about a position, the checklist is telling you something and the correct response is to walk away, not to argue with it.</p>

      <Callout variant="real-talk">
        <p>The line between investing and gambling is not the risk level. Some legitimate investments are wildly volatile, and some casino games have tiny stakes. The difference is structural: investing means a reasoned edge you can articulate, a size you chose deliberately, and a plan written before you entered. Gambling means an outcome determined by chance and a position taken because of a feeling you are hoping to get.</p>
        <p>Which means you can gamble on a blue-chip stock and invest in something speculative. It depends entirely on what is in your head and on your paper, not on the ticker.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Name the idea, then go condition by condition. Be specific about the ones it fails — that is the useful part.">
        <p>Take one speculative idea you have actually considered — a company, a sector, anything you have thought about buying but have not. Run it through all five conditions in writing, plus the “did I read about it this week” question.</p>
        <p>Look up the real numbers before you write: pull the company’s current price, market cap and last annual revenue from Yahoo Finance or its investor-relations page. Then write, in your own words, what the market appears to be pricing in and what you believe is different. Finish with the honest part: which conditions does your idea fail, and by how much? An idea that fails three of five is a completely normal result and a better outcome than one you talked yourself into.</p>
      </TryIt>

      <h2>What to carry out of this</h2>

      <p>Speculation is defensible when it is small, structured, written down and optional — and it stops being defensible the moment any one of those four words falls away. The conditions in this lesson are not there to make you money. They are there to make sure that when you are wrong, and you will be wrong, the cost was a number you chose rather than a number that happened to you.</p>

      <p>If you remember one thing: the shape of the bet, not the strength of the story, is what makes it defensible. Stories are free and infinitely available. A capped downside sized at 1% of your portfolio is a structural fact that holds even when the story turns out to be nonsense.</p>

      <p>Next up is the closing lesson of the Hard track, where all of this gets assembled into a single written plan: how the speculative slice sits alongside the core, how to review your positions on a schedule instead of on impulse, and how to keep a record of your decisions so that a year from now you can tell the difference between a good process and a lucky outcome.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
