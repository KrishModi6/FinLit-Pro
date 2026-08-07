import Callout from '../../components/ui/Callout.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'Which single sentence best summarises the Beginner track?',
    options: [
      'Stocks go up over time, so buy as much as you can',
      'A share is part-ownership of a real business, priced by whatever two people last agreed on',
      'The market is rigged against small investors',
      'Timing your entry is the most important skill',
    ],
    answer: 1,
    explanation:
      'Everything in this track rests on that one sentence. Exchanges, quotes, dividends and indices are all machinery built on top of it, and every later track keeps returning to the split between what a business is worth and what its price happens to be today.',
  },
  {
    prompt: 'You now know enough to judge whether a particular stock is a good buy.',
    type: 'tf',
    answer: false,
    explanation:
      'Not yet, and the honest answer matters. This track taught you what the pieces are and how the market works mechanically. Deciding whether a company is stable or speculative needs the metrics in the Intermediate track, and deciding how much to hold needs the sizing rules in the Hard track.',
  },
  {
    prompt: 'What should determine how much of your money is in stocks at all?',
    options: [
      'How confident you feel about the market',
      'Your time horizon, your cash cushion and how you actually behave in a fall',
      'How much your friends have invested',
      'The current level of the S&P 500',
    ],
    answer: 1,
    explanation:
      'Capacity beats confidence. Money needed within a few years generally should not be in stocks regardless of how you feel, and a long horizon only helps if a surprise expense will not force you to sell early.',
  },
  {
    prompt: 'A company receives money every time its share price rises.',
    type: 'tf',
    answer: false,
    explanation:
      'It received money at the IPO. After that, shares change hands between investors and the cash goes from buyer to seller. A high price helps the company in other ways, but no money arrives from your purchase.',
  },
]

export default function Recap({ moduleId }) {
  return (
    <>
      <p className="lead">
        That is the whole foundation. Before moving on, it is worth seeing the seven lessons as one
        argument rather than seven separate topics, because they were building toward something.
      </p>

      <h2>What you actually learned</h2>

      <p>
        <strong>A stock is ownership.</strong> A <Term k="share">share</Term> is a slice of a real business
        with real customers and real problems. You are last in line if it fails, and that last-in-line
        position is exactly what you are being compensated for.
      </p>

      <p>
        <strong>The market is a matching service, not a shop.</strong> An{' '}
        <Term k="exchange">exchange</Term> pairs buyers with sellers. Your{' '}
        <Term k="brokerage">broker</Term> is the door you walk through. Nobody sets the price; it is simply
        the last number two people agreed on.
      </p>

      <p>
        <strong>Prices move on expectations, not events.</strong> This is the one most people never learn.
        A company can report record profits and fall, because the market had already priced in something
        better. Price and value are related over long horizons and can diverge wildly over short ones.
      </p>

      <p>
        <strong>You can read a quote.</strong> Price, volume, market cap, the 52-week range. You know that
        a $12 stock is not cheaper than a $600 one, and that{' '}
        <Term k="market cap">market cap</Term> is the number that lets you compare company sizes.
      </p>

      <p>
        <strong>Indices are yardsticks.</strong> The S&amp;P 500, the price-weighted Dow, the tech-heavy
        NASDAQ Composite. You buy them through a fund, not directly. And you know what a{' '}
        <Term k="bear market">bear market</Term> and a <Term k="correction">correction</Term> formally are.
      </p>

      <p>
        <strong>Time is the variable that changes everything.</strong>{' '}
        <Term k="compound interest">Compounding</Term> is back-loaded, which is the entire argument for
        starting early. Over a day, price movement is noise. Over decades, business results dominate.
      </p>

      <p>
        <strong>Your own temperament is an input.</strong> Risk tolerance is psychological, risk capacity
        is arithmetic, and when they disagree capacity wins.
      </p>

      <Callout variant="real-talk" title="What you should not conclude">
        <p>
          Nothing in this track said that investing is easy, that stocks always go up, or that more risk
          reliably means more reward. Higher expected return is compensation for a wider range of outcomes,
          and plenty of high-risk positions deliver only the risk. If you finish this track feeling
          confident rather than oriented, re-read the lesson on why prices move.
        </p>
      </Callout>

      <h2>What you still cannot do</h2>

      <p>
        Being honest about the gap is more useful than a summary that flatters you. Right now you can read
        a quote page but not interpret it. You know a share is ownership of a business, but not how to tell
        a durable business from a fragile one, and not how much of any single thing to hold.
      </p>

      <p>Those are exactly the next two tracks.</p>

      <h2>What comes next</h2>

      <p>
        <strong>Intermediate: Stable vs Unstable Stocks.</strong> This is where the quote page stops being
        a wall of numbers. You will learn what <Term k="beta">beta</Term>,{' '}
        <Term k="pe ratio">P/E</Term>, EPS and <Term k="debt to equity">debt-to-equity</Term> actually
        measure and where each one misleads. You will learn why an{' '}
        <Term k="etf">ETF</Term> is structurally lower risk than one excellent company, and why a portion
        of your money should always sit in something boring.
      </p>

      <p>
        After that comes <strong>Examples</strong>, where the invented numbers stop and you look at real
        five-year charts of real companies, and then <strong>Hard</strong>, which deals honestly with
        options, leverage and speculation.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="The one idea that changed how you think, and the one thing still unclear…"
      >
        <p>
          Before continuing, write two things down. First: which single idea from this track most changed
          how you think about money? Second: what is still genuinely unclear to you?
        </p>
        <p>
          Come back to the second one at the end of the Intermediate track and see whether it got answered.
          If it did not, that is worth chasing rather than glossing over.
        </p>
      </TryIt>

      <h2>One thing to carry forward</h2>

      <p>
        Behind every ticker is a business. Every metric in the next track is just a different way of asking
        the same two questions: what does this business actually earn, and what am I being asked to pay for
        it?
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
