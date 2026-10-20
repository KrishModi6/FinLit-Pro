# Data sources

Where every number in FinLit Pro comes from, what each source permits, how often it is fetched,
and what happens when it fails. The **Data sources** panel at the bottom of the window shows, for
the loaded ticker, each dataset's provider, status, as-of date and retrieval time, with a link
(double-click a row). Every view repeats its own sources under its charts, and the exported report
ends with the full list.

## Summary

| Data | Provider | Official? | Cached for | If it fails |
| --- | --- | --- | --- | --- |
| Daily prices, dividends, splits | Yahoo Finance chart API | No (unofficial, undocumented) | 15 minutes | yfinance, then the last cached copy, then an imported CSV |
| Watchlist quotes | Yahoo Finance chart API | No | 2 minutes | The row stays blank |
| Ticker search | Yahoo Finance search API | No | 24 hours | Type the exact symbol instead |
| Headlines | Yahoo Finance search API | No | 15 minutes | Omitted from the research brief |
| Risk-free rate | Yahoo Finance `^IRX` (13-week T-bill) | No | 6 hours | The rate in Settings (default 4%) |
| Option chains | Yahoo Finance, through `yfinance` | No | 2 minutes, in memory | Enter the contract by hand |
| Ticker to CIK | SEC `company_tickers.json` | Yes | 7 days | Fundamentals unavailable, with the reason |
| Financial statements | SEC XBRL company facts | Yes | 12 hours | Last cached copy, marked "Offline copy" |
| Company profile, filing index | SEC submissions | Yes | 6 hours | Last cached copy |
| Filing text (10-K, 10-Q) | SEC EDGAR Archives | Yes | 7 days (filed documents do not change) | Listed as a data gap in the note |

Status labels, used everywhere a source is shown:

| Status | Meaning |
| --- | --- |
| Live | Fetched now |
| Cached | From the disk cache, within its lifetime above |
| Offline copy | The provider failed; this is the last copy saved, and its retrieval time says how old |
| Imported file | From a CSV you imported (File > Import prices) |
| Simulated | The DEMO ticker: generated data, not a real security |

## Yahoo Finance

**Endpoints.** `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}` (with `query2` as a
second host), `/v1/finance/search`, and the options data `yfinance` reads.

**Terms.** Yahoo does not offer these endpoints as a public API: they are undocumented, have no
published rate limit, and can change or be blocked without notice. The `yfinance` project states it
is not affiliated with Yahoo, that it is intended for research and educational purposes, and that
Yahoo's data is intended for personal use; Yahoo's own terms of use govern what you may do with the
data. FinLit Pro is built on that basis: single-user, personal research, nothing republished.
**Do not assume these sources are guaranteed or unrestricted.**

**How FinLit Pro treats them.**

* At most 2 requests per second to Yahoo hosts, from all views combined.
* Retries with backoff on HTTP 429 and 5xx, honouring `Retry-After`; a 15-second timeout.
* Everything cached on disk (`%LOCALAPPDATA%\FinLitPro\cache` on Windows).
* A provider chain for prices: chart API, then `yfinance`, then the last cached copy, then a CSV you
  imported. Each failed step is recorded and shown in the provider log beside the sources table,
  and in a notice above the views.
* An unknown symbol stops the chain at once with a clear message, rather than asking every provider.
* Delayed quotes: option and price data may be 15 minutes old or more during market hours. The
  as-of date shown is the date of the last bar, and the retrieval time is when FinLit Pro fetched it.

**Adjustments.** Returns, the prediction model and the Monte Carlo use the adjusted close
(dividends and splits); the chart shows traded prices. Split events also restate per-share figures
from SEC filings made before a split (see ALGORITHMS.md, section 6).

**When Yahoo is unavailable.** Import a CSV of daily prices (Yahoo's download layout, or any file
with Date and Close columns; Open, High, Low, Adj Close and Volume are optional). It is stored in
`%APPDATA%\FinLitPro\data\imports` and used whenever the online providers fail.

## SEC EDGAR

**Endpoints.** `https://www.sec.gov/files/company_tickers.json`,
`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`,
`https://data.sec.gov/submissions/CIK##########.json`, and filing documents under
`https://www.sec.gov/Archives/edgar/data/`.

**Terms.** EDGAR data is public and free. The SEC's fair access policy asks automated tools to
declare a User-Agent that identifies the requester with a contact email, and to stay at or below 10
requests per second. FinLit Pro sends `FinLitPro/<version> <your email>` and stays at 5 requests per
second. The email is set once (the Fundamentals view asks for it, or Settings > Data) and is sent
only to sec.gov. Without it, every view except Fundamentals, Filings and the SEC parts of the note
still works.

**What is read.**

* Annual figures from 10-K, 20-F and 40-F filings, ten fiscal years, choosing for each year the
  most recently filed value (restatements win) and merging the XBRL tags companies switch between.
* Trailing-twelve-month flows from the latest 10-Q's year-to-date figures.
* The latest balance sheet and the cover-page share count.
* Every figure keeps the filing it came from (form, filed date, accession number, link). Hover a cell
  in the Fundamentals table to see it; double-click to open the filing on sec.gov.
* Filing text: Item 1, 1A and 7 of the latest 10-K, and Item 2 and 1A of a newer 10-Q, extracted
  from the primary HTML document and cut to the length set in Settings. The Filings view shows the
  text that the research note reads.

**Limits.** ETFs, indices, funds, crypto and most non-US listings do not file XBRL financial
statements; for those, the price, model, Monte Carlo and options views work and the Fundamentals
view says why it is empty. Foreign filers that report under IFRS are not parsed. XBRL tagging varies
between companies; a missing figure is shown as n/a, never guessed.

## Analysis engines (optional)

The research note can be written by Claude (Anthropic) or an OpenAI model when you store a key, or
by the built-in rules engine with no key. With a language model, the research brief (the figures,
filing excerpts and headlines the note is based on, which you can read with **Show brief**) is sent
to that provider's API. Nothing is sent anywhere until you press **Generate note**.

## Timestamps

* **As of**: the date the data describes (the last price bar, the balance sheet date, the filing's
  period).
* **Retrieved**: when FinLit Pro fetched it (for a cached copy, when it was first fetched).
* **Filed**: for SEC data, the date the filing was made, shown with the accession number.

The research brief and note carry the same three, per source ID.

## Simulated data

The **DEMO** ticker (with its **DEMO-MKT** benchmark) is a seeded random walk with matching
simulated financial statements. It never goes online and is labelled "Simulated" everywhere,
including in the research note. It exists so every view can be tried with no network.
