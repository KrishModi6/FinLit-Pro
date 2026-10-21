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
from finlit_pro.data.models import CACHE, STALE, DataError, NetworkError, NewsItem, NotFoundError, PriceHistory, Source

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


def spelling_key(symbol: str) -> str:
    """The cache key under which the spelling Yahoo answered to (BRK.B -> BRK-B) is remembered."""
    return f"yahoo:spelling:{symbol}"


def _get(path: str, ttl_s: float, not_found: str | None = None, allow_stale: bool = True, cache_key: str | None = None, check: Callable[[object], object] | None = None) -> Fetched:
    """The first Yahoo host that answers.

    First Version: any failure, including a timeout or a refused connection, moved
    on to the second host, so a network that was down or hanging cost two full
    timeouts. Current Version: a not-found answer or a network failure stops here
    (both hosts sit behind the same network); other errors (HTTP 5xx, unreadable
    data) still try the second host.

    First Version: each host was asked with allow_stale, so when query1 answered
    HTTP 5xx, http.get_json returned query1's old copy (three days old in the
    audit, labelled Offline copy) and query2, which was up, was never asked. This
    hit the risk-free rate, watchlist quotes, search and headlines. Current
    Version: a fresh copy saved from either host is used first; otherwise every
    host is asked for a live answer, and only when all of them fail (or the
    network is down) is the newest old copy returned, labelled Offline copy.
    """
    urls = [host + path for host in HOSTS]
    keys = dict.fromkeys(cache_key or url for url in urls)  # one shared key when cache_key is given
    store = cache()
    if ttl_s > 0:
        for key, url in zip(keys, urls):
            fresh = store.get(key, ttl_s)
            if fresh is not None:
                return Fetched(fresh[0], CACHE, fresh[1], url)
    last_error: DataError | None = None
    for url in urls:
        try:
            return get_json(url, headers=HEADERS, ttl_s=0, not_found_message=not_found, service=SERVICE, allow_stale=False, cache_key=cache_key, check=check)
        except NotFoundError:
            raise
        except NetworkError as exc:
            last_error = exc
            break
        except DataError as exc:
            last_error = exc
    if allow_stale:
        copies = [(entry, url) for key, url in zip(keys, urls) if (entry := store.get(key, None)) is not None]
        if copies:
            (value, saved_at), url = max(copies, key=lambda c: c[0][1])
            return Fetched(value, STALE, saved_at, url)
    assert last_error is not None
    raise last_error


def _chart(symbol: str, query: str, ttl_s: float, allow_stale: bool = True, key: Callable[[str], str] | None = None) -> tuple[str, Fetched]:
    """A v8 chart response and the spelling Yahoo answered to.

    First Version: BRK.B, the usual way to write Berkshire's class B shares, failed
    with "does not recognise" (and HTTP 404 in the watchlist), because Yahoo spells it
    BRK-B; searching "BRK.B" as advised found an unrelated ETF. Current Version: when
    Yahoo does not know a class-share spelling, the dash spelling is tried once.

    First Version: BRK.B was asked for first on every load and every watchlist
    refresh, so each one sent Yahoo a 404 before BRK-B, even while the BRK-B copy
    was fresh, and offline inside the 15-minute window BRK.B fell through to
    yfinance and the Offline copy while AAPL showed Cached. Current Version: the
    spelling Yahoo answered to is remembered on disk and asked for first, so a
    fresh BRK-B copy is found with no request and a refresh sends one request.

    Every chart payload must parse (parse_chart) before it is saved, so an
    unreadable answer never replaces a good copy.
    """
    names = spellings(symbol)
    message = not_found_message(symbol, names[1:])
    remembered = cache().get(spelling_key(symbol), None) if len(names) > 1 else None
    if remembered and remembered[0] in names:
        names = [remembered[0], *(n for n in names if n != remembered[0])]
    for name in names:
        path = f"/v8/finance/chart/{urlquote(name, safe='^=')}?{query}"
        try:
            fetched = _get(path, ttl_s, not_found=message, allow_stale=allow_stale, cache_key=key(name) if key else None, check=lambda value, name=name: parse_chart(value, name))
        except NotFoundError:
            if name == names[-1]:
                raise
            continue
        if (remembered[0] if remembered else symbol) != name:
            cache().put(spelling_key(symbol), name)
        return name, fetched
    raise AssertionError("unreachable")


def _positive(value) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and np.isfinite(value) and value > 0 else None


def _exchange_tz(meta: dict) -> str | None:
    """The exchange's time zone name from meta (America/New_York), or None when missing or unknown."""
    tz = meta.get("exchangeTimezoneName")
    if not isinstance(tz, str) or not tz.strip():
        return None
    try:
        pd.Timestamp(0, unit="s", tz="UTC").tz_convert(tz)
    except (KeyError, IndexError, TypeError, ValueError):  # an unknown zone name: fall back to gmtoffset
        return None
    return tz


def _days(seconds, tz: str | None, offset: int) -> pd.DatetimeIndex:
    """Exchange-local calendar dates (naive, at midnight) of Unix timestamps.

    First Version: every timestamp was shifted by meta.gmtoffset, the exchange's
    UTC offset today, so once daylight saving changed, bars stamped at local
    midnight on the other side of the change moved to the previous day: with the
    winter offset, two years of GC=F (and CL=F) had 65 bars dated on a weekend and
    70 trading days missing, and EURUSD=X 60 and 61 (London changes on 2026-10-25).
    Current Version: each timestamp is converted with the exchange's time zone
    (meta.exchangeTimezoneName), which applies the offset in force on that day, as
    yfinance does; gmtoffset is used only when meta names no known time zone.
    """
    stamps = pd.to_datetime(np.asarray(seconds, dtype="int64"), unit="s", utc=True)
    local = stamps.tz_convert(tz) if tz else stamps + pd.Timedelta(seconds=offset)
    return pd.DatetimeIndex(local).tz_localize(None).normalize()


def _add_latest_session(bars: pd.DataFrame, dropped: pd.DataFrame, meta: dict, tz: str | None, offset: int, price: float | None) -> pd.DataFrame:
    """Add the session meta reports when Yahoo has not filled in its daily bar yet.

    First Version: after the close Yahoo often sends the day's bar with a null close
    while meta.regularMarketPrice already holds that close. The null bar was dropped,
    so the price came from the new session and the previous close from two sessions
    back (AMZN +5.05% instead of +0.07%; MSFT shown up when it fell), the as-of date
    was a day old, and the model's last price differed from the Monte Carlo's.
    Current Version: when regularMarketTime falls on a later exchange-local date than
    the last bar with a close, a bar for that session is added with close =
    regularMarketPrice. The price, the last bar, the previous close and the as-of
    date then agree.

    First Version: that added bar threw away the open, high, low and volume Yahoo
    had sent with the null close, and took the previous close as its open (and the
    previous close and the price as its high and low when meta had none): ASML.AS
    (open 1452.6, close 1455.4) and AIR.PA were drawn as down days when they were
    up, and VOD.L, which sent 0.0 for all three, got a made-up range. Current
    Version: the session's own open, high, low and volume are kept when they are
    above zero, meta's day high, low and volume fill the gaps, only the close comes
    from regularMarketPrice, and anything still unknown is the close, the same rule
    as every other bar. The high and low always include the open and the close.
    """
    when = meta.get("regularMarketTime")
    if price is None or bars.empty or not isinstance(when, (int, float)) or isinstance(when, bool):
        return bars
    day = _days([when], tz, offset).as_unit(bars.index.unit)
    if day[0] <= bars.index[-1]:
        return bars
    own = dropped[dropped.index == day[0]]
    sent = own.iloc[-1] if len(own) else pd.Series(dtype="float64")
    open_ = _positive(sent.get("open")) or _positive(meta.get("regularMarketOpen")) or price
    high = max(_positive(sent.get("high")) or _positive(meta.get("regularMarketDayHigh")) or price, open_, price)
    low = min(_positive(sent.get("low")) or _positive(meta.get("regularMarketDayLow")) or price, open_, price)
    volume = _positive(sent.get("volume")) or _positive(meta.get("regularMarketVolume")) or 0.0
    row = pd.DataFrame({"open": open_, "high": high, "low": low, "close": price, "adjclose": price, "volume": volume}, index=day, dtype="float64")
    return pd.concat([bars, row])


def parse_chart(payload: dict, symbol: str) -> PriceHistory:
    """Turn a v8 chart response into a PriceHistory. Raises DataError.

    First Version: a payload in an unexpected shape (quote: [None], a close list
    shorter than the timestamps, a null timestamp) raised AttributeError, ValueError
    or TypeError. prices.load_history catches only DataError, so yfinance, the
    offline copy and the imported CSV were never tried and the window showed
    "Unexpected error". Current Version: any such payload is a DataError that says
    so, and the chain moves on; a dividend or split without a date is skipped.
    """
    try:
        return _parse_chart(payload, symbol)
    except DataError:
        raise
    except (AttributeError, KeyError, IndexError, TypeError, ValueError, OverflowError) as exc:
        raise DataError(f'Yahoo Finance sent price data for "{symbol}" that could not be read ({exc.__class__.__name__}). Try again in a few minutes.') from None


def _events(raw: dict, tz: str | None, offset: int, value: Callable[[dict], float | None]) -> pd.Series:
    """Dividends or splits by exchange-local date. Entries without a date or a usable value are skipped."""
    rows = [(e["date"], value(e)) for e in (raw or {}).values() if isinstance(e, dict) and isinstance(e.get("date"), (int, float)) and not isinstance(e.get("date"), bool)]
    rows = [(d, v) for d, v in rows if v is not None and np.isfinite(v)]
    if not rows:
        return pd.Series(dtype="float64")
    series = pd.Series([v for _, v in rows], index=_days([d for d, _ in rows], tz, offset), dtype="float64")
    return series[~series.index.duplicated(keep="last")].sort_index()


def _number(value) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _ratio(split: dict) -> float | None:
    num, den = _number(split.get("numerator")), _number(split.get("denominator"))
    return num / den if num and den else None


def _parse_chart(payload: dict, symbol: str) -> PriceHistory:
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

    # Dates are taken on the exchange's clock (see _days), or late bars land on
    # the next calendar day and midnight bars on the previous one.
    offset = int(meta.get("gmtoffset") or 0)
    tz = _exchange_tz(meta)
    index = _days(result["timestamp"], tz, offset)

    def col(name: str, values) -> pd.Series:
        return pd.Series(values if values is not None else [np.nan] * len(index), index=index, name=name, dtype="float64")

    raw = pd.concat(
        [col("open", q.get("open")), col("high", q.get("high")), col("low", q.get("low")), col("close", q.get("close")),
         col("adjclose", adj if adj is not None else q.get("close")), col("volume", q.get("volume"))],
        axis=1,
    )
    # Yahoo pads gaps with nulls; a bar without a close is not a bar. The latest
    # one may still be the session meta reports (see _add_latest_session).
    has_close = raw["close"].notna() & (raw["close"] > 0)
    bars = raw[has_close]
    bars = bars[~bars.index.duplicated(keep="last")].sort_index()
    for name in ("open", "high", "low"):
        bars[name] = bars[name].fillna(bars["close"])
    bars["adjclose"] = bars["adjclose"].fillna(bars["close"])
    bars["volume"] = bars["volume"].fillna(0)
    price = _positive(meta.get("regularMarketPrice"))
    bars = _add_latest_session(bars, raw[~has_close], meta, tz, offset, price)
    if len(bars) < 2:
        raise DataError(f'Not enough price history for "{symbol}". It may be newly listed.')

    events = result.get("events") or {}
    dividends = _events(events.get("dividends"), tz, offset, lambda d: _number(d.get("amount")))
    splits = _events(events.get("splits"), tz, offset, _ratio)

    price = price or float(bars["close"].iloc[-1])
    sym = str(meta.get("symbol") or symbol).upper()
    return PriceHistory(
        symbol=sym,
        name=meta.get("longName") or meta.get("shortName") or sym,
        # First Version: a payload without a currency was labelled USD. Current
        # Version: an unknown currency is left blank (""), never assumed.
        currency=meta.get("currency") or "",
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
    """(price, day change) from a five-day chart: a small payload for the watchlist.

    First Version: an old copy, however old, was accepted when Yahoo could not be
    reached, and only the price and change were returned, so after three days
    offline the watchlist showed three-day-old prices as current. Current Version:
    only a live answer or a copy under two minutes old is used; otherwise this
    raises DataError and the watchlist row stays blank, as DATA_SOURCES.md says.
    """
    symbol = validation.ticker(symbol)
    name, fetched = _chart(symbol, "range=5d&interval=1d", 120, allow_stale=False)
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
