import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'What is the single strongest argument for keeping a stable core?',
    options: [
      'Stable assets produce higher returns than speculative ones',
      'Losses and gains are not symmetric, so avoiding a catastrophic fall matters more than catching a spectacular rise',
      'Financial advisers require it',
      'Stable assets never fall in value',
    ],
    answer: 1,
    explanation:
      'A 50% fall needs a 100% gain to recover, and a 90% fall needs 900%. The stable core is not there to maximise returns. It is there to make sure you are still in the game to have more attempts.',
  },
  {
    prompt: 'A low P/E means a stock is cheap and a high P/E means it is expensive.',
    type: 'tf',
    answer: false,
    explanation:
      'A high P/E is the market pricing in growth; a low one is often the market pricing in decline, which is the value trap. A P/E only means something compared with the same company’s history and with direct competitors in the same industry.',
  },
  {
    prompt: 'A stock has a beta of 0.6. What does that tell you?',
    options: [
      'It is a safe investment',
      'It historically moved less than the market, which says nothing about company-specific risk',
      'It will fall less than the market in any future crash',
      'It is undervalued',
    ],
    answer: 1,
    explanation:
      'Beta is backward-looking and market-relative. A company awaiting one trial result or one court ruling can have a low beta and still be a coin flip, because its risk is idiosyncratic rather than market-driven. Low beta is not a synonym for safe.',
  },
  {
    prompt: 'Owning five different technology companies is well diversified.',
    type: 'tf',
    answer: false,
    explanation:
      'Sectors move together, so that is closer to one bet wearing five costumes. Real diversification spreads across industries and asset types, which is why a single broad index fund often does more of the job than a carefully assembled handful of favourites.',
  },
]

export default function Recap({ moduleId }) {
  return (
    <>
      <p className="lead">
        The Beginner track taught you what the pieces are. This track taught you how to sort them. Here is
        the whole argument in one page before the course does something different with it.
      </p>

      <h2>What you actually learned</h2>

      <p>
        <strong>Stable and unstable are ends of a spectrum, not two boxes.</strong> What separates them is
        the range of likely outcomes: size, predictable demand, profitability today, a manageable balance
        sheet and a long history on one end; small size, unprofitability, single-product concentration and
        story-driven valuation on the other.
      </p>

      <p>
        <strong>The metrics, and where each one lies to you.</strong>{' '}
        <Term k="beta">Beta</Term> is backward-looking and blind to company-specific risk.{' '}
        <Term k="pe ratio">P/E</Term> is meaningless without a peer group.{' '}
        <Term k="eps">EPS</Term> can be lifted by buybacks without the business earning more.{' '}
        <Term k="debt to equity">Debt-to-equity</Term> varies so much by industry that cross-industry
        comparison tells you nothing. Charts, moving averages and{' '}
        <Term k="rsi">RSI</Term> describe what already happened rather than what will.
      </p>

      <p>
        <strong>Diversification is the one free thing.</strong> You cannot diversify away market-wide risk,
        but company-specific risk you can, cheaply, with one order. An{' '}
        <Term k="etf">ETF</Term> tracking a broad index is hundreds of companies, and a{' '}
        <Term k="expense ratio">expense ratio</Term> difference of well under one percent compounds into
        real money over decades.
      </p>

      <p>
        <strong>The stable core is not a suggestion.</strong> Recovery maths is asymmetric, and that
        asymmetry is the whole reason avoiding catastrophic losses matters more than catching spectacular
        gains.
      </p>

      <Callout variant="real-talk" title="The thing most people take away wrongly">
        <p>
          Unstable does not mean bad, and stable does not mean safe. Some volatile companies have rewarded
          holders enormously; some solid ones have quietly gone nowhere for a decade. What changes is the{' '}
          <em>distribution</em> of outcomes, and therefore the appropriate{' '}
          <Term k="position sizing">position size</Term>. Stability is an input to how much you hold, not a
          verdict on quality.
        </p>
        <p>
          If you finish this track believing "high risk, high reward" is a strategy, re-read it. That phrase
          describes compensation for a wider range of outcomes, not a causal link. Plenty of high-risk
          positions deliver only the risk.
        </p>
      </Callout>

      <h2>What comes next, and why it is different</h2>

      <p>
        Everything so far has used invented numbers, deliberately, so the arithmetic stayed clean and you
        could check it. That has a cost: hypothetical charts always behave.
      </p>

      <p>
        The <strong>Examples</strong> track drops that. It pulls real five-year price histories of real
        companies, live, and asks what they actually show. You will see a stock that rose enormously and
        gave nearly all of it back, the years after the GameStop squeeze that nobody posts about, and two
        deliberately boring charts next to them.
      </p>

      <p>
        The point is not to admire or condemn any company. It is that a real chart contains things a
        constructed example never does: the periods where nothing happens, the falls that last long enough
        to break people, and the uncomfortable fact that the same five years produced completely different
        outcomes depending only on when somebody happened to buy.
      </p>

      <p>
        After that, the <strong>Hard</strong> track deals with options, leverage and speculation, and every
        sizing rule it gives you traces straight back to the recovery maths in this one.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="Your triage of one real company, and where it landed…"
      >
        <p>
          Before moving on, run the five-question triage from the stable-vs-unstable lesson on any company
          you find interesting: is it profitable today, what is the market cap, what is its beta, does one
          product or customer dominate, and would it still have customers in a recession?
        </p>
        <p>
          Write down where it landed and, more importantly, what position size that placement implies. Keep
          it. The Examples track will show you what a chart of something in that category actually looks
          like.
        </p>
      </TryIt>

      <h2>One thing to carry forward</h2>

      <p>
        No metric on its own is a signal. Each one narrows the question and tells you what to investigate
        next. The moment a number starts feeling like an answer rather than a prompt, you have stopped
        analysing and started justifying.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
