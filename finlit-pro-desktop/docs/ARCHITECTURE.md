# Architecture

FinLit Pro is a Python desktop application on Qt (PySide6). It is layered so that everything below
the user interface works without Qt: the data, model, analytics and research layers can be used from
a script or a notebook, and the tests exercise them without a window.

```
                         +--------------------------------------------------+
  ui/                    |  MainWindow: toolbar, docks, menus, status bar   |
  (PySide6, pyqtgraph,   |  views/: Chart, Returns and Risk, Prediction,    |
   matplotlib)           |  Monte Carlo, Options, Fundamentals, Filings,    |
                         |  Research Note        workers.py: background jobs|
                         +-------------------------+------------------------+
                                                   | Workspace (one ticker)
                         +-------------------------v------------------------+
  pipeline.py            |  load prices -> risk -> model -> evaluation ->   |
  workspace.py           |  Monte Carlo -> SEC fundamentals -> ratios/DCF   |
                         +---+-------------+---------------+-----------+----+
                             |             |               |           |
  data/                  model/         analytics/      research/   credentials.py
  http (rate limit,      interface      indicators      sources      config.py
   retry, cache)         (integration   montecarlo      brief        validation.py
  prices (provider        point)        options         note         framing.py
   chain)                finlit_        risk            rules        fmt.py
  yahoo, yf_provider      predictor     valuation       claude
  sec, filings           evaluation                     openai_provider
  demo, models           registry                       render
```

## Layers

**`data/`** fetches and normalises. `http.py` is the only module that touches the network: a
per-host rate limiter, retries with backoff, timeouts, the disk cache with a stale-copy fallback,
and error messages that say what to do. `prices.py` runs the provider chain (Yahoo chart API,
yfinance, offline copy, imported CSV). `sec.py` turns XBRL company facts into annual, TTM and
balance-sheet figures with a `FactRef` (form, filed date, accession, link) for each value.
`filings.py` extracts the sections an analyst reads from 10-K and 10-Q HTML. Every dataset carries a
`Source` (provider, URL, retrieved time, as-of date, status).

**`model/`** holds the owner's prediction model and the contract any model must meet.
`interface.py` defines `PredictionModel` and `Forecast`; `finlit_predictor.py` is the FinLit AI
Predictor (v1.0 original, v1.1 corrected); `registry.py` lists the available models;
`evaluation.py` runs the point-in-time walk-forward test against any registered model. See
[MODEL.md](MODEL.md).

**`analytics/`** is pure computation on pandas and numpy: technical indicators, the Monte Carlo
engine and its calibration, risk statistics, valuation (ratios, Piotroski, Altman, DCF, reverse
DCF), and option pricing, probabilities and the worth-it verdict.

**`research/`** writes the research note. `sources.py` numbers every source; `brief.py` writes the
brief with source tags on every line; `claude.py` and `openai_provider.py` request the note as JSON
against `note.SCHEMA`; `rules.py` writes the same structure without a language model; `note.py`
parses and checks citations; `render.py` turns it into HTML.

**`ui/`** is the only layer that imports Qt. Views receive a `Workspace` and render it; they emit
signals for user requests, and `MainWindow` runs the work.

## One ticker, one Workspace

`Workspace` (in `workspace.py`) holds everything computed for the loaded symbol: price history,
benchmark, risk-free rate and their sources, fundamentals and ratios, the forecast and its
evaluation, the Monte Carlo result and calibration, risk statistics, filing text and headlines.
Views read from it; nothing else is shared between them. `pipeline.load("MSFT", email=...)` builds a
complete Workspace without a window:

```python
from finlit_pro import pipeline
ws = pipeline.load("MSFT", email="you@example.com")
ws.forecast.verdict, ws.evaluation.metric("Skill vs no-change").display, ws.ratios["pe"]
```

## Threads and stale results

Network calls and long computations run on Qt's thread pool (`ui/workers.py`). Each job carries a
request id per kind of work (load, model, evaluation, Monte Carlo, option chain, filings, research,
search). When a job finishes, the window ignores the result unless its id is still the latest and
its symbol is still the loaded one, so switching tickers quickly can never put one company's numbers
under another's name. Long jobs (evaluation, research) receive `progress` and `cancelled` callbacks
and can be stopped from the view.

On load, prices, SEC fundamentals and headlines are requested in parallel. When prices arrive the
chart, returns and options views render, and the model and Monte Carlo start; when the model
finishes, its evaluation starts. Each view shows what it has as soon as it has it.

## Errors

Expected failures (`DataError`, `ValidationError`, `AnalysisError`, `NoteError`, `CredentialError`)
carry a message written for the user and are shown in the relevant view's notice bar. Anything else
is logged with a traceback and shown as "Unexpected error (type: message)", so the window never
closes on an exception.

## Input validation

Every field the user types into goes through `validation.py` (ticker symbols, whole numbers,
decimals, ranges, emails, API keys). Each check rejects blanks, letters where a number is needed,
decimals where a whole number is needed, zero and negatives where they make no sense, and out-of-range
values, with a message that says what to type instead. Forms mark each bad field in red and show a
summary above the form.

## Definitions on hover

`glossary.py` holds every term the app displays (more than 320): its name, a plain-language
meaning, how to read it, and the labels it appears under. The shared widgets look labels up as they
are created, so views need no tooltip code of their own:

* `KpiStrip` and `Field` captions, table column headings and the first cell of each table row get
  the definition of the label; the other cells in a row get the row's definition, so hovering a
  number explains it. A view can add a note about the particular value (for example the filing a
  figure came from), which is appended.
* A KPI whose value is itself a term (a verdict such as STRONG SELL) explains that value.
* `install_tooltips(window)` walks the finished window once and adds definitions to captions,
  checkboxes, buttons, list choices and tabs that do not already have one.
* The research note carries definitions as HTML `title` attributes, which `TipBrowser` shows.

Unknown labels get no tooltip rather than a guess; ambiguous words such as "Price" or "Value" are
deliberately left out. Help > Glossary (F1) shows every term with a search box.

## Settings and credentials

`config.py` stores preferences (benchmark, ranges, watchlist, model choices, window layout) as JSON
in `%APPDATA%\FinLitPro\config\settings.json` and validates types on load. API keys never go there:
`credentials.py` stores them in the operating system's credential store through `keyring` (Windows
Credential Manager), reads `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` first if set, and refuses to save
a key at all when no secure store is available. The Settings dialog shows where a key comes from,
never the key, and **Test key** checks a key and the chosen model through the provider's Models API
(`research.check_key`), which costs nothing. The disk cache lives in `%LOCALAPPDATA%\FinLitPro\cache`. Setting `FINLIT_PRO_HOME`
moves all three folders (the tests and the self-test use this).

## Charts

Time series (price, volume, indicators, returns, drawdown, rolling statistics, model fan chart,
strategy equity) use pyqtgraph for fast pan, zoom and crosshair readouts on long histories.
Distributions and the options payoff use matplotlib, embedded with the QtAgg backend. Both follow
the theme in `ui/theme.py`.

## Packaging

`packaging/finlit_pro.spec` builds a folder app with PyInstaller (`dist\FinLitPro\FinLitPro.exe`).
`FinLitPro.exe --self-test` opens the window offscreen on DEMO in a temporary folder and exits 0 if
every core view loaded; the build workflow runs it on Windows.
