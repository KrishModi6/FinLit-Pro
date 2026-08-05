import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'Two companies sit in the Dow. Company A trades at $400 per share, Company B at $40. Both rise exactly 1% today. Which one pushes the Dow further?',
    options: [
      'Company B, because a 1% move counts the same for every member',
      'Company A, because the Dow adds up dollar changes in share price',
      'Whichever company is larger by market cap, since the Dow weights by size',
      'Neither, because the Dow gives every member an equal weight',
    ],
    answer: 1,
    explanation: 'The Dow is price weighted, so it reacts to dollars per share, not percentages and not company size. A 1% move on a $400 stock is $4; on a $40 stock it is 40 cents. Option C is the tempting one because market-cap weighting is what the S&P 500 does, but the Dow has never worked that way.',
  },
  {
    prompt: 'The S&P 500 holds exactly 500 companies and gives each of them an equal weight.',
    type: 'tf',
    answer: false,
    explanation: 'Both halves are off. The count hovers around 500 rather than sitting locked on it, and the weighting is float-adjusted market cap, so the largest members move the index far more than the smallest ones do.',
  },
  {
    prompt: 'A major US index closes 14% below its record high. What is that conventionally called?',
    options: ['A bear market', 'A correction', 'A recession', 'Nothing: declines are unnamed until they pass 5%'],
    answer: 1,
    explanation: 'A correction is a decline of roughly 10% to 20% from a high; a bear market starts at 20%. A recession is a description of the economy, measured from output and employment data, not a threshold on an index chart.',
  },
  {
    prompt: 'Your portfolio falls 50%. What percentage gain from that lower level gets you back to where you started?',
    options: ['50%', '75%', '100%', '150%'],
    answer: 2,
    explanation: '$100 that falls 50% is $50, and $50 has to double to reach $100 again, a 100% gain. The instinct to answer 50% is exactly the arithmetic trap that makes deep losses so expensive.',
  },
  {
    prompt: 'Because the US market has recovered from every bear market so far, a recovery from any future bear market is guaranteed.',
    type: 'tf',
    answer: false,
    explanation: 'The historical record is real, and it is also not a promise. A perfect track record over one country and a few centuries is evidence, not a law of nature, and it says nothing about how long any particular recovery takes.',
  },
]

export default function IndicesAndMarketCycles({ moduleId }) {
  return (
    <>
      <p className="lead">Every evening someone on the news says the market was up or down by some number of points. There is no single object called “the market,” and nobody quotes a price on it. What is actually being reported is a number that a company built by picking a specific list of stocks and doing specific arithmetic to their prices.</p>

      <h2>A thermometer, not the weather</h2>

      <p>An <Term k="index">index</Term> is a measuring stick. It takes a defined basket of stocks, applies a fixed rule for how much each one counts, and produces a single number you can track over time. When that number falls 2%, nothing happened to the index itself. The shares underneath it moved, and the index reported the result.</p>

      <p>The thermometer analogy is worth holding onto. A thermometer reading 38 degrees did not heat the room, and smashing it will not cool the room down. Indices work the same way: they describe, they do not cause. This also means you cannot buy an index directly the way you buy a share of Apple. There is no certificate to own. What you can buy is a fund that holds the underlying companies and tries to match the index, which is a different thing wearing the same name.</p>

      <KeyTerm term="Index" />

      <h2>The three you will hear named</h2>

      <h3>S&amp;P 500</h3>

      <p>Roughly 500 large US companies, weighted by float-adjusted market capitalisation, meaning each company counts in proportion to the market value of its shares that are actually available to trade. The consequence matters more than the definition. Apple, when it sits near the top of the list, can move the index more in a single day than a large group of the smallest members combined. The 400th-largest member is technically in the index and practically invisible in it.</p>

      <p>Those 500 companies represent something on the order of 80% of total US stock market value. That is why the S&amp;P 500 is the default answer to “how did the market do today.” It is not the whole market, but it is close enough that professionals treat it as the benchmark and measure their own results against it.</p>

      <h3>Dow Jones Industrial Average</h3>

      <p>Thirty companies. Not five hundred, not a thousand. Thirty. And here is the part almost nobody knows: the Dow is <em>price weighted</em>, so a company influences it based on its share price, not its size.</p>

      <Callout variant="did-you-know">
        <p>Suppose one Dow member trades at $500 and another at $50, and both rise 1% today. The first stock gains $5 per share, the second gains 50 cents. The Dow adds up dollars, so the $500 stock counts ten times as much, even if the $50 company is worth three times more as a business.</p>
        <p>A stock split changes nothing about a company but instantly changes its influence on the Dow. That should tell you how much the index really measures.</p>
      </Callout>

      <p>Being honest about this: as a measure of the US market, the Dow is poor. A 30-company sample weighted by an arbitrary number survives mostly on tradition, a familiar name, and the fact that it has been quoted since 1896. Know what it is so you can discount headlines built on it.</p>

      <h3>NASDAQ Composite</h3>

      <p>Essentially every stock listed on the NASDAQ exchange, thousands of them, weighted by market cap. Because NASDAQ has been the listing home for so many technology companies, the Composite leans heavily toward tech. That tilt is the whole personality of the index: it swings harder than the S&amp;P 500 in both directions. From its March 2000 peak, the Composite fell roughly 78% over the following bust and did not regain that level until 2015. Fifteen years is a long time to be told that the market always comes back.</p>

      <h2>The rest of the map</h2>

      <p>Two more names give you the shape of everything the big three leave out. The Russell 2000 tracks about two thousand smaller US companies, so it is the usual reference point for small-cap performance and often behaves quite differently from the S&amp;P 500. MSCI World and the various total-market indices extend past the US border into developed markets globally, and broader versions add emerging markets on top.</p>

      <p>The US is the single largest slice of global stock market value. It is not the whole pie, and an investor who only ever watches the S&amp;P 500 has a genuinely incomplete picture of what stocks around the world are doing.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Index</th>
              <th>Holdings</th>
              <th>Weighting</th>
              <th>What it tells you</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>S&amp;P 500</td>
              <td>About 500 large US companies</td>
              <td>Float-adjusted market cap</td>
              <td>The standard read on the US market</td>
            </tr>
            <tr>
              <td>Dow Jones Industrial Average</td>
              <td>30 large US companies</td>
              <td>Share price</td>
              <td>Mostly headline value and history</td>
            </tr>
            <tr>
              <td>NASDAQ Composite</td>
              <td>Thousands of NASDAQ listings</td>
              <td>Market cap</td>
              <td>How tech-heavy growth stocks are doing</td>
            </tr>
            <tr>
              <td>Russell 2000</td>
              <td>About 2,000 smaller US companies</td>
              <td>Market cap</td>
              <td>The health of small caps</td>
            </tr>
            <tr>
              <td>MSCI World / total market</td>
              <td>Hundreds to thousands, many countries</td>
              <td>Market cap</td>
              <td>Whether the whole world is moving, or just the US</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>How you actually own one</h2>

      <p>Since the index itself is just arithmetic, ownership happens through a fund that buys the components and charges you a small annual fee for the trouble. VOO, SPY and IVV are three well-known funds tracking the S&amp;P 500: same index, three different providers, and their returns land in nearly the same place before fees. QQQ is a familiar NASDAQ-linked example, though it tracks the NASDAQ-100 rather than the full Composite, which is a distinction the ticker does not advertise.</p>

      <p>Those are illustrations of the mechanism, not picks. The Intermediate lesson on the <Term k="etf">exchange-traded fund</Term> covers how these funds are constructed, what an expense ratio quietly removes from your returns each year, and how to compare two funds that claim to track the same thing.</p>

      <h2>Bulls, bears and the words in between</h2>

      <p>Prices do not rise in a straight line, so the industry invented labels for the phases. A <Term k="bull market">bull market</Term> is a sustained stretch of rising prices; the label is used loosely, though a 20% rise off a low is a common marker. A <Term k="bear market">bear market</Term> is a decline of 20% or more from a recent high. A <Term k="correction">correction</Term> is a decline of roughly 10% to 20%.</p>

      <p>These are conventions, not laws of physics. No committee rings a bell at exactly minus 20%, and nothing mechanical changes as an index crosses that line. The thresholds exist because journalists and analysts needed shared vocabulary, and shared vocabulary is genuinely useful, as long as you remember it was chosen by people rather than discovered in nature.</p>

      <Callout variant="note">
        <p>Corrections have historically shown up about once a year on average. Not every year, and never on schedule, but often enough that a 10% drop is ordinary weather rather than evidence that something has broken.</p>
      </Callout>

      <h2>What the record shows, and what it does not</h2>

      <p>Two patterns hold up in the historical data. Bull markets have lasted considerably longer than bear markets, and the US market has recovered from every bear market so far and gone on to new highs.</p>

      <p>Read that sentence again and notice how much work “so far” is doing. It is a description of what has happened, not a guarantee about what will. Recoveries have taken anywhere from months to more than a decade, and an investor who needed the money during the slow ones did not get to wait. Other countries offer harsher examples. Treat the record as encouraging evidence about long horizons, not as a promise with a delivery date.</p>

      <p>The reason this matters is behavioural. Bear markets are where permanent mistakes get made, because selling near the bottom converts a paper loss into a realised one and then leaves you out of the recovery you were waiting for.</p>

      <Callout variant="warning" title="The arithmetic of getting back to even">
        <p>A <Term k="drawdown">drawdown</Term> is unkind in a way most people underestimate. Start with $100. A 20% fall leaves $80, and $80 has to gain 25% to return to $100. A 50% fall leaves $50, which needs a 100% gain. A 90% fall leaves $10, which needs a 900% gain.</p>
        <p>The hole gets steeper the deeper it goes. This is the real argument for owning things you can hold through a bad year, and the Intermediate lesson on building a stable core is where that gets turned into an actual plan.</p>
      </Callout>

      <Callout variant="real-talk">
        <p>“The market is down 3% today” almost always means the S&amp;P 500 is down 3%. It may say very little about what you own. If your money sits in small caps, in a single company, or in international funds, your day can look nothing like the headline.</p>
        <p>Check your own holdings before you react to a number describing 500 companies you may not own.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Paste your three numbers, then write two or three sentences comparing them.">
        <p>Go to Yahoo Finance and look up three symbols: ^GSPC for the S&amp;P 500, ^DJI for the Dow, and ^IXIC for the NASDAQ Composite. Record the one-year percentage change for each one, along with the date you checked.</p>
        <p>Then answer in a few sentences: which of the three moved most over that year, and does the weighting rule you learned above help explain why? If the three numbers are close, say so. That is a real finding too.</p>
      </TryIt>

      <h2>The one thing to keep</h2>

      <p>An index is a rule for summarising a list of companies, and the rule decides what the number can honestly tell you. Once you know the S&amp;P 500 weights by size, the Dow weights by share price, and the NASDAQ Composite is packed with technology, the daily market report stops being one vague number and becomes three specific claims you can evaluate.</p>

      <p>The cycle vocabulary works the same way. Correction, bear market, bull market are conventions worth knowing precisely, so that a 12% drop registers as a named and ordinary event instead of a reason to panic. What history offers is context, not a guarantee, and the drawdown arithmetic is the reason that distinction is worth money.</p>

      <p>Next up: how to read a stock quote line by line: bid, ask, volume and the rest of the numbers your broker shows you the moment you type in a ticker.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
