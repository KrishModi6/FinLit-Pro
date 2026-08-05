import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A daily candle has a small body, a very long upper wick, and closes near where it opened. What actually happened during that day?',
    options: [
      'The stock was flat all day and barely traded',
      'Buyers pushed the price well above the open, then sellers pushed it back down before the close',
      'The stock gapped down at the open and never recovered',
      'A reversal is now confirmed and the price will fall tomorrow',
    ],
    answer: 1,
    explanation: 'The wick marks the high of the period, so price did travel up there; it just did not stay. The tempting answer is the last one: a long upper wick describes a struggle that already happened, it does not schedule tomorrow’s move.',
  },
  {
    prompt: 'A golden cross, the 50-day moving average crossing above the 200-day, is a forecast that the stock is about to rise.',
    type: 'tf',
    answer: false,
    explanation: 'Both averages are built entirely from past closing prices, so the cross can only happen after a trend has already been underway for weeks. It is a confirmation that something changed, not a prediction that something will.',
  },
  {
    prompt: 'Five consecutive closing prices are $30, $32, $31, $35 and $32. What is the 5-day simple moving average?',
    options: ['$31', '$32', '$33', '$160'],
    answer: 1,
    explanation: 'Add them to get $160, then divide by 5 to get $32. The last option is the sum, which is the most common slip: a moving average is a mean, not a total.',
  },
  {
    prompt: 'A stock has had an RSI above 70 for six straight weeks. What is the most accurate reading?',
    options: [
      'It is guaranteed to fall soon because it is overbought',
      'RSI is broken and should be reset',
      'Momentum has been strongly positive for a sustained period, which can continue',
      'The company’s earnings must be improving',
    ],
    answer: 2,
    explanation: 'RSI measures the size of recent gains against recent losses, nothing more. Strong stocks can sit above 70 for months. “Overbought” is a label for fast recent gains, not a countdown timer, and RSI says nothing about earnings.',
  },
  {
    prompt: 'Support and resistance levels are partly self-fulfilling: they hold in part because enough traders are watching the same round numbers and prior highs.',
    type: 'tf',
    answer: true,
    explanation: 'Some of the effect is genuine market memory (people who bought at a level remember it) and some is coordination, because widely watched levels attract clustered orders. Both explanations are real, and neither makes a level a guarantee.',
  },
]

export default function TechnicalAnalysis({ moduleId }) {
  return (
    <>
      <p className="lead">Switch any stock chart from a line to candlesticks and it stops looking like a price and starts looking like a code. Red and green blocks, thin spikes above and below, smooth lines drifting through the middle. None of it is mystical. Every mark is a compressed record of what buyers and sellers actually did, and reading it is mostly a matter of knowing what each mark is made of.</p>

      <h2>Two different questions</h2>
      <p>Fundamental analysis asks what a business is worth. Revenue, margins, debt, competitive position, the price you are paying for a claim on future earnings. Technical analysis asks something else entirely: it sets the business aside and studies the price and <Term k="volume">trading volume</Term> of the stock itself, on the theory that the record of what people have paid carries information about what they will pay next.</p>
      <p>Now the part most chart tutorials leave out. The academic evidence that individual traders consistently profit from chart patterns is weak. Barber and Odean’s well-known study of thousands of US brokerage accounts in the 1990s found that the households which traded most actively earned meaningfully lower net returns than the market, mostly through costs and poor timing. That is not proof that charts are useless. It is a strong hint that the edge people believe they are extracting from them is usually smaller than the trading costs of chasing it.</p>
      <p>So here is the honest framing for this lesson. These tools are excellent at describing what has already happened and at supporting risk decisions: how much this thing moves, where you would admit you were wrong, whether today is unusual. They are poor as prediction machines. Learn them properly, then hold them loosely.</p>

      <h2>Candlesticks: four numbers per period</h2>
      <p>A single <Term k="candlestick">candlestick</Term> covers one period. On a daily chart that is one trading day; on a five-minute chart, five minutes. Each candle encodes exactly four numbers: the open, the high, the low and the close for that period. Everything else about its shape follows from those four.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Part of the candle</th>
              <th>What it marks</th>
              <th>What it tells you</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Body</td>
              <td>The range between the open and the close</td>
              <td>Where the period started and finished: the net result</td>
            </tr>
            <tr>
              <td>Colour (green or hollow)</td>
              <td>Close above open</td>
              <td>The period ended higher than it began</td>
            </tr>
            <tr>
              <td>Colour (red or filled)</td>
              <td>Close below open</td>
              <td>The period ended lower than it began</td>
            </tr>
            <tr>
              <td>Upper wick</td>
              <td>From the top of the body to the high</td>
              <td>How far above the body price reached and failed to hold</td>
            </tr>
            <tr>
              <td>Lower wick</td>
              <td>From the bottom of the body to the low</td>
              <td>How far below the body price fell and recovered from</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Work through what a long upper wick actually means. Suppose a stock opens at $50, trades up to $56 during the day, then closes at $50.40. The body is a stubby green sliver and the wick above it is enormous. That single candle is telling you buyers were confident enough to bid the price up 12%, and sellers were willing enough to give all of it back before the close. Two crowds met at $56 and one of them won. That is a story about a struggle, not a symbol with a meaning.</p>
      <p>Named patterns follow from the same logic. A doji is a candle whose open and close are nearly identical, producing a body that is barely a line, conventionally read as indecision. A hammer has a small body with a long lower wick, read as a rejection of lower prices. Take both with real caution: studies of individual candlestick patterns have produced mixed and often unimpressive results, and reliability varies with the market, the timeframe and who is measuring.</p>

      <Callout variant="did-you-know">
        <p>Candlestick charting is generally traced to Japanese rice traders in the 1700s, and it reached a wide Western audience through Steve Nison’s 1991 book on the subject. The visual convention is centuries older than the indicators most people pair it with.</p>
      </Callout>

      <h2>Moving averages</h2>
      <KeyTerm term="Moving Average" />
      <p>A simple <Term k="moving average">moving average</Term> is the mean closing price over the last N periods, recalculated each period. That is the entire idea. The 50-day and 200-day versions are the conventional ones, mostly because enough people use them that they became the shared reference points.</p>

      <Callout variant="example" title="A 5-day SMA, by hand">
        <p>Closing prices for five days: $20, $22, $21, $24, $23. They sum to $110, and 110 divided by 5 is $22. That is the 5-day SMA on day five.</p>
        <p>On day six the stock closes at $25. Drop the oldest price and add the newest: 22 + 21 + 24 + 23 + 25 = $115, divided by 5 is $23. The average moved up a dollar. Nothing else happened: no signal, no magic, just a window sliding forward one day.</p>
      </Callout>

      <p>What moving averages are genuinely good at is smoothing. Daily prices are noisy enough that a real trend can be invisible inside the jitter; averaging fifty of them strips most of that out and leaves a line whose direction you can actually see. When a chart looks like chaos and the 200-day line is quietly rising, that is useful information.</p>
      <p>Two crossovers have names. A golden cross is the 50-day rising above the 200-day; a death cross is the 50-day falling below it. Both get treated as events on financial television. Both are, by construction, lagging: an average of the last 200 closes cannot move until those closes have already moved. By the time a golden cross prints, the trend it describes has usually been running for weeks. Moving averages confirm. They do not predict, and any source telling you otherwise is selling something.</p>

      <h2>RSI, and the mistake almost everyone makes</h2>
      <KeyTerm term="RSI" />
      <p>The relative strength index is a momentum oscillator bounded between 0 and 100, calculated by default over 14 periods. Conceptually it compares the average size of recent up moves to the average size of recent down moves. If gains have dominated, <Term k="rsi">RSI</Term> is high; if losses have dominated, it is low. Readings above 70 are conventionally labelled “overbought” and readings below 30 “oversold”.</p>
      <p>Those two words cause more damage than any other pair in technical analysis, because they sound like verdicts on value. They are not. RSI never looks at the business, the balance sheet or the price you are paying for earnings. It looks at the shape of recent price changes and nothing else.</p>

      <Callout variant="note" title="How the misreading plays out">
        <p>A stock rips higher on genuinely good news and its RSI hits 78. A reader who has learned “above 70 means sell” shorts it, or sells shares they intended to hold for years. The stock keeps climbing, because sustained buying is exactly what a strong trend looks like, and RSI stays above 70 for the next four months.</p>
        <p>The mirror version is worse. A company in real trouble prints an RSI of 18 and it looks like a bargain. But “oversold” during a collapse simply means the price is falling quickly, which is what a stock does on its way to being worth much less. Enron’s shares slid from around $90 in mid-2000 toward nothing by the December 2001 bankruptcy, and there were plenty of low RSI readings along the way.</p>
      </Callout>

      <p>Used well, RSI answers a narrow question: has this moved fast recently, relative to its own recent behaviour? That is worth knowing. It is not a schedule for reversals.</p>

      <h2>Support, resistance and volume</h2>
      <p>Support is a price area where buying has repeatedly appeared; resistance is one where selling has. Two honest explanations sit behind them. The first is market memory: someone who bought at $80 and watched it fall to $60 often sells the moment they are back to even, which creates real selling pressure near $80. The second is coordination: prior highs, prior lows and round numbers are visible to everybody, so orders cluster there and the level partly creates itself.</p>
      <p>Volume is the confirmation layer. A move on unusually heavy volume means many shares changed hands to produce it; the same move on thin volume means very few participants set that price. Neither guarantees anything, but a breakout through a widely watched level on heavy volume is a more substantial event than the same breakout on a quiet afternoon.</p>

      <Callout variant="real-talk">
        <p>If you are investing over years rather than trading over days, the most valuable thing a chart gives you is context, not entries. How <Term k="volatility">volatile</Term> has this actually been? How far is it below its high? Is today’s 4% drop unusual for this company, or an ordinary Tuesday?</p>
        <p>Those answers change how much you buy and whether you panic. They are worth more than any crossover signal, and you can read them off a plain one-year chart in about thirty seconds.</p>
      </Callout>

      <Callout variant="warning" title="The pattern-matching trap">
        <p>Humans find patterns in randomness. That is not a character flaw, it is how perception works, and price charts are noisy enough to contain any shape you go looking for. Generate a chart from coin flips and you will find head-and-shoulders formations, clean support lines and textbook breakouts in it.</p>
        <p>The practical test is simple: if an indicator only ever tells you to do what you already wanted to do, it is not informing your decision, it is decorating it. A tool you cannot lose an argument with is not a tool.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Ticker, what the chart showed you, and one thing it could not tell you…">
        <p>Open a one-year chart for any company you find interesting on Yahoo Finance or your broker. Switch the chart type to candlesticks, then add the 50-day and 200-day simple moving averages from the indicators menu.</p>
        <p>Write four or five sentences answering two things. First, what does this chart tell you: is the 200-day rising or falling, how far is the current price from the twelve-month high, and can you find a single day with an unusually long wick? Second, and be specific here, name at least two things this chart cannot tell you about the company.</p>
      </TryIt>

      <h2>What to keep</h2>
      <p>One idea survives this whole lesson: charts describe, they do not decide. A candle is four numbers about a period that has already ended. A moving average is an average of prices that have already printed. RSI is a summary of gains and losses that have already occurred. Every one of these is a rear-view mirror, and rear-view mirrors are genuinely useful right up until you try to steer with one.</p>
      <p>That does not make them worthless, and it does not make the people who use them foolish. Traders use these tools to size positions, place exits and avoid buying something that has already run 60% in a month. Long-term investors get real value from a chart as a volatility check before committing money. The failure mode is not using the tools; it is believing they see forward.</p>
      <p>Next up: risk management. Position sizing, drawdowns and the arithmetic of recovery, including why a 50% loss requires a 100% gain to get back to even.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
