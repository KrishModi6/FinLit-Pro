"""Yahoo Finance: daily history, quotes, ticker search, headlines, T-bill yield.

These are Yahoo's public but undocumented endpoints. They need no key, are
not covered by any service agreement, and can change or rate limit without
notice; Yahoo's terms allow personal, non-commercial use. The app treats
them accordingly: everything is cached, requests are throttled, and
`prices.py` falls back to other routes when this one fails.
"""

from __future__ import annotations

import time
from datetime import datetime
from urllib.parse import quote as urlquote

import numpy as np
import pandas as pd

from finlit_pro import validation
from finlit_pro.data.http import BROWSER_UA, get_json
from finlit_pro.data.models import DataError, NewsItem, PriceHistory, Source

HOSTS = ("https://query1.finance.yahoo.com", "https://query2.finance.yahoo.com")
HEADERS = {"User-Agent": BROWSER_UA, "Accept": "application/json"}
SERVICE = "Yahoo Finance"
QUOTE_PAGE = "https://finance.yahoo.com/quote/{symbol}"


def _get(path: str, ttl_s: float, not_found: str | None = None, allow_stale: bool = True):
    last_error: DataError | None = None
    for host in HOSTS:
        try:
            return get_json(host + path, headers=HEADERS, ttl_s=ttl_s, not_found_message=not_found, service=SERVICE, allow_stale=allow_stale)
        except DataError as exc:
            if not_found and str(exc) == not_found:
                raise
            last_error = exc
    assert last_error is not None
    raise last_error


def parse_chart(payload: dict, symbol: str) -> PriceHistory:
    """Turn a v8 chart response into a PriceHistory. Raises DataError."""
    chart = (payload or {}).get("chart") or {}
    if chart.get("error"):
        desc = (chart["error"] or {}).get("description") or "unknown error"
        raise DataError(f'Yahoo Finance has no data for "{symbol}" ({desc}). Check the ticker.')
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

    price = meta.get("regularMarketPrice")
    price = float(price) if isinstance(price, (int, float)) and price > 0 else float(bars["close"].iloc[-1])
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
    """Full daily history since listing (period1=0), with dividends and splits."""
    symbol = validation.ticker(symbol)
    path = (
        f"/v8/finance/chart/{urlquote(symbol, safe='^=')}"
        f"?period1=0&period2={int(time.time()) // 3600 * 3600}&interval=1d&events=div%2Csplit&includeAdjustedClose=true"
    )
    # period2 is rounded to the hour so the cache key is stable within an hour.
    fetched = _get(path, ttl_s=0 if force else 900, not_found=f'Yahoo Finance does not recognise "{symbol}". Check the spelling or search by name.', allow_stale=allow_stale)
    hist = parse_chart(fetched.value, symbol)
    hist.source.status = fetched.status
    hist.source.retrieved_at = datetime.fromtimestamp(fetched.saved_at)
    return hist


def quote(symbol: str) -> tuple[float, float | None]:
    """(price, day change) from a five-day chart: a small payload for the watchlist."""
    symbol = validation.ticker(symbol)
    fetched = _get(f"/v8/finance/chart/{urlquote(symbol, safe='^=')}?range=5d&interval=1d", ttl_s=120)
    h = parse_chart(fetched.value, symbol)
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


def news(symbol: str, limit: int = 10) -> list[NewsItem]:
    fetched = _get(f"/v1/finance/search?q={urlquote(symbol)}&quotesCount=0&newsCount={limit}", ttl_s=900)
    items = []
    for raw in fetched.value.get("news") or []:
        ts = raw.get("providerPublishTime")
        if raw.get("title"):
            items.append(NewsItem(raw["title"], raw.get("publisher") or "", datetime.fromtimestamp(ts) if isinstance(ts, (int, float)) else None, raw.get("link") or ""))
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
