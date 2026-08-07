import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'What is the one thing you fully control as an investor?',
    options: [
      'Whether your analysis turns out to be right',
      'How much it costs you to be wrong',
      'When the market falls',
      'Which companies succeed',
    ],
    answer: 1,
    explanation:
      'You cannot control outcomes. You can always control position size, and that is what decides whether a bad outcome is a dent or an ending. Every rule in the Hard track reduces to this one.',
  },
  {
    prompt: '"High risk, high reward" means taking more risk will get you a higher return.',
    type: 'tf',
    answer: false,
    explanation:
      'It means you must be offered more to accept a wider range of outcomes. Risk does not cause reward. Plenty of high-risk positions deliver only the risk, and the phrase has probably cost more beginners money than any other in investing.',
  },
  {
    prompt: 'An option buyer is right about the direction and still loses everything. What happened?',
    options: [
      'Their broker made an error',
      'The move was too small or too slow, so the contract expired worthless',
      'Options cannot profit from correct predictions',
      'They forgot to exercise',
    ],
    answer: 1,
    explanation:
      'A buyer needs direction, magnitude and timing to cooperate at once, which is three independent ways to be wrong. Time value erodes every day, so being right eventually is indistinguishable from being wrong.',
  },
  {
    prompt: 'What most reliably protected people in every failure case this course examined?',
    options: [
      'Better research',
      'Selling quickly at the first sign of trouble',
      'Position sizing decided before the trade',
      'Diversifying across several speculative names',
    ],
    answer: 2,
    explanation:
      'Research does not defend against fraud, as Enron showed, and it does not defend against arriving late, as GameStop showed. Several speculative names in one sector move together. Only sizing, decided in advance, worked in every case.',
  },
  {
    prompt: 'Finishing this course means you are ready to trade options.',
    type: 'tf',
    answer: false,
    explanation:
      'It means you can read an option chain and understand what you would be buying, which is different. The most defensible conclusion from the Hard track is that most people should keep speculation to a small deliberate sleeve or skip it entirely, and that is a legitimate outcome of having read it.',
  },
]

export default function Recap({ moduleId }) {
  return (
    <>
      <p className="lead">
        That is the whole course. Four tracks, and underneath them a single argument that is worth stating
        plainly now that you have all the pieces.
      </p>

      <h2>What the Hard track established</h2>

      <p>
        <strong>The instruments are not mysterious, and that is the problem.</strong> Penny stocks,{' '}
        <Term k="option">options</Term>, leveraged ETFs and meme stocks are all comprehensible in an
        afternoon. Understanding the mechanism is easy; surviving it is not, and confusing the two is how
        people get hurt.
      </p>

      <p>
        <strong>Expected value, not win rate.</strong> Being right nine times out of ten can still lose
        money if the tenth outcome is large enough. Any claim about a strategy that reports how often it
        wins, without the size of the wins and losses, is telling you nothing.
      </p>

      <p>
        <strong>Position sizing is the whole game.</strong> Risking 2% survives ten consecutive losses with
        about 82% of the account intact. Risking 50% is finished after two. Nothing you learn about a
        company changes that arithmetic.
      </p>

      <p>
        <strong>The psychology is not optional.</strong>{' '}
        <Term k="fomo">FOMO</Term> reliably produces buying near tops.{' '}
        <Term k="loss aversion">Loss aversion</Term> produces selling winners and holding losers.
        Overconfidence turns a rising market into evidence of skill. Knowing about a bias does not remove
        it; only written rules made in calm conditions do.
      </p>

      <h2>The argument the whole course was making</h2>

      <p>
        Every track was approaching the same claim from a different direction.
      </p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Track</th>
              <th>What it was really arguing</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Beginner</td>
              <td>Behind every ticker is a business, and price is only what two people last agreed on</td>
            </tr>
            <tr>
              <td>Intermediate</td>
              <td>Outcomes have a range, and the width of that range is what you are sizing against</td>
            </tr>
            <tr>
              <td>Examples</td>
              <td>Real charts fall further and for longer than constructed ones, and timing decides volatile outcomes</td>
            </tr>
            <tr>
              <td>Hard</td>
              <td>You cannot control being right, so control what being wrong costs</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>
        Which reduces to one sentence: <strong>survive first, and let time do the compounding</strong>. Not
        because caution is virtuous, but because the arithmetic of recovery is asymmetric and the person
        still holding after a bad decade is the one who ends up ahead.
      </p>

      <Callout variant="warning" title="The sentence this course spent 27 lessons arguing against">
        <p>
          "High risk, high reward." It is the most repeated phrase in retail investing and it is a
          misreading. Higher expected return is <em>compensation</em> for accepting a wider range of
          outcomes; risk does not produce reward. If it did, the reward would not be uncertain, and it would
          not be a risk.
        </p>
        <p>
          Anyone who tells you a position is good <em>because</em> it is risky has the logic backwards, and
          that includes the version of you that will eventually want to believe it.
        </p>
      </Callout>

      <h2>An honest word on what to do now</h2>

      <p>
        This course cannot tell you what to buy, and would be wrong to try. What it can say is what the
        material in it supports.
      </p>

      <p>
        The unglamorous conclusion is that for most people, most of the time, a broad diversified core held
        for a very long time does the overwhelming majority of the work, and the interesting part of a
        portfolio should be small enough that being wrong about it changes nothing important. The Hard track
        is not an argument for speculating. It is what you need in order to decide, with your eyes open,
        whether to speculate at all, and deciding not to is a perfectly good outcome of having read it.
      </p>

      <p>
        Before any of that, three things come first and none of them involve a ticker: no high-interest
        debt, a cash cushion you do not touch, and money you genuinely will not need for at least five
        years. If those are not true, the correct move is not a better stock pick.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="Your rules, in your own words, written before you need them…"
      >
        <p>
          Write your own investing rules, in your own words, in under ten lines. What proportion sits in
          something boring, what is the most you would ever put in one speculative idea, what would make you
          sell, and what would make you add.
        </p>
        <p>
          Date it. The only reason those rules are worth anything is that you wrote them now, calmly, rather
          than in the middle of a fall. Come back and read them the first time something you own drops 30%.
        </p>
      </TryIt>

      <h2>Where to go from here</h2>

      <p>
        Use the <strong>Simulator</strong>. Pull real charts in the Market Explorer, build a portfolio and
        look at its concentration, price out an options trade and see the break-even you would need. Ask the
        AI Advisor about anything here that stayed fuzzy.
      </p>

      <p>
        Then go and read a company's actual annual report, particularly its Risk Factors section, where a
        business is legally obliged to argue against itself. Twenty minutes there will teach you more than
        any amount of scrolling.
      </p>

      <p>
        And if you take one thing from all of this: the single most profitable decision most people ever
        make is the boring one they make in their twenties, and then leave alone.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
