import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'Two companies both returned about 9% last year. Company A moved between +3% and +14% during the year; Company B swung from −40% to +60% before landing at +9%. What does this tell you?',
    options: [
      'Company B is the better investment because it showed it can move fast',
      'Company A is the better investment because it made the same return with less drama',
      'They had similar returns but very different distributions of possible outcomes, which matters for how much you would size a position',
      'Nothing useful: only the final return matters',
    ],
    answer: 2,
    explanation: 'Stability describes the range of outcomes, not the outcome you happened to get. B’s wide path means the realistic bad year is far worse, so the same dollar position carries much more risk. Saying B is simply “better” or A is simply “better” both skip the actual lesson: identical returns can come from completely different risk profiles, and that difference drives position sizing rather than a verdict on quality.',
  },
  {
    prompt: 'A company has been a Dividend Aristocrat for 30 years. Which conclusion is actually supported?',
    options: [
      'Its dividend is guaranteed to keep growing',
      'It cannot fall more than 20% in a bear market',
      'It has generated enough real cash to raise its dividend through multiple recessions, which is evidence about the past business',
      'It is a low-risk investment regardless of the price you pay for it',
    ],
    answer: 2,
    explanation: 'The streak is a track record of cash generation surviving 2008, 2020 and every other rough stretch in between: genuinely informative evidence. But it is backward-looking. Aristocrats have been removed from the list after cutting or freezing dividends, and a great company bought at a terrible price is still a bad outcome. Nothing about the streak caps your downside.',
  },
  {
    prompt: 'A stock with a beta of 1.6 is expected to move about 60% more than the market in both directions, up and down.',
    type: 'tf',
    answer: true,
    explanation: 'Beta is a symmetric measure of historical sensitivity to market moves. A beta of 1.6 implies roughly a 1.6% move for every 1% market move, which cuts both ways. Students often remember only the upside half. Beta also says nothing about company-specific risk like a failed product or an accounting fraud, and it is calculated from past data, so it can shift.',
  },
  {
    prompt: 'An unstable stock is always a worse investment than a stable one.',
    type: 'tf',
    answer: false,
    explanation: 'Amazon fell over 90% after the dot-com bubble burst and was punishingly volatile for years, yet holders who stayed were rewarded enormously. Meanwhile plenty of “safe” large caps have gone nowhere for a decade while inflation ate the difference. Instability changes the width of the outcome distribution, which changes how large a position is sensible. It is not a quality grade.',
  },
  {
    prompt: 'You are running a three-minute triage on an unfamiliar ticker. Which single finding should most increase your caution?',
    options: [
      'The company pays no dividend',
      'The stock is down 15% over the past year',
      'The company is not profitable and is funding operations by regularly issuing new shares',
      'The company is in the technology sector',
    ],
    answer: 2,
    explanation: 'A business that burns cash and repeatedly issues shares dilutes existing owners and depends on capital markets staying friendly. If funding dries up, the equity can go to very little. Paying no dividend is normal for young growth companies, a 15% decline may simply be noise or opportunity, and “technology” is a sector label, not a risk measure.',
  },
]

export default function StableVsUnstable({ moduleId }) {
  return (
    <>
      <p className="lead">Ask most people to sort stocks into “safe” and “risky” and they will do it in about four seconds, using vibes. Coca-Cola in one pile, some crypto-adjacent penny stock in the other. That instinct is not wrong, exactly. It is just far too coarse to be useful, and it hides the question that actually matters.</p>

      <h2>Stability is a spectrum, and it is not about direction</h2>

      <p>There is no line in the market with stable companies on one side and unstable ones on the other. There is a long gradient, and almost everything you will ever look at sits somewhere in the middle of it. A regional utility is more stable than a mid-size software company, which is more stable than a pre-revenue biotech, which is more stable than a shell company with one press release and a message board following. Every one of those is a difference of degree.</p>

      <p>The bigger correction is this: stability is not a prediction that a stock goes up. It is a statement about the <em>range</em> of things that could plausibly happen. A stable stock has a narrow range: in a normal year it might move 10% either way, and in a genuinely bad year maybe 25%. An unstable stock has a wide one: it might double, or it might lose 70%, and both are inside the realm of ordinary. Two stocks can have the same expected return and completely different ranges around it.</p>

      <p>Once you hold that idea, a lot of confusing market behaviour stops being confusing. Stable does not mean it will rise. Unstable does not mean it will fall. Both mean: here is how wide the fan of possible futures is.</p>

      <h2>What actually makes a company stable</h2>

      <p>Stability is not one property. It is the accumulation of several structural traits, each of which narrows the fan a little. Here is what to look for, and more importantly, why each one matters.</p>

      <h3>Size and market position</h3>
      <p>A company with a large <Term k="market cap">market capitalisation</Term> is usually large because it won something, and winners are hard to dislodge. Displacing an entrenched incumbent takes capital, distribution, brand trust and time: four things a challenger rarely has all at once. Size also buys optionality: a big company can absorb a failed product line, a lawsuit, or a bad quarter without it being existential. A small company often cannot.</p>

      <h3>Predictable demand</h3>
      <p>People buy toothpaste in a recession. They pay their electricity bill, keep their car insurance, and refill their prescriptions. When household budgets tighten, the cuts land on the new laptop and the vacation, not on soap. A business whose demand barely notices the economic cycle has genuinely more predictable revenue, and predictable revenue is the raw material of a predictable stock.</p>

      <h3>A long operating history through multiple recessions</h3>
      <p>A company that has traded through 2000, 2008 and 2020 has already shown you how it behaves when things break. That is evidence, and evidence beats speculation. It is not proof. Enron had a long history right up until December 2001, when it filed for bankruptcy with a stock that had fallen from around $90 in mid-2000 to essentially nothing. Treat the record as a strong prior, not a guarantee.</p>

      <h3>A strong balance sheet</h3>
      <p>Low <Term k="debt to equity">debt relative to equity</Term> and real cash on hand mean the company controls its own timeline. Debt-heavy companies do not get to decide when to refinance; the credit market decides for them, and it tends to decide at the worst possible moment. Cash is what lets a business survive a bad two years instead of being forced to sell assets or issue shares at depressed prices.</p>

      <h3>Profitable now, not later</h3>
      <p>This one filters more aggressively than anything else on the list. A company that earns money today does not depend on anyone else’s willingness to fund it. A company that is projected to be profitable in 2029 depends on investors continuing to believe in 2029, every single quarter between now and then. When sentiment turns, the profitable business keeps operating and the unprofitable one starts negotiating.</p>

      <h3>Diversified revenue</h3>
      <p>Diversification inside a single company matters as much as diversification across your portfolio. If revenue comes from many products, many customers and many countries, no single failure can take the whole thing down. If 60% of revenue comes from one customer, that customer effectively controls the company’s future.</p>

      <h3>Low beta, and often a dividend record</h3>
      <p>A low <Term k="beta">beta</Term> tells you the stock has historically moved less than the market. It is a measured, quantitative confirmation of the qualitative traits above, which is exactly why it is useful: it is hard to argue with. And many stable companies pay a growing dividend, because a business that can commit real cash to shareholders every quarter for decades is implicitly telling you its cash flows are dependable. Not all stable companies pay dividends, though, so treat it as supporting evidence rather than a requirement.</p>

      <Callout variant="note">
        <p>None of these traits are binary. A company can be large, profitable and diversified while carrying uncomfortable debt. You are building a weight of evidence, not ticking a box.</p>
      </Callout>

      <h2>Blue chips</h2>

      <KeyTerm term="Blue Chip" />

      <p>The <Term k="blue chip">blue chip</Term> label gets thrown around loosely, so hold it to a standard: large, long-established, consistently profitable, financially sound, and a recognised leader in its industry. Coca-Cola, Johnson &amp; Johnson, Procter &amp; Gamble and Microsoft are the kinds of companies people mean (used here purely as illustrations of the category, not as suggestions).</p>

      <p>Now the part that gets skipped. Blue chips fall. In the 2008 financial crisis, household-name companies lost half their value or more, and in the March 2020 crash almost nothing was spared. The sell-off was broad and fast, and being famous did not exempt anyone. What blue chips tend to do is fall <em>less</em>, and recover more reliably, because the underlying business is still there when the panic ends. That is a meaningfully different claim from “they do not fall.”</p>

      <Callout variant="warning">
        <p>“Blue chip” is a description of a business, not a promise about a price. General Electric was a blue chip by any definition for decades and still lost the large majority of its value between 2000 and 2018. Quality reduces the odds of permanent loss; it does not remove them.</p>
      </Callout>

      <h2>Dividend Aristocrats</h2>

      <KeyTerm term="Dividend Aristocrat" />

      <p>A <Term k="dividend aristocrat">Dividend Aristocrat</Term> is an S&amp;P 500 member that has raised its dividend for at least 25 consecutive years. The streak is worth more than it first appears, and it is worth understanding why.</p>

      <p>To keep a 25-year increase streak alive, a company had to raise its dividend during the 2008 financial crisis and again in 2020, when revenue was collapsing and every instinct said conserve cash. You cannot fake that with accounting; raising a dividend requires actually sending money out the door. The streak is therefore a hard, cash-verified record of the business generating real profits through the worst conditions of the last quarter century. Management teams also treat these streaks as close to sacred (breaking one is a public admission of trouble), which means they will cut almost everything else first.</p>

      <p>The honest caveat: the streak describes the past. A company is an Aristocrat right up until the moment it isn’t, and companies have been removed from the list after freezing or cutting their dividend under pressure. The list is a well-constructed screen for durable businesses, not a guarantee about the next 25 years.</p>

      <h2>What makes a stock unstable</h2>

      <p>Instability comes from the mirror image of the traits above, plus a few of its own.</p>

      <ul>
        <li><strong>High <Term k="volatility">volatility</Term> and high beta.</strong> The stock has historically made large moves, and it amplifies market moves in both directions. Past movement is a decent predictor of future movement; calm stocks tend to stay calm and jumpy stocks tend to stay jumpy.</li>
        <li><strong>Small market cap.</strong> Less cushion to absorb a bad quarter, thinner trading, and a single institutional buyer or seller can move the price meaningfully on its own.</li>
        <li><strong>Unprofitable, funded by issuing shares or debt.</strong> Every new share issued makes your existing share a slightly smaller slice of the company. If capital markets tighten, the funding tap closes and the equity can be worth very little very quickly.</li>
        <li><strong>Single-product or single-customer concentration.</strong> One drug in trials, one contract, one platform that could change its rules. The whole company is effectively a bet on one outcome.</li>
        <li><strong>Story-driven valuation.</strong> The price reflects a future that has not happened yet. Stories can be revised in an afternoon; earnings cannot. This is why story stocks fall so hard on news that barely dents the actual business.</li>
        <li><strong>Heavy debt, especially when rates rise.</strong> Debt taken at 3% becomes a very different burden when it has to be refinanced at 7%. Interest expense eats profit before shareholders see anything.</li>
        <li><strong>Low volume and wide spreads.</strong> Thin trading means you may not get out near the price you see on the screen, and the gap between bid and ask is a cost you pay on the way in and again on the way out.</li>
        <li><strong>Attention detached from results.</strong> When a stock is moving on social-media momentum rather than earnings, the price is being set by a crowd that can leave as fast as it arrived. GameStop went from under $20 at the start of January 2021 to an intraday high near $483 on 28 January 2021, then fell roughly 90% within weeks. Those are pre-split figures; GME did a 4-for-1 split in July 2022.</li>
      </ul>

      <h2>Side by side</h2>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Trait</th>
              <th>Typical stable stock</th>
              <th>Typical unstable stock</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Market cap</td>
              <td>Large, often above $50B</td>
              <td>Small, frequently under $2B</td>
            </tr>
            <tr>
              <td>Beta</td>
              <td>Roughly 0.4 to 0.9</td>
              <td>Above 1.5, sometimes far above</td>
            </tr>
            <tr>
              <td>Profitability</td>
              <td>Profitable now, for many years running</td>
              <td>Losing money, profitability projected</td>
            </tr>
            <tr>
              <td>Revenue predictability</td>
              <td>Recurring, cycle-resistant demand</td>
              <td>Lumpy, tied to one product or contract</td>
            </tr>
            <tr>
              <td>Debt</td>
              <td>Modest, comfortably covered by cash flow</td>
              <td>Heavy, or growing to fund operations</td>
            </tr>
            <tr>
              <td>Dividend</td>
              <td>Often paid and steadily raised</td>
              <td>None, and none realistically coming</td>
            </tr>
            <tr>
              <td>Typical annual swing</td>
              <td>Around 10 to 20% peak to trough</td>
              <td>50% or more, in either direction</td>
            </tr>
            <tr>
              <td>What a bad year looks like</td>
              <td>Down 25 to 35%, business intact, recovery plausible</td>
              <td>Down 70 to 90%, dilution, going-concern questions</td>
            </tr>
          </tbody>
        </table>
      </div>

      <Callout variant="did-you-know">
        <p>Recovery arithmetic is brutally asymmetric and explains why the bottom row of that table matters so much. A 25% loss needs a 33% gain to break even. A 50% loss needs 100%. A 90% loss needs a 900% gain (a ten-bagger) just to get back to where you started.</p>
      </Callout>

      <h2>The nuance that separates a good analyst from a bad one</h2>

      <p>Here is where most students go wrong: they hear “unstable” and mentally file it as “bad”, and “stable” as “safe”. Both are mistakes, and they are expensive ones.</p>

      <p>Amazon was extraordinarily volatile for years. It fell more than 90% when the dot-com bubble burst, spent long stretches unprofitable by design, and was mocked repeatedly as a company that could not turn a profit. Holders who understood the business and sized their position so they could survive the drawdown were rewarded enormously. The instability was real; so was the outcome. Meanwhile, a long list of large, respectable, dividend-paying companies have quietly gone sideways for a decade while inflation reduced what those returns were worth. Nothing dramatic happened. That is its own kind of loss.</p>

      <p>What changes between a stable and an unstable stock is the distribution of outcomes: how wide the fan is, and how bad the left tail gets. And the correct response to a wider distribution is not avoidance, it is smaller size. A 2% position in a volatile company that falls 80% costs you 1.6% of your portfolio, which is survivable. The same company at 30% of your portfolio is a catastrophe. Stability is an input to position sizing. It is not a verdict on quality.</p>

      <Callout variant="real-talk">
        <p>The most common way beginners get hurt is not picking a volatile stock. It is picking a volatile stock and then sizing it as though it were a stable one, because the story was exciting and the position felt like a sure thing.</p>
      </Callout>

      <h2>A three-minute triage</h2>

      <p>You will not do a full analysis on every ticker someone mentions to you. You do not need to. Five questions, all answerable from a free finance site in a few minutes, will tell you roughly where a company sits on the spectrum.</p>

      <ol>
        <li><strong>Is it profitable today?</strong> Look at net income and earnings per share over the last few years. Positive and reasonably consistent is a different animal from negative and widening.</li>
        <li><strong>What is the market cap?</strong> This sets your expectations for how much cushion exists and how thinly the shares might trade.</li>
        <li><strong>What is beta?</strong> Under 1 means it has historically moved less than the market. Over 1.5 means it amplifies. Note it, do not worship it.</li>
        <li><strong>Does one product or one customer dominate revenue?</strong> Check the revenue breakdown in the annual report or the summary on the company’s investor-relations page. Concentration is the fastest route from stable to fragile.</li>
        <li><strong>Would this business still have customers in a recession?</strong> Answer it honestly and out loud. Insurance, electricity, groceries: yes. A luxury travel platform or a company selling optional software to startups: much less certain.</li>
      </ol>

      <Callout variant="example">
        <p>Suppose you run the triage on a hypothetical company and get: profitable for eight straight years, market cap around $180B, beta near 0.6, no product above 20% of revenue, and it sells household consumables. That is a strongly stable profile across all five.</p>
        <p>Now suppose you get: losing money, market cap around $400M, beta near 2.3, one drug in phase two trials, and demand that only exists if the drug is approved. That is a strongly unstable profile, which tells you to size it small if you touch it at all, not automatically that it is a bad company.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Company 1 (you think stable): profitable? / market cap? / beta? / concentration? / recession-proof? → where it landed. Then company 2…">
        <p>Pick two real companies: one you would call stable and one you would call risky. Look each one up on Yahoo Finance or your broker and run all five triage questions on both. Write down the actual numbers, not your impression of them.</p>
        <p>Then answer this: did either company land somewhere different from where your instinct put it? The interesting cases are the ones where a famous, comfortable-sounding name turns out to carry heavy debt, or where a company you assumed was speculative turns out to be quietly profitable.</p>
      </TryIt>

      <h2>What to carry forward</h2>

      <p>If you remember one sentence from this lesson, make it this one: stability describes the width of the range of outcomes, not the direction of the next move, and its real use is telling you how large a position should be.</p>

      <p>That reframing does a lot of work. It stops you dismissing volatile companies out of hand, it stops you treating blue chips as if they were savings accounts, and it gives you a concrete decision (size) instead of a vague feeling. The five-question triage is deliberately fast because a habit you actually run beats a rigorous process you skip.</p>

      <p>Next up: how to read the numbers you just looked up. We will take the metrics that appeared in the triage (market cap, beta, earnings per share, the price-to-earnings ratio) and go through what each one measures, what it hides, and the specific ways each can mislead you when read on its own.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
