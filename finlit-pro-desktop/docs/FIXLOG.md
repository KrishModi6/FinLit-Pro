# Fix log

Every defect found while building FinLit Pro Desktop, including the ones inherited from the two
earlier FinLit Pro versions it grew out of (the Streamlit app in `finlit-pro-legacy`, and the
website's JavaScript simulator). Each entry says what the first version did, what the current
version does, and why. The same First Version / Current Version notes sit in the code next to
each fix.

The prediction model is a special case. Its defects (entries 3 to 6) are **fixed in v1.1 and kept
in v1.0 on purpose**: v1.0 is the original model, reproduced exactly so its numbers can be checked
against the Streamlit app, and the evaluation can compare the two versions on the same history.

---

## Inherited from earlier FinLit Pro versions

### 1. Monte Carlo drift had the Ito correction applied twice
**Where:** FinLit Pro website, `src/pages/simulator/AiPredictor.jsx`.
**First Version:** drift was the mean of daily LOG returns, then each step used
`exp((drift - vol^2/2) dt + ...)`, the formula for an ARITHMETIC drift.
**Current Version:** a mean log return is already the log drift, so it is used as is
(`montecarlo.estimate`). The `sigma^2/2` term appears only when an arithmetic return is converted.
**Why it mattered:** every path was dragged down by `sigma^2/2` a year: 2% for a 20%-vol stock,
12.5% for a 50%-vol stock. High-volatility stocks looked far worse than their own history.
**Test:** `test_historical_drift_is_not_ito_corrected_twice`. (The website itself is not changed
here.)

### 2. Monte Carlo ran in a Python loop
**Where:** Streamlit app, AI Predictor.
**First Version:** two nested Python `for` loops, one `np.random.normal` call per day per path.
**Current Version:** one vectorised matrix of shocks and a cumulative sum.
**Result:** 10,000 paths over 252 days in 0.29 s instead of 3.65 s (13x), while also computing
path drawdowns and percentile bands for the fan chart.

### 3. RSI was the wrong RSI
**First Version:** gains and losses averaged with a plain 14-day rolling mean (Cutler's RSI).
**Current Version (v1.1, and every chart):** Wilder's smoothing, as every charting platform and the
FinLit Pro website use. v1.0 keeps the rolling mean.
**Test:** `test_rsi_matches_wilder_definition`, and `test_v11_changes_only_the_documented_parts`.

### 4. "10-day" momentum was 9 days
**First Version:** `closes[-10]`, which is nine sessions before `closes[-1]`.
**Current Version (v1.1):** `closes[-11]`, and `closes[-31]` for 30 days.

### 5. EMA target exploded at long horizons
**First Version:** the MACD gap was extrapolated linearly over the whole horizon, so a 3% gap
became a +63% "target" at one year. Harmless at the old 7 to 90 day horizons, absurd at 252.
**Current Version (v1.1):** momentum decays with a 60-session half-life. Short horizons are almost
unchanged (21 days counts as 18.6); 90 days counts as 56.

### 6. A made-up "confidence %"
**First Version:** "confidence" was `90 - disagreement between the three models`, shown with a %
sign next to a probability. It was not a probability of anything.
**Current Version:** v1.1 reports the disagreement itself as "model agreement" and drops the
percentage. v1.0 still shows it, labelled "original heuristic, not a probability". The real
measure of honesty is the out-of-sample evaluation (entry 16).

### 7. Every failure said "not enough data"
**First Version:** `except: return None` around the data fetch, so a typo, a timeout and a
delisted ticker all produced the same message.
**Current Version:** `data/http.py` maps each failure to its own message (timeout, no connection,
rate limited, unknown ticker, SEC needs an email) and falls back to cached data when it can.

---

## Found while building this version

### 8. Old EPS and share counts ignored stock splits
**Found with:** live Apple data. EPS read 9.21 for FY2017 and 2.98 for FY2018.
**First Version:** annual EPS and diluted shares were tabulated exactly as filed.
**Current Version:** each value keeps the filing date it came from, and `sec.apply_splits` restates
anything filed before a split using Yahoo's split events. Apple's FY2017 EPS now reads 2.30, and
NVIDIA's two splits (4:1 in 2021, 10:1 in 2024) give one consistent EPS series.
**Why it mattered:** the 5-year EPS growth rate, the share-count trend and the F-score's dilution
test were all wrong for any company that split. A share-ratio heuristic was rejected because Apple's
buybacks turned its 4:1 split into a 3.81x jump that a 4% tolerance missed.

### 9. P/E could mix pre- and post-split EPS
**First Version:** P/E = price / TTM EPS, where TTM EPS summed a 10-K and 10-Q figures.
**Current Version:** P/E = market cap / TTM net income, which has no per-share basis to mix up.

### 10. A failed Piotroski test said the opposite
**First Version:** "Cash flow exceeds net income: Fail ... Earnings backed by cash, low accruals".
**Current Version:** every test's detail shows the two numbers compared.

### 11. Insider filings buried the 10-K
**First Version:** the filings table listed the last 60 filings, which for Apple were nearly all
Form 4 insider trades.
**Current Version:** the last 300 are read, the table defaults to key forms (10-K, 10-Q, 8-K,
proxy, ownership), and the insider count over 90 days is shown separately.

### 12. Toolbar style leaked onto its buttons
**First Version:** the toolbar's stylesheet had no selector, so the Analyze button inherited the
toolbar's background and border and looked disabled.
**Current Version:** the rule targets `QWidget#Toolbar` only.

### 13. Panels spread their titles apart
**First Version:** a panel stretched by a taller neighbour shared the spare height between its
title, subtitle and table.
**Current Version:** panel content sits in an inner layout above a stretch.

### 14. Name collision in the Yahoo module
**First Version:** a new watchlist `quote()` function shadowed `urllib.parse.quote`, so building a
chart URL would have called the watchlist function and crashed. Caught in review before it ran.
**Current Version:** the import is `quote as urlquote`.

### 15. The demo market lost money
**First Version:** the simulated DEMO-MKT benchmark had a negative 3-year return by chance of the
seed, which made every DEMO risk number look strange.
**Current Version:** a seed with a market of about 6% a year and a stock of about 11%, and a DEMO
price that gives a believable P/E of 23.

---

## Found while building FinLit Pro Desktop

### 16. The model was never evaluated
**First Version:** the AI Predictor printed a verdict, a target and a "confidence" with no record of
how often it had been right.
**Current Version:** `model/evaluation.py` runs a point-in-time walk-forward test on the loaded
ticker: hit rate against the naive majority call with a p-value, error skill against a no-change
forecast, information coefficient with its t-statistic, 10-90 band coverage, Brier score, results by
verdict, and a long/flat and long/short strategy after costs against buy-and-hold. Nothing is fitted
to the evaluation period, origins do not overlap by default, and the history is truncated before
each forecast, which `test_walk_forward_is_point_in_time_and_scores_against_the_future` checks.

### 17. Forecast chart stretched back to 1970
**First Version:** the percentile bands were drawn from invisible curves (`pen=None`) that carry no
data bounds, and the fill between them reported an empty rectangle at the origin, so auto-range
included the year 1970 and the forecast was a sliver at the right edge.
**Current Version:** faint band edges, and fills added with `ignoreBounds=True`.

### 18. Axes printed raw scientific notation
**First Version:** the volume axis read "1e+07", the evaluation equity curve read "x0.001" from
pyqtgraph's automatic SI prefix, and the log-scale price chart labelled its axis with log values.
**Current Version:** `pgcharts.ValueAxis` labels volume as 12.5M and converts log axes back to
prices, with ticks at round prices.

### 19. "-0.00" in tables
**First Version:** a value of -0.001 formatted to two decimals printed "-0.00", for example the
market-implied expected value of a fairly priced option.
**Current Version:** `fmt` rounds first and never prints a negative zero.

### 20. The nearest option expiry was tomorrow
**First Version:** the option chain opened on the first listed expiry, usually a weekly expiring
the next day, where every probability collapses to the strike.
**Current Version:** it opens on the expiry closest to 30 days out; any listed expiry can be chosen.

### 21. The options payoff chart did not fit short contracts
**First Version:** the price axis was fixed at 60% to 140% of spot, so a one-week contract's whole
distribution was a sliver in the middle.
**Current Version:** the axis spans about 3.5 standard deviations of the terminal price, widened to
keep the strike and breakeven in view.

### 22. The research note and the Returns view disagreed on the 1-year return
**First Version:** the rules engine measured "past year" as 252 sessions; the Returns view uses one
calendar year. They differed by a few days and so by a few points.
**Current Version:** both use one calendar year.

### 23. "Net debt is -$1.4B"
**First Version:** a company with more cash than debt was described with a negative net debt.
**Current Version:** "Net cash is $1.4B (cash exceeds debt)".

### 24. Unknown model keys fell back silently
**First Version:** `registry.get("finlit-v9")` returned the default model without saying so.
**Current Version:** it raises an error naming the models that exist.

### 25. Settings files were trusted
**First Version:** `load_settings` passed any value in the JSON file straight into the settings, so
a hand-edited file could put text where a number belongs and crash a view later.
**Current Version:** only known fields of the right type are loaded; anything else is ignored, and
an unreadable file falls back to defaults. API keys are never in this file (they live in Windows
Credential Manager), and any old key field is dropped.

### 26. Literal dash characters in a regular expression
**First Version:** the pattern that finds "Item 7 - Management's Discussion" contained literal en and
em dash characters, which are easy to break when the file is re-saved in another encoding.
**Current Version:** they are written as `\u2013` and `\u2014` escapes.
