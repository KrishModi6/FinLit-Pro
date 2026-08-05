import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'An index falls 10% one day and rises 11.1% the next, ending roughly flat. A 3x daily leveraged ETF tracking it would end those two days approximately where?',
    options: [
      'Also roughly flat, since the index is flat',
      'Up about 3.3%, because leverage amplifies the recovery',
      'Down about 6.7%, because each day’s return compounds off a smaller base',
      'Down exactly 30%, because the first day’s loss is permanent',
    ],
    answer: 2,
    explanation: 'The fund goes 0.70 × 1.333 = 0.9331, so it is down about 6.7%. The tempting answer is “flat”, because we assume the fund tracks the index over the period. It does not. It targets 3x the DAILY return and rebalances every day, so the second day’s gain is calculated on a base that already shrank by 30%.',
  },
  {
    prompt: 'Because a 3x leveraged ETF is designed to deliver three times the daily move, holding it for a full year should deliver roughly three times that year’s index return.',
    type: 'tf',
    answer: false,
    explanation: 'Daily targeting does not add up to period targeting. Over many days the returns compound off a moving base, and in choppy markets the fund can lose value even when the index ends higher. The prospectuses of these funds say directly that they are not designed to be held long term.',
  },
  {
    prompt: 'Why is poor liquidity such a serious problem in a thinly traded penny stock?',
    options: [
      'It means the company pays no dividend, so there is no income to offset losses',
      'It means the quoted price may not be a price at which you can actually sell any real quantity',
      'It means the stock is banned from major exchanges by regulation',
      'It means the share price updates only once per day',
    ],
    answer: 1,
    explanation: 'A quote is only meaningful if there is a buyer behind it. With few buyers and a wide spread, selling a real position pushes the price down as you go, so the screen price and your exit price can differ enormously. The dividend answer is tempting but irrelevant: plenty of perfectly liquid stocks pay nothing.',
  },
  {
    prompt: 'Which of these positions can leave you owing money beyond what you originally put in?',
    options: [
      'Buying shares of a broad index fund',
      'Buying a call option and holding it to expiry',
      'Buying stock with borrowed money in a margin account',
      'Buying shares of a 3x leveraged ETF',
    ],
    answer: 2,
    explanation: 'Margin is a loan, and the loan does not shrink when the position does. If the collateral falls far enough the broker liquidates, and any shortfall is a debt you owe. A bought option and a leveraged ETF are both brutal (you can lose everything you paid), but neither can take more than 100% of that amount.',
  },
  {
    prompt: 'In this course, “high risk” is defined as a wide distribution of outcomes with meaningful probability of total loss, rather than simply “the price moves around a lot”.',
    type: 'tf',
    answer: true,
    explanation: 'Movement alone is not the issue. A broad index fund moves plenty and has never gone to zero. The instruments in this track are different in kind: a real fraction of the possible outcomes end at nothing, and that is what the word “risk” is doing in the phrase.',
  },
]

export default function WhatHighRiskMeans({ moduleId }) {
  return (
    <>
      <p className="lead">Somebody is going to show you a screenshot of a 400% gain. It will be on a phone screen, it will look effortless, and nobody will show you the account that went to zero. This track exists because you will meet these instruments whether or not anyone explains them properly, and understanding how a thing works is exactly as useful for deciding to stay away from it as for deciding to use it.</p>

      <Callout variant="real-talk">
        <p>I am not going to tell you these products are evil, and I am not going to tell you they are fine. Each one has a real mechanism and a real failure mode, and the failure modes are specific enough to name. That is the whole lesson: learn the mechanism, then decide.</p>
      </Callout>

      <h2>Penny stocks</h2>

      <p>A <Term k="penny stock">penny stock</Term> is a share trading at a very low price, conventionally under $5, usually issued by a company small enough that it never qualified for a major exchange listing. Many trade over the counter, through dealer networks rather than on the NASDAQ or NYSE, where the disclosure requirements are far lighter. That last part matters more than the price does. You may be buying into a company whose financial statements are thin, late, or unaudited.</p>

      <KeyTerm term="Penny Stock" />

      <h3>How a pump and dump actually works</h3>

      <p>The scheme is old and mechanically simple. Promoters accumulate a large block of a near-worthless stock while it is quiet and cheap. Then they generate attention: paid newsletters, group chats, short videos, a press release about a vague partnership. New buyers arrive, the price rises on genuinely small volume, and the rise itself becomes the evidence people cite for buying. The promoters sell into exactly that demand. When their selling exhausts the new money, there is nobody left to buy, and the price returns to roughly where it started.</p>

      <p>Notice that the promoter needs no lie about the future to profit. They only need you to arrive after they did.</p>

      <h3>The exit problem</h3>

      <p>The second failure mode is <Term k="liquidity">liquidity</Term>, and it surprises people who have only ever traded large companies. If a stock trades a few thousand dollars of volume a day with a bid of $0.42 and an ask of $0.55, that spread is roughly a quarter of the price, and the quoted bid may only be good for a few hundred shares. Selling a real position means walking down through progressively worse prices.</p>

      <Callout variant="warning">
        <p>A quote is not a promise. In an illiquid stock, the price you see on your screen and the price you can actually get out at are different numbers, and the gap widens exactly when everyone wants out at once. Assume that in a genuine panic, your exit is worse than the last printed trade.</p>
      </Callout>

      <h2>Options, briefly</h2>

      <p>An <Term k="option">option</Term> is a contract, not a share. Buying one gives you the right to buy or sell 100 shares of the underlying stock at a fixed price before a fixed date, and you pay a premium for that right. If the move you expected does not happen by expiry, the contract expires worthless and the premium is gone. This is the sharpest difference from owning stock: a stock that falls 60% is still an asset you hold, while an expired option is nothing at all. We take the mechanics apart properly in the next lesson.</p>

      <h2>Leveraged ETFs and the arithmetic nobody checks</h2>

      <p>This is the one almost everyone gets wrong, including people who have owned them for months. A 3x leveraged ETF does not promise three times the return of its index. It promises three times the index’s <em>daily</em> return, and it rebalances its exposure at the end of every trading day to keep that ratio. Over any period longer than one day, your return compounds off a base that keeps moving.</p>

      <h3>A two-day example</h3>

      <ol>
        <li>Day one, the index falls 10%. A $100 index position becomes $90. The 3x fund falls 30%, so $100 becomes $70.</li>
        <li>Day two, the index rises 11.1%. The index position goes from $90 to about $100, so over two days the index is flat.</li>
        <li>The 3x fund rises 33.3% that same day: $70 × 1.333 = $93.31.</li>
        <li>The index ended flat. The leveraged fund ended down about 6.7%, and nothing went wrong. No fees, no tracking error, no bad luck. Just compounding.</li>
      </ol>

      <p>This effect is called volatility decay, and it gets worse as <Term k="volatility">volatility</Term> rises and as the holding period lengthens. A choppy sideways market is the specific environment in which a leveraged fund bleeds while the thing it tracks does nothing.</p>

      <Callout variant="did-you-know">
        <p>You do not have to take my word for any of this. Leveraged and inverse ETFs state it in their own prospectuses and fact sheets: they seek daily investment results, they are intended for short-term trading, and they are not suitable as long-term holdings. Pull up the fact sheet for any of them and read the paragraph in bold near the top.</p>
      </Callout>

      <h2>Meme stocks</h2>

      <p>A meme stock is one whose price is driven by coordinated attention rather than by business results. The classic case is GameStop, which started January 2021 under $20 a share, hit an intraday high near $483 on 28 January 2021 on a pre-split basis, and fell roughly 90% within weeks.</p>

      <p>What makes these structurally hard is not that they are volatile. It is that the thing you would need to forecast is not a company. Ordinary analysis asks whether earnings will grow; here you are trying to predict how long several hundred thousand strangers stay interested, which is a question with no financial statement behind it. Crowds also disperse without an announcement. There is no filing that tells you attention peaked yesterday.</p>

      <Callout variant="note">
        <p>Part of the 2021 move was a genuine <Term k="short squeeze">short squeeze</Term>, in which traders who had bet against the stock were forced to buy it back as it rose, pushing it higher still. That is a real mechanism worth understanding, and we cover it later in the track. It is also self-limiting: once the forced buying is done, the fuel is gone.</p>
      </Callout>

      <h2>The rest of the menu</h2>

      <p><strong>Crypto-adjacent equities.</strong> Miners, corporate holders and exchanges are companies whose share price behaves like a geared bet on an underlying crypto asset. Buying them means taking crypto price risk, plus ordinary company risk such as debt and operating costs, plus dilution risk, since these firms frequently issue new shares to fund purchases or operations. That is strictly more risk than the underlying asset carries by itself, which is the opposite of what most buyers assume they are getting.</p>

      <p><strong>SPACs.</strong> A blank-cheque company raises money first and finds a business to merge with later. You are underwriting a deal that does not exist yet, on terms set by sponsors whose economics differ from yours.</p>

      <p><strong>Binary biotech events.</strong> A small drug developer with one candidate in trials is a coin flip with a date on it. A single readout can move the stock 80% in either direction overnight, and no amount of chart reading tells you which way, because the result is sealed until it is published.</p>

      <p><strong>Margin.</strong> Borrowing from your broker to hold a larger position is the purest form of <Term k="leverage">leverage</Term> available to a retail account. The mechanism that hurts is the margin call: when your collateral falls below the maintenance requirement, the broker demands more cash, and if it does not arrive, sells your positions for you. That forced sale happens when prices are already down, which means the structure converts a temporary decline into a permanent loss and removes your ability to wait.</p>

      <KeyTerm term="Leverage" />

      <h2>The risk ladder</h2>

      <p>Risk is a spectrum, not a good-versus-bad split. Reading down this table, notice that the worst cases change in kind, not just in size.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Instrument</th>
              <th>What can go right</th>
              <th>What can go wrong</th>
              <th>Realistic worst case</th>
              <th>Lose more than you put in?</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Cash in a bank</td>
              <td>The number never falls</td>
              <td>Inflation outpaces the interest</td>
              <td>You quietly lose a few percent of purchasing power a year</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Broad index fund</td>
              <td>You own hundreds of businesses at very low cost</td>
              <td>The whole market falls together</td>
              <td>A drawdown near 50% that takes years to recover</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Blue chip stock</td>
              <td>Durable business, often a dividend</td>
              <td>The business decays, or a scandal lands</td>
              <td>Permanent impairment; Enron went from around $90 in mid-2000 to near zero by December 2001</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Small cap stock</td>
              <td>Real growth from a small base</td>
              <td>Funding dries up, shares get diluted</td>
              <td>Near-total loss</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Meme stock</td>
              <td>The crowd arrives before you sell</td>
              <td>The crowd leaves before you sell</td>
              <td>A decline of 80% or more within weeks</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Bought option</td>
              <td>A large percentage gain on a small premium</td>
              <td>The move does not arrive before expiry</td>
              <td>The entire premium, gone at expiry</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Leveraged ETF</td>
              <td>Three times a favourable daily move</td>
              <td>Volatility decay in a choppy market</td>
              <td>Value grinding down while the index goes nowhere</td>
              <td>No</td>
            </tr>
            <tr>
              <td>Stock bought on margin</td>
              <td>A larger position than your cash allows</td>
              <td>A margin call forces liquidation at the low</td>
              <td>Account wiped out and a debt still owed to the broker</td>
              <td>Yes</td>
            </tr>
          </tbody>
        </table>
      </div>

      <TryIt moduleId={moduleId} placeholder="Instrument, what the holder owns, and the exact path to zero…">
        <p>Pick one instrument from this lesson that you have personally seen promoted online: a specific ticker, fund or contract, not a category. Look it up on Yahoo Finance or the issuer’s own fact sheet, then write three things: what a holder of it literally owns, the specific mechanism by which it could go to zero, and one number from the page that surprised you. If you cannot find a clear answer to the first question in five minutes, that is itself the finding, and worth writing down.</p>
      </TryIt>

      <h2>What high risk actually means</h2>

      <p>Here is the definition worth keeping. High risk does not mean “the price moves around a lot”. It means the distribution of possible outcomes is wide <em>and</em> a meaningful share of that distribution ends at total loss. An index fund moves plenty and has never gone to zero. A single pre-revenue biotech can move less on a quiet week and still have a real chance of being worth nothing within two years. Movement is not the variable that matters; the fat part of the left tail is.</p>

      <Callout variant="warning">
        <p>One rule holds up the entire rest of this track: never put money into any of these instruments that you cannot afford to lose entirely. And be honest about what that phrase means. It does not mean the loss would sting. It means the loss changes nothing about your life: not your rent, not your tuition, not your relationship with the person who lent you the money, not your sleep.</p>
      </Callout>

      <p>If that condition is not met, no amount of research fixes it, because the problem is not your analysis. It is your position size relative to your life. That is a topic we return to in detail, and it is the single most reliable difference between people who survive this part of the market and people who do not.</p>

      <p>Next up: options in full. What the contract actually says, what the premium is made of, why time itself works against a buyer, and why “only $200 at risk” is a sentence that deserves more scrutiny than it usually gets.</p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
