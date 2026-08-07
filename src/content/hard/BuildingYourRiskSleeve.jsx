import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'A $10,000 portfolio is split 90/10 between a broad index core and a risky sleeve. Over a year the sleeve goes to zero and the core finishes flat. What happened to the portfolio?',
    options: ['It fell about 1%', 'It fell about 10%', 'It fell about 50%', 'It fell about 90%'],
    answer: 1,
    explanation: 'The sleeve was $1,000 of a $10,000 portfolio, so losing all of it costs 10% of the total. People instinctively pick the 90% answer because a total loss feels total, but the whole point of the structure is that a wipeout in the satellite is a bad year, not a ruined one. The core never funded the sleeve, so the core is untouched.',
  },
  {
    prompt: 'If your risky sleeve grows from 10% of your portfolio to 30% because the positions worked, your overall risk level has not changed, since it is the same money you were always willing to lose.',
    type: 'tf',
    answer: false,
    explanation: 'Once the sleeve is 30% of the portfolio, a total loss there costs you 30%, not 10%. The dollars at risk tripled. You drifted into a much more aggressive portfolio without ever making the decision to, which is exactly why rebalancing exists: it forces the drift back into a choice you actually make on purpose.',
  },
  {
    prompt: 'Which of these qualifies as a catalyst in the technical sense?',
    options: ['The company has a compelling long-term story', 'A regulatory decision scheduled for 14 March', 'The chart looks like it wants to break out', 'A lot of people are posting about the stock'],
    answer: 1,
    explanation: 'A catalyst is a specific, dated event that forces the market to re-price: earnings, a regulatory ruling, a launch, a court decision. A compelling story is a thesis, not a catalyst, and it can stay uncompelling to everyone else for a decade. Chart shapes and social chatter have no scheduled resolution date at all.',
  },
  {
    prompt: 'A stock has short interest equal to 25% of its float. What does that number actually tell you?',
    options: ['The stock is very likely to squeeze upward', 'The company is probably committing fraud', 'A large amount of capital has taken the view that the price will fall', 'The stock cannot fall much further from here'],
    answer: 2,
    explanation: 'High short interest describes positioning: many people researched this company and concluded it is worth less. Sometimes crowded shorts unwind violently, which is where the squeeze narrative comes from, but far more often heavily shorted stocks keep falling because the short sellers were right. Treating the number as a squeeze forecast is reading a description as a prediction.',
  },
  {
    prompt: 'Your sleeve is wiped out in March. Your funding rule says the sleeve is topped up once a year in January. What does the rule require you to do?',
    options: ['Sell part of the core to refill the sleeve now', 'Add fresh savings immediately so you can trade back to even', 'Leave the sleeve empty until the next scheduled funding date', 'Take one much larger position to recover the loss faster'],
    answer: 2,
    explanation: 'A dead sleeve stays dead until the calendar says otherwise. Refilling right after a loss is the single most common way a 10% allocation quietly becomes half the portfolio, because the refill is always motivated by the loss rather than by a plan. Selling the core is worse still: it converts a survivable setback into permanent damage to the part that was supposed to be untouchable.',
  },
]

export default function BuildingYourRiskSleeve({ moduleId }) {
  return (
    <>
      <p className="lead">Almost nobody destroys a portfolio with one catastrophic decision. They do it in increments: one speculative position that felt exciting, then a second to make back the first, then a third funded by selling something boring and permanent. The defence is structural rather than emotional. You decide in advance how much of your money is allowed to be adventurous, and then you build a wall around it.</p>

      <h2>Core and satellite</h2>

      <p>The structure has a name that professionals use: core and satellite. The core is the part that is supposed to be dull. Broad index funds, held permanently, rebalanced on a schedule, never traded on news. It is where <Term k="diversification">owning hundreds of companies at once</Term> does its quiet work, and its job is to be there in twenty years whether or not you turn out to be good at picking stocks.</p>

      <p>The satellite is the risky sleeve. It is small, it is deliberate, and it is money you have honestly decided you could lose entirely without changing anything about your life. Not money you would be annoyed to lose. Money you could watch go to zero and still sleep.</p>

      <p>A commonly discussed starting frame is 90/10: ninety per cent core, ten per cent sleeve. Treat that as one reference point, not a rule. The right number depends on how much you earn, how stable that income is, what you already have saved, and how you actually behave when a position is down 40%. For plenty of people the honest answer is 100/0, and choosing that is not a failure of nerve.</p>

      <h2>What 90/10 does to the arithmetic</h2>

      <p>Take a hypothetical $10,000 portfolio at 90/10. The core holds $9,000. The sleeve holds $1,000. Here is what three different years look like if the core happens to finish flat, so we can see the sleeve on its own.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Scenario</th>
              <th>Core</th>
              <th>Sleeve</th>
              <th>Portfolio</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Sleeve goes to zero</td>
              <td>$9,000</td>
              <td>$0</td>
              <td>$9,000</td>
              <td>-10%</td>
            </tr>
            <tr>
              <td>Sleeve doubles</td>
              <td>$9,000</td>
              <td>$2,000</td>
              <td>$11,000</td>
              <td>+10%</td>
            </tr>
            <tr>
              <td>Sleeve triples</td>
              <td>$9,000</td>
              <td>$3,000</td>
              <td>$12,000</td>
              <td>+20%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>Look at the shape of that. The worst case is capped at minus ten per cent, and the core is completely intact underneath it. The upside is not capped at anything in particular. That asymmetry is the entire argument for a sleeve, and it exists only because the sleeve is small. At 50/50 the same three rows read minus fifty, plus fifty, plus one hundred, and the first of those is not a bad year, it is a decade of compounding erased.</p>

      <h2>Five rules that keep a sleeve a sleeve</h2>

      <ol>
        <li>It is funded once, from savings, on a schedule you set in advance. Never by selling the core.</li>
        <li>Losses are not replenished. If the sleeve dies in March, it stays dead until the next funding date.</li>
        <li>Gains above a threshold are harvested into the core. If the sleeve doubles, move the profit into the index fund. This is the mechanism that converts luck into permanent progress, and without it every win just becomes a bigger bet.</li>
        <li>Cap the number of concurrent positions, three or four for most people. This is <Term k="position sizing">deciding in advance how large any one bet is allowed to be</Term>, and it also keeps the sleeve small enough that you can actually follow every name in it.</li>
        <li>Every position is written up before entry. No write-up, no trade. We will get to the template.</li>
      </ol>

      <h2>The rebalancing trap</h2>

      <p>Suppose your sleeve works. The $1,000 becomes $5,000 while the core drifts up to $10,000. You now have $15,000, and a third of it is speculation. You have a 67/33 portfolio, and at no point did you sit down and decide to run a third of your money in high-risk positions. Success moved you there.</p>

      <p>That matters because the risk moved with it. A 50% <Term k="drawdown">fall from the sleeve peak</Term> used to cost you $500. Now it costs $2,500, which is about 17% of everything you own. Rebalancing is what keeps the structure real: you sell the sleeve back down to its target weight, put the difference in the core, and go back to the risk level you actually chose.</p>

      <Callout variant="warning" title="Sleeve creep is the real failure mode">
        <p>The thing that ruins people is almost never one bad pick. It is topping up after a loss. You put in $1,000, lose $600, add $600 back because the thesis is still good. Then the position halves again and you add another $1,000 because now it is cheap. Six months later you have put $2,600 into a sleeve you budgeted $1,000 for. On a $10,000 portfolio that is a 26% speculative allocation, and you never once sat down and decided to run one.</p>
        <p>The rule that stops this is boring and absolute: the sleeve gets funded on dates, not on feelings.</p>
      </Callout>

      <h2>Researching a play</h2>

      <p>The structure tells you how much you can risk. It says nothing about whether a specific idea deserves any of it. Work the following sequence in order, and be willing to stop at any step.</p>

      <h3>What does this company actually do?</h3>

      <p>State the business and how it makes money in two sentences. Who pays it, for what, and roughly how much of what they pay is left over. If you cannot do this without opening a browser tab, you do not have an investment idea, you have a ticker you heard about. Stop here. This one filter removes most bad trades before they exist.</p>

      <h3>Can it fund itself?</h3>

      <p>If the company is profitable, good. If it is not, find the cash burn: how much money it loses each quarter, and how much cash it has. Cash divided by quarterly burn gives you the runway. A company with $200 million in cash burning $50 million a quarter has four quarters before it must raise money or shrink, and that deadline will shape everything the stock does.</p>

      <h3>What would have to be true?</h3>

      <Callout variant="example">
        <p>Suppose a company has a market cap of $20 billion. For the stock to double, the market has to conclude the entire business is worth $40 billion. So ask: what revenue, at what margin, would justify $40 billion? Then ask whether the total market for the product is even large enough to contain that.</p>
        <p>If the whole global market for what they sell is $5 billion a year, you have just learned something no price chart would have told you. Framing the upside as a valuation rather than a percentage is the single most clarifying habit in speculative research.</p>
      </Callout>

      <h3>What is the catalyst, and when exactly?</h3>

      <p>A thesis without a <Term k="catalyst">dated event that forces the market to re-price</Term> has no reason to resolve. It can be completely correct and simply never pay you, because being right about a company and being paid for it are different things separated by time.</p>

      <KeyTerm term="Catalyst" />

      <p>Write the date down. Earnings, a regulatory decision, a product launch, a court ruling, a contract award. If you cannot name one in the next twelve months, you are not making a speculative bet, you are just holding something volatile and hoping.</p>

      <Callout variant="warning" title="Holding through earnings is a different bet">
        <p>Know your company’s exact earnings date before you enter, because the position you hold the day before earnings is not the position you researched. It is a bet on one number, released after the close, that can move the stock 20% before you get any chance to react.</p>
        <p>That may be exactly the bet you want. Just make it deliberately, and size it as its own decision rather than discovering on a Tuesday evening that you were holding through a coin flip.</p>
      </Callout>

      <h3>Who is on the other side?</h3>

      <p>Check the <Term k="short interest">proportion of the tradable shares that have been sold short</Term>, usually quoted as a percentage of float.</p>

      <KeyTerm term="Short Interest" />

      <Callout variant="real-talk">
        <p>High short interest is often sold to beginners as a squeeze setup. Be honest about what it actually is: evidence that a lot of capital has studied this company and concluded the price should fall. Those people are sometimes wrong, and when a crowded short unwinds the move can be violent. They are also frequently right, and heavily shorted stocks very often keep falling.</p>
        <p>Short interest describes positioning. It does not predict a squeeze. Use it to understand who you are trading against, not as a reason to buy.</p>
      </Callout>

      <p>Then look at insider transactions in the SEC Form 4 filings. Sustained executive selling with no buying is not proof of anything, but a pattern is worth explaining before you commit money.</p>

      <Callout variant="note" title="Track the share count">
        <p>Pull the share count from filings across the last three or four years. If a company keeps issuing new shares, your ownership stake shrinks every year even when the business improves, because the same pie is being cut into more slices. A company that grew revenue 40% while raising the share count 50% made its shareholders poorer.</p>
      </Callout>

      <p>Last, go find the strongest bear case, written by someone who genuinely holds the opposite view. Not a strawman you constructed to knock down. If you cannot state the bear case well enough that a bear would nod at it, you do not understand the trade yet.</p>

      <h2>The pre-trade checklist</h2>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Where to find it</th>
              <th>Red flag</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Business model</td>
              <td>Annual report, investor relations deck</td>
              <td>You cannot state it in two sentences</td>
            </tr>
            <tr>
              <td>Profitability and runway</td>
              <td>Quarterly filings, cash flow statement</td>
              <td>Under a year of cash at current burn</td>
            </tr>
            <tr>
              <td>Market cap and the double</td>
              <td>Any quote page, then your own arithmetic</td>
              <td>Doubling needs an implausible valuation</td>
            </tr>
            <tr>
              <td>Dated catalyst</td>
              <td>Company IR calendar, regulatory docket</td>
              <td>No dated event in the next year</td>
            </tr>
            <tr>
              <td>Earnings date</td>
              <td>IR calendar, broker earnings tab</td>
              <td>You do not know it</td>
            </tr>
            <tr>
              <td>Short interest</td>
              <td>Exchange reports, broker data page</td>
              <td>You are reading it as a squeeze forecast</td>
            </tr>
            <tr>
              <td>Dilution history</td>
              <td>Share count over several years of filings</td>
              <td>Share count rising every single year</td>
            </tr>
            <tr>
              <td>Insider activity</td>
              <td>SEC Form 4 filings</td>
              <td>Sustained selling, no buying</td>
            </tr>
            <tr>
              <td>Bear case</td>
              <td>Someone who publicly holds the opposite view</td>
              <td>You cannot state it convincingly</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>The written thesis</h2>

      <p>Before any sleeve position, write these eight lines. It takes fifteen minutes and it is the highest-value habit in this entire lesson.</p>

      <ol>
        <li>What it is: the company, the ticker, and what it sells.</li>
        <li>What I believe: the specific thing I think is true about this business.</li>
        <li>Why the market disagrees: what other people are pricing in, and why I think that is wrong.</li>
        <li>The catalyst: the exact event and the exact date.</li>
        <li>My size: the dollar amount, and what percentage of my sleeve and my total portfolio it represents.</li>
        <li>My exit if I am right: the price or the event that means the thesis played out.</li>
        <li>My exit if I am wrong: the price, the date, or the news that means I was wrong, decided now while I am calm.</li>
        <li>The date I wrote this.</li>
      </ol>

      <TryIt moduleId={moduleId} placeholder="1. What it is… 2. What I believe… 3. Why the market disagrees… (continue through all eight lines)">
        <p>Pick any speculative idea you have actually been curious about, and write the complete eight-line thesis for it using real numbers you look up yourself. Get the market cap and the next earnings date from a quote page such as Yahoo Finance, and find the catalyst date on the company’s own investor relations calendar.</p>
        <p>Then do the part most people skip: set a calendar reminder for the catalyst date, and a second one for three months from today that says review this thesis. You do not have to buy anything. The exercise is the write-up.</p>
      </TryIt>

      <h2>Why the write-up is the whole point</h2>

      <p>The write-up is not bureaucracy and it is not there to slow you down, although slowing you down is a pleasant side effect. It exists so that six months later you can answer one question: was I skilled, or was I lucky?</p>

      <p>Without a written thesis, every winner feels like insight and every loser feels like bad luck, and you learn nothing from either. With one, you can check whether the thing you predicted is the thing that actually happened. Sometimes you will find that you were right about the company and paid for an unrelated reason. That is a loss disguised as a win, and it is far more dangerous than an honest loss, because it teaches you to repeat a process that did not work.</p>

      <p>That distinction is the entire difference between improving and just playing. Keep the sleeve small, keep the core untouched, harvest gains into the boring part, and write down what you believed before you find out. The next lesson picks up where the write-up ends: reviewing your own decisions honestly, and learning to tell a good decision with a bad outcome apart from a bad decision that happened to pay.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
