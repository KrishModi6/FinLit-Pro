import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A stock has a beta of 1.5. Over a stretch where the market index falls 8%, what does beta alone suggest about the stock?',
    options: [
      'It fell about 5.3%',
      'It fell about 8%, because beta only applies to gains',
      'It fell about 12%',
      'It rose about 12%, because high beta hedges declines',
    ],
    answer: 2,
    explanation: 'Beta scales the market move in both directions: 1.5 × 8% = 12%. The tempting wrong answer is that beta only amplifies the upside — it does not. A beta above 1 historically meant harder falls as well as bigger rallies.',
  },
  {
    prompt: 'A stock with a beta of 0.4 is a low-risk investment.',
    type: 'tf',
    answer: false,
    explanation: 'Beta only measures the portion of a stock’s movement that tracks the market. A small biotech waiting on one trial result can post a low beta and still be close to a coin flip, because its risk is company-specific rather than market-driven. Low beta means low market sensitivity, not low risk.',
  },
  {
    prompt: 'Two reputable finance sites show betas of 1.12 and 1.34 for the same company on the same day. What is the most likely explanation?',
    options: [
      'One of the sites has a calculation bug',
      'They use different reference indexes and different lookback windows',
      'The company’s beta genuinely changed between the two page loads',
      'One site is quoting beta and the other is quoting standard deviation',
    ],
    answer: 1,
    explanation: 'Beta is the slope of a regression, and the slope depends on which index you regress against and how far back you look. Three years of monthly returns against one index will not match five years against another. Both numbers can be correctly computed and still disagree.',
  },
  {
    prompt: 'A portfolio holds 50% in a stock with beta 1.4, 30% in a stock with beta 1.8, and 20% in a stock with beta 0.7. What is the weighted-average portfolio beta?',
    options: ['1.30', '1.38', '1.63', '0.97'],
    answer: 1,
    explanation: '(0.50 × 1.4) + (0.30 × 1.8) + (0.20 × 0.7) = 0.70 + 0.54 + 0.14 = 1.38. Averaging the three betas without weighting them gives 1.30, which is the common mistake — position size matters as much as the beta itself.',
  },
  {
    prompt: 'Standard deviation of returns measures how much a stock moves relative to the market.',
    type: 'tf',
    answer: false,
    explanation: 'That description belongs to beta. Standard deviation measures total variability in a stock’s own returns, whether or not the market had anything to do with it. A stock can have a middling beta and still be one of the most volatile names you own.',
  },
]

export default function BetaAndVolatility({ moduleId }) {
  return (
    <>
      <p className="lead">Say the S&amp;P 500 has a rough month and closes down 6%. You open your account: one holding is down about 4%, another is down 11%. Neither company announced anything, and nothing in either business changed. That gap has a name, a number, and a very specific set of limits.</p>

      <h2>The question beta answers</h2>

      <p>When the market moves 1%, how much has this stock historically moved? That is the whole question. <Term k="beta">Beta</Term> is the answer, compressed into one number, and once you read it that way it stops feeling like statistics jargon.</p>

      <p>A beta of 1.0 means the stock has historically tracked the market roughly one-for-one. A beta of 1.5 means it swung about 50% harder — in both directions, which is the part people forget. A beta of 0.6 means it was steadier than the market, moving about six-tenths as much on an average move. Utilities and consumer-staples companies often sit below 1. High-growth technology names often sit above it.</p>

      <KeyTerm term="Beta" />

      <h2>Where the number actually comes from</h2>

      <p>Formally, beta is the slope of a regression of the stock’s returns against a market index’s returns over some historical window. Plot the index return on one axis and the stock return on the other, one dot per period, and draw the best-fit line through the cloud. The steepness of that line is beta.</p>

      <p>Two choices go into that calculation, and neither is usually displayed anywhere near the number itself. First, which index you regress against — the S&amp;P 500 is common in the US, but not universal. Second, the lookback window and the return frequency, most often three or five years of monthly returns. Change either input and the slope changes.</p>

      <Callout variant="note">
        <p>This is why two reputable websites can show different betas for the same company on the same day and both be right. Yahoo Finance labels its figure “Beta (5Y Monthly)” precisely because the label is part of the number. When you write a beta down, write down the window too, or you are recording half a fact.</p>
      </Callout>

      <h2>What each beta would have implied</h2>

      <p>Here is the arithmetic laid out. Read these as historical tendencies, not forecasts.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Beta</th>
              <th>Market up 10%</th>
              <th>Market down 10%</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>0.5</td>
              <td>+5%</td>
              <td>-5%</td>
            </tr>
            <tr>
              <td>1.0</td>
              <td>+10%</td>
              <td>-10%</td>
            </tr>
            <tr>
              <td>1.5</td>
              <td>+15%</td>
              <td>-15%</td>
            </tr>
            <tr>
              <td>2.0</td>
              <td>+20%</td>
              <td>-20%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Now the caveat that matters more than the table. These are average tendencies fitted across dozens of past periods, not rules that hold on any given day. A stock with a beta of 1.8 can fall on a day the market rallies, and often does, because on any single day company news swamps the market signal. Beta describes the pattern in the fog, not the weather this afternoon.</p>

      <h3>Negative beta</h3>

      <p>A negative beta means the asset tended to move opposite the market. It is rare among individual stocks. Gold-related assets sometimes drift toward zero or slightly negative over certain windows, which is where the “safe haven” reputation comes from.</p>

      <Callout variant="did-you-know">
        <p>The relationship is much less dependable than the reputation suggests. In a severe liquidity crunch, investors sell whatever is easiest to sell, and assets that normally zig while stocks zag can end up falling together. Treat a negative beta as an observation about one historical window, not a guarantee about the next crisis.</p>
      </Callout>

      <h2>What beta is not</h2>

      <p>This is the part of the lesson worth carrying out the door. Beta gets misread constantly, usually in the same four or five ways.</p>

      <ul>
        <li>It is not a measure of business quality. A wonderful company with rising profits can have a beta of 1.6, and a struggling one can have a beta of 0.8.</li>
        <li>It is not a prediction. It is a backward-looking description of returns that already happened.</li>
        <li>It is not stable. As a company changes — takes on debt, enters a new market, matures from growth into a slow compounder — its beta drifts. A five-year beta is partly a description of a company that no longer exists.</li>
        <li>It is close to meaningless for a stock with a short trading history. Fifteen months of data since an <Term k="ipo">IPO</Term> is not enough to fit a stable slope, and any beta you see for such a name deserves suspicion.</li>
      </ul>

      <h3>The limitation that costs people money</h3>

      <p>Beta only captures the part of a stock’s movement that moves with the market. Everything else — the lawsuit, the failed product, the accounting scandal, the trial result — is invisible to it.</p>

      <p>Picture a small pharmaceutical company whose entire value rests on one drug in late-stage trials. Its share price barely reacts to macro news, so its measured beta might come out around 0.5. On the day results are announced, the stock could double or lose three-quarters of its value. The risk is enormous, but it is idiosyncratic rather than market-driven, so beta never saw it coming and never claimed to.</p>

      <Callout variant="warning">
        <p>Low beta gets read as “safe” constantly, and it is not the same claim. Enron’s stock went from around 90 dollars in mid-2000 to essentially nothing when the company filed for bankruptcy in December 2001 — a collapse driven by fraud inside one company, exactly the kind of risk beta cannot see.</p>
        <p>If you are using a low beta to justify a large position, stop and ask a different question: what would have to go wrong at this specific company, and how much of my money is standing in front of that answer?</p>
      </Callout>

      <h2>The other volatility number</h2>

      <KeyTerm term="Volatility" />

      <p>Standard deviation of returns is the complementary measure, and the difference is worth stating cleanly. Beta measures market-relative movement: how much of this stock’s swing came from the market swinging. Standard deviation measures total <Term k="volatility">volatility</Term>: how widely this stock’s own returns scattered around their average, regardless of cause. A stock whose price jumps on its own news and ignores the index can post a modest beta and a large standard deviation at the same time. If you want to know how bumpy the ride was, standard deviation answers that. If you want to know how much of the bumpiness came from the market, beta answers that.</p>

      <h2>Beta as a portfolio dial</h2>

      <p>Beta is far more useful at the portfolio level than the single-stock level, because betas add up in a straightforward way: the beta of a portfolio is the weighted average of the betas of its holdings.</p>

      <p>Work a small one. Suppose a portfolio holds three positions:</p>

      <ol>
        <li>50% in a stock with beta 1.4, contributing 0.50 × 1.4 = 0.70</li>
        <li>30% in a stock with beta 1.8, contributing 0.30 × 1.8 = 0.54</li>
        <li>20% in a stock with beta 0.7, contributing 0.20 × 0.7 = 0.14</li>
      </ol>

      <p>Add the contributions: 0.70 + 0.54 + 0.14 = 1.38. If the market falls 20%, this portfolio would historically have fallen closer to 28%. On a 10,000 dollar balance, that is roughly a 2,800 dollar decline against the market’s 2,000 dollars — an extra 800 dollars of <Term k="drawdown">drawdown</Term> that came from the portfolio’s construction rather than from any single decision you remember making.</p>

      <Callout variant="real-talk">
        <p>Almost nobody builds a high-beta portfolio on purpose. It happens one reasonable decision at a time: you research companies you find interesting, the interesting ones are growth companies, growth companies tend to carry higher betas, and eight individually defensible picks turn into one portfolio that will fall much harder than the market in a bad year.</p>
        <p>Running the weighted average once a quarter takes about two minutes and tells you something owning eight different tickers cannot. Holding many names is not automatically <Term k="diversification">diversification</Term> if they all move to the same drumbeat.</p>
      </Callout>

      <h2>Where to find it</h2>

      <p>On a Yahoo Finance quote page, beta appears in the summary statistics under the price chart, labelled with its window. Most brokerage research pages, stock screeners and data providers show a version of it somewhere in the key-statistics block. The number is easy to find. The window it was computed over takes slightly more looking, and it is the part you actually need.</p>

      <TryIt moduleId={moduleId} placeholder="Company 1, beta and window… Company 2, beta and window… why the gap exists…">
        <p>Pick one utility or consumer-staples company and one high-growth technology company. Look up the beta for each on Yahoo Finance or your broker, and write down three things per company: the ticker, the beta, and the exact lookback window shown next to it.</p>
        <p>Then explain the gap in two or three sentences. What is it about each business — customer demand, revenue predictability, how much of the valuation rests on profits years away — that would make its share price more or less sensitive to the market as a whole?</p>
      </TryIt>

      <h2>The single idea to keep</h2>

      <p>Beta tells you how much of a stock’s past movement came from the market moving, and nothing else. It is a description, not a forecast, computed over a window someone else chose, on a business that has since changed.</p>

      <p>Use it as a dial for the whole portfolio rather than a verdict on one company. If your weighted-average beta drifts well above 1, you have taken on more market sensitivity than you probably intended, and no amount of confidence in the individual businesses changes the arithmetic of a bad year. If it sits below 1, you have given up some of the upside in exchange for a shallower fall — a real trade-off, not a free lunch.</p>

      <p>Next up: valuation ratios, starting with the P/E ratio and the earnings-per-share figure sitting underneath it — a number that describes what you are paying rather than how much the price moves.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
