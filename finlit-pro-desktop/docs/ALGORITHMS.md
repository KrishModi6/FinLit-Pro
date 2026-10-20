# Algorithms

How every number in FinLit Pro is computed, in plain pseudocode. Each section names the file that
implements it, under `finlit_pro/`.

Notation: `P[t]` is the adjusted close on trading day `t`, `r[t] = ln(P[t] / P[t-1])` is the daily
log return, `h` is a horizon in trading days, and a year is 252 trading days.

---

## 1. Prices: the provider chain (`data/prices.py`, `data/yahoo.py`, `data/yf_provider.py`)

```
load_history(symbol):
    if symbol is DEMO or DEMO-MKT: return the seeded simulation (never online)
    attempts = []
    try Yahoo chart API, live or fresh cache       -> return it
        if Yahoo says the symbol does not exist: stop and say so (no point asking elsewhere)
        else attempts += reason
    try yfinance                                   -> return it, with attempts
    try the last cached Yahoo copy, however old    -> return it as "Offline copy", with attempts
    try a CSV the user imported for this symbol    -> return it as "Imported file", with attempts
    fail with every attempt listed and what to do next (wait, or import a CSV)
```

Parsing the Yahoo chart response:

```
GET chart?period1=0&period2=<now, rounded to the hour>&interval=1d&events=div,split
for each bar:
    date  = timestamp + exchange UTC offset, truncated to the day
    skip the bar if close is missing or <= 0          # Yahoo pads gaps with nulls
    open/high/low default to close if missing         # a flat candle, not a hole
previous_close = close of the previous daily bar
splits = { date: numerator / denominator }
source = Source("Yahoo Finance chart API (SYMBOL)", quote page URL, retrieved now, as of last bar date)
```

Returns use the dividend- and split-adjusted close; the chart uses the traded OHLC. Every request
passes through `data/http.py`, which spaces requests per host (SEC 5 per second, Yahoo 2 per
second), retries 429 and 5xx with backoff, times out after 15 seconds, caches to disk, and turns
every failure into a message that says what to do.

## 2. The FinLit AI Predictor (`model/finlit_predictor.py`)

Both versions share this structure. Differences are marked **v1.0** (the original, reproduced
exactly) and **v1.1** (the corrected version).

```
input  = the last 730 calendar days of daily bars, auto-adjusted:
         open/high/low/close *= adjclose / close      # what yfinance history(period="730d") returned
require at least 60 sessions

1. Monte Carlo (40% weight)
   mu, sigma = mean and population stdev (ddof 0) of daily log returns
   RandomState(42); shocks = Normal(mu, sigma), shape (simulations, h)
   path = P_0 * exp(cumulative sum of shocks)          # same stream as the original's nested loops
   mc_median = median(terminal); P10..P90; prob_up = share of terminal > P_0

2. Regression trend (30% weight)
   least-squares line through the last 120 closes, evaluated h - 1 steps past the last point
   R^2 reported as a diagnostic

3. EMA momentum (30% weight)
   m = (EMA12 - EMA26) / EMA26                        # pandas ewm, adjust=True
   v1.0: ema_target = P * (1 + m * h / 12)            # momentum extrapolated linearly
   v1.1: ema_target = P * (1 + m * D(h) / 12),  D(h) = (1 - e^(-k h)) / k,  k = ln 2 / 60

4. Six signals, each -2..+2, summed into a score in -12..+12
5. composite = 0.4 * mc_median + 0.3 * trend + 0.3 * ema_target
   verdict  = STRONG BUY if score >= 4, BUY >= 2, STRONG SELL <= -4, SELL <= -2, else HOLD
   spread   = stdev(mc_median, trend, ema_target) / P: agreement High < 2%, Medium < 5%, else Low
   v1.0 only: confidence % = min(95, 90 - spread) | min(80, 75 - spread) | max(30, 60 - spread)
```

Signal thresholds (unchanged from the original):

| Signal | +2 | +1 | -1 | -2 |
| --- | --- | --- | --- | --- |
| RSI 14 | < 30 | < 40 | > 60 | > 70 |
| MACD 12,26,9 | above signal and histogram rising | above signal | below signal | below and histogram falling |
| Moving averages | price > SMA20 > SMA50 | price > SMA20 | price < SMA20 | price < SMA20 < SMA50 |
| Bollinger 20,2 position | < 5% | < 20% | > 80% | > 95% |
| Volume vs 20-day average | > 1.5x on an up day | > 1.2x on an up day | | > 1.5x on a down day |
| Momentum | 10d > 5% and 30d > 10% | 10d > 2% | 10d < -2% | 10d < -5% and 30d < -10% |

```
RSI   v1.0: 100 - 100 / (1 + rolling_mean(gains, 14) / rolling_mean(losses, 14))   # Cutler's RSI
      v1.1: Wilder's smoothing (alpha = 1/14)
"10d" v1.0: closes[-10] (nine sessions back), "30d" closes[-30]
      v1.1: closes[-11] and closes[-31]
```

## 3. Walk-forward evaluation (`model/evaluation.py`)

```
step  = h (non-overlapping) unless the user picks every 5 sessions
first = first session with a full 730-day lookback behind it
origins = first, first + step, ... while origin + h is inside the data   (most recent 250 kept)
for each origin t:
    f = model.predict(bars[0 .. t], h, 500 simulations, seed 42)   # nothing after t is visible
    realised = P[t + h] / P[t] - 1
    record f.expected_return, f.target, f.verdict, f.P10, f.P90, f.prob_up, realised

hit rate       = share where sign(forecast) == sign(realised)
naive          = max(share up, share down)              # always call the majority direction
p-value        = one-sided normal test of hit rate > naive, se = sqrt(naive (1 - naive) / n)
MAE            = mean |target - realised price| / P[t];   no-change MAE uses the price itself
skill          = 1 - MAE / no-change MAE
IC             = Spearman rank correlation(forecast return, realised);  t = IC sqrt((n-2)/(1-IC^2))
coverage       = share of realised prices inside [P10, P90]   (calibrated = about 80%)
Brier          = mean (prob_up - 1[realised > 0])^2,  against the constant base rate
strategy       long/flat: +1 on BUY or STRONG BUY else 0;  long/short adds -1 on SELL or STRONG SELL
               period return = position * realised - |change in position| * cost
               CAGR, Sharpe (annualised with 252/h periods per year), max drawdown, exposure
buckets        per verdict: count, mean realised return, hit rate, mean forecast
```

Flags appear next to a metric when it fails its comparison (for example "not significantly better
than the naive call"). Every figure is computed for the selected ticker at run time; none is
stored or quoted as general performance.

## 4. Monte Carlo simulation (`analytics/montecarlo.py`)

### Estimation

```
r       = last `lookback` daily log returns            # default 3 years
hist_mu = mean(r);  sigma = stdev(r)   (or the user's volatility override / sqrt(252))
kurt    = mean((r - hist_mu)^4) / mean((r - hist_mu)^2)^2 - 3
t_df    = clamp(4 + 6 / kurt, 3, 30)  if kurt > 0 else 30
          # excess kurtosis of a Student-t is 6 / (df - 4), inverted

drift (daily log drift actually simulated):
    historical: mu = hist_mu                          # already a log drift: no correction
    zero:       mu = -sigma^2 / 2                     # makes E[P_h] = P_0
    custom R:   mu = ln(1 + R) / 252 - sigma^2 / 2    # arithmetic R -> log drift
```

The `sigma^2 / 2` term appears only where an arithmetic return is converted into a log drift.
The FinLit Pro website applied it to a log drift as well (FIXLOG #1).

### Simulation and statistics

```
for every path i and day d (vectorised as an n x h matrix):
    gbm:        shock = mu + sigma * Z,                        Z ~ Normal(0, 1)
    student_t:  shock = mu + sigma * T * sqrt((df-2)/df),      T ~ t(df), unit variance
    bootstrap:  random blocks of 10 consecutive historical returns, demeaned, plus mu
path[i, d] = P_0 * exp(cumulative sum of shocks up to d)

terminal = path[:, h];  percentiles 5..95;  prob_up = share of terminal > P_0
loss = 1 - terminal / P_0;  VaR95 = 95th percentile of loss;  CVaR95 = mean loss beyond it
max_dd[i] = max over d of 1 - path[i, d] / running max;  expected max drawdown = mean
```

### Calibration

```
for origin t = lookback, lookback + step, ... while t + h is in the data:
    window = r[t - lookback : t]                       # only data available at t
    z = (ln(P[t+h] / P[t]) - mean(window) h) / (stdev(window) sqrt(h))
    pit = NormalCDF(z)                                 # where the outcome fell, 0..1
coverage(lo..hi) = share of pit inside [lo, hi]
verdict: too narrow if 10-90 coverage < 70%, too wide if > 90%, else reasonably calibrated
```

## 5. Options (`analytics/options.py`)

```
t = calendar days to expiry / 365;   r = risk-free;   q = dividend yield (trailing 12m / price)

Black-Scholes-Merton with dividends:
    d1 = (ln(S/K) + (r - q + vol^2/2) t) / (vol sqrt t);   d2 = d1 - vol sqrt t
    call = S e^(-qt) N(d1) - K e^(-rt) N(d2);   put = K e^(-rt) N(-d2) - S e^(-qt) N(-d1)
    Greeks: delta, gamma, theta per calendar day, vega and rho per 1 percentage point
implied vol = bisection on [0.1%, 500%] until BSM price = premium (none below intrinsic)

Under a lognormal price with continuous drift mu and volatility vol:
    P(S_T > x) = N( (ln(S/x) + (mu - vol^2/2) t) / (vol sqrt t) )
    E[call payoff] = F N(d1) - K N(d2),  F = S e^(mu t),  d1 = (ln(F/K) + vol^2 t / 2) / (vol sqrt t)

For each scenario:
    Market-implied:   vol = implied vol, mu = r - q    -> expected value is 0 by construction
    Your assumptions: vol = your volatility, mu = ln(1 + your expected return)
    Fat-tailed MC:    terminal prices from the Student-t simulation at the same horizon
    P(profit)   = P(S_T beyond breakeven);   P(ITM) = P(S_T beyond strike)
    fair value  = e^(-rt) E[payoff];         EV = fair value - premium (long), premium - fair (short)

Verdict, from "Your assumptions":
    edge = EV / premium
    Worth it if edge >= +5%;  Not worth it if edge <= -5%;  otherwise Marginal
Notes: implied vs your volatility when they differ by 10% or more; a long option with
P(profit) < 25% is flagged as relying on a minority of large moves.
```

## 6. Fundamentals from SEC EDGAR (`data/sec.py`)

### Annual figures, with provenance

```
for each metric (revenue, net income, ...):
    for each XBRL tag that can carry it, in priority order:
        keep facts from 10-K/20-F/40-F whose duration is 340..390 days
        for each fiscal year end, keep the fact from the most recently FILED document
    merge the tags: for each year, the highest-priority tag with a value wins
    refs[metric][year] = (form, filed date, accession, link to the filing index)
```

Companies switch tags (revenue moved to `RevenueFromContractWithCustomer...` in 2018), every 10-K
repeats two prior years, and a later filing's comparative is the restated number. The `refs` let
every cell in the Fundamentals table, and every SEC figure in the research note, cite its filing.

### Trailing twelve months

```
FY       = latest annual value
YTD      = value from the latest 10-Q with the longest duration starting after FY end
priorYTD = the fact of the same length ending about 364 days earlier
TTM = FY + YTD - priorYTD           (or FY if no 10-Q since)
```

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
        if the filing it came from was filed before S: EPS /= k; shares *= k
    if the cover-page share count is dated before S: shares_outstanding *= k
```

## 7. Filing text (`data/filings.py`)

```
html -> text: drop <script>, <style>, <head>, hidden inline-XBRL headers; block tags become
              line breaks; entities decoded; runs of blank lines collapsed
for each section (10-K: Item 1, 1A, 7;  10-Q: Part I Item 2, Part II Item 1A):
    starts = every match of the section heading;  ends = every match of the next heading
    take the LONGEST span start -> next end      # the table of contents is a one-line span
    under 500 characters: report "not found" (often incorporated by reference)
    cut to the configured length on a line break, and mark it truncated
latest reports = the newest 10-K, plus the newest 10-Q if it was filed after that 10-K
```

## 8. Ratios, quality scores and valuation (`analytics/valuation.py`)

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

**Piotroski F-score** (current year vs prior): ROA > 0; CFO > 0; ROA rose; CFO > net income;
debt to average assets fell; current ratio rose; diluted shares did not rise; gross margin rose;
asset turnover rose. A test without inputs is n/a and not counted.

**Altman Z** = 1.2 WC/TA + 1.4 RE/TA + 3.3 EBIT/TA + 0.6 MVE/TL + 1.0 Sales/TA. Safe above 2.99,
distress below 1.81, not meaningful for banks and insurers.

**DCF**

```
fcf = base FCF
for year y = 1 .. high + fade:
    g = growth if y <= high else growth + (terminal - growth) * (y - high) / (fade + 1)
    fcf = fcf * (1 + g);  PV += fcf / (1 + r)^y
TV = fcf * (1 + terminal) / (r - terminal), discounted by (1 + r)^(high + fade)
value per share = (PV + TV + net cash) / shares
```

Defaults: TTM FCF, the lower of 5-year revenue and FCF growth clamped to -5%..15%, r = 9%,
terminal 2.5%. **Reverse DCF**: bisection on stage-one growth until value = price. **Monte Carlo
DCF**: 20,000 draws of growth, discount rate and terminal growth; reports P(value > price).

## 9. Returns and risk (`analytics/risk.py`)

Daily simple returns `R` over the selected date range, risk-free per day `rf_d = (1 + rf)^(1/252) - 1`:

```
volatility = stdev(R) sqrt(252);   Sharpe = mean(R - rf_d) 252 / volatility
Sortino    = mean(R - rf_d) 252 / (downside deviation sqrt(252))
max DD     = max over t of 1 - P[t] / running max;   Calmar = CAGR / max DD
VaR95      = -5th percentile of R;   CVaR95 = -mean(R where R <= -VaR95)
beta       = cov(R, Rb) / var(Rb);   alpha = (mean(R - rf_d) - beta mean(Rb - rf_d)) 252
tracking error = stdev(R - Rb) sqrt(252);   information ratio = mean(R - Rb) 252 / TE
up capture = mean(R | Rb > 0) / mean(Rb | Rb > 0)   (down capture likewise)
```

## 10. Research note (`research/`)

```
brief.build(workspace):
    registry = numbered sources S1, S2, ...: price dataset, benchmark, risk-free, SEC company facts,
               each 10-K/10-Q cited by accession, each filing section read, each FinLit Pro
               computation (ratios, DCF, model, Monte Carlo), each headline (marked unverified)
    every line of the brief ends with the IDs of the records it came from, e.g. [S3, S4]

engine:
    Claude (official SDK, streamed, structured output against the note's JSON schema,
            server-side fallbacks on Opus 5.5 and Sonnet 5.5)
    or OpenAI (json_schema, strict)
    or the rules engine (no key needed)

parse(note JSON, registry):
    every cited ID is normalised ("[s3]" -> "S3") and checked against the registry
    a fact citing an unknown ID, or nothing, is kept but marked UNVERIFIED and counted in a warning
    confidence and recommendation values outside the schema fall back to Low / No recommendation
render: facts grouped by topic with linked citations; interpretation with confidence;
        risks; uncertainties; data gaps; the full source table with dates and retrieval times
```

**Rules engine** (`research/rules.py`): facts are read directly from the workspace and cited with
the same IDs. Interpretations come from fixed thresholds, each adding to a score: ROIC (> 15%: +2,
> 8%: +1, else -1), 3-year revenue CAGR (> 15%: +2, > 5%: +1, < 0: -1), FCF yield (> 6%: +2,
> 4%: +1, < 2%: -1), implied versus delivered FCF growth (gap > 5 pts: -1, < -5 pts: +1),
interest coverage (< 2: -2, > 8: +1), Piotroski (>= 70% of tests: +1, <= 35%: -1), Sharpe
(> 0.8: +1, < 0: -1), and the prediction model's verdict (+1 or -1) only if its out-of-sample skill,
hit rate and IC all pass. Buy at >= 5, Accumulate >= 2, Sell <= -5, Reduce <= -2, else Hold;
conviction Medium at |score| >= 6. It states in its uncertainties that it does not read filing text.
