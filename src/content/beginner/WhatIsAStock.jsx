import Callout from '../../components/ui/Callout.jsx'
import KeyTerm from '../../components/ui/KeyTerm.jsx'
import Quiz from '../../components/ui/Quiz.jsx'
import Term from '../../components/ui/Term.jsx'
import TryIt from '../../components/ui/TryIt.jsx'

const QUESTIONS = [
  {
    prompt: 'You buy one share of a company that has 1,000,000 shares outstanding. What do you own?',
    options: [
      'A loan to the company that it must pay back',
      'One-millionth of the company itself',
      'The right to one product from the company each year',
      'A guarantee of a share of next year’s profit',
    ],
    answer: 1,
    explanation:
      'A share is a unit of ownership, not a loan. One share out of a million is a one-millionth claim on the business: its assets, its future profits, and its problems. Nothing about it is guaranteed.',
  },
  {
    prompt:
      'A company sells 10 million new shares in its IPO at $20 each. Two weeks later the stock trades at $34. How much extra cash did the company receive from that rise?',
    options: ['$140 million', '$340 million', 'Nothing', 'It depends on trading volume'],
    answer: 2,
    explanation:
      'Nothing. The company was paid at the IPO. After that, shares trade between investors. Money moves from buyer to seller, not to the company. A rising price helps the company indirectly (cheaper future fundraising, valuable stock compensation), but no cash arrives.',
  },
  {
    prompt: 'Shareholders are paid before bondholders if a company goes bankrupt.',
    type: 'tf',
    answer: false,
    explanation:
      'The opposite. Shareholders sit last in the queue, behind lenders, bondholders and suppliers. That last-in-line position is exactly why stocks have historically returned more than bonds over long periods: you are being paid to take the worst seat.',
  },
  {
    prompt: 'Which of these is the strongest reason a healthy, profitable company might still issue stock?',
    options: [
      'It has run out of money and has no other option',
      'It wants to raise capital without taking on debt it must repay with interest',
      'Regulators require every large company to be publicly traded',
      'Issuing stock automatically increases its profits',
    ],
    answer: 1,
    explanation:
      'Equity is capital you never have to repay. A loan demands interest every quarter regardless of how business is going; selling ownership does not. The cost is dilution: the founders now own a smaller slice.',
  },
  {
    prompt: 'If a stock’s price doubles, the company has definitely become twice as profitable.',
    type: 'tf',
    answer: false,
    explanation:
      'Price reflects what buyers and sellers currently believe about the future, not a measurement of present profit. Prices double on expectations, hype, takeover rumours and interest rate changes. Profit is one input among many.',
  },
]

export default function WhatIsAStock({ moduleId }) {
  return (
    <>
      <p className="lead">
        Almost everyone learns about stocks backwards. You see a green number on somebody’s phone, or a
        headline about a crash, long before anyone tells you what the thing being bought and sold actually
        is. So let’s fix the order.
      </p>

      <h2>A stock is a slice of a company</h2>

      <p>
        Imagine your school runs a genuinely good bubble tea stand. It takes $10,000 to set up (equipment,
        supplies, a licence), and you have $1,000. So you find nine friends with $1,000 each, but there’s a
        catch: none of you wants to <em>lend</em> the money, because a loan has to be repaid whether the stand
        works or not.
      </p>

      <p>
        Instead you split the business into 10 equal pieces and sell one to each person. Each piece is a{' '}
        <Term k="share">share</Term>. Nobody has to be repaid. If the stand makes $5,000 in profit, each
        owner has a claim on $500 of it. If the stand fails, everyone loses what they put in and no one owes
        anybody anything.
      </p>

      <p>
        That is a stock. The only difference between your bubble tea stand and Apple is the number of slices:
        Apple’s business is divided into roughly 15 billion of them instead of 10.
      </p>

      <KeyTerm term="Share" />

      <p>
        This has an immediate practical consequence that trips up almost every beginner:{' '}
        <strong>share price alone tells you nothing about whether a company is big or cheap.</strong> A $12
        stock is not “cheaper” than a $600 stock. It just means the pie was cut into more slices. To compare
        company sizes you need price multiplied by the number of slices, which is{' '}
        <Term k="market cap">market capitalisation</Term>.
      </p>

      <Callout variant="example">
        <p>
          Company A: 1 billion shares at $10 → market cap $10 billion.
          <br />
          Company B: 10 million shares at $600 → market cap $6 billion.
        </p>
        <p>
          The “expensive” $600 stock is the smaller company. Price per share is an accident of how the shares
          were divided up; market cap is the real price tag.
        </p>
      </Callout>

      <h2>What you actually get for your money</h2>

      <p>Owning a share of a public company entitles you to four specific things:</p>

      <ol>
        <li>
          <strong>A claim on future profits.</strong> Either paid to you directly as a{' '}
          <Term k="dividend">dividend</Term>, or kept inside the business to make it more valuable. Both
          routes belong to you as an owner.
        </li>
        <li>
          <strong>A vote.</strong> One share, one vote, on things like board members and major decisions. With
          one share out of a billion your vote is mathematically irrelevant, but the right is real, and for
          large holders it matters enormously.
        </li>
        <li>
          <strong>The right to sell.</strong> You can convert your slice back into cash at whatever price
          somebody will pay you today. This is called <Term k="liquidity">liquidity</Term> and it is genuinely
          valuable. Try selling one-tenth of a private bubble tea stand.
        </li>
        <li>
          <strong>A residual claim in bankruptcy.</strong> If the company is wound up, you get whatever is
          left after everyone else is paid. In practice that is usually zero.
        </li>
      </ol>

      <Callout variant="real-talk" title="The part that gets skipped">
        <p>
          That fourth point is the whole deal. In a bankruptcy, the queue runs: secured lenders, then
          unpaid wages and tax authorities, then bondholders and suppliers, and <em>then</em> shareholders. You are last.
        </p>
        <p>
          This is not a flaw in the system; it is the trade. Bondholders get paid first and earn a modest
          fixed return. Shareholders accept the worst seat in the house and, in exchange, capture the entire
          upside if the business does well. Higher expected return is compensation for a genuinely worse
          position, not a free gift.
        </p>
      </Callout>

      <h2>Why would a company give away ownership?</h2>

      <p>
        This is the question that makes the whole system click, and hardly anyone asks it. If you built a
        company, why on earth would you sell parts of it to strangers?
      </p>

      <h3>1. To raise money that never has to be repaid</h3>

      <p>
        A company that wants to build a new factory has two options. It can borrow, and then owe interest
        every quarter forever, in good years and bad, with the lender able to force bankruptcy if a payment is
        missed. Or it can sell ownership. Equity capital comes with no repayment schedule and no interest. If
        the factory fails, the shareholders simply lose value; nobody sends bailiffs.
      </p>

      <p>
        That is why even wildly profitable companies raise equity. It is not desperation. It is choosing the
        financing that cannot kill you in a bad year.
      </p>

      <h3>2. To let early backers cash out</h3>

      <p>
        The engineer who joined in year two and took shares instead of a proper salary has, on paper, a
        fortune, and no way to spend it. Going public converts paper into money that can buy a house. This
        is a large part of why companies list at all.
      </p>

      <h3>3. To pay people in something better than cash</h3>

      <p>
        Public companies pay staff partly in shares. It costs no cash, and it means the people building the
        company are owners of it. A startup competing with a giant for engineers cannot match the salary, but
        it can offer a slice of what the company might become.
      </p>

      <KeyTerm term="IPO" />

      <Callout variant="did-you-know">
        <p>
          When a stock rises 40% in a month, the company receives <strong>none</strong> of that money. After
          the IPO, shares change hands between investors: your money goes to whoever sold you the share, not
          to the business.
        </p>
        <p>
          Apple has not received a cent from anyone buying AAPL on the open market in decades. A high price
          still helps a company (it makes future share issues more lucrative, makes employee stock more
          valuable, and makes hostile takeovers harder), but no cash arrives from your purchase.
        </p>
      </Callout>

      <h2>Common stock vs preferred stock</h2>

      <p>
        Nearly everything you will ever buy is <strong>common stock</strong>: votes, dividends when declared,
        last in line if things collapse.
      </p>

      <p>
        <strong>Preferred stock</strong> is a hybrid. Holders usually get a fixed dividend and rank ahead of
        common shareholders in a bankruptcy, but typically give up voting rights and most of the upside. It
        behaves more like a bond wearing a stock costume. You are unlikely to need it as a beginner, but you
        will see the term, so now it isn’t a mystery.
      </p>

      <h2>What a stock is not</h2>

      <ul>
        <li>
          <strong>Not a loan to the company.</strong> That is a bond. Bondholders are creditors; shareholders
          are owners.
        </li>
        <li>
          <strong>Not a promise of anything.</strong> There is no guaranteed return, no protected principal,
          no obligation on anyone to buy it back from you.
        </li>
        <li>
          <strong>Not a bet against another person.</strong> Buying a share is not a wager where someone must
          lose for you to win. Over long periods, shareholders as a group can all do well, because the
          underlying businesses genuinely produce more value. (Options and futures, in the Hard track, are a
          different story: those <em>are</em> zero-sum.)
        </li>
        <li>
          <strong>Not a number on a screen.</strong> This is the one to hold onto. Behind every ticker is a
          real business with real employees, customers and problems. Everything in the Intermediate track
          comes back to that.
        </li>
      </ul>

      <TryIt moduleId={moduleId} placeholder="Company, share price, market cap, and what surprised you…">
        <p>
          Pick a company whose products you personally use: a phone, a game, a drink, a shoe brand. Search “
          <em>[company name]</em> stock” and find two numbers: the share price, and the market cap.
        </p>
        <p>
          Now answer this: does the market cap sound bigger or smaller than you expected for a company that
          size? Almost everyone guesses wrong the first time, and noticing the gap is the point.
        </p>
      </TryIt>

      <h2>The one idea to take with you</h2>

      <p>
        A stock is <strong>ownership of a real business</strong>, priced by whatever the last two people
        agreed on. Every other concept in this course (dividends, volatility, P/E ratios, even options) is
        built on top of that single sentence.
      </p>

      <p>
        Next up: where those shares actually change hands, and what really happens in the two seconds after
        you tap Buy.
      </p>

      <Quiz moduleId={moduleId} questions={QUESTIONS} />
    </>
  )
}
