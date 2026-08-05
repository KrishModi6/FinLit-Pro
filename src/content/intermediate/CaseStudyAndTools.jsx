import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'In January 2021, what mechanically forced GameStop’s price higher once buying pressure started?',
    options: [
      'GameStop reported record quarterly earnings that beat every estimate',
      'Short sellers buying shares to close losing positions, which added more demand',
      'The company announced a large special dividend',
      'Index funds were required to add GameStop to the S&P 500',
    ],
    answer: 1,
    explanation:
      'A short seller who borrowed and sold shares must buy them back to exit. As the price rose, losses mounted and forced buying added to demand, pushing the price higher still. The tempting wrong answer is earnings: GameStop’s business was shrinking, not booming. That is the point of the case study — the move came from positioning, not from results.',
  },
  {
    prompt: 'Someone bought GameStop at roughly $350 on 28 January 2021 because it was the top story everywhere. What does the case study say about that decision?',
    options: [
      'They were early, since the squeeze had barely begun',
      'They were buying from earlier holders who were selling into the spike',
      'They were protected because brokers guaranteed order execution',
      'They had an edge because the news confirmed the thesis',
    ],
    answer: 1,
    explanation:
      'Every share bought near the top came from someone selling it. A squeeze transfers money from late buyers to early ones. By the time a story is the top headline, the information is already reflected in the price, so the news is not an edge — it is the crowd you are trading against.',
  },
  {
    prompt: 'A stock’s 10-K annual report is written by the company, so its Risk Factors section is just marketing.',
    type: 'tf',
    answer: false,
    explanation:
      'Risk Factors is the one place a company is legally obliged to argue against itself. Because there is legal liability for omitting known risks, it tends to be the most candid section in the entire filing. Twenty minutes there usually teaches you more than an hour of commentary.',
  },
  {
    prompt: 'What is a stock screener actually for?',
    options: [
      'It predicts which stocks will rise over the next quarter',
      'It filters thousands of listed companies down to the few that match numeric criteria you set',
      'It executes trades automatically when your conditions are met',
      'It reveals what large institutions are buying before they buy it',
    ],
    answer: 1,
    explanation:
      'A screener narrows the universe. You set filters — market cap above a threshold, P/E below one, a sector, a country — and it returns the list that matches. It generates candidates for research; it does not do the research, and it certainly does not forecast. The prediction answer is the seductive one, and it is wrong.',
  },
  {
    prompt: 'During extreme volatility, some brokers restricted buying in GameStop and a few other stocks.',
    type: 'tf',
    answer: true,
    explanation:
      'Several brokers restricted opening new positions in GameStop and related names during the peak in late January 2021, citing clearing and collateral requirements. Whatever you think of the reasons, the lesson stands: your ability to transact is not guaranteed in exactly the moments you most want it.',
  },
]

export default function CaseStudyAndTools({ moduleId }) {
  return (
    <>
      <p className="lead">
        On 4 January 2021, GameStop closed under $20 a share. Seventeen trading days later it touched
        an intraday high near $483. Then it fell roughly 90% within weeks. Almost everything worth
        knowing about how markets, crowds and research actually work is hiding inside that one month.
      </p>

      <h2>What GameStop was before it was a headline</h2>

      <p>
        Strip away the mythology and start with the business. GameStop sold video games and consoles
        out of physical stores, most of them in shopping malls, at the exact moment the industry was
        moving to digital downloads. Revenue was shrinking. Stores were closing. This was not a
        misunderstood gem — by conventional measures it was a retailer in structural decline, and
        professional investors said so openly.
      </p>

      <p>
        Which is why so many of them bet against it. GameStop had unusually high{' '}
        <Term k="short interest">short interest</Term>: a very large fraction of its available shares
        had been borrowed and sold by traders who expected to buy them back cheaper later. Some
        estimates at the time put the shorted amount at more than the company’s entire freely traded
        share count, which is possible because borrowed shares can be re-lent and sold again.
      </p>

      <KeyTerm term="short interest" />

      <p>
        Then a crowd noticed. On Reddit’s WallStreetBets and across social media, retail investors
        built a thesis that the shorts were overextended and could be forced out. Buying accelerated
        through mid-January. And here is the mechanical part that matters more than any of the
        storytelling: a short seller who wants out has to buy the stock back. Rising prices produced
        losses, losses produced forced buying, forced buying produced higher prices. That feedback
        loop is a <Term k="short squeeze">short squeeze</Term>.
      </p>

      <KeyTerm term="short squeeze" />

      <Callout variant="did-you-know">
        <p>
          Every GameStop price you read from that period is pre-split. GME carried out a 4-for-1 stock
          split in July 2022, so a chart today shows those levels divided by four. The dollar figures
          in this lesson are the 2021 numbers as they were quoted at the time.
        </p>
      </Callout>

      <h2>The part nobody should shy away from</h2>

      <p>
        Some people made life-changing money. That is true, it is not a footnote, and pretending
        otherwise would make everything else here less believable. There were students who paid off
        loans and people who cleared debts they had carried for years. Good for them.
      </p>

      <p>
        Now the honest version of the same sentence. The winners were overwhelmingly the people who
        bought early — in December or the first half of January, when the position was unpopular and
        genuinely uncomfortable — and who then sold into the spike. Selling is the part that gets
        skipped in the retellings, and it is the part that determined who kept the money.
      </p>

      <p>
        So ask where their money came from. Not from GameStop, which issued no new value that month.
        It came from two places: short sellers closing at a loss, and later buyers. If you bought at
        $300 or $400 on 28 January because it was the lead story on every feed you opened, you were
        buying shares from someone who had bought at $20 and had decided that day was a good day to
        be done. A squeeze is a transfer. The transfer runs from late buyers to early ones.
      </p>

      <Callout variant="warning" title="You may not be able to trade when you want to">
        <p>
          At the peak, several brokers restricted opening new positions in GameStop and a handful of
          other stocks, citing clearing and collateral requirements. Customers could sell but not buy.
          Whatever your view of why, treat it as a permanent lesson about market structure:{' '}
          <Term k="liquidity">liquidity</Term> and access are assumptions, not guarantees, and they
          fail exactly in the conditions that made you want to act.
        </p>
      </Callout>

      <h2>The boring comparison</h2>

      <p>
        Put a different kind of investment next to it. Johnson &amp; Johnson is a{' '}
        <Term k="dividend aristocrat">dividend aristocrat</Term> — an S&amp;P 500 company that has
        raised its dividend every year for more than 60 consecutive years. VOO is an{' '}
        <Term k="etf">ETF</Term> tracking the S&amp;P 500, holding roughly 500 large US companies at
        an expense ratio around 0.03%. Neither has ever been anyone’s favourite story at a party.
      </p>

      <p>
        I am deliberately not going to tell you what either returned from January 2021 to today,
        because I would be inventing precision I do not have and you would have no way to check it.
        What I can describe honestly is the character of the outcome: modest annual moves, dividends
        arriving on a schedule and compounding if reinvested, drawdowns along the way including a
        rough 2022 for the index, and a result that came from time in the market rather than from
        picking a day. Nobody screenshots it.
      </p>

      <p>
        Go and get the real numbers yourself — the tools in the second half of this lesson will have
        you doing it in about four minutes. Looking it up will teach you more than a figure I hand
        you, and it builds exactly the habit this lesson is trying to install.
      </p>

      <h2>Two investments, side by side</h2>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Dimension</th>
              <th>GME in January 2021</th>
              <th>A broad index fund</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>What drove the price</td>
              <td>Positioning: crowded shorts, forced covering, options hedging, attention</td>
              <td>Aggregate earnings and cash flows of about 500 companies</td>
            </tr>
            <tr>
              <td>What you had to get right</td>
              <td>Direction and timing, on entry and on exit</td>
              <td>That the US economy keeps producing profits over decades</td>
            </tr>
            <tr>
              <td>Range of outcomes</td>
              <td>Roughly 20x for the earliest sellers, near total loss for the latest buyers</td>
              <td>Historically a mid-single-digit to low-double-digit annualised range, with real losing years</td>
            </tr>
            <tr>
              <td>Did timing matter</td>
              <td>Enormously — days and sometimes hours changed everything</td>
              <td>Barely, over a long enough horizon</td>
            </tr>
            <tr>
              <td>Could you always transact</td>
              <td>No — some brokers restricted buying at the peak</td>
              <td>Yes, in normal conditions, with deep liquidity</td>
            </tr>
            <tr>
              <td>Holding three more years</td>
              <td>Gave back the great majority of the peak; the squeeze did not repeat</td>
              <td>Kept compounding, with dividends reinvested, through a down year and a recovery</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>Four lessons that transfer</h2>

      <p>
        <strong>Extreme moves are usually about positioning, not results.</strong> GameStop’s business
        did not improve 20-fold in three weeks. When you see a violent move, ask who is being forced
        to trade and why, before you construct a story about the company.
      </p>

      <p>
        <strong>You must be right about direction and timing.</strong> Being right about the squeeze
        and wrong about the week was still a loss. Buy-and-hold investing lets you be roughly right
        about direction and vague about timing; speculation does not extend that courtesy.
      </p>

      <p>
        <strong>Access can fail.</strong> Restrictions, halts, gapping prices and widening spreads all
        cluster in the same moments. Any plan that depends on executing precisely during chaos should
        be assumed fragile.
      </p>

      <p>
        <strong>A story that is everywhere is already in the price.</strong> By the time something is
        the top post, the top video and the evening news, the people who acted on the information
        acted days or weeks ago. Ubiquity is the opposite of an edge.
      </p>

      <h2>Your research toolkit</h2>

      <p>
        Everything above is only useful if you can go and check things. Here is the practical stack,
        roughly in the order you would use it.
      </p>

      <h3>Yahoo Finance</h3>

      <p>
        The best free general-purpose starting point. Search a ticker and you get a quote page, then
        tabs worth knowing: <strong>Statistics</strong> gives you{' '}
        <Term k="market cap">market cap</Term>, P/E ratio, beta, margins and share count in one
        screen. <strong>Financials</strong> shows several years of income statement, balance sheet
        and cash flow. <strong>Holders</strong> shows institutional ownership and — relevant here —
        short interest figures. <strong>Analysis</strong> collects Wall Street estimates, which are
        useful as a sentiment gauge rather than as truth.
      </p>

      <h3>Finviz</h3>

      <p>
        Finviz is where you meet the screener. A screener is a filter over the entire listed universe:
        you specify numeric conditions and it returns only the companies that satisfy all of them.
        Market cap above $10 billion, P/E under 20, dividend yield above 2%, US-listed, healthcare
        sector — run it and thousands of companies become eleven.
      </p>

      <p>
        That changes the shape of research. Instead of starting from names you happen to have heard
        of, which is how most people accidentally build a portfolio out of advertising, you start
        from criteria you chose deliberately. Finviz also has heat maps for seeing an entire sector
        or index move at a glance.
      </p>

      <h3>Google Finance</h3>

      <p>
        The cleanest interface of the three and the fastest for a quick quote or a watchlist you
        check on your phone. It is lighter on fundamental data than the other two, so treat it as a
        dashboard rather than a research tool.
      </p>

      <h3>The primary sources</h3>

      <p>
        Every site above is copying from the same place. Public US companies file with the SEC, and
        those filings are free at SEC EDGAR: the <strong>10-K</strong> is the annual report, the{' '}
        <strong>10-Q</strong> is quarterly. Company investor-relations pages carry the same filings
        plus earnings releases and slide presentations written for shareholders.
      </p>

      <Callout variant="note" title="Read the Risk Factors first">
        <p>
          Section 1A of the 10-K is called Risk Factors, and it is the one place a company is legally
          obliged to argue against itself. Competition, dependence on a single customer, regulatory
          exposure, debt covenants — it is all disclosed there, in plain language, because omitting a
          known risk carries legal liability.
        </p>
        <p>
          Reading the Risk Factors of a company you are curious about is the single highest-value 20
          minutes of research available to a beginner, and almost nobody does it.
        </p>
      </Callout>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Tool</th>
              <th>Best for</th>
              <th>Cost</th>
              <th>Watch out for</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Yahoo Finance</td>
              <td>General research, statistics, financial statements, holders</td>
              <td>Free, paid tier exists</td>
              <td>Occasional stale or mismatched data points; verify anything decisive</td>
            </tr>
            <tr>
              <td>Finviz</td>
              <td>Screening the whole market, sector heat maps, fast comparison</td>
              <td>Free, paid tier for real-time and more filters</td>
              <td>Free quotes are delayed; a screen produces candidates, not conclusions</td>
            </tr>
            <tr>
              <td>Google Finance</td>
              <td>Quick quotes and watchlists</td>
              <td>Free</td>
              <td>Thin fundamental data; not enough on its own</td>
            </tr>
            <tr>
              <td>SEC EDGAR</td>
              <td>10-K and 10-Q filings, the original source of record</td>
              <td>Free</td>
              <td>Long and dense; use the table of contents and go straight to a section</td>
            </tr>
            <tr>
              <td>Investor relations page</td>
              <td>Earnings releases, presentations, dividend history</td>
              <td>Free</td>
              <td>Written to persuade; the numbers are audited, the framing is not</td>
            </tr>
          </tbody>
        </table>
      </div>

      <Callout variant="warning" title="Where ideas come from is not where facts come from">
        <p>
          Social media, YouTube and forums are legitimate for finding ideas. They are never acceptable
          for verifying them. If a video tells you a company has no debt, that claim gets confirmed on
          the balance sheet in the 10-K or it does not count.
        </p>
        <p>
          And remember who is talking. Anyone showing you a screenshot of gains has a position, and
          quite possibly an incentive for you to buy the thing they already own. That is not a
          conspiracy theory, it is just how attention and positioning interact. Assume it, and verify
          independently.
        </p>
      </Callout>

      <TryIt
        moduleId={moduleId}
        placeholder="Company 1 (speculative): market cap __, P/E __, beta __ | Company 2 (blue chip): market cap __, P/E __, beta __ | The metric that differed most was..."
      >
        <p>
          Pick two companies: one speculative name you have heard people talk about online, and one
          large established blue chip. Using Yahoo Finance’s Statistics tab or a Finviz screen, pull
          the same three metrics for each — market cap, P/E ratio, and beta.
        </p>
        <p>
          Write all six numbers down, then answer one question in a sentence: which of the three
          differs most dramatically between them, and what does that difference tell you about how
          the market is pricing each company’s future? If the speculative company has no P/E at all,
          say so and explain what that absence means.
        </p>
      </TryIt>

      <h2>What to carry forward</h2>

      <p>
        If you keep one idea from this lesson, keep this one: the GameStop winners were paid by the
        GameStop losers, and which group you land in is decided almost entirely by when you arrive.
        Nothing about the excitement of a story tells you where you are in that sequence. The numbers
        do, and you now know where to find them.
      </p>

      <p>
        The tools are not the hard part. Yahoo Finance, a screener, and the Risk Factors section of a
        10-K are all free and all available to you this afternoon. The hard part is using them before
        you have an opinion rather than after, because research done to confirm a decision you have
        already made is not research.
      </p>

      <p>
        Next lesson we build the discipline that makes all of this survivable: position sizing and
        risk management — how much of your money any single idea is allowed to touch, and why that
        number matters more than the idea itself.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
