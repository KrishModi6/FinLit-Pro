import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'Which type of risk can NOT be reduced by owning more stocks?',
    options: [
      'The risk that one company commits accounting fraud',
      'The risk that a CEO resigns unexpectedly',
      'The risk that the whole market falls in a recession',
      'The risk that one factory burns down',
    ],
    answer: 2,
    explanation: 'A recession, a rate shock or a war moves nearly everything at once. That is systematic risk, and spreading across 500 names does not remove it. The other three are company-specific (idiosyncratic) events, and those are exactly what diversification dilutes.',
  },
  {
    prompt: 'Two funds track the same index. Fund A charges 0.03% and Fund B charges 0.75%. Over 30 years on the same $10,000, the most accurate statement is:',
    options: [
      'The difference is trivial, since 0.72% is less than one percent a year',
      'Fund B costs you roughly $18,000 of ending value in this illustration',
      'Fund B must perform better, or nobody would pay the higher fee',
      'The fee only applies to profits, so it costs nothing in a flat market',
    ],
    answer: 1,
    explanation: 'The fee is charged on the whole balance every year, so it compounds against you. In the worked example the gap is close to $18,000, larger than the original investment. Fund B charging more is not evidence of skill, and the expense ratio is deducted from assets whether or not the fund made money.',
  },
  {
    prompt: 'Owning a market-cap-weighted S&P 500 index fund means your money is spread evenly across 500 companies.',
    type: 'tf',
    answer: false,
    explanation: 'Weighting is by company size, not by headcount. The largest handful of holdings routinely make up a substantial share of the whole fund, while the smallest members are a fraction of a percent each. You are diversified compared with owning one stock, and less evenly diversified than the phrase “500 companies” suggests.',
  },
  {
    prompt: 'What is the clearest structural difference between an ETF and a traditional mutual fund?',
    options: [
      'ETFs are guaranteed against losses; mutual funds are not',
      'ETFs trade throughout the session at a live price; mutual funds price once per day',
      'Only mutual funds can hold hundreds of companies',
      'ETFs are always cheaper than every mutual fund',
    ],
    answer: 1,
    explanation: 'An ETF trades on an exchange like a share, so you can buy at 10:14am at whatever the market is quoting. A mutual fund order fills at the net asset value struck after the close. Neither wrapper protects you from losses, both can hold hundreds of positions, and plenty of index mutual funds are as cheap as their ETF twins.',
  },
  {
    prompt: 'A portfolio holding five different technology companies is well diversified because it holds five separate stocks.',
    type: 'tf',
    answer: false,
    explanation: 'Stocks in the same sector share the same demand cycle, the same regulation and the same investor mood, so they tend to fall together. Five names in one sector is closer to one concentrated bet wearing five costumes than to five independent bets.',
  },
]

export default function EtfsAndDiversification({ moduleId }) {
  return (
    <>
      <p className="lead">Put every dollar you have into one company and let that company fail: your loss is 100%. Own five hundred companies and let one of them fail: your loss is roughly 0.2%. That gap between total wipeout and rounding error is the whole argument, and the strange part is that closing it costs almost nothing.</p>

      <h2>Two kinds of risk, only one of which you can escape</h2>

      <p>Every stock you own carries two separate hazards bundled together. The first is <strong>idiosyncratic risk</strong>, sometimes called company-specific risk: the CEO resigns, the drug trial fails, the accounting turns out to be fiction. Enron traded around $90 in mid-2000 and was worth close to nothing when it filed for bankruptcy in December 2001. Nothing about the broader economy caused that. It was one company, and if it was your only company, that was your whole outcome.</p>

      <p>The second is <strong>systematic risk</strong>, also called market risk: recessions, interest-rate shocks, wars, pandemics. These move nearly everything at once. You cannot own your way out of them, because there is no set of stocks that stays up when the entire market goes down.</p>

      <p>Here is the part worth memorising. Idiosyncratic risk is not compensated: the market does not pay you extra for taking a risk you could have removed for free. Systematic risk is the risk you are actually paid to bear. So <Term k="diversification">spreading your money across many companies</Term> is not a compromise or a way of playing it safe. It is deleting a risk that was never earning you anything.</p>

      <Callout variant="did-you-know">
        <p>Most of the benefit arrives faster than people expect. Moving from one stock to twenty removes a large share of company-specific risk. Moving from twenty to five hundred removes some more, but the curve flattens hard. The first twenty positions do the heavy lifting.</p>
      </Callout>

      <h2>What an ETF actually is</h2>

      <KeyTerm term="ETF" />

      <p>The mechanics are simpler than the acronym suggests. A fund manager assembles a basket of assets (say, every company in a broad US <Term k="index">market index</Term>), and then that basket itself is listed on an <Term k="exchange">exchange</Term> and trades under a ticker like any ordinary share. You place one order for one ticker, and you own a proportional slice of everything inside.</p>

      <p>That is genuinely new in historical terms. Building a five-hundred-company portfolio yourself would mean five hundred orders, five hundred commissions, and a rebalancing job you would never finish. An <Term k="etf">exchange-traded fund</Term> collapses that into a single line on your brokerage screen.</p>

      <h2>Index funds versus active managers</h2>

      <p>An <Term k="index fund">index fund</Term> does not try to be clever. It buys the index and holds it, in the index weights, with essentially no judgement involved. An actively managed fund pays a team of analysts to pick which companies to own and when, aiming to beat the same benchmark.</p>

      <p>The active pitch is intuitive: surely a room of trained professionals beats a rulebook. The evidence collected over decades by index providers and fund researchers points the other way. A large majority of active managers underperform their benchmark over long horizons once fees are subtracted, and the funds that beat it in one period are not reliably the ones that beat it in the next. This is one of the most consistently reported findings in the field, and the mechanism is not mysterious: active managers collectively are the market, so before costs their average result is roughly the market’s result, and after costs it is the market minus their fees.</p>

      <Callout variant="real-talk">
        <p>None of this means active management is a scam or that no manager has skill. It means skill has to clear a fee hurdle every single year, forever, and identifying that manager in advance is a much harder problem than it looks in a marketing brochure.</p>
      </Callout>

      <h2>The fee arithmetic, which is the whole lesson in one number</h2>

      <KeyTerm term="Expense Ratio" />

      <p>Suppose you invest a hypothetical $10,000 and it earns a hypothetical 8% a year for 30 years. The <Term k="expense ratio">annual fee the fund deducts</Term> comes off the top, so compare a broad index fund at 0.03% with an active fund at 0.75%.</p>

      <ol>
        <li>Net return in the cheap fund: 8% minus 0.03% equals 7.97% a year.</li>
        <li>Net return in the expensive fund: 8% minus 0.75% equals 7.25% a year.</li>
        <li>Cheap fund after 30 years: 10,000 multiplied by 1.0797 raised to the 30th power, which is roughly $99,800.</li>
        <li>Expensive fund after 30 years: 10,000 multiplied by 1.0725 raised to the 30th power, which is roughly $81,600.</li>
      </ol>

      <p>The gap is close to $18,000 (more than the amount you originally invested), produced by a fee difference of 0.72 percentage points a year. It compounds because the fee is charged on the entire balance annually, including on the growth you would otherwise have kept, and then on the growth that growth would have produced.</p>

      <p>Treat those figures as an illustration of the mechanism rather than a forecast. Returns are not a smooth 8%, and no fund guarantees anything. But the direction is not in doubt: fees are the one input to your return that you can know in advance and control exactly.</p>

      <h2>ETF or mutual fund?</h2>

      <p>Three practical differences. An ETF trades intraday at a live market price, while a mutual fund order fills once a day at the net asset value struck after the close. Mutual funds often set a minimum initial investment, whereas an ETF costs whatever one share costs, and many brokers now support fractional shares. In US taxable accounts the ETF creation-and-redemption process tends to generate fewer capital-gains distributions passed on to holders, which is a real but modest advantage that disappears entirely inside a tax-sheltered retirement account.</p>

      <h2>Sectors: five costumes, one bet</h2>

      <p>Companies are grouped into eleven standard sectors under the GICS classification, and stocks inside a sector tend to move together because they share customers, regulation, input costs and investor sentiment.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Sector</th>
              <th>What sits inside</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Information technology</td><td>Semiconductors, software, hardware</td></tr>
            <tr><td>Health care</td><td>Pharmaceuticals, insurers, device makers</td></tr>
            <tr><td>Financials</td><td>Banks, insurers, asset managers</td></tr>
            <tr><td>Consumer staples</td><td>Food, drinks, household products</td></tr>
            <tr><td>Consumer discretionary</td><td>Retail, cars, restaurants, travel</td></tr>
            <tr><td>Energy</td><td>Oil and gas producers, refiners, services</td></tr>
            <tr><td>Industrials</td><td>Aerospace, machinery, transport</td></tr>
            <tr><td>Utilities</td><td>Electricity, water, gas distribution</td></tr>
            <tr><td>Materials</td><td>Chemicals, mining, packaging</td></tr>
            <tr><td>Real estate</td><td>Property owners and REITs</td></tr>
            <tr><td>Communication services</td><td>Telecoms, media, interactive entertainment</td></tr>
          </tbody>
        </table>
      </div>

      <Callout variant="example">
        <p>An investor in early 2000 who owned five different technology companies would have described that as a diversified portfolio. Five tickers, five management teams, five business models. When the dot-com bubble deflated over the following two years, all five fell together and the investor discovered they had never owned five positions. They had owned one bet on a single sector, split five ways.</p>
      </Callout>

      <p>Sector diversification is the second layer. The first layer is owning many companies; the second is making sure those companies do not all depend on the same thing going right. A broad index fund gives you the second layer automatically, because the index spans all eleven sectors.</p>

      <h2>The concentration hiding inside your index fund</h2>

      <p>This is the part most people never check. The S&amp;P 500 is float-adjusted market-cap-weighted, which means each company’s share of the fund is proportional to its size, not to its headcount in the list. A company worth a hundred times another company gets about a hundred times the weight.</p>

      <p>The consequence is that the largest holdings dominate. In a market-cap-weighted fund the top ten names can represent a substantial share of the entire portfolio, while the smallest members sit at a fraction of a percent each. Your dollar is not split five hundred ways. It is heavily tilted toward whichever companies happen to be biggest right now, and in recent years the biggest companies have clustered in a small number of related sectors.</p>

      <Callout variant="note">
        <p>“I own the index, so I am diversified” is true relative to owning one stock, and less true than most people assume. Both halves of that sentence matter. Broad index funds remain one of the most sensible tools available to an ordinary investor; they are simply not the perfectly even spread the name implies.</p>
      </Callout>

      <TryIt moduleId={moduleId} placeholder="Ticker, expense ratio, number of holdings, top-10 combined weight, and one sentence on whether that surprised you.">
        <p>Pick one broad index ETF. A total-market or large-cap US fund is ideal. Open its official fund page on the issuer’s site, or look it up on Yahoo Finance, and find three things: the expense ratio, the number of holdings, and the combined weight of the top ten holdings. Write all three down, then add one sentence answering whether that last number was higher or lower than you expected, and what it tells you about how concentrated the fund really is.</p>
      </TryIt>

      <h2>The outer layer: beyond stocks entirely</h2>

      <p>Everything so far diversifies you within one asset class. The outermost layer is owning different classes altogether: bonds, which are loans to governments or companies and often behave differently from equities during downturns; international equity, which spreads you across economies and currencies rather than betting entirely on one country; and cash, which earns little but is the only holding that is guaranteed to still be there when you need it next month. How much of each belongs in a portfolio depends on your time horizon and your tolerance for watching a number fall, which is a question this course will keep returning to rather than answer for you.</p>

      <Callout variant="warning">
        <p>Two failure modes to watch. The first is over-diversification: owning eight funds that hold largely the same companies adds fees and confusion without adding a single new bet. Check overlap before you add anything.</p>
        <p>The second is more expensive. Plenty of products are shaped like ETFs and sold with the vocabulary of diversification while being concentrated, fragile bets: single-sector funds, narrow thematic funds built around a story, and leveraged or inverse ETFs that use derivatives to multiply daily moves. Leveraged funds in particular reset their exposure daily, so in a choppy market they can lose value even when the thing they track ends up flat. The Hard track takes these apart properly. Until then, the safe assumption is that a fund is exactly as diversified as its actual holdings list, not as its name.</p>
      </Callout>

      <h2>What to carry forward</h2>

      <p>The single idea: diversification is the one place in investing where you genuinely get something for nothing, because it removes a risk you were never being paid to take. Everything else in this lesson is detail about how to collect that free lunch cheaply and how to notice when a product only pretends to offer it.</p>

      <p>The two numbers to check before you ever buy a fund are its expense ratio and its top-ten concentration. The first tells you what the fund charges you every year regardless of results. The second tells you what you are actually betting on, which is frequently not what the fund’s name says.</p>

      <p>Next up: <Term k="position sizing">how much of your money any single holding should represent</Term>, and how to assemble the pieces from this lesson into a portfolio you can actually hold through a bad year.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
