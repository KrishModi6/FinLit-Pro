import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'In a short squeeze, where does the money that late buyers lose actually go?',
    options: [
      'It is destroyed, because the company never issued those shares',
      'To the people who sold to them — earlier buyers and, eventually, the shorts who covered lowest',
      'To the exchange, which collects it as a squeeze fee',
      'To the company, which receives the proceeds of every trade in its stock',
    ],
    answer: 1,
    explanation:
      'A squeeze does not create wealth; it moves it. Every share bought near $400 was sold by someone at $400, and that seller banked the gain. The company itself gets nothing from secondary-market trading — it was paid once, at issuance — which is why “the stock went up so the company made money” is wrong.',
  },
  {
    prompt:
      'An investor who read Enron’s public financial statements carefully in 2000 could have detected the fraud using standard ratio analysis.',
    type: 'tf',
    answer: false,
    explanation:
      'The debt and losses had been shifted off the balance sheet into related entities, so the ratios an investor could compute were built on numbers that were not true. Careful analysis of false inputs produces confident wrong answers. That is precisely why the defence against fraud is sizing, not scrutiny.',
  },
  {
    prompt:
      'Which fact about GameStop in January 2021 best explains why “being right about the setup” was not enough?',
    options: [
      'The company was profitable and growing the whole time',
      'The intraday high near $483 on 28 January was followed by a fall of roughly 90% within weeks',
      'Short interest was unusually low, so there was nobody to squeeze',
      'Trading was suspended for the entire month by regulators',
    ],
    answer: 1,
    explanation:
      'Plenty of people identified the crowded short position correctly. The move happened, and then most of it unwound within weeks. Being right about the mechanism told you nothing about which minute to sell, and the exit is the part almost nobody had planned.',
  },
  {
    prompt:
      'Why is holding a large position in your own employer’s stock riskier than holding the same amount in an unrelated company?',
    options: [
      'Employee shares are legally barred from being sold',
      'Your salary and your investment depend on the same company, so one bad event can hit both at once',
      'Company stock is always more volatile than the market by definition',
      'Employers charge a higher expense ratio on internal share plans',
    ],
    answer: 1,
    explanation:
      'The problem is correlation. If the company fails, you lose income and savings in the same week, at the moment you most need the savings. Volatility is not the issue — a low-volatility employer creates the same trap.',
  },
  {
    prompt:
      'What single defence would have limited the damage in BOTH the GameStop and Enron cases?',
    options: [
      'More rigorous fundamental analysis before buying',
      'Using stop-loss orders on every position',
      'Never holding a position large enough that being completely wrong ends you',
      'Waiting for a regulator to approve the investment first',
    ],
    answer: 2,
    explanation:
      'Analysis fails against fraud, because the inputs are lies. Stop-losses fail in gaps and halts, when the price you get is nothing like the price you set. Position size is the one control that still works when everything else has stopped working.',
  },
]

export default function WhenBetsGoBad({ moduleId }) {
  return (
    <>
      <p className="lead">
        Two stocks. Two disasters that look nothing alike. One of them made a handful of
        ordinary people rich and then took most of it back within a month; the other quietly
        deleted the retirement savings of thousands of people who had done everything they
        were told to do. The reason to study both is that they fail in completely different
        ways, and only one defence works against both of them.
      </p>

      <h2>GameStop, January 2021</h2>
      <p>
        Start with what GameStop actually was. A mall-based video game retailer with declining
        revenue, in a business being eaten alive by digital downloads. Not a fraud, not a
        scandal — just a company that a lot of professional investors had concluded was going
        to keep shrinking. So they bet against it, heavily, and that bet showed up in the
        stock’s <Term k="short interest">short interest</Term>: the fraction of shares that had
        been borrowed and sold, waiting to be bought back cheaper.
      </p>
      <p>
        It got unusually crowded. And a crowded short position has a structural weakness that
        has nothing to do with whether the bet is correct. Anyone who is short must eventually
        buy the shares back. If the price rises instead of falling, their losses grow without a
        ceiling and their broker starts demanding more collateral. At some point they stop
        arguing with the market and buy — which pushes the price up further, which forces the
        next short to buy, and so on.
      </p>

      <KeyTerm term="short squeeze" />

      <p>
        In January 2021 a large, loosely coordinated wave of retail buying, centred on Reddit’s
        WallStreetBets, pushed hard into exactly that pressure point. The sequence was fast.
        GameStop traded under $20 at the start of January 2021. On 28 January 2021 it reached
        an intraday high near $483. Those are pre-split prices; the company did a 4-for-1 stock
        split in July 2022, so charts you look up today will show the old highs divided by four.
        Within weeks, the stock had fallen roughly 90% from that peak.
      </p>

      <h3>The winners were real</h3>
      <p>
        It would be easy, and dishonest, to tell this story as though everyone lost. People
        bought at $15 and sold at $200. Some of them paid off student loans, cleared medical
        debt, put a deposit on a house. That money was real, it was theirs, and pretending
        otherwise is the kind of lie that makes readers stop trusting the rest of the lesson.
      </p>
      <p>
        But look at the structure of where it came from.
      </p>

      <h3>A squeeze is a transfer, not a creation</h3>
      <p>
        No wealth was manufactured in January 2021. GameStop did not suddenly start selling more
        games. Every share someone sold at $300 was bought by someone else at $300. For the
        person who bought near the top to have made money, another person would have had to buy
        even higher — and eventually, inevitably, there was no one left willing to.
      </p>
      <p>
        That is why the same event was simultaneously the best trade and the worst trade of many
        people’s lives, and the difference between those two groups was not intelligence or
        conviction. It was timing.
      </p>

      <Callout variant="example">
        <p>
          Suppose two people believed the identical thesis: the short position is crowded and
          the stock will spike. One buys at $40 and sells at $250, turning $2,000 into $12,500.
          The second reads the same posts three weeks later, buys at $350, and holds through the
          collapse to $40. That $2,000 becomes about $230.
        </p>
        <p>
          Same analysis. Same conviction. A 525% gain and a 89% loss, separated only by when
          they clicked buy and whether they had any plan at all for clicking sell.
        </p>
      </Callout>

      <h3>The part nobody had priced</h3>
      <p>
        At the peak of the frenzy, several brokers restricted buying in GameStop and other
        affected names, allowing customers to sell but not to open new positions. The stated
        reason involved clearinghouse collateral requirements that spiked with the volatility.
        Whatever the cause, the effect on users was immediate: people who had planned a trade
        found they could not place it. Congressional hearings followed, and the episode became a
        long-running argument about market plumbing.
      </p>
      <p>
        The transferable lesson is narrower and more useful than the conspiracy theories.{' '}
        In extreme events, your ability to transact is itself a risk you probably did not price.
        You may plan around price. You cannot easily plan around a halted stock, a frozen order
        button, a broker outage, or an order that fills nowhere near where you expected.
      </p>

      <Callout variant="warning">
        <p>
          A stop-loss order does not guarantee your exit price. It becomes a market order once
          triggered, so in a violent gap it can fill far below where you set it. In a squeeze
          unwinding at speed, “I’ll just sell if it drops 20%” is a plan that assumes a
          functioning, liquid market at exactly the moment you are least likely to have one.
        </p>
      </Callout>

      <p>
        So the GameStop lesson is about sequencing, not stock picking. Being right about the
        setup gets you nothing on its own. You also have to be right about the timing, and about
        the exit — and the exit is the half of the trade that almost nobody writes down in
        advance.
      </p>

      <h2>Enron, 2001</h2>
      <p>
        Now a failure with the opposite shape. Enron was an energy and commodities-trading
        company, and for six consecutive years in the late 1990s and 2000 it was named one of
        America’s most innovative companies by Fortune. It was widely held, widely recommended,
        and treated as a serious, respectable holding. Its shares traded around $90 in mid-2000.
      </p>
      <p>
        Underneath, the reported picture was being managed. Enron used accounting arrangements
        that pushed debt and losses off its own balance sheet and into related entities, which
        made the business look far more profitable and far less indebted than it actually was.
        The auditor, Arthur Andersen — one of the largest accounting firms in the world — was
        implicated in the collapse and was effectively destroyed by it. Enron filed for
        bankruptcy in December 2001. The stock went to near zero.
      </p>

      <Callout variant="did-you-know">
        <p>
          Enron’s collapse produced the Sarbanes-Oxley Act of 2002, which tightened US corporate
          disclosure rules, made senior executives personally certify financial statements, and
          overhauled oversight of auditors.
        </p>
        <p>
          Most of the investor protections you now take for granted exist because something
          terrible happened first. Regulation is downstream of disasters, which means the
          protections against the next kind of disaster do not exist yet.
        </p>
      </Callout>

      <h3>The part that should genuinely bother you</h3>
      <p>
        Many Enron employees held large portions of their retirement savings in company stock.
        When the company failed, they lost their jobs and their savings in the same event, in the
        same few weeks, at exactly the moment they most needed a cushion to fall back on.
      </p>
      <p>
        That is the most extreme possible failure of{' '}
        <Term k="diversification">diversification</Term>. It is not just concentration in one
        stock. It is concentration in one stock that is perfectly correlated with your income,
        your health insurance, your professional network, and your ability to find the next job
        in an industry that now associates you with a scandal. Every risk you hold points the
        same direction.
      </p>

      <Callout variant="warning" title="Your employer is the worst diversification error">
        <p>
          If your company offers stock, an employee purchase plan, or equity compensation, take
          it seriously as compensation and take it seriously as risk. Holding a large share of
          your savings in your employer means one bad event can remove your paycheque and your
          safety net simultaneously.
        </p>
        <p>
          This is not a comment on any specific employer, and it applies just as much to boring,
          stable companies as to volatile ones. Enron looked extremely stable in 1999. The issue
          is the correlation, not the company.
        </p>
      </Callout>

      <h3>Why analysis could not save you</h3>
      <p>
        Every fundamental tool you have learned — <Term k="pe ratio">price-to-earnings</Term>,{' '}
        <Term k="debt to equity">debt-to-equity</Term>, margin trends, free cash flow — takes
        reported numbers as its input. If the reported numbers are false, the ratios are false
        too, and the more carefully you compute them the more confident you become in an answer
        that is wrong. There is no ratio that detects a lie in its own denominator.
      </p>
      <p>
        Some skeptics did raise questions about Enron before the collapse, mostly around how
        opaque the disclosures were and how hard the business was to explain. That is a genuine
        signal worth respecting: if you cannot explain in two sentences how a company makes
        money, that is information. But be honest about how weak a defence it is. Plenty of
        opaque companies are fine, and plenty of skeptics were early and loud and ignored.
      </p>
      <p>
        The defence that actually works against fraud you cannot detect is not better analysis.
        It is <Term k="position sizing">position sizing</Term>. If Enron is 2% of your portfolio,
        the fraud costs you 2% and you are irritated. If it is 60%, the same fraud restructures
        your life.
      </p>

      <h2>Two failure modes, side by side</h2>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Dimension</th>
              <th>GameStop, 2021</th>
              <th>Enron, 2001</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>What failed</td>
              <td>Timing and exit discipline in a crowd-driven price spiral</td>
              <td>The truthfulness of the reported financial statements</td>
            </tr>
            <tr>
              <td>Could analysis have caught it?</td>
              <td>Partly — the crowded short was public, but the top was not knowable</td>
              <td>No — the inputs to every ratio were false</td>
            </tr>
            <tr>
              <td>Who lost</td>
              <td>Late buyers and squeezed short sellers</td>
              <td>Shareholders, and employees holding company stock in retirement accounts</td>
            </tr>
            <tr>
              <td>Warning signs</td>
              <td>Vertical price move, no change in the underlying business</td>
              <td>Opaque disclosures, a business nobody could explain simply</td>
            </tr>
            <tr>
              <td>What actually protected you</td>
              <td>A written exit plan and a small position</td>
              <td>Diversification and a small position</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>
        Read the bottom row again. Two disasters with almost nothing in common, and the same
        word appears in both cells.
      </p>

      <TryIt
        moduleId={moduleId}
        placeholder="Company, the specific 80% scenario, and what that loss would do to your total portfolio…"
      >
        <p>
          Pick a company you would describe as obviously safe — the kind you would name without
          hesitating. Look it up on Yahoo Finance or its own investor-relations page and skim the
          most recent annual report’s risk factors section.
        </p>
        <p>
          Then write down three things: the specific scenario in which that company’s stock falls
          80% (a real mechanism — lost lawsuit, obsolete product, accounting restatement, key
          market closed — not just “the market crashes”); what percentage of a hypothetical
          portfolio you would have put in it; and whether that portfolio survives the scenario you
          just described. If the answer is no, the position was too big, regardless of how safe
          the company looked.
        </p>
      </TryIt>

      <h2>The one idea to keep</h2>
      <p>
        These two cases are different failure modes. GameStop is being right too late. Enron is
        being lied to. No amount of research fixes the first, because the top of a squeeze is
        unknowable in advance. No amount of research fixes the second, because your research was
        reading fiction.
      </p>
      <p>
        Only one defence covers both, and it is unglamorous: never hold a position large enough
        that being completely wrong ends you. Not wrong-and-annoyed. Wrong-and-finished. A 50%{' '}
        <Term k="drawdown">drawdown</Term> on a position that is 3% of your money costs you 1.5%
        of your total. The identical mistake at 50% of your money costs you a quarter of
        everything you have, and it takes a 33% gain on what remains just to get back to even.
        The mistake was the same size. The sizing was not.
      </p>
      <p>
        Next up: how to actually build that sizing rule — how much of a portfolio a single
        speculative idea should ever occupy, how to set the number before you are emotionally
        involved, and why the rule has to be written down while you are calm to survive the day
        you are not.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
