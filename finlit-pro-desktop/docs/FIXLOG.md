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

### 27. Closing the window during an evaluation printed a traceback
**First Version:** a background job still running when the window closed (the walk-forward
evaluation takes several seconds) emitted its progress on a signal object Qt had already deleted,
which printed "RuntimeError: Signal source has been deleted" at exit.
**Current Version:** jobs emit through `Job._emit`, which notices the window has gone, marks the job
cancelled and stops quietly; closing the window also cancels every running job and waits up to three
seconds for them to stop.

### 28. A test that passed before the window was ready
**First Version:** a test waited for `w.ws and w.ws.forecast and ...`, which evaluates to `None`
while loading; pytest-qt treats a callback returning `None` as "condition met", so the test went on
before the model had finished and failed for the wrong reason.
**Current Version:** the condition is wrapped in `bool(...)`.


### 29. Work for the old symbol kept running after loading a new one
**First Version:** loading a new ticker while a research note or evaluation was running for the old
one left that job going: its progress appeared under the new symbol and its buttons stayed disabled.
The prediction and Monte Carlo views also kept the old symbol's charts until the new model finished.
**Current Version:** `load()` cancels research and evaluation, retires every job id of the old
symbol (model, evaluation, Monte Carlo, option chain, research, filings, benchmark) and clears the
prediction and Monte Carlo views straight away.

### 30. A failed load showed the old charts under the new name
**First Version:** typing a symbol that does not exist left the previous company's charts on screen
while the title, quote line and "Add to watchlist" button used the failed symbol.
**Current Version:** the window goes back to the symbol that did load, re-renders it and says
"Still showing X". With nothing loaded before, the title and status bar are reset.

### 31. "None" printed as a currency
**First Version:** when Yahoo did not report a currency, the quote line and the HTML report showed
"123.45 None".
**Current Version:** the currency is left out when unknown.

### 32. Smaller window fixes
**First Version / Current Version:**
* A failed SEC request left the Fundamentals and Filings views showing "loading"; now they show the
  reason. Funds and ETFs are told SEC fundamentals do not apply instead of searching for them.
* The benchmark could finish before prices and be dropped; it is now kept until prices arrive.
* The engine label said "Claude" when no Anthropic key was stored; it now says "(no API key stored)".
* The HTML report asked for charts that had no data; it now includes only charts that were drawn.
* Exporting CSV to a folder that cannot be written failed with no clear message; it now says what failed.
* Changing the fallback risk-free rate in Settings did nothing until the next load; it now applies at
  once when no live rate was found.
* "Add to watchlist" worked before prices loaded; it now waits for them.
* Valuation kept the previous symbol's DCF result when the new one could not be valued, and gave
  a generic reason; it clears the result and gives the specific reason (for example, banks).
* Piotroski showed "0 / 9" when none of the nine tests could be run; it now shows "n/a".
* Headlines are searched with the company name as well, so thinly covered tickers still get news.

### 33. Settings changed stored keys and then refused to save
**First Version:** with Claude selected, ticking "Remove the stored key" deleted the key from the
credential store, and only then did Save refuse because Claude had no key. The key was gone and the
settings were unchanged.
**Current Version:** Save works out first whether the selected engine will still have a key and
refuses before touching the store; after storing, each key row refreshes where its key now lives.

### 34. Exported prices lost precision
**First Version:** the price CSV used six significant digits for every column, so 1,234.567 was
written as 1234.57 and a volume of 51,234,567 as 5.12346e+07.
**Current Version:** prices keep ten significant digits and volume is written as a whole number.

### 35. The macOS build artifact did not open
**First Version:** the build uploaded `dist/` directly; the upload drops symlinks and the executable
bit, so the downloaded `FinLitPro.app` would not start.
**Current Version:** the app bundle is zipped with `ditto` first and the zip is uploaded.

### 36. Prices from Yahoo: second round
**First Version / Current Version:**
* **Latest session bar.** The bar rebuilt from Yahoo's quote summary used the previous close as its
  open and made up a high and low, so ASML.AS and AIR.PA were drawn as down days on up days. Now
  Yahoo's own open, high, low and volume are kept; only a missing value is filled, from the close.
* **Multi-ticker CSV.** A `yf.download` file holding AAPL and MSFT imported as MSFT took AAPL's
  prices (0 of 251 closes right). Now only the imported symbol's columns are used, and a file without
  that symbol is refused with the tickers it does hold.
* **Number formats in CSVs.** "2,007.00" became 2.007 and a "1.234.567" volume became 0. The
  convention is now decided once per file, and a file whose numbers can be read two ways is refused
  with what to do.
* **Offline copy.** One answer with no usable prices replaced the only good offline copy. A payload
  must now parse before it is saved.
* **BRK.B.** Every load first asked for "BRK.B" and got a 404. The spelling Yahoo answers to is now
  remembered.
* **Bar dates.** Every bar was dated with today's time offset, so after a daylight-saving change
  futures and currency bars moved to the previous day (65 weekend-dated bars for GC=F). Each bar is
  now dated in the exchange's own time zone; GC=F, EURUSD=X and AAPL match yfinance date for date.
* **Watchlist.** With the network down, a three-day-old price was shown as current. Only a copy
  under two minutes old is used now; otherwise the row stays blank.
* **Second host.** When `query1` answered 5xx, an old copy was returned without asking `query2`.
* **Malformed answers** raised a Python error that stopped the provider chain; they are now a data
  error and the chain moves on to yfinance.
* **Options as-of** used today's date; it is now the date of the newest trade in the chain.
* **Unknown currency** printed "None" or was assumed to be USD; it is now left out.
* **Cache clear** left temporary files behind; the CSV "missing column" message now names the
  file's columns.

### 37. SEC fundamentals: second round
**First Version / Current Version:**
* **One debt decision.** `sec.py` said "Total debt is n/a" while the ratios separately treated missing
  debt as zero unless interest expense was tagged, so SHOP and PLTR carried two contradictory notes
  and DASH and PINS were called debt-free. Now `sec.py` decides once (reported, none or unknown, see
  DATA_SOURCES.md) with at most one note, and reads notes, convertible notes, credit lines and
  commercial paper. DASH $2.7B, PINS $981M, ORCL $125.3B and MAR $16.9B now match yfinance.
* **ORCL.** Its notes payable were not read and a $0 long-term debt line won, so debt/equity read
  0.11 against more than $125B of debt.
* **CAT.** Its latest balance sheet tags no debt line; the figure from the fiscal year end is used,
  with a note giving its date.
* **One-class share counts.** HEI's count covered one share class, so its market cap was $16.8B
  instead of about $43B. A count outside 0.5 to 2 times the diluted count is now replaced, with a
  note; diluted counts tagged in thousands or millions are recognised.
* **Year-ago balance sheet.** ROE and ROA averaged fiscal-year ends; they now average the balance
  sheets a year apart. NVDA's ROE reads 117.2%, as yfinance does, instead of 99.9%.
* **False "no quarterly figures" note** for companies whose 10-Qs SEC had not yet published as XBRL
  (C); the note now names the filings that are waiting.
* **Filing sections.** A Risk Factors heading on the same line as "PART II" was missed, and short
  10-Q Risk Factors ("no material changes") were dropped as not found.
* **Form 20-F filers** (TSM) are told where to read their statements; an invalid email is reported
  once, not once per filing.

### 38. Ratios, model and simulation: second round
**First Version / Current Version:**
* **Debt in the ratios.** Valuation no longer decides or notes debt; it uses the SEC figure, and
  leaves EV, EV/EBIT, net debt, debt/equity, ROIC and the DCF's net cash blank when debt is unknown.
* **Old interest expense.** Interest coverage used the newest year with any interest expense, so
  AAPL's came from FY2023 and PLTR's 759x from years ago. Only TTM or the last fiscal year is used now.
* **CAGR** counted reported values instead of years, so DELL's "5-year" EPS CAGR ran over six years.
* **One financial-company test** for ratios, the DCF, Piotroski and Altman, covering exchanges and
  brokers (CME, GS, SCHW) and not insurance brokers (AON).
* **Strategy equity** could go below zero for a short position and keep compounding (drawdowns
  above 1,000%, a CAGR of "+nan%"); capital that is gone now stays gone. A loss in the first period
  now counts toward the maximum drawdown.
* **Information coefficient.** A significantly negative IC (forecasts ranking outcomes backwards)
  was shown without a flag; only a significantly positive one clears it now.
* **Evaluation messages.** No forecast at all raised a KeyError; advice to try a shorter horizon
  named horizons the model does not offer ("4 days"); "about 1 months" now reads "about 1 month".
* **Constant prices** (a money market fund such as VMFXX) crashed v1.0 with an IndexError, as the
  original did; it now refuses with a message that says why. Every other input gives exactly the
  original's numbers (the v1.0 reproduction test is unchanged).
* **Volatility override.** With historical drift, raising the volatility raised the expected return
  (MSFT +22% to +95% a year); the historical arithmetic return is now kept.
* **Implied volatility** returned the 500% search bound when no volatility reaches the premium; it
  now returns nothing and the Market-implied row is dropped.
* **Monte Carlo and calibration messages.** A history too short for the simulation no longer says
  "shorten the lookback"; when calibration cannot run, the window shows the reason.
* **BRK.B** is loaded as BRK-B, the spelling Yahoo uses, so SEC lookups and headlines match it.
* **ALGORITHMS.md** now describes the regression trend step as the code computes it (h steps past
  the last point).

### 39. Research note, inputs and settings: second round
**First Version / Current Version:**
* **Claude engine.** Only the first text block was kept, so when the server-side fallback finished a
  note in a second block, half the JSON was lost; all text blocks are joined now. Cancel was checked
  only once answer text arrived; every stream event is checked now and the stream is closed. An
  error inside the stream read "error (200)"; it now names the error (for example "overloaded"). A
  context-window stop is reported as such instead of as invalid JSON.
* **OpenAI engine.** Cancel did nothing and the note appeared anyway; a cancelled run now discards
  it, and the window ignores a note that arrives after Cancel. A cut-off answer ("length") and a 400
  error now say what happened and what to change.
* **Citations.** "S1, S3" in one entry was read as one unknown ID and the fact marked unverified;
  unknown IDs in interpretations and risks were dropped silently and are now named in a warning.
* **Brief.** Trailing returns counted trading sessions while the screen uses calendar days (AAPL 1Y
  +35.1% in the brief, +29.9% on screen); both use one table now. "52-week range" is labelled
  "Range since ..." for a shorter history. The DCF lines now cite the price and the filings.
* **Rules engine.** A negative free cash flow yield "prices in substantial growth", and an operating
  loss "covers interest -3.2 times"; both are now described as cash burn and no interest cover.
* **Number fields** deleted every comma, so "102,5" became 1025; a comma must now separate thousands
  ("1,000"), and anything else is refused with a message.
* **Suggestions and bounds.** "-3.5 paths" suggested -3, which the same field refuses, and bounds
  printed as "1e+06"; suggestions now fall inside the allowed range and numbers are written out.
* **Hidden characters** in a pasted key or email (a zero-width space) passed and later crashed the
  request; they are refused with a message.
* **Settings file.** Out-of-range values in a hand-edited `settings.json` (a negative excerpt length,
  an unknown engine) are dropped so the defaults apply.
* **Credential store.** With no secure store, Settings said keys were kept in "Keyring"; it now says
  the store is unavailable.
* **Money format.** 999,960 printed "$1,000.0K"; it now prints "$1.0M". An unknown currency no longer
  leaves "None" or a trailing space.
