"""
📚 Financial Education Module
=============================
Comprehensive financial literacy lessons for students.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text

console = Console()

class EducationModule:
    """Financial education content manager."""
    
    def __init__(self):
        self.console = Console()
    
    def display_lesson(self, title: str, content: str):
        """Display a lesson with formatted content."""
        self.console.clear()
        self.console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))
        self.console.print(Markdown(content))
    
    def stock_market_basics(self):
        """Module 1: Stock Market Basics."""
        content = """
# 📖 Module 1: Stock Market Basics

## What is a Stock?

A **stock** (also called a **share** or **equity**) represents ownership in a company. 
When you buy a stock, you become a **partial owner** of that company.

### Example:
If a company has 1,000 shares and you own 10 shares, you own **1%** of that company!

---

## Why Do Companies Issue Stocks?

Companies issue stocks to **raise money** (capital) for:
- 🏗️ Expanding their business
- 💻 Research and development
- 💰 Paying off debt
- 🌍 Entering new markets

This is called an **Initial Public Offering (IPO)** when a company first sells shares to the public.

---

## How Does the Stock Market Work?

The stock market is like an **auction house** where buyers and sellers trade stocks:

```
Buyer wants to buy AAPL at $150  ←→  Seller wants to sell AAPL at $150
                          ↓
                    TRADE EXECUTED!
```

### Key Participants:
| Participant | Role |
|-------------|------|
| **Investors** | Buy and hold stocks for long-term growth |
| **Traders** | Buy and sell frequently for short-term profits |
| **Market Makers** | Provide liquidity by always being willing to buy/sell |
| **Brokers** | Connect buyers and sellers (e.g., Robinhood, Fidelity) |

---

## Major Stock Exchanges

| Exchange | Location | Notable Stocks |
|----------|----------|----------------|
| **NYSE** (New York Stock Exchange) | New York, USA | Berkshire Hathaway, Coca-Cola, Disney |
| **NASDAQ** | New York, USA | Apple, Microsoft, Google, Amazon |
| **LSE** (London Stock Exchange) | London, UK | BP, HSBC, Unilever |
| **TSE** (Tokyo Stock Exchange) | Tokyo, Japan | Toyota, Sony, Nintendo |

---

## Stock Ticker Symbols

Every publicly traded company has a **ticker symbol** - a unique abbreviation:

| Company | Ticker Symbol |
|---------|--------------|
| Apple | **AAPL** |
| Microsoft | **MSFT** |
| Tesla | **TSLA** |
| Amazon | **AMZN** |
| Google (Alphabet) | **GOOGL** |

---

## Bull vs Bear Markets

### 🐂 Bull Market
- Prices are **rising** or expected to rise
- Investor **optimism**
- Strong economic conditions
- Named after how a bull attacks (thrusting horns **upward**)

### 🐻 Bear Market
- Prices are **falling** (typically 20%+ decline)
- Investor **pessimism**
- Weak economic conditions
- Named after how a bear attacks (swiping paws **downward**)

---

## Key Terms to Know

| Term | Definition |
|------|------------|
| **Dividend** | Payment companies make to shareholders from profits |
| **Market Cap** | Total value of all shares (Share Price × Total Shares) |
| **Volume** | Number of shares traded in a period |
| **Bid** | Highest price a buyer will pay |
| **Ask** | Lowest price a seller will accept |
| **Spread** | Difference between bid and ask price |

---

## 💡 Key Takeaways

1. **Stocks = Ownership** - When you buy stocks, you own part of a company
2. **Supply & Demand** - Stock prices change based on how many people want to buy vs. sell
3. **Long-term Focus** - Historically, the stock market has grown over time
4. **Research Matters** - Always research before investing in any stock

---

*"The stock market is a device for transferring money from the impatient to the patient."*
— Warren Buffett
        """
        self.display_lesson("Module 1: Stock Market Basics", content)
    
    def investment_fundamentals(self):
        """Module 2: Investment Fundamentals."""
        content = """
# 💡 Module 2: Investment Fundamentals

## The Core Principle: Risk vs Return

The fundamental rule of investing:

> **Higher potential returns = Higher risk**
> **Lower risk = Lower potential returns**

```
     High ┃         🎰 Crypto
  Return  ┃      📈 Growth Stocks
          ┃    🏢 Blue-Chip Stocks
          ┃   📊 Index Funds
          ┃  🏦 Bonds
     Low  ┃ 💵 Savings Account
          ┗━━━━━━━━━━━━━━━━━━━━━━
            Low              High
                   RISK
```

---

## The Magic of Compound Interest

**Compound interest** is when your earnings generate more earnings. It's called the 
**"eighth wonder of the world"** by Albert Einstein!

### Formula:
```
A = P(1 + r)^t

Where:
A = Final amount
P = Principal (initial investment)
r = Annual interest rate
t = Time in years
```

### Example: $1,000 invested at 10% annual return

| Year | Starting Balance | Interest (10%) | Ending Balance |
|------|-----------------|----------------|----------------|
| 1 | $1,000 | $100 | $1,100 |
| 5 | $1,464 | $146 | $1,610 |
| 10 | $2,358 | $236 | $2,594 |
| 20 | $6,116 | $612 | $6,728 |
| 30 | $15,863 | $1,586 | **$17,449** |

**Your money grew 17x in 30 years!**

---

## Diversification: Don't Put All Eggs in One Basket

**Diversification** means spreading investments across different:
- **Asset classes** (stocks, bonds, real estate)
- **Sectors** (tech, healthcare, energy)
- **Geographic regions** (US, Europe, Asia)
- **Company sizes** (large-cap, mid-cap, small-cap)

### Why Diversify?

| Scenario | Undiversified Portfolio | Diversified Portfolio |
|----------|------------------------|----------------------|
| Tech Crash | 📉 -40% (all in tech) | 📉 -15% (spread out) |
| Healthcare Boom | ❌ Missed opportunity | ✅ Partial benefit |
| Market Recovery | Depends on one sector | Balanced recovery |

---

## The Power of Dollar-Cost Averaging (DCA)

**DCA** means investing a fixed amount regularly, regardless of price.

### Example: $100/month into a stock

| Month | Stock Price | Shares Bought | Total Shares |
|-------|-------------|---------------|--------------|
| Jan | $50 | 2.0 | 2.0 |
| Feb | $40 | 2.5 | 4.5 |
| Mar | $25 | 4.0 | 8.5 |
| Apr | $33 | 3.0 | 11.5 |
| May | $50 | 2.0 | 13.5 |

**Average cost per share: $29.63** (vs. $39.60 average price)

DCA helps you:
- ✅ Remove emotion from investing
- ✅ Buy more when prices are low
- ✅ Build wealth consistently

---

## Time in the Market vs. Timing the Market

### ❌ Market Timing (Risky)
Trying to predict when to buy low and sell high.
- Requires perfect prediction
- Often leads to missing best days
- Stress and frequent trading

### ✅ Time in the Market (Proven)
Staying invested for the long term.
- Historical market growth: ~10% annually
- Compound growth over time
- Less stress and fewer fees

### The Cost of Missing the Best Days (S&P 500, 20 years):

| Strategy | Annual Return |
|----------|---------------|
| Fully Invested | 9.85% |
| Missed 10 Best Days | 5.60% |
| Missed 20 Best Days | 2.94% |
| Missed 30 Best Days | 0.76% |

---

## The Rule of 72

A quick way to estimate how long it takes for money to double:

```
Years to Double = 72 ÷ Annual Return Rate
```

| Annual Return | Years to Double |
|---------------|-----------------|
| 4% | 18 years |
| 6% | 12 years |
| 8% | 9 years |
| 10% | 7.2 years |
| 12% | 6 years |

---

## 💡 Key Takeaways

1. **Start Early** - Time is your greatest asset (compound interest)
2. **Diversify** - Spread risk across different investments
3. **Stay Consistent** - Use dollar-cost averaging
4. **Think Long-Term** - Time in market beats timing the market
5. **Understand Risk** - Higher returns come with higher risk

---

*"Investing should be more like watching paint dry or watching grass grow. 
If you want excitement, take $800 and go to Las Vegas."*
— Paul Samuelson
        """
        self.display_lesson("Module 2: Investment Fundamentals", content)
    
    def technical_analysis(self):
        """Module 3: Technical Analysis."""
        content = """
# 📊 Module 3: Technical Analysis

## What is Technical Analysis?

**Technical analysis** studies historical price and volume data to predict 
future price movements. It's based on the idea that:

> "History tends to repeat itself, and price patterns are predictable."

---

## Reading Candlestick Charts

Each **candlestick** shows 4 prices for a time period:

```
        High ─────┬───── (Wick/Shadow)
                  │
         ┌────────┤ ← Close (Green candle)
         │████████│    or
         │████████│ ← Open (Red candle)
         └────────┤
                  │
         Low ─────┴───── (Wick/Shadow)

🟢 Green/White: Close > Open (Price went UP)
🔴 Red/Black: Close < Open (Price went DOWN)
```

---

## Key Technical Indicators

### 1️⃣ Moving Averages (MA)

**Simple Moving Average (SMA)** - Average price over X periods

```
SMA = (P1 + P2 + P3 + ... + Pn) / n
```

**Common periods:**
- **SMA 20** - Short-term trend
- **SMA 50** - Medium-term trend  
- **SMA 200** - Long-term trend

**Signals:**
- Price ABOVE SMA = Bullish 🐂
- Price BELOW SMA = Bearish 🐻
- **Golden Cross**: SMA 50 crosses ABOVE SMA 200 = Strong Buy
- **Death Cross**: SMA 50 crosses BELOW SMA 200 = Strong Sell

---

### 2️⃣ Relative Strength Index (RSI)

RSI measures **momentum** on a scale of 0-100.

```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss
```

| RSI Value | Interpretation |
|-----------|----------------|
| > 70 | **Overbought** (might fall) |
| 50-70 | Bullish momentum |
| 30-50 | Bearish momentum |
| < 30 | **Oversold** (might rise) |

---

### 3️⃣ MACD (Moving Average Convergence Divergence)

MACD shows trend **direction and momentum**.

```
MACD Line = 12-day EMA - 26-day EMA
Signal Line = 9-day EMA of MACD Line
Histogram = MACD Line - Signal Line
```

**Signals:**
- MACD crosses ABOVE Signal = **Buy** 📈
- MACD crosses BELOW Signal = **Sell** 📉
- Histogram increasing = Strengthening trend

---

### 4️⃣ Bollinger Bands

Bollinger Bands show **volatility** using standard deviations.

```
Middle Band = 20-day SMA
Upper Band = Middle + (2 × Standard Deviation)
Lower Band = Middle - (2 × Standard Deviation)
```

**Interpretation:**
- Price near Upper Band = Potentially overbought
- Price near Lower Band = Potentially oversold
- Bands widening = Increasing volatility
- Bands narrowing = Decreasing volatility (breakout coming?)

---

## Support and Resistance Levels

### Support 🟢
A price level where buying pressure prevents further decline.
- Acts as a "floor" for the price
- Multiple bounces = Stronger support

### Resistance 🔴
A price level where selling pressure prevents further rise.
- Acts as a "ceiling" for the price
- Multiple rejections = Stronger resistance

```
         ─────────────── Resistance ($150) 🔴
              /\    /\
             /  \  /  \
            /    \/    \  ← Price bounces between levels
           /            \
    ──────────────────────── Support ($100) 🟢
```

**Key concept:** When support is broken, it often becomes resistance (and vice versa).

---

## Common Chart Patterns

### Bullish Patterns (Price likely to go UP)
| Pattern | Description |
|---------|-------------|
| **Cup and Handle** | U-shaped recovery with small dip |
| **Double Bottom** | W-shape, price bounced off support twice |
| **Ascending Triangle** | Higher lows, flat resistance |

### Bearish Patterns (Price likely to go DOWN)
| Pattern | Description |
|---------|-------------|
| **Head and Shoulders** | Three peaks, middle is highest |
| **Double Top** | M-shape, price rejected at resistance twice |
| **Descending Triangle** | Lower highs, flat support |

---

## Volume Analysis

**Volume** confirms price movements:

| Price Movement | Volume | Interpretation |
|----------------|--------|----------------|
| Price UP | High Volume | Strong bullish signal ✅ |
| Price UP | Low Volume | Weak move, possible reversal ⚠️ |
| Price DOWN | High Volume | Strong bearish signal ✅ |
| Price DOWN | Low Volume | Weak move, possible reversal ⚠️ |

---

## Putting It All Together

**Example Analysis:**
```
Stock: AAPL
Price: $150
SMA 20: $148 (Price ABOVE = Bullish)
SMA 50: $145 (Price ABOVE = Bullish)
RSI: 65 (Bullish, but approaching overbought)
MACD: Above signal line (Bullish)
Volume: Increasing with price

📊 Overall: BULLISH trend, but watch for RSI hitting 70
```

---

## 💡 Key Takeaways

1. **Technical analysis is not 100% accurate** - Use it as one tool among many
2. **Multiple indicators = Better signals** - Don't rely on just one
3. **Trend is your friend** - Trade with the trend, not against it
4. **Volume confirms** - Strong moves need strong volume
5. **Practice with paper trading** - Test strategies without real money first

---

*"The trend is your friend until the end when it bends."*
— Ed Seykota
        """
        self.display_lesson("Module 3: Technical Analysis", content)
    
    def fundamental_analysis(self):
        """Module 4: Fundamental Analysis."""
        content = """
# 📋 Module 4: Fundamental Analysis

## What is Fundamental Analysis?

**Fundamental analysis** evaluates a company's intrinsic value by examining:
- Financial statements
- Industry conditions
- Management quality
- Economic factors

> The goal: Determine if a stock is **overvalued**, **undervalued**, or **fairly valued**.

---

## The Three Financial Statements

### 1️⃣ Income Statement (Profit & Loss)
Shows revenue, expenses, and profit over a period.

```
Revenue (Sales)           $100,000
- Cost of Goods Sold       -$40,000
= Gross Profit             $60,000
- Operating Expenses       -$30,000
= Operating Income         $30,000
- Interest & Taxes         -$10,000
= Net Income               $20,000 ← The "bottom line"
```

### 2️⃣ Balance Sheet
Shows what the company owns and owes at a point in time.

```
ASSETS = LIABILITIES + SHAREHOLDERS' EQUITY

Assets (What they own):
- Cash: $50,000
- Inventory: $30,000
- Property: $200,000

Liabilities (What they owe):
- Loans: $100,000
- Accounts Payable: $30,000

Equity (What's left for shareholders):
- $150,000
```

### 3️⃣ Cash Flow Statement
Shows actual cash coming in and going out.

| Section | Examples |
|---------|----------|
| Operating | Cash from business operations |
| Investing | Buying/selling equipment, acquisitions |
| Financing | Issuing stock, paying dividends, loans |

---

## Key Financial Ratios

### Valuation Ratios

| Ratio | Formula | Interpretation |
|-------|---------|----------------|
| **P/E** (Price-to-Earnings) | Stock Price ÷ EPS | Lower = potentially undervalued |
| **P/B** (Price-to-Book) | Stock Price ÷ Book Value per Share | < 1 might be undervalued |
| **P/S** (Price-to-Sales) | Market Cap ÷ Revenue | Compare within industry |
| **PEG** (P/E to Growth) | P/E ÷ Earnings Growth Rate | < 1 = undervalued considering growth |

### Example P/E Analysis:
```
Company A: P/E = 15 (Stock costs $15 for each $1 of earnings)
Company B: P/E = 30 (Stock costs $30 for each $1 of earnings)

Industry Average P/E: 20

→ Company A might be undervalued
→ Company B might be overvalued (or has high growth expectations)
```

---

### Profitability Ratios

| Ratio | Formula | What It Shows |
|-------|---------|---------------|
| **Gross Margin** | Gross Profit ÷ Revenue | Efficiency of production |
| **Operating Margin** | Operating Income ÷ Revenue | Efficiency of operations |
| **Net Margin** | Net Income ÷ Revenue | Overall profitability |
| **ROE** (Return on Equity) | Net Income ÷ Shareholders' Equity | How well they use investor money |
| **ROA** (Return on Assets) | Net Income ÷ Total Assets | How well they use all assets |

**Higher margins = More profitable company**

---

### Financial Health Ratios

| Ratio | Formula | Healthy Range |
|-------|---------|---------------|
| **Current Ratio** | Current Assets ÷ Current Liabilities | > 1.5 |
| **Debt-to-Equity** | Total Debt ÷ Shareholders' Equity | < 1 (varies by industry) |
| **Interest Coverage** | Operating Income ÷ Interest Expense | > 3 |

---

## Earnings Per Share (EPS)

**EPS** shows profit allocated to each share of stock.

```
EPS = (Net Income - Dividends on Preferred Stock) ÷ Shares Outstanding
```

### Example:
- Net Income: $10 million
- Shares Outstanding: 5 million
- EPS = $10M ÷ 5M = **$2.00 per share**

**Growing EPS** year over year is a positive sign! 📈

---

## Evaluating Company Quality

### ✅ Good Signs
- Growing revenue and earnings
- Strong profit margins
- Low debt levels
- Positive free cash flow
- Consistent dividend growth
- Competitive advantages (moat)

### ❌ Red Flags
- Declining revenue
- Negative earnings
- High debt
- Negative cash flow
- Accounting irregularities
- Frequent management changes

---

## Competitive Advantage (Economic Moat)

Warren Buffett looks for companies with "moats" - sustainable competitive advantages:

| Moat Type | Example |
|-----------|---------|
| **Brand Power** | Coca-Cola, Apple |
| **Network Effects** | Facebook, Visa |
| **Cost Advantage** | Walmart, Costco |
| **Switching Costs** | Microsoft Office, Adobe |
| **Patents/IP** | Pharmaceutical companies |

---

## Comparing Companies: A Framework

| Criteria | Company A | Company B | Better |
|----------|-----------|-----------|--------|
| P/E Ratio | 18 | 25 | A |
| Revenue Growth | 8% | 15% | B |
| Net Margin | 12% | 8% | A |
| Debt-to-Equity | 0.5 | 1.2 | A |
| ROE | 15% | 20% | B |

**Analysis:** Company A is cheaper and more profitable, but Company B is growing faster. 
Your choice depends on whether you prioritize value or growth!

---

## 💡 Key Takeaways

1. **Read the statements** - Income, Balance Sheet, Cash Flow tell the full story
2. **Compare ratios** - Always compare to industry peers and historical averages
3. **Quality matters** - Look for sustainable competitive advantages
4. **Growth vs Value** - Know what type of investor you are
5. **Do your research** - Never invest in what you don't understand

---

*"Price is what you pay. Value is what you get."*
— Warren Buffett
        """
        self.display_lesson("Module 4: Fundamental Analysis", content)
    
    def types_of_investments(self):
        """Module 5: Types of Investments."""
        content = """
# 🏦 Module 5: Types of Investments

## Overview of Investment Vehicles

Different investments offer different risk/return profiles:

```
     High ┃  🎰 Individual Stocks
  Return  ┃    🏢 REITs
          ┃      📊 Index Funds/ETFs
          ┃        🏛️ Mutual Funds
          ┃          💵 Bonds
     Low  ┃            🏦 Savings Account
          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Low                  High
                    RISK
```

---

## 1️⃣ Stocks (Equities)

**What:** Ownership shares in individual companies

| Pros | Cons |
|------|------|
| High growth potential | High volatility |
| Dividend income possible | Risk of total loss |
| Ownership rights | Requires research |
| Easy to buy/sell | Emotional decisions |

### Types of Stocks:

| Type | Characteristics | Examples |
|------|-----------------|----------|
| **Growth Stocks** | High growth, reinvest profits | Tesla, Amazon |
| **Value Stocks** | Undervalued, steady | Berkshire, Johnson & Johnson |
| **Dividend Stocks** | Regular income payments | Coca-Cola, Procter & Gamble |
| **Blue Chips** | Large, stable, reliable | Apple, Microsoft |
| **Penny Stocks** | Low price, high risk | Various (be careful!) |

---

## 2️⃣ Bonds (Fixed Income)

**What:** Loans you make to governments or companies

```
You → Lend $1,000 → Company/Government
     ← Receive interest payments (coupon)
     ← Get $1,000 back at maturity
```

| Pros | Cons |
|------|------|
| Steady income | Lower returns than stocks |
| Lower risk | Interest rate risk |
| Portfolio diversification | Inflation risk |
| Predictable returns | Credit/default risk |

### Types of Bonds:

| Type | Risk Level | Return |
|------|------------|--------|
| **Treasury Bonds** (Government) | Very Low | Low |
| **Municipal Bonds** | Low | Low-Medium |
| **Corporate Bonds** (Investment Grade) | Medium | Medium |
| **High-Yield (Junk) Bonds** | High | High |

---

## 3️⃣ Mutual Funds

**What:** Pooled money managed by professionals

```
       Investor A ─┐
       Investor B ─┼→ Mutual Fund → Stocks, Bonds, etc.
       Investor C ─┘
```

| Pros | Cons |
|------|------|
| Professional management | Management fees |
| Instant diversification | Less control |
| Low minimum investment | May underperform index |
| Easy to understand | Tax inefficient |

**Types:** Actively managed (try to beat market) vs. Passively managed (track index)

---

## 4️⃣ Exchange-Traded Funds (ETFs)

**What:** Like mutual funds, but trade like stocks on exchanges

| Feature | Mutual Fund | ETF |
|---------|-------------|-----|
| Trading | End of day | Throughout day |
| Minimum Investment | Often $1,000+ | Price of 1 share |
| Fees | Higher (avg 0.5-1%) | Lower (avg 0.1-0.5%) |
| Tax Efficiency | Lower | Higher |

### Popular ETFs:
- **SPY** - Tracks S&P 500
- **QQQ** - Tracks Nasdaq 100
- **VTI** - Total US Stock Market
- **BND** - Total Bond Market

---

## 5️⃣ Index Funds

**What:** Track a specific market index (like S&P 500)

```
S&P 500 Index Fund:
├── Apple (7%)
├── Microsoft (6%)
├── Amazon (3%)
├── ... (497 other companies)
└── Automatically rebalanced
```

| Pros | Cons |
|------|------|
| Very low fees | Can't beat the market |
| Broad diversification | No flexibility |
| No manager risk | Hold "bad" companies too |
| Tax efficient | Market returns only |

> Warren Buffett recommends index funds for most investors!

---

## 6️⃣ REITs (Real Estate Investment Trusts)

**What:** Companies that own income-producing real estate

```
Types of REITs:
├── Residential (apartments)
├── Commercial (offices)
├── Retail (shopping malls)
├── Industrial (warehouses)
└── Healthcare (hospitals)
```

| Pros | Cons |
|------|------|
| Real estate exposure | Sensitive to interest rates |
| High dividends (90% must be distributed) | Can be volatile |
| More liquid than physical property | Property market risk |
| Professional management | Tax complexity |

---

## 7️⃣ Cryptocurrency

**What:** Digital currencies using blockchain technology

| Cryptocurrency | Purpose |
|----------------|---------|
| **Bitcoin (BTC)** | Digital gold, store of value |
| **Ethereum (ETH)** | Smart contracts platform |
| **Stablecoins** (USDC, USDT) | Pegged to USD |

| Pros | Cons |
|------|------|
| High growth potential | Extreme volatility |
| Decentralized | Regulatory uncertainty |
| 24/7 trading | Security risks |
| Inflation hedge (debated) | No intrinsic value (debated) |

⚠️ **Warning:** Very high risk! Only invest what you can afford to lose.

---

## Portfolio Allocation by Age

A common rule: **100 - Your Age = % in Stocks**

| Age | Stocks | Bonds | Strategy |
|-----|--------|-------|----------|
| 20 | 80% | 20% | Aggressive growth |
| 30 | 70% | 30% | Growth focus |
| 40 | 60% | 40% | Balanced |
| 50 | 50% | 50% | Income focus |
| 60 | 40% | 60% | Capital preservation |

---

## Sample Portfolios

### 🚀 Aggressive (Young Investor)
- 70% Stocks (40% US, 20% International, 10% Small-cap)
- 15% REITs
- 10% Bonds
- 5% Crypto

### ⚖️ Balanced (Middle-Aged)
- 50% Stocks (30% US, 20% International)
- 10% REITs
- 35% Bonds
- 5% Cash

### 🛡️ Conservative (Near Retirement)
- 30% Stocks
- 55% Bonds
- 10% Cash
- 5% REITs

---

## 💡 Key Takeaways

1. **Diversify across asset classes** - Don't just own stocks
2. **Match risk to timeline** - More time = more risk tolerance
3. **Consider fees** - They compound negatively over time
4. **Index funds for most** - Simple, cheap, effective
5. **Understand what you own** - Don't invest blindly

---

*"Do not put all your eggs in one basket."*
— Traditional Proverb
        """
        self.display_lesson("Module 5: Types of Investments", content)
    
    def risk_management(self):
        """Module 6: Risk Management."""
        content = """
# ⚠️ Module 6: Risk Management

## Why Risk Management Matters

> "Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1."
> — Warren Buffett

**Risk management** is about protecting your capital while still achieving growth.

---

## Types of Investment Risk

### 1️⃣ Market Risk (Systematic Risk)
Risk affecting the entire market that can't be diversified away.

| Type | Description | Example |
|------|-------------|---------|
| **Economic Risk** | Recessions, GDP decline | 2008 Financial Crisis |
| **Interest Rate Risk** | Central bank policy changes | Fed rate hikes |
| **Inflation Risk** | Purchasing power erosion | 1970s high inflation |
| **Political Risk** | Government policy changes | Trade wars, regulations |

### 2️⃣ Specific Risk (Unsystematic Risk)
Risk specific to a company or industry - CAN be diversified away.

| Type | Description | Example |
|------|-------------|---------|
| **Business Risk** | Poor management decisions | Company bankruptcy |
| **Credit Risk** | Inability to pay debts | Bond default |
| **Liquidity Risk** | Unable to sell quickly | Real estate during crash |
| **Sector Risk** | Industry-specific problems | Oil price collapse |

---

## Measuring Risk

### Standard Deviation (Volatility)
Measures how much returns vary from the average.

```
Higher Standard Deviation = More Volatile = More Risk

Asset A: Average Return 8%, Std Dev 5%
  → Returns likely between 3% and 13%

Asset B: Average Return 8%, Std Dev 20%
  → Returns likely between -12% and 28%
```

### Beta
Measures volatility relative to the market (S&P 500 = 1.0)

| Beta | Meaning | Example |
|------|---------|---------|
| **β = 1.0** | Moves with market | Index fund |
| **β > 1.0** | More volatile than market | Tech stocks (β ≈ 1.2) |
| **β < 1.0** | Less volatile than market | Utilities (β ≈ 0.5) |
| **β < 0** | Moves opposite to market | Gold (sometimes) |

### Maximum Drawdown
The largest peak-to-trough decline in portfolio value.

```
Portfolio hits $100,000 (peak)
Portfolio drops to $60,000 (trough)
Maximum Drawdown = -40%

Recovery needed: 67% gain just to break even!
```

---

## Risk Management Strategies

### 1️⃣ Diversification

**Across asset classes:**
```
Portfolio:
├── 60% Stocks
│   ├── 40% US
│   └── 20% International
├── 30% Bonds
└── 10% Alternatives (REITs, Gold)
```

**Within asset classes:**
- Don't put more than 5-10% in any single stock
- Own at least 20-30 different stocks for proper diversification

### 2️⃣ Position Sizing

**Never risk more than you can afford to lose on a single trade.**

| Rule | Description |
|------|-------------|
| **1% Rule** | Never risk more than 1% of portfolio on one trade |
| **2% Rule** | Maximum 2% risk per trade for aggressive traders |
| **5% Rule** | No single position > 5% of portfolio |

**Example:**
```
Portfolio: $10,000
1% Rule: Maximum loss per trade = $100

If stock could drop 10% before you sell:
Position size = $100 ÷ 10% = $1,000
```

### 3️⃣ Stop-Loss Orders

Automatic sell orders to limit losses.

```
Buy AAPL at $150
Set stop-loss at $135 (-10%)

If price drops to $135:
  → Automatically sells
  → Loss limited to 10%
```

| Stop-Loss Type | Description |
|----------------|-------------|
| **Fixed** | Sell at specific price ($135) |
| **Trailing** | Sell if drops X% from highest point |
| **Time-based** | Sell after X days if not profitable |

### 4️⃣ Asset Allocation Rebalancing

Keep your portfolio at target allocation by periodically rebalancing.

```
Target: 60% Stocks / 40% Bonds

After a bull market:
  Actual: 70% Stocks / 30% Bonds
  → Sell stocks, buy bonds to rebalance

After a bear market:
  Actual: 50% Stocks / 50% Bonds
  → Sell bonds, buy stocks to rebalance
```

**Rebalancing forces you to buy low and sell high!**

---

## The Psychology of Risk

### Common Behavioral Mistakes:

| Bias | Description | Solution |
|------|-------------|----------|
| **Loss Aversion** | Fear losses more than enjoy gains | Set rules, stick to them |
| **Overconfidence** | Thinking you can beat the market | Use index funds |
| **Herd Mentality** | Following the crowd | Do your own research |
| **Recency Bias** | Overweight recent events | Look at long-term data |
| **Anchoring** | Stuck on purchase price | Focus on current value |

### Emotional Cycle of Investing:
```
         Euphoria ← "I'm a genius!"
            ↑
       Excitement
            ↑
       Optimism ← "This is going well"
            ↑                        ↓
        Hope  ←←←←←←←←←←←←←←←←←←←← Anxiety ← "Is this temporary?"
            ↓                        ↓
    Relief ←←←←←←←←←←←←←←←←←←←← Denial ← "It'll come back"
                                     ↓
                                  Fear ← "Maybe I should sell?"
                                     ↓
                              Desperation ← "How do I get out?"
                                     ↓
                                  Panic ← "SELL EVERYTHING!"
                                     ↓
                              Capitulation ← "I'm done with stocks"
                                     ↓
                              Depression ← "I lost everything"
```

**Best investors buy at depression/desperation and sell at euphoria!**

---

## Emergency Fund First!

Before investing, have **3-6 months of expenses** in cash.

```
Monthly Expenses: $2,000
Emergency Fund: $6,000 - $12,000 in savings account

Why? So you don't have to sell investments at bad times!
```

---

## Risk Tolerance Quiz

Ask yourself:

1. If my portfolio dropped 30%, would I:
   - a) Panic and sell everything
   - b) Hold and wait
   - c) Buy more at lower prices

2. When do I need this money?
   - a) Less than 2 years
   - b) 2-10 years
   - c) More than 10 years

3. What's my primary goal?
   - a) Preserve capital
   - b) Balanced growth
   - c) Maximum growth

**Mostly A's:** Conservative investor
**Mostly B's:** Moderate investor
**Mostly C's:** Aggressive investor

---

## 💡 Key Takeaways

1. **Know your risks** - Understand what could go wrong
2. **Diversify properly** - Don't put all eggs in one basket
3. **Size positions appropriately** - Never bet the farm
4. **Use stop-losses** - Protect against catastrophic losses
5. **Control emotions** - Have a plan and stick to it
6. **Rebalance regularly** - Maintain your target allocation
7. **Emergency fund first** - Don't invest money you might need soon

---

*"In investing, what is comfortable is rarely profitable."*
— Robert Arnott
        """
        self.display_lesson("Module 6: Risk Management", content)


# For testing
if __name__ == "__main__":
    edu = EducationModule()
    edu.stock_market_basics()
