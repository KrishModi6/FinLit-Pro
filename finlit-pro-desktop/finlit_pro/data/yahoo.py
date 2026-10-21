"""Yahoo Finance: daily history, quotes, ticker search, headlines, T-bill yield.

These are Yahoo's public but undocumented endpoints. They need no key, are
not covered by any service agreement, and can change or rate limit without
notice; Yahoo's terms allow personal, non-commercial use. The app treats
them accordingly: everything is cached, requests are throttled, and
`prices.py` falls back to other routes when this one fails.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from datetime import datetime
from urllib.parse import quote as urlquote

import numpy as np
import pandas as pd

from finlit_pro import validation
from finlit_pro.data.http import BROWSER_UA, Fetched, cache, get_json
from finlit_pro.data.models import STALE, DataError, NetworkError, NewsItem, NotFoundError, PriceHistory, Source

HOSTS = ("https://query1.finance.yahoo.com", "https://query2.finance.yahoo.com")
HEADERS = {"User-Agent": BROWSER_UA, "Accept": "application/json"}
SERVICE = "Yahoo Finance"
QUOTE_PAGE = "https://finance.yahoo.com/quote/{symbol}"
# About 1900-01-01, the start yfinance has used for period="max". Yahoo accepts
# dates before 1970 and returns everything from the first listed day.
EARLIEST = -2208994789
# Class shares as people usually write them (BRK.B, BF.B); Yahoo spells them BRK-B, BF-B.
CLASS_SHARE = re.compile(r"^[A-Z]{1,5}\.[A-Z]$")


def not_found_message(symbol: str, also: list[str] | None = None) -> str:
    """What to say when Yahoo has nothing under a symbol: a typo, or a company that is gone."""
    tried = "".join(f' or "{s}"' for s in also or [])
    return (
        f'Yahoo Finance has no data for "{symbol}"{tried}. The symbol may be misspelled, or the company may have been '
        "delisted or acquired. Check the spelling, or search by company name to find its current ticker."
    )


def spellings(symbol: str) -> list[str]:
    """The symbol, then the dash spelling Yahoo uses for a class share (BRK.B -> BRK-B).

    Exchange suffixes (SAP.DE, 7203.T, SHOP.TO) never match, and a single-letter
    suffix that Yahoo knows (BP.L) is found on the first try, so neither is rewritten.
    """
    return [symbol, symbol.replace(".", "-")] if CLASS_SHARE.match(symbol) else [symbol]


def history_key(symbol: str) -> str:
    """The cache key of a symbol's full history: stable, so the offline copy is always found."""
    return f"yahoo:history:{symbol}"


def _get(path: str, ttl_s: float, not_found: str | None = None, allow_stale: bool = True, cache_key: str | None = None) -> Fetched:
    """The first Yahoo host that answers.

    First Version: any failure, including a timeout or a refused connection, moved
    on to the second host, so a network that was down or hanging cost two full
    timeouts. Current Version: a not-found answer or a network failure stops here
    (both hosts sit behind the same network); other errors (HTTP 5xx, unreadable
    data) still try the second host.
    """
    last_error: DataError | None = None
    for host in HOSTS:
        try:
            return get_json(host + path, headers=HEADERS, ttl_s=ttl_s, not_found_message=not_found, service=SERVICE, allow_stale=allow_stale, cache_key=cache_key)
        except (NotFoundError, NetworkError):
            raise
        except DataError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def _chart(symbol: str, query: str, ttl_s: float, allow_stale: bool = True, key: Callable[[str], str] | None = None) -> tuple[str, Fetched]:
    """A v8 chart response and the spelling Yahoo answered to.

    First Version: BRK.B, the usual way to write Berkshire's class B shares, failed
    with "does not recognise" (and HTTP 404 in the watchlist), because Yahoo spells it
    BRK-B; searching "BRK.B" as advised found an unrelated ETF. Current Version: when
    Yahoo does not know a class-share spelling, the dash spelling is tried once.
    """
    names = spellings(symbol)
    message = not_found_message(symbol, names[1:])
    for name in names:
        try:
            path = f"/v8/finance/chart/{urlquote(name, safe='^=')}?{query}"
            return name, _get(path, ttl_s, not_found=message, allow_stale=allow_stale, cache_key=key(name) if key else None)
        except NotFoundError:
            if name == names[-1]:
                raise
    raise AssertionError("unreachable")


def _positive(value) -> float | None:
    return float(value) if isinstance(value, (int, float)) and np.isfinite(value) and value > 0 else None


def _add_latest_session(bars: pd.DataFrame, meta: dict, offset: int, price: float | None) -> pd.DataFrame:
    """Add the session meta reports when Yahoo has not filled in its daily bar yet.

    First Version: after the close Yahoo often sends the day's bar with a null close
    while meta.regularMarketPrice already holds that close. The null bar was dropped,
    so the price came from the new session and the previous close from two sessions
    back (AMZN +5.05% instead of +0.07%; MSFT shown up when it fell), the as-of date
    was a day old, and the model's last price differed from the Monte Carlo's.
    Current Version: when regularMarketTime falls on a later exchange-local date than
    the last bar with a close, a bar for that session is built from meta (close =
    regularMarketPrice, the day's high, low and volume; the chart meta has no open, so
    the previous close stands in, kept within the day's range). The price, the last
    bar, the previous close and the as-of date then agree.
    """
    when = meta.get("regularMarketTime")
    if price is None or bars.empty or not isinstance(when, (int, float)):
        return bars
    day = pd.DatetimeIndex(pd.to_datetime(np.asarray([when], dtype="int64") + offset, unit="s")).normalize().as_unit(bars.index.unit)
    if day[0] <= bars.index[-1]:
        return bars
    prev = float(bars["close"].iloc[-1])
    open_ = _positive(meta.get("regularMarketOpen")) or prev
    high = max(_positive(meta.get("regularMarketDayHigh")) or max(open_, price), price)
    low = min(_positive(meta.get("regularMarketDayLow")) or min(open_, price), price)
    open_ = min(max(open_, low), high)
    volume = meta.get("regularMarketVolume")
    volume = float(volume) if isinstance(volume, (int, float)) and volume >= 0 else 0.0
    row = pd.DataFrame({"open": open_, "high": high, "low": low, "close": price, "adjclose": price, "volume": volume}, index=day, dtype="float64")
    return pd.concat([bars, row])


def parse_chart(payload: dict, symbol: str) -> PriceHistory:
    """Turn a v8 chart response into a PriceHistory. Raises DataError."""
    chart = (payload or {}).get("chart") or {}
    if chart.get("error"):
        error = chart["error"] or {}
        if str(error.get("code") or "").lower() == "not found":
            raise NotFoundError(not_found_message(symbol))
        desc = error.get("description") or "unknown error"
        raise DataError(f'Yahoo Finance has no data for "{symbol}" ({desc}). Check the ticker, or try again later.')
    result = (chart.get("result") or [None])[0]
    if not result or not result.get("timestamp"):
        raise DataError(f'Yahoo Finance returned no price history for "{symbol}".')

    meta = result.get("meta") or {}
    q = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    adj = (((result.get("indicators") or {}).get("adjclose") or [{}])[0]).get("adjclose")

    # Shift by the exchange's UTC offset before taking the date, or late bars
    # land on the next calendar day.
    offset = int(meta.get("gmtoffset") or 0)
    index = pd.to_datetime(np.asarray(result["timestamp"], dtype="int64") + offset, unit="s").normalize()

    def col(name: str, values) -> pd.Series:
        return pd.Series(values if values is not None else [np.nan] * len(index), index=index, name=name, dtype="float64")

    bars = pd.concat(
        [col("open", q.get("open")), col("high", q.get("high")), col("low", q.get("low")), col("close", q.get("close")),
         col("adjclose", adj if adj is not None else q.get("close")), col("volume", q.get("volume"))],
        axis=1,
    )
    # Yahoo pads gaps with nulls; a bar without a close is not a bar.
    bars = bars[bars["close"].notna() & (bars["close"] > 0)]
    bars = bars[~bars.index.duplicated(keep="last")].sort_index()
    for name in ("open", "high", "low"):
        bars[name] = bars[name].fillna(bars["close"])
    bars["adjclose"] = bars["adjclose"].fillna(bars["close"])
    bars["volume"] = bars["volume"].fillna(0)
    price = _positive(meta.get("regularMarketPrice"))
    bars = _add_latest_session(bars, meta, offset, price)
    if len(bars) < 2:
        raise DataError(f'Not enough price history for "{symbol}". It may be newly listed.')

    events = result.get("events") or {}
    dividends = pd.Series(
        {pd.to_datetime(int(d["date"]) + offset, unit="s").normalize(): float(d["amount"]) for d in (events.get("dividends") or {}).values() if "amount" in d},
        dtype="float64",
    ).sort_index()
    splits = pd.Series(
        {
            pd.to_datetime(int(s["date"]) + offset, unit="s").normalize(): float(s["numerator"]) / float(s["denominator"])
            for s in (events.get("splits") or {}).values()
            if s.get("numerator") and s.get("denominator")
        },
        dtype="float64",
    ).sort_index()

    price = price or float(bars["close"].iloc[-1])
    sym = str(meta.get("symbol") or symbol).upper()
    return PriceHistory(
        symbol=sym,
        name=meta.get("longName") or meta.get("shortName") or sym,
        currency=meta.get("currency") or "USD",
        exchange=meta.get("fullExchangeName") or meta.get("exchangeName"),
        instrument_type=meta.get("instrumentType"),
        price=price,
        # On daily bars the previous bar is the previous session. Yahoo's
        # chartPreviousClose is the close before the whole requested range.
        previous_close=float(bars["close"].iloc[-2]),
        bars=bars,
        source=Source(f"Yahoo Finance chart API ({sym})", QUOTE_PAGE.format(symbol=urlquote(sym, safe="^=")), datetime.now(), str(bars.index[-1].date())),
        dividends=dividends,
        splits=splits,
    )


def history(symbol: str, force: bool = False, allow_stale: bool = True) -> PriceHistory:
    """Full daily history since listing, with dividends and splits.

    First Version: period1=0 (1970-01-01) cut off older history (KO lost 1,987
    bars, 1962 to 1969), and the cache key was the URL, whose period2 was "now"
    rounded to the hour. The offline copy was therefore found only within the
    clock hour it was saved, and each hour wrote another full copy to disk.
    Current Version: period1 is about 1900 (KO starts 1962-01-02, as yfinance's
    period="max" does), and the copy is saved under history_key(symbol), which
    never changes, so the last copy is always the one found and replaced.
    """
    symbol = validation.ticker(symbol)
    query = f"period1={EARLIEST}&period2={int(time.time())}&interval=1d&events=div%2Csplit&includeAdjustedClose=true"
    name, fetched = _chart(symbol, query, 0 if force else 900, allow_stale, history_key)
    hist = parse_chart(fetched.value, name)
    hist.source.status = fetched.status
    hist.source.retrieved_at = datetime.fromtimestamp(fetched.saved_at)
    return hist


def cached_history(symbol: str) -> PriceHistory | None:
    """The last history saved for `symbol`, however old, read from disk with no network call.

    Labelled Offline copy, with the time it was saved. None when no copy was ever
    saved or the saved copy cannot be read.
    """
    symbol = validation.ticker(symbol)
    for name in spellings(symbol):
        entry = cache().get(history_key(name), None)
        if entry is None:
            continue
        try:
            hist = parse_chart(entry[0], name)
        except DataError:
            continue
        hist.source.status = STALE
        hist.source.retrieved_at = datetime.fromtimestamp(entry[1])
        return hist
    return None


def quote(symbol: str) -> tuple[float, float | None]:
    """(price, day change) from a five-day chart: a small payload for the watchlist."""
    symbol = validation.ticker(symbol)
    name, fetched = _chart(symbol, "range=5d&interval=1d", 120)
    h = parse_chart(fetched.value, name)
    return h.price, h.day_change


def search(query: str, limit: int = 8) -> list[dict]:
    q = (query or "").strip()
    if not q:
        return []
    fetched = _get(f"/v1/finance/search?q={urlquote(q)}&quotesCount={limit}&newsCount=0&enableFuzzyQuery=false", ttl_s=86400)
    out = []
    for item in fetched.value.get("quotes") or []:
        sym = item.get("symbol")
        if sym:
            out.append({"symbol": sym, "name": item.get("longname") or item.get("shortname") or sym, "exchange": item.get("exchDisp") or item.get("exchange") or "", "type": item.get("typeDisp") or item.get("quoteType") or ""})
    return out


def news(symbol: str, limit: int = 10, name: str | None = None) -> list[NewsItem]:
    """Recent headlines. Yahoo's search finds none for symbols with a dash (BRK-B, BF-B), so the company name is tried next."""
    items: list[NewsItem] = []
    for query in dict.fromkeys(q for q in (symbol, name) if q):
        fetched = _get(f"/v1/finance/search?q={urlquote(query)}&quotesCount=0&newsCount={limit}", ttl_s=900)
        for raw in fetched.value.get("news") or []:
            ts = raw.get("providerPublishTime")
            if raw.get("title"):
                items.append(NewsItem(raw["title"], raw.get("publisher") or "", datetime.fromtimestamp(ts) if isinstance(ts, (int, float)) else None, raw.get("link") or ""))
        if items:
            break
    return items


def risk_free_rate() -> tuple[float, Source] | None:
    """13-week T-bill yield (^IRX) as a decimal, with its source, or None."""
    try:
        fetched = _get("/v8/finance/chart/%5EIRX?range=5d&interval=1d", ttl_s=6 * 3600)
        meta = fetched.value["chart"]["result"][0]["meta"]
        value = float(meta["regularMarketPrice"])
    except (DataError, KeyError, IndexError, TypeError, ValueError):
        return None
    if not 0 <= value <= 20:  # quoted in percent; anything else is a bad print
        return None
    return value / 100, Source("Yahoo Finance ^IRX (13-week T-bill)", QUOTE_PAGE.format(symbol="%5EIRX"), datetime.fromtimestamp(fetched.saved_at), status=fetched.status)
