"""Yahoo Finance: daily price history, ticker search, headlines, T-bill yield.

Uses the same public v8 chart endpoint the FinLit Pro website proxies, called
directly: a desktop app has no CORS problem, so it needs no proxy. No key, no
crumb. The response is normalised into a PriceHistory so nothing downstream
ever sees Yahoo's envelope.
"""

from __future__ import annotations

from datetime import datetime
from urllib.parse import quote as urlquote

import numpy as np
import pandas as pd

from finlit_quant import validation
from finlit_quant.data import demo
from finlit_quant.data.http import BROWSER_UA, get_json
from finlit_quant.data.models import DataError, NewsItem, PriceHistory

HOSTS = ("https://query1.finance.yahoo.com", "https://query2.finance.yahoo.com")
HEADERS = {"User-Agent": BROWSER_UA, "Accept": "application/json"}
SERVICE = "Yahoo Finance"


def _get(path: str, ttl_s: float, not_found: str | None = None):
    last_error: DataError | None = None
    for host in HOSTS:
        try:
            return get_json(host + path, headers=HEADERS, ttl_s=ttl_s, not_found_message=not_found, service=SERVICE)
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
        raise DataError(f'Yahoo Finance has no data for "{symbol}" ({desc}). Check the ticker and try again.')
    result = (chart.get("result") or [None])[0]
    if not result or not result.get("timestamp"):
        raise DataError(f'No price history came back for "{symbol}". Check the ticker and try again.')

    meta = result.get("meta") or {}
    quote_ = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    adj = (((result.get("indicators") or {}).get("adjclose") or [{}])[0]).get("adjclose")

    # Shift timestamps by the exchange's UTC offset before taking the date, or
    # a US close at 16:00 New York becomes the next day in UTC for late bars.
    offset = int(meta.get("gmtoffset") or 0)
    index = pd.to_datetime(np.asarray(result["timestamp"], dtype="int64") + offset, unit="s").normalize()

    def col(name: str, values) -> pd.Series:
        return pd.Series(values if values is not None else [np.nan] * len(index), index=index, name=name, dtype="float64")

    bars = pd.concat(
        [
            col("open", quote_.get("open")),
            col("high", quote_.get("high")),
            col("low", quote_.get("low")),
            col("close", quote_.get("close")),
            col("adjclose", adj if adj is not None else quote_.get("close")),
            col("volume", quote_.get("volume")),
        ],
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
        raise DataError(f'Not enough price history for "{symbol}" to analyse. It may be newly listed.')

    divs = ((result.get("events") or {}).get("dividends") or {}).values()
    dividends = pd.Series(
        {pd.to_datetime(int(d["date"]) + offset, unit="s").normalize(): float(d["amount"]) for d in divs if "amount" in d},
        dtype="float64",
    ).sort_index()

    raw_splits = ((result.get("events") or {}).get("splits") or {}).values()
    splits = pd.Series(
        {
            pd.to_datetime(int(s["date"]) + offset, unit="s").normalize(): float(s["numerator"]) / float(s["denominator"])
            for s in raw_splits
            if s.get("numerator") and s.get("denominator")
        },
        dtype="float64",
    ).sort_index()

    price = meta.get("regularMarketPrice")
    price = float(price) if isinstance(price, (int, float)) and price > 0 else float(bars["close"].iloc[-1])

    return PriceHistory(
        symbol=str(meta.get("symbol") or symbol).upper(),
        name=meta.get("longName") or meta.get("shortName") or symbol,
        currency=meta.get("currency") or "USD",
        exchange=meta.get("fullExchangeName") or meta.get("exchangeName"),
        instrument_type=meta.get("instrumentType"),
        price=price,
        # On daily bars the previous bar is the previous session. Yahoo's
        # chartPreviousClose is the close before the whole range instead,
        # which makes a 10-year chart report a 10-year move as the day's.
        previous_close=float(bars["close"].iloc[-2]),
        bars=bars,
        dividends=dividends,
        splits=splits,
    )


def history(symbol: str, years: int = 10, force: bool = False) -> PriceHistory:
    """Daily bars for up to `years` years. DEMO tickers never touch the network."""
    symbol = validation.ticker(symbol)
    if demo.is_demo(symbol):
        return demo.history(symbol)

    rng = "10y" if years >= 10 else ("5y" if years >= 5 else "2y")
    path = (
        f"/v8/finance/chart/{urlquote(symbol, safe='^=')}"
        f"?range={rng}&interval=1d&events=div%2Csplit&includeAdjustedClose=true"
    )
    fetched = _get(path, ttl_s=0 if force else 300, not_found=f'Yahoo Finance does not recognise "{symbol}". Check the spelling, or search by company name.')
    hist = parse_chart(fetched.value, symbol)
    hist.source = fetched.source
    hist.fetched_at = datetime.fromtimestamp(fetched.saved_at)
    return hist


def quote(symbol: str) -> tuple[float, float | None]:
    """(price, day change) from a five-day chart: a small payload for the watchlist."""
    symbol = validation.ticker(symbol)
    if demo.is_demo(symbol):
        h = demo.history(symbol)
        return h.price, h.day_change
    fetched = _get(f"/v8/finance/chart/{urlquote(symbol, safe='^=')}?range=5d&interval=1d", ttl_s=120)
    h = parse_chart(fetched.value, symbol)
    return h.price, h.day_change


def search(query: str, limit: int = 8) -> list[dict]:
    """Ticker lookup by company name or partial symbol."""
    q = (query or "").strip()
    if len(q) < 1:
        return []
    fetched = _get(f"/v1/finance/search?q={urlquote(q)}&quotesCount={limit}&newsCount=0&enableFuzzyQuery=false", ttl_s=86400)
    out = []
    for item in fetched.value.get("quotes") or []:
        sym = item.get("symbol")
        if not sym:
            continue
        out.append(
            {
                "symbol": sym,
                "name": item.get("longname") or item.get("shortname") or sym,
                "exchange": item.get("exchDisp") or item.get("exchange") or "",
                "type": item.get("typeDisp") or item.get("quoteType") or "",
            }
        )
    return out


def news(symbol: str, limit: int = 10) -> list[NewsItem]:
    if demo.is_demo(symbol):
        return []
    fetched = _get(f"/v1/finance/search?q={urlquote(symbol)}&quotesCount=0&newsCount={limit}", ttl_s=900)
    items = []
    for raw in fetched.value.get("news") or []:
        ts = raw.get("providerPublishTime")
        items.append(
            NewsItem(
                title=raw.get("title") or "",
                publisher=raw.get("publisher") or "",
                published=datetime.fromtimestamp(ts) if isinstance(ts, (int, float)) else None,
                url=raw.get("link") or "",
            )
        )
    return [i for i in items if i.title]


def risk_free_rate() -> float | None:
    """The 13-week T-bill yield (^IRX) as a decimal, or None if unavailable."""
    try:
        fetched = _get("/v8/finance/chart/%5EIRX?range=5d&interval=1d", ttl_s=6 * 3600)
        meta = fetched.value["chart"]["result"][0]["meta"]
        value = float(meta["regularMarketPrice"])
    except (DataError, KeyError, IndexError, TypeError, ValueError):
        return None
    # ^IRX is quoted in percent. Anything outside 0..20% is a bad print.
    return value / 100 if 0 <= value <= 20 else None
