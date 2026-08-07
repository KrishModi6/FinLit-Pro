import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import StockExample from '../../components/ui/StockExample.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'Why does this chart start after January 2021 rather than including the squeeze itself?',
    options: [
      'The data before then does not exist',
      'Because the aftermath is the part that affected most people, and the part nobody posts about',
      'Because the squeeze was not important',
      'Because charts cannot show single-day moves',
    ],
    answer: 1,
    explanation:
      'The squeeze week is the most documented event in retail investing. The years afterwards, which is what the people who bought during the excitement actually lived through, get almost no attention. That asymmetry in what gets shared is itself worth understanding.',
  },
  {
    prompt: 'A short squeeze transfers money from short sellers to everyone who owns the stock, so all holders win.',
    type: 'tf',
    answer: false,
    explanation:
      'A squeeze is a transfer, but the direction runs from late buyers to early sellers. For somebody to sell near the top, somebody else had to buy near the top. The winners and the losers were both in the same trade, separated only by timing.',
  },
  {
    prompt: 'What did the 2021 GameStop event most clearly demonstrate about brokers?',
    options: [
      'That commission-free trading is a scam',
      'That your ability to transact can be restricted exactly when you most want to act',
      'That brokers always side with hedge funds',
      'That limit orders do not work',
    ],
    answer: 1,
    explanation:
      'Several brokers restricted buying in the affected names during the peak. Whatever the reasons, the practical lesson stands: access to the market is not guaranteed in extreme conditions, and that is a risk you cannot see on any chart.',
  },
  {
    prompt: 'Being right that a stock had high short interest was enough to make money on it.',
    type: 'tf',
    answer: false,
    explanation:
      'You also had to be right about when, and about when to leave. Short interest describes positioning, not a schedule. Plenty of people identified the setup correctly and still lost money by arriving late or staying too long.',
  },
]

export default function GameStopAfterTheCrowd({ moduleId }) {
  return (
    <>
      <p className="lead">
        Everyone has seen the January 2021 GameStop chart. It gets posted constantly, always the same
        near-vertical line. What almost nobody posts is what happened next, so that is what this lesson
        looks at.
      </p>

      <h2>The years after the week</h2>

      <StockExample
        ticker="GME"
        range="5y"
        caption="GameStop Corp, five years of daily closes. Note that GME did a 4-for-1 stock split in July 2022, so prices before that date are shown split-adjusted and will look smaller than the headline numbers you remember from 2021."
      />

      <p>
        The squeeze itself sits before the left edge of this window. In January 2021 the stock went from
        under $20 at the start of the month to an intraday high near $483 on 28 January, all in pre-split
        terms, and then fell roughly 90% within weeks. What you are looking at above is the long tail after
        that: still volatile, still capable of sharp bursts, and over the whole window not a chart anybody
        would frame.
      </p>

      <Callout variant="real-talk" title="The winners were real">
        <p>
          It would be dishonest to pretend otherwise. People made life-changing money in that week, and
          some of them have the screenshots to prove it. This lesson is not here to sneer at them.
        </p>
        <p>
          But notice the structure. For a person to sell at $400, another person had to buy at $400. A{' '}
          <Term k="short squeeze">short squeeze</Term> does not create wealth out of nothing; it moves it,
          largely from people who arrived late to people who arrived early. Both groups were in the same
          trade and believed roughly the same thing. The difference was timing, which is the thing nobody
          controls.
        </p>
      </Callout>

      <h2>Three things this chart teaches that the famous one does not</h2>

      <h3>1. Attention is not a business</h3>

      <p>
        The move was driven by positioning and coordination, not by GameStop selling more games. When the
        attention moved on, the thing holding the price up moved on with it. Price driven by a crowd
        depends on the crowd staying, and crowds disperse without announcing it.
      </p>

      <h3>2. You had to be right three times</h3>

      <p>
        Identifying that <Term k="short interest">short interest</Term> was unusually high was the easy
        part, and thousands of people did it. You also had to be right about when it would break, and right
        about when to leave. Getting two of three still loses money. This is the same three-way requirement
        the Hard track describes for options, showing up in a plain stock.
      </p>

      <h3>3. You may not be able to trade</h3>

      <p>
        During the peak, several brokers restricted buying in the affected names. Regardless of the reasons,
        the practical consequence is worth internalising: in genuinely extreme conditions, the ability to
        transact is not guaranteed. That is a risk that appears on no chart and in no ratio, and the only
        defence against it is not having a position whose survival depends on being able to act instantly.
      </p>

      <Callout variant="warning" title="The screenshot problem">
        <p>
          Every gain screenshot you have ever seen was posted because it was a gain. Nobody screenshots the
          account that went to nearly nothing, so the evidence you are exposed to is filtered before it
          reaches you. You are seeing the survivors of a process, not the outcomes of it.
        </p>
        <p>
          When you find yourself thinking "everyone made money on this", check whether you have any way of
          knowing that, or whether you have simply never been shown the other side.
        </p>
      </Callout>

      <h2>What would have protected you</h2>

      <p>
        Not better analysis. Somebody with a perfect read on the short interest and the mechanics could
        still have bought on the Wednesday and lost most of it. What protected people was size.
      </p>

      <p>
        A position small enough that a total loss was survivable produced two outcomes: a memorable win, or
        a small dent and a story. A position large enough to matter produced the same two outcomes, except
        the second one was serious. The event was identical in both cases. The sizing decision, made before
        any of it, is what differed.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="What you would have needed to believe, and what would have made you sell…"
      >
        <p>
          Imagine you bought during the excitement, near the top, with money you cared about. Write down
          two things: what you would have needed to believe to hold through the fall that followed, and
          what specific event would have told you to sell.
        </p>
        <p>
          Then answer honestly whether you would have written either of those down before buying, or only
          afterwards.
        </p>
      </TryIt>

      <h2>The one idea to take with you</h2>

      <p>
        The famous chart is the exception. This chart is the rule, and it is the one that describes what
        most participants actually experienced. When you next see a vertical line posted as proof that
        something is easy, ask what the five years either side of it look like.
      </p>

      <p>
        Next: the same five years, for two boring things nobody posts about at all.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
