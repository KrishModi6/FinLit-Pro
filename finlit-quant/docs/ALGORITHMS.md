# Algorithms

How every number in FinLit Quant is computed, in plain pseudocode. Each section names the file
that implements it.

Notation: `P[t]` is the adjusted close on trading day `t`, `r[t] = ln(P[t] / P[t-1])` is the daily
log return, `h` is a horizon in trading days, and a year is 252 trading days.

---

## 1. Loading prices (`data/yahoo.py`)

```
GET chart?range=10y&interval=1d&events=div,split
for each bar:
    date  = timestamp + exchange UTC offset, truncated to the day
    skip the bar if close is missing or <= 0          # Yahoo pads gaps with nulls
    open/high/low default to close if missing         # a flat candle, not a hole
previous_close = close of the previous daily bar      # not chartPreviousClose, which is
                                                      # the close before the whole 10 years
splits = { date: numerator / denominator }
```

Returns use the dividend- and split-adjusted close; the chart uses the traded OHLC.

## 2. Monte Carlo predictor (`analytics/montecarlo.py`)

### Estimation

```
r      = last `lookback` daily log returns            # default 3 years
hist_mu = mean(r)
sigma   = stdev(r)
kurt    = mean((r - hist_mu)^4) / mean((r - hist_mu)^2)^2 - 3
t_df    = clamp(4 + 6 / kurt, 3, 30)  if kurt > 0 else 30
          # excess kurtosis of a Student-t is 6 / (df - 4), inverted

drift (daily log drift actually simulated):
    historical: mu = hist_mu                          # already a log drift: no correction
    zero:       mu = -sigma^2 / 2                     # makes E[P_h] = P_0
    custom R:   mu = ln(1 + R) / 252 - sigma^2 / 2    # arithmetic R -> log drift
```

The `sigma^2 / 2` term appears only where an arithmetic return is converted into a log drift. The
FinLit Pro website applied it to a log drift as well, which is the bug in FIXLOG #1.

### Simulation

```
for every path i and day d (vectorised as an n x h matrix):
    gbm:        shock = mu + sigma * Z,             Z ~ Normal(0, 1)
    student_t:  shock = mu + sigma * T * sqrt((df-2)/df),  T ~ t(df)   # unit variance
    bootstrap:  pick random blocks of 10 consecutive historical returns,
                demean them, add mu
path[i, d] = P_0 * exp(cumulative sum of shocks up to d)
```

### Statistics

```
terminal     = path[:, h]
percentiles  = 5, 10, 25, 50, 75, 90, 95 of terminal (and of each day, for the fan chart)
prob_up      = share of terminal > P_0
loss         = 1 - terminal / P_0
VaR95        = 95th percentile of loss
CVaR95       = mean of loss where loss >= VaR95
max_dd[i]    = max over d of (1 - path[i, d] / running max of path[i, :d])
expected_max_dd = mean(max_dd)
```

### Calibration (walk-forward test)

```
for origin t = lookback, lookback + step, ... while t + h is in the data:
    window = r[t - lookback : t]                       # only data available at t
    mu, sigma = mean(window), stdev(window)
    z = (ln(P[t+h] / P[t]) - mu*h) / (sigma * sqrt(h))
    pit = NormalCDF(z)                                 # where the outcome fell, 0..1
coverage(band lo-hi) = share of pit inside [lo, hi]
verdict: "too narrow" if 10-90 coverage < 70%, "too wide" if > 90%, else "reasonably calibrated"
```

`step = max(5, h/4)`, so neighbouring tests overlap and are correlated; the panel says so.

## 3. Signal engine, from the original AI Predictor (`analytics/predictor.py`)

Six signals, each scored -2..+2, same thresholds as the Streamlit app:

| Signal | +2 | +1 | -1 | -2 |
| --- | --- | --- | --- | --- |
| RSI(14, Wilder) | < 30 | < 40 | > 60 | > 70 |
| MACD(12,26,9) | above signal and histogram rising | above signal | below signal | below and histogram falling |
| Moving averages | price > SMA20 > SMA50 | price > SMA20 | price < SMA20 | price < SMA20 < SMA50 |
| Bollinger position | < 5% | < 20% | > 80% | > 95% |
| Volume vs 20-day avg | > 1.5x on an up day | > 1.2x up | | > 1.5x on a down day |
| Momentum | 10d > 5% and 30d > 10% | 10d > 2% | 10d < -2% | 10d < -5% and 30d < -10% |

```
verdict  = Strong bullish if score >= 4, Bullish >= 2, Strong bearish <= -4, Bearish <= -2, else Neutral
trend    = least-squares line through the last 120 closes, extended h days
ema      = P * (1 + (EMA12 - EMA26) / EMA26 * D(h) / 12)
           D(h) = (1 - e^(-k h)) / k,  k = ln 2 / 60     # momentum decays, half-life 60 days
composite = 0.4 * MC median + 0.3 * trend + 0.3 * ema
agreement = stdev(MC median, trend, ema) / P: High < 2%, Medium < 5%, else Low
```

## 4. Fundamentals from SEC EDGAR (`data/sec.py`)

### Annual figures

```
for each metric (revenue, net income, ...):
    for each XBRL tag that can carry it, in priority order:
        keep facts from 10-K/20-F/40-F whose duration is 340..390 days
        for each fiscal year end, keep the fact from the most recently FILED document
    merge the tags: for each year, the highest-priority tag with a value wins
```

Why: companies switch tags (revenue moved to `RevenueFromContractWithCustomer...` in 2018),
every 10-K repeats two prior years, and a later filing's comparative is the restated number.

### Trailing twelve months

```
FY      = latest annual value
YTD     = value from the latest 10-Q with the longest duration starting after FY end
priorYTD = the fact of the same length ending about 364 days earlier
TTM = FY + YTD - priorYTD           (or FY if no 10-Q since)
```

10-Qs report year-to-date figures, so this one formula works after Q1, Q2 and Q3.

### Total debt without double counting

```
if LongTermDebt exists:       debt = LongTermDebt + ShortTermBorrowings     # LTD includes current part
elif DebtCurrent exists:      debt = LongTermDebtNoncurrent + DebtCurrent   # DebtCurrent includes it too
else:                         debt = noncurrent + current portion + short-term borrowings
```

### Stock splits

```
for each split (date S, ratio k) reported by Yahoo:
    for each annual EPS or diluted share value:
        if the filing it came from was filed before S:
            EPS /= k;  shares *= k
    if the cover-page share count is dated before S: shares_outstanding *= k
```

Filings made after a split restate the years they repeat; older years are never restated.

## 5. Ratios and quality scores (`analytics/valuation.py`)

```
market cap = price * cover-page shares outstanding
EV         = market cap + total debt - cash - short-term investments
P/E        = market cap / TTM net income          (only when net income > 0)
FCF        = operating cash flow - capex;  FCF yield = FCF / market cap
ROE        = net income / average of the last two years' equity
ROIC       = operating income * (1 - tax rate) / (debt + equity - cash)
             tax rate = tax / pretax income, or 21% if that is outside 0..50%
CAGR(n)    = (last / value n years earlier)^(1/n) - 1
```

**Piotroski F-score**, current year (c) vs prior (p), assets from the start of each year:
ROA > 0; CFO > 0; ROA(c) > ROA(p); CFO > net income; debt/avg assets fell; current ratio rose;
diluted shares did not rise; gross margin rose; asset turnover rose. A test whose inputs are not in
the filings is shown as n/a and not counted.

**Altman Z** = 1.2 WC/TA + 1.4 RE/TA + 3.3 EBIT/TA + 0.6 MVE/TL + 1.0 Sales/TA.
Safe above 2.99, distress below 1.81, flagged as not meaningful for banks and insurers.

## 6. Discounted cash flow (`analytics/valuation.py`)

```
fcf = base FCF
for year y = 1 .. high + fade:
    g = growth                                             if y <= high
        growth + (terminal - growth) * (y - high)/(fade + 1)   otherwise
    fcf = fcf * (1 + g)
    PV += fcf / (1 + r)^y
TV  = fcf * (1 + terminal) / (r - terminal),  discounted by (1 + r)^(high + fade)
value per share = (PV + TV + net cash) / shares
```

Defaults: TTM FCF, the lower of 5-year revenue and FCF growth clamped to -5%..15%, r = 9%,
terminal = 2.5%. Checks: FCF > 0, r > terminal, terminal <= 5%.

**Reverse DCF**: bisection on stage-one growth in [-50%, 100%] until value = price.

**Monte Carlo DCF**: 20,000 draws of growth ~ N(g, 4 pts), r ~ N(r, 1 pt),
terminal ~ N(t, 0.5 pt); draws with r <= terminal + 1 pt are discarded; report percentiles and
P(value > price).

## 7. Risk (`analytics/risk.py`)

Daily simple returns `R`, risk-free per day `rf_d = (1 + rf)^(1/252) - 1`:

```
volatility = stdev(R) * sqrt(252)
Sharpe     = mean(R - rf_d) * 252 / volatility
Sortino    = mean(R - rf_d) * 252 / (sqrt(sum(min(R - rf_d, 0)^2) / N) * sqrt(252))
max DD     = max over t of 1 - P[t] / running max;   Calmar = CAGR / max DD
VaR95      = -5th percentile of R;   CVaR95 = -mean(R where R <= -VaR95)
beta       = cov(R, Rb) / var(Rb)
alpha      = (mean(R - rf_d) - beta * mean(Rb - rf_d)) * 252
tracking error = stdev(R - Rb) * sqrt(252);   information ratio = mean(R - Rb) * 252 / TE
up capture = mean(R | Rb > 0) / mean(Rb | Rb > 0)   (down capture likewise)
```

## 8. Efficient frontier (`analytics/portfolio.py`)

```
mu  = mean daily return * 252 per asset;  Cov = daily covariance * 252
repeat 5,000 times: w ~ Dirichlet(1, ..., 1)            # random long-only weights summing to 1
    return = w . mu;  vol = sqrt(w' Cov w);  Sharpe = (return - rf) / vol
mark the max-Sharpe and minimum-volatility portfolios
```

## 9. The offline analyst (`ai/offline.py`)

Five pillars, each a sum of fixed rules (for example ROIC > 15% is +2, interest coverage < 2 is
-2). Stance = Bullish if the total is >= 4, Bearish if <= -3, else Neutral; conviction is medium
when |total| >= 7. Every rule and its points are printed in the memo.
