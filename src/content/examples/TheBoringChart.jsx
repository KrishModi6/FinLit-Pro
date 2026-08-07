import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import StockExample from '../../components/ui/StockExample.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'Why does a broad index fund have a much smaller worst fall than either single stock in this track?',
    options: [
      'Because index funds are guaranteed by the government',
      'Because one company failing is a rounding error inside hundreds of companies',
      'Because index funds do not hold risky companies',
      'Because their prices are averaged monthly',
    ],
    answer: 1,
    explanation:
      'A fund holding hundreds of companies cannot be destroyed by any one of them going wrong. It can still fall, because market-wide risk affects everything at once, but the company-specific risk that produced the two charts before this one is diversified away.',
  },
  {
    prompt: 'The boring chart proves index funds cannot lose money.',
    type: 'tf',
    answer: false,
    explanation:
      'Look at the worst-fall figure under the chart. It is real and it happened inside these five years. The claim is not that broad funds do not fall; it is that they fall less far and recover more reliably, because no single business failure can take them out.',
  },
  {
    prompt: 'Over these five years, which produced the better outcome for a typical holder?',
    options: [
      'The volatile stocks, because they had bigger peaks',
      'The broad fund, because the peaks the volatile stocks reached were not held',
      'Impossible to say, since it depends entirely on when each person bought and sold',
      'They were identical',
    ],
    answer: 2,
    explanation:
      'This is the honest answer and the one worth internalising. The broad fund produced a similar result for almost everyone who held it. The volatile names produced wildly different results depending on timing. Comparing single outcomes hides that the spread of outcomes is what actually differs.',
  },
  {
    prompt: 'A stable stock and a broad index fund carry the same kind of risk.',
    type: 'tf',
    answer: false,
    explanation:
      'A single large company, however solid, still carries company-specific risk: one accounting scandal, one lost lawsuit, one failed product line. A fund of hundreds does not. Both fall in a market-wide decline, but only one of them can be ruined by a single event.',
  },
]

export default function TheBoringChart({ moduleId }) {
  return (
    <>
      <p className="lead">
        Two charts in this track went up enormously and gave most of it back. Here are two that did
        neither. They are, by design, much less interesting to look at, and that is the entire argument.
      </p>

      <h2>A broad index fund</h2>

      <StockExample
        ticker="VOO"
        range="5y"
        caption="Vanguard S&P 500 ETF, five years of daily closes. One share of this is a slice of roughly 500 large US companies at once."
      />

      <p>
        Compare the worst-fall figure under this chart with the same figure under the Roblox and GameStop
        charts. That gap is not luck and it is not skill. It is{' '}
        <Term k="diversification">diversification</Term> doing the only thing it promises: making sure no
        single company's bad year can be your bad year.
      </p>

      <p>
        Note what this chart does not claim. It fell, visibly, and there is a stretch in the middle where
        anyone holding it watched a real amount of money disappear for months. Broad funds are not safe in
        the sense of not falling. They are safe in the narrower and more useful sense that they cannot be
        destroyed by one company, because the fund simply replaces it.
      </p>

      <h2>A single large, stable company</h2>

      <StockExample
        ticker="JNJ"
        range="5y"
        caption="Johnson &amp; Johnson, five years of daily closes. A dividend aristocrat, meaning it has raised its dividend every year for decades."
      />

      <p>
        This is what the Intermediate track meant by a{' '}
        <Term k="blue chip">blue chip</Term>. Large, profitable, selling things people buy in a recession,
        with a dividend record measured in decades. Its chart still moves, and its worst fall is still real,
        but the shape is recognisably different from the first two.
      </p>

      <Callout variant="note" title="Stable is not the same as diversified">
        <p>
          These two charts look similar, but the risks underneath them are not. The fund cannot be ruined by
          one company because it holds hundreds. A single company, however solid, can be: one accounting
          scandal, one lost court case, one product withdrawn. Enron was a widely held, widely respected
          company right up until it was not.
        </p>
        <p>
          That is why the Intermediate track argued for a broad core rather than a handful of good
          companies. Good is not the same as many.
        </p>
      </Callout>

      <h2>The comparison, honestly</h2>

      <p>
        It would be easy and dishonest to end here with "boring wins". Look at the actual figures under all
        four charts before accepting that.
      </p>

      <p>
        Over some five-year windows a volatile stock will beat a broad fund substantially, and somebody
        holding it will have done far better than the boring alternative. That is not a fluke; it is what
        high volatility means. A wide range of outcomes includes the good end.
      </p>

      <p>
        The real difference is not which produced the bigger number. It is <strong>how much the outcome
        depended on timing</strong>. Almost everyone who held the broad fund for these five years got
        something close to the same result. The people who held the volatile names got results that ranged
        from excellent to painful, determined mostly by which month they happened to buy and whether they
        had the nerve to hold.
      </p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Question</th>
              <th>Volatile single stock</th>
              <th>Broad index fund</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Does timing dominate the outcome?</td>
              <td>Yes, heavily</td>
              <td>Much less</td>
            </tr>
            <tr>
              <td>Can one company ruin it?</td>
              <td>Yes, entirely</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Does it fall in a market-wide decline?</td>
              <td>Yes, usually harder</td>
              <td>Yes</td>
            </tr>
            <tr>
              <td>How much homework does it need?</td>
              <td>Ongoing and real</td>
              <td>Very little</td>
            </tr>
            <tr>
              <td>What does being wrong cost?</td>
              <td>Potentially most of the position</td>
              <td>A drawdown you wait out</td>
            </tr>
          </tbody>
        </table>
      </div>

      <Callout variant="did-you-know">
        <p>
          Nobody posts a screenshot of a broad index fund. There is nothing to post: the good outcome takes
          a decade and looks like a gently rising line. This means the investing content you encounter is
          selected almost entirely from the category with the widest range of outcomes, and shown to you by
          the people at the good end of it.
        </p>
      </Callout>

      <TryIt
        moduleId={moduleId}
        placeholder="The four worst-fall figures, and which chart you would have held through…"
      >
        <p>
          Go back through this track and write down the worst-fall figure shown under each of the four
          charts. Then answer one question honestly: which of those four could you have held through
          without selling, if it had been real money that you cared about?
        </p>
        <p>
          Your answer to that is a more accurate risk profile than any questionnaire, including the one
          earlier in this course.
        </p>
      </TryIt>

      <h2>The one idea to take with you</h2>

      <p>
        The boring chart is not boring because it is worse. It is boring because its outcome does not depend
        much on you being clever or lucky, and that is precisely what makes it the sensible thing to build
        a portfolio around.
      </p>

      <p>Next: a short recap of what these four charts, taken together, actually establish.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
