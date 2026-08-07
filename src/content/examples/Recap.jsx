import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'What did the four charts in this track have in common?',
    options: [
      'All four ended higher than they started',
      'All four fell substantially at some point within the five years',
      'All four were driven by social media attention',
      'All four recovered quickly from every fall',
    ],
    answer: 1,
    explanation:
      'Every one of them, including the deliberately boring pair, had a real fall inside the window. Falling is not the exception; it is the normal texture of owning anything. What differed was how far each one fell and how much the outcome depended on timing.',
  },
  {
    prompt: 'Knowing when to sell means being able to identify the top.',
    type: 'tf',
    answer: false,
    explanation:
      'Nobody identifies tops reliably. It means deciding in advance what would make you act: what would tell you the reason you bought is no longer true, and what rise would make you take some off the table. Both are decisions made while calm, not predictions.',
  },
  {
    prompt: 'A stock falls 70% from its peak. What does this most reliably tell you about the company?',
    options: [
      'The company is failing',
      'The company was overvalued at the peak',
      'Very little on its own, because price reflects changing expectations rather than measuring business health',
      'The company will recover eventually',
    ],
    answer: 2,
    explanation:
      'Price is what people currently pay for a claim on future profits. Expectations can reset hard while revenue keeps growing. Reading business health off a price line is exactly the price-versus-value confusion the earlier tracks warned about.',
  },
  {
    prompt: 'Why is the investing content most people see systematically misleading?',
    options: [
      'Because most of it is deliberately fraudulent',
      'Because it is selected after the fact from the winners, and losses are rarely posted',
      'Because charts are hard to read',
      'Because it usually discusses index funds',
    ],
    answer: 1,
    explanation:
      'Nobody screenshots the account that went to nearly nothing, and nobody posts a broad index fund. You are shown the survivors of a process rather than its outcomes, which makes the good end of a wide distribution look like the typical result.',
  },
]

export default function Recap({ moduleId }) {
  return (
    <>
      <p className="lead">
        Four real charts, no invented numbers. Taken together they establish a handful of things that no
        constructed example can, because a made-up chart always behaves and a real one does not.
      </p>

      <h2>What the four charts agreed on</h2>

      <p>
        <strong>Everything falls.</strong> All four had a real drawdown inside five years, including the two
        chosen specifically for being boring. Falling is not a malfunction; it is the ordinary texture of
        owning anything. The question was never whether a fall happens but how far, and whether you are
        still solvent and calm when it does.
      </p>

      <p>
        <strong>A gain you did not sell is not a gain.</strong> The Roblox chart made this concrete. A large
        rise followed by a large fall leaves somebody roughly where they started, and the difference between
        the peak number and the final one was not a market event. It was the absence of a decision.
      </p>

      <p>
        <strong>Percentages are not symmetric.</strong> You saw the recovery maths from the Intermediate
        track appear in real price history: the further something falls, the disproportionately larger the
        rise needed to undo it.
      </p>

      <p>
        <strong>Timing dominates volatile outcomes and barely touches boring ones.</strong> This is the
        finding worth keeping. Almost everyone who held the broad fund got a similar result. The people who
        held the volatile names got results ranging from excellent to painful, decided largely by which
        month they bought.
      </p>

      <p>
        <strong>Crowds are not businesses.</strong> A price held up by attention falls when attention moves
        on, and attention gives no notice. The GameStop chart after the famous week is what that looks like.
      </p>

      <Callout variant="real-talk" title="What this track did not say">
        <p>
          It did not say volatile stocks are bad or that anybody should avoid them. Over some windows they
          beat everything else, which is exactly what a wide range of outcomes means. Nor did it say
          anything about whether any of these four companies is worth owning, and nothing here is a
          suggestion to buy or avoid any of them.
        </p>
        <p>
          What it said is narrower and more useful: the range of outcomes differs enormously between these
          categories, and the correct response to a wide range is a smaller{' '}
          <Term k="position sizing">position</Term>, not more confidence.
        </p>
      </Callout>

      <h2>The skill this track was really teaching</h2>

      <p>
        Looking at a chart and describing what happened, without immediately deciding what it means about
        the future. That sounds trivial and is not. Most people look at a rising line and feel that it will
        keep rising, look at a falling one and feel that it is broken, and never separate the description
        from the prediction.
      </p>

      <p>
        You can now open a five-year chart, read the worst fall, notice how much of the outcome depended on
        entry timing, and ask whether the move was driven by results or by attention. That is a genuinely
        different way of looking at a stock from the one you started this course with.
      </p>

      <h2>What comes next, and a warning about it</h2>

      <p>
        The <strong>Hard</strong> track covers what most people mean when they talk about making money fast:
        options, leverage, penny stocks, meme stocks. It is the most useful track in this course and the
        most dangerous one to read carelessly.
      </p>

      <p>
        It exists because you will encounter these instruments whether or not anyone explains them, and
        understanding something is the prerequisite for deciding not to do it as much as for doing it. It
        will show you what a total loss actually looks like alongside every upside scenario, because a
        framework that shows you only the upside is selling something.
      </p>

      <p>
        Read it for the <Term k="position sizing">sizing</Term> rules more than the mechanics. The mechanics
        are interesting; the sizing is the part that determines whether being wrong is survivable.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="A ticker you know, its worst fall, and whether you could have held it…"
      >
        <p>
          Open the Market Explorer in the Simulator and pull up any company you personally care about, set
          to five years. Write down its worst fall and its return over the period.
        </p>
        <p>
          Then answer the only question that matters before the Hard track: if that had been real money you
          needed, could you have held through the worst part without selling? Your honest answer sets how
          much of the next track applies to you.
        </p>
      </TryIt>

      <h2>One thing to carry forward</h2>

      <p>
        Charts are evidence about the past and nothing more. Their value is that they show you the
        magnitude of things you would otherwise underestimate: how far real prices fall, how long the bad
        stretches last, and how much of any single result was simply when somebody happened to arrive.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
