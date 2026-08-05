import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import RiskProfile from '../../components/ui/RiskProfile.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'What is the difference between risk tolerance and risk capacity?',
    options: [
      'They are two names for the same thing',
      'Tolerance is how much loss you can emotionally handle; capacity is how much your circumstances can absorb',
      'Tolerance applies to stocks, capacity applies to bonds',
      'Capacity is set by your broker; tolerance is set by you',
    ],
    answer: 1,
    explanation:
      'Tolerance is psychological: what you can sit through without selling. Capacity is arithmetic: what your time horizon, income and obligations can actually absorb. When they disagree, capacity wins, because no amount of confidence turns money you need next year into money you can risk.',
  },
  {
    prompt: 'A questionnaire says you are Aggressive. That means you should hold mostly speculative positions.',
    type: 'tf',
    answer: false,
    explanation:
      'A profile describes how much volatility you can probably live with. It says nothing about which holdings are sensible. An aggressive profile with a long horizon usually still points at broad index funds doing the heavy lifting, with speculation kept to a small deliberate sleeve.',
  },
  {
    prompt: 'Why is a risk profile measured during a calm market unreliable?',
    options: [
      'Markets are closed during calm periods',
      'Questionnaires expire after twelve months',
      'Almost everyone overestimates their tolerance until they have actually watched real money fall',
      'Calm markets change the mathematics of drawdown recovery',
    ],
    answer: 2,
    explanation:
      'Predicting your own behaviour under stress is something humans are reliably bad at. "I would hold through a 30% drop" is cheap to say and expensive to discover. The only real test is having done it, which is why experience is one of the questions.',
  },
  {
    prompt: 'You have a 15-year horizon but no emergency savings at all. What does that combination mean?',
    options: [
      'The long horizon cancels out the missing cushion',
      'Your capacity is lower than your horizon suggests, because any surprise expense forces you to sell',
      'You should hold more speculative positions to build the cushion faster',
      'Nothing, emergency savings are unrelated to investing',
    ],
    answer: 1,
    explanation:
      'A long horizon only helps if you can actually leave the money alone for that long. With no cushion, a broken laptop or a lost job turns into a forced sale, quite possibly at the worst moment. The cushion is what makes the horizon real.',
  },
  {
    prompt: 'Your risk profile should be reassessed after a large market drop.',
    type: 'tf',
    answer: true,
    explanation:
      'A crash is the only honest test of tolerance you will ever get. How you actually behaved, rather than how you predicted you would, is far better data than any questionnaire. It is also the moment your circumstances may genuinely have changed.',
  },
]

export default function KnowYourRiskProfile({ moduleId }) {
  return (
    <>
      <p className="lead">
        Two people can be handed the same portfolio and have completely different experiences of it. One
        checks it twice a year and forgets about it. The other cannot sleep during a bad week and sells at
        the bottom. The portfolio was never the variable.
      </p>

      <h2>Two different questions that get confused</h2>

      <p>
        Almost every conversation about risk collapses two separate things into one word, and separating
        them is the whole point of this lesson.
      </p>

      <p>
        <strong>Risk tolerance</strong> is psychological. It is how much of a fall you can watch without
        doing something destructive. It is about temperament, experience and how much you check your phone.
      </p>

      <p>
        <strong>Risk capacity</strong> is arithmetic. It is how much loss your actual circumstances can
        absorb before something breaks. It is set by your time horizon, whether you have money coming in,
        whether you have a cash cushion, and what the money is eventually for.
      </p>

      <KeyTerm term="Volatility" />

      <p>
        These two often disagree, and when they do, capacity wins. A confident nineteen-year-old with a
        thirty-year horizon has enormous capacity. That same person with tuition due in eight months has
        almost none for that particular money, no matter how relaxed they feel about volatility. Feelings do
        not change deadlines.
      </p>

      <Callout variant="real-talk" title="The uncomfortable version">
        <p>
          Nearly everyone rates themselves as more tolerant than they turn out to be. Saying "I would hold
          through a 30% drop" costs nothing in a calm market. Actually watching a third of your money
          disappear over four months, while people online explain that this time it is different, is a
          completely different experience.
        </p>
        <p>
          This is not a character flaw. Predicting your own behaviour under stress is something humans are
          simply bad at. It is why the questionnaire below asks whether you have actually lived through a
          crash, and why an untested Aggressive result should be treated as a guess.
        </p>
      </Callout>

      <h2>Work out where you sit</h2>

      <p>
        Answer these honestly rather than aspirationally. Nobody sees the result, nothing is uploaded, and a
        flattering answer only costs you accuracy. Your answers save in this browser so you can come back
        after a bad month and see whether they changed.
      </p>

      <RiskProfile />

      <h2>What the result is actually for</h2>

      <p>
        A profile does not tell you what to buy. It tells you{' '}
        <strong>how much volatility to build into the portfolio</strong>, which is a different and much more
        useful question. Two people can own the identical broad index fund and be in completely different
        situations because one has 20% of their money in it and the other has 95%.
      </p>

      <p>Concretely, the result should influence three decisions:</p>

      <ol>
        <li>
          <strong>How much sits in stocks at all.</strong> Money needed within a few years generally should
          not, regardless of profile.
        </li>
        <li>
          <strong>How large the stable core is</strong> relative to everything else. The Intermediate track
          builds the full argument for why that core is non-negotiable.
        </li>
        <li>
          <strong>How big any single speculative position can be.</strong> This is the number the Hard track
          turns into an actual rule.
        </li>
      </ol>

      <Callout variant="warning" title="A profile is not permission">
        <p>
          Scoring Aggressive does not mean speculation is now a good idea. It means you could probably
          tolerate a volatile portfolio without panic-selling. Those are different claims. A high tolerance
          combined with no research and no <Term k="position sizing">position sizing</Term> is not an
          investing strategy, it is just a higher tolerance for losing money.
        </p>
      </Callout>

      <h2>The four things that move your profile most</h2>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Factor</th>
              <th>Pushes you conservative</th>
              <th>Pushes you aggressive</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Time horizon</td>
              <td>Money needed within 2 to 5 years</td>
              <td>Decades before you touch it</td>
            </tr>
            <tr>
              <td>Cash cushion</td>
              <td>No emergency savings, so a surprise forces a sale</td>
              <td>Several months of expenses set aside separately</td>
            </tr>
            <tr>
              <td>Income</td>
              <td>Nothing more to add; this is all there is</td>
              <td>Reliable ability to keep adding on a schedule</td>
            </tr>
            <tr>
              <td>Tested experience</td>
              <td>Never held through a real fall</td>
              <td>Held, and kept buying, through a genuine crash</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>
        Notice that three of those four have nothing to do with how brave you feel. That is the point.
        Capacity is mostly circumstance, and circumstance is checkable.
      </p>

      <Callout variant="did-you-know">
        <p>
          The single most common reason a young investor sells at the bottom is not fear of the market. It is
          needing the money. A cash cushion held completely separately is what converts a paper loss into
          something you can simply ignore, which is why it appears in a questionnaire about risk rather than
          in one about budgeting.
        </p>
      </Callout>

      <h2>Your profile is not permanent</h2>

      <p>
        Reassess after anything that changes the arithmetic: a new job, a new deadline, a large expense, or
        the end of a long horizon. And reassess after every serious market fall, because that is the only
        honest test of tolerance you will ever be given. What you actually did during a crash is far better
        evidence than what you predicted you would do before one.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="Your result, the answer you least liked giving, and what you would change…"
      >
        <p>
          Write down the profile you scored, then answer two things. First: which single question did you
          most want to answer differently from the truth? Second: what would have to change in your life for
          your score to move up one band, and is that change a real plan or just a hope?
        </p>
      </TryIt>

      <h2>The one idea to take with you</h2>

      <p>
        Your risk profile is not a label and it is not a permission slip. It is the input that decides{' '}
        <strong>how much</strong>, and how much is the only variable you fully control. You cannot control
        whether a company succeeds. You can always control whether being wrong about it matters.
      </p>

      <p>
        Next up: the capstone of this track, where all of it becomes concrete. A complete walkthrough of
        actually buying your first share, from the three things that need to be true before you start to
        what to do in the first month afterwards.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
