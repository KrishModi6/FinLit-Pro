# Fix log

Every defect found while building FinLit Quant, including the ones inherited from the two earlier
FinLit Pro versions it grew out of (the Streamlit app in `finlit-pro-legacy`, and the website's
JavaScript simulator). Each entry says what the first version did, what the current version does,
and why. The same First Version / Current Version notes sit in the code next to each fix.

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
**Current Version:** Wilder's smoothing, as every charting platform and the FinLit Pro website use.
**Test:** `test_rsi_matches_wilder_definition` compares against a line-by-line transcription.

### 4. "10-day" momentum was 9 days
**First Version:** `closes[-10]`, which is nine sessions before `closes[-1]`.
**Current Version:** `closes[-11]`.

### 5. EMA target exploded at long horizons
**First Version:** the MACD gap was extrapolated linearly over the whole horizon, so a 3% gap
became a +63% "target" at one year. Harmless at the old 7 to 90 day horizons, absurd at 252.
**Current Version:** momentum decays with a 60-session half-life. Short horizons are almost
close (21 days counts as 18.6); a year counts as 82 days instead of 252.

### 6. A made-up "confidence %"
**First Version:** "confidence" was `90 - disagreement between the three models`, shown with a %
sign next to a probability. It was not a probability of anything.
**Current Version:** the disagreement itself is reported, labelled "model agreement", and the real
honesty measure is the calibration test.

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
