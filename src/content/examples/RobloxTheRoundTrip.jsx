import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import StockExample from '../../components/ui/StockExample.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A stock rises 400% from its low and then falls 70% from its peak. Someone who bought at the low and never sold is:',
    options: [
      'Still up a lot, because 400% is bigger than 70%',
      'Roughly back where they started, because the fall applies to the much larger peak value',
      'Down, because percentage gains and losses cancel out',
      'Exactly break-even, always',
    ],
    answer: 1,
    explanation:
      'Percentages are not symmetric because they apply to different bases. A 400% gain turns $100 into $500. A 70% fall from $500 leaves $150. Still up, but nothing like the 400% that appeared on screen at the peak. This is why a gain you never realised is not the same as a gain you had.',
  },
  {
    prompt: 'The Roblox chart proves the company is badly run.',
    type: 'tf',
    answer: false,
    explanation:
      'A chart shows what the market paid, not how the business performed. Price fell because expectations reset, which can happen to a company whose revenue is still growing. Judging management from a price line is exactly the confusion the Intermediate track warned about: price is not value.',
  },
  {
    prompt: 'What is the most useful thing to decide before a position rises sharply?',
    options: [
      'The maximum price it could reach',
      'What would make you sell, written down in advance',
      'Which broker has the lowest fees',
      'Whether the company will still exist in twenty years',
    ],
    answer: 1,
    explanation:
      'You cannot control where a price goes. You can decide, while calm, what would make you take some off the table. Almost nobody who rode a chart like this down had a written exit; they had a feeling that it would keep going.',
  },
  {
    prompt: 'Volatility this large is unusual for an individual stock.',
    type: 'tf',
    answer: false,
    explanation:
      'It is normal, and that is the point of the track. Single companies routinely swing far harder than the market. What is unusual is a person who plans for it before it happens rather than discovering it live.',
  },
]

export default function RobloxTheRoundTrip({ moduleId }) {
  return (
    <>
      <p className="lead">
        Every number in this course so far has been invented, so the arithmetic stayed clean. Here is a
        real one. The chart below is live, pulled the moment you loaded this page, so the figures are
        whatever they actually are today rather than whatever they were when this was written.
      </p>

      <h2>Five years of Roblox</h2>

      <p>
        Roblox is a company most students actually know, which is why it makes a better teaching example
        than an industrial supplier you have never heard of. Look at the shape before you read anything
        else about it.
      </p>

      <StockExample
        ticker="RBLX"
        range="5y"
        caption="Roblox Corporation, five years of daily closes. The four figures below the chart are computed from that data, not typed in, so they update as the market does."
      />

      <p>
        The shape is a round trip. A long slide, then a powerful multi-year climb that took it to the
        highest price on the chart, and then a fall that gave back most of that climb. The reader who only
        saw the middle third of this chart would have concluded something completely different from the
        reader who sees all of it.
      </p>

      <h2>The arithmetic that catches people</h2>

      <p>
        Percentage gains and losses are not symmetric, because each one applies to a different starting
        number. Work a clean version of the same shape.
      </p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Stage</th>
              <th>What happens</th>
              <th>$100 becomes</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Buy near the low</td>
              <td>Starting point</td>
              <td>$100</td>
            </tr>
            <tr>
              <td>The climb</td>
              <td>Rises 400%</td>
              <td>$500</td>
            </tr>
            <tr>
              <td>The fall</td>
              <td>Drops 70% from the peak</td>
              <td>$150</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>
        That person is still up 50%, which is a perfectly good five years. But at the peak they were up
        400%, and the difference between those two numbers is not a market event. It is the absence of a
        decision. Nothing forced them to hold through the whole descent except not having decided
        beforehand what would make them stop.
      </p>

      <p>
        Now run it for the person who bought near the top, which is when a stock is most talked about and
        therefore when most people first hear of it. They took the 70% fall without the 400% climb.
        Recovering that requires a gain of over 230%, which is the recovery asymmetry from the
        Intermediate track appearing in a real chart rather than a table.
      </p>

      <Callout variant="real-talk" title="Why the top is where the crowd arrives">
        <p>
          A stock gets written about, posted about and recommended after it has already risen. That is
          what makes it newsworthy. So the moment a company is most visible to someone who does not follow
          markets is, structurally, close to the moment its price has run furthest. It is not a conspiracy;
          it is just how attention works, and it is why <Term k="fomo">FOMO</Term> reliably produces buying
          near tops.
        </p>
      </Callout>

      <h2>What the chart does not say</h2>

      <p>
        Be careful about the conclusion you draw. A falling price does not mean the company is failing, and
        this is where beginners consistently over-read a chart.
      </p>

      <p>
        Price is what the market currently pays for a claim on future profits. It moves when expectations
        about those future profits change, and expectations can reset hard while the business itself keeps
        growing. A company can add users and revenue every year and still see its share price halve,
        because the price already assumed it would add more.
      </p>

      <p>
        The reverse trap is just as common. A rising price is not evidence that a business is healthy. It
        is evidence that people are willing to pay more than they were, which is a fact about buyers rather
        than a fact about the company.
      </p>

      <Callout variant="warning" title="Do not turn this into a rule about Roblox">
        <p>
          This lesson is not saying anything about whether Roblox is a good or bad company, and nothing here
          is a suggestion to buy or avoid it. It is here because the shape of its chart teaches something
          clearly. A different five-year window would tell a different story, which is itself part of the
          lesson: the period you choose to look at changes the conclusion you reach.
        </p>
      </Callout>

      <h2>So what does "know when to get out" actually mean?</h2>

      <p>
        It does not mean predicting the top. Nobody does that reliably, and anyone who tells you they do is
        describing luck after the fact. It means deciding, in advance and in writing, what would change
        your mind. Concretely, that is three numbers written down before you buy:
      </p>

      <ol>
        <li>
          <strong>What would make you sell at a loss.</strong> A price, or a specific event, that tells you
          the reason you bought is no longer true.
        </li>
        <li>
          <strong>What would make you take some off the table.</strong> Not all of it. Selling a portion
          after a large rise converts a paper gain into a real one while leaving you exposed if it keeps
          going.
        </li>
        <li>
          <strong>How much you were willing to lose in the first place.</strong> The sizing decision, which
          is the only one of the three you fully control.
        </li>
      </ol>

      <p>
        Notice that none of those require you to be right about the future. They require you to have made a
        decision while you were calm, which is the only time anybody makes good ones about money.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="The two dates, roughly what the price was at each, and what you would have done…"
      >
        <p>
          Look at the chart above and find two moments: the highest point, and roughly a year before it.
          Imagine you had bought at that earlier moment and were sitting on a large gain at the peak.
        </p>
        <p>
          Write down what you honestly think you would have done, and then what you would want a written
          plan to have told you to do. If those two answers are different, that gap is the entire reason
          plans get written down in advance.
        </p>
      </TryIt>

      <h2>The one idea to take with you</h2>

      <p>
        A gain you never sold is not a gain. It is a number on a screen that the market can take back, and
        it usually does at least once. The people who keep some of a move like this are not the ones who
        predicted the top. They are the ones who decided in advance what would make them act.
      </p>

      <p>
        Next: the same treatment applied to GameStop, but deliberately not the famous week. The five years
        after it, which is the part almost nobody posts about.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
