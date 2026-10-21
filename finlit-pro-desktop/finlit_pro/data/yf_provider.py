"""Yahoo Finance through the `yfinance` library.

A second route to the same data. yfinance manages Yahoo's session cookie
and crumb and imitates a browser's TLS handshake, which Yahoo now requires
for its options endpoint; the plain chart API used by `yahoo.py` does not
need it. Both routes are unofficial and carry the same caveats.
"""

from __future__ import annotations

import threading
import time
from datetime import date, datetime

import numpy as np
import pandas as pd

from finlit_pro.data.models import DataError, OptionChain, OptionQuote, PriceHistory, Source
from finlit_pro.data.yahoo import spellings

_lock = threading.Lock()
_chains: dict[tuple[str, str], tuple[float, OptionChain]] = {}
CHAIN_TTL_S = 120
OPTIONS_PAGE = "https://finance.yahoo.com/quote/{symbol}/options"


def _yf():
    try:
        import yfinance
    except ImportError:
        raise DataError("The yfinance package is not installed, so this route to Yahoo data is unavailable.") from None
    return yfinance


def _meta_text(meta, key: str) -> str | None:
    """One field of Ticker.history_metadata, or None. Reads only that key: the
    mapping fetches more data from Yahoo when some other keys are touched."""
    try:
        value = meta.get(key) if meta is not None else None
    except Exception:  # a lazy mapping that fails to load is just missing data
        return None
    return value.strip() if isinstance(value, str) and value.strip() else None


def history(symbol: str) -> PriceHistory:
    """Full daily history through yfinance, labelled from the listing's own metadata.

    First Version: every listing was labelled USD, with the symbol as its name and
    no exchange, so 7203.T (JPY), SHOP.TO (CAD) and SAP.DE (EUR) prices were shown
    and used as dollars whenever this fallback answered. Current Version: currency,
    name, exchange and instrument type come from Ticker.history_metadata, which
    yfinance fills from the same chart response; an unknown currency is left None,
    never assumed to be USD. A class share written with a dot (BRK.B) is retried
    with Yahoo's dash spelling (BRK-B), as the chart API route does.
    """
    yf = _yf()
    raw, ticker, name = None, None, symbol.upper()
    for name in spellings(symbol.upper()):
        try:
            ticker = yf.Ticker(name)
            raw = ticker.history(period="max", interval="1d", auto_adjust=False, actions=True)
        except Exception as exc:  # yfinance raises many types; treat any as provider failure
            raise DataError(f"yfinance could not load {symbol} ({exc.__class__.__name__}).") from None
        if raw is not None and not raw.empty and "Close" in raw:
            break
    if raw is None or raw.empty or "Close" not in raw:
        raise DataError(f"yfinance returned no history for {symbol}.")
    try:
        meta = ticker.history_metadata
    except Exception:
        meta = None
    sym = (_meta_text(meta, "symbol") or name).upper()
    raw.index = pd.to_datetime(raw.index).tz_localize(None).normalize()
    bars = pd.DataFrame(
        {
            "open": raw["Open"],
            "high": raw["High"],
            "low": raw["Low"],
            "close": raw["Close"],
            "adjclose": raw.get("Adj Close", raw["Close"]),
            "volume": raw["Volume"].fillna(0),
        }
    ).dropna(subset=["close"])
    bars = bars[bars["close"] > 0]
    if len(bars) < 2:
        raise DataError(f"yfinance returned too little history for {symbol}.")
    dividends = raw["Dividends"][raw["Dividends"] > 0] if "Dividends" in raw else pd.Series(dtype=float)
    splits = raw["Stock Splits"][raw["Stock Splits"] > 0] if "Stock Splits" in raw else pd.Series(dtype=float)
    return PriceHistory(
        symbol=sym,
        name=_meta_text(meta, "longName") or _meta_text(meta, "shortName") or sym,
        currency=_meta_text(meta, "currency"),  # type: ignore[arg-type]  # None when unknown, never a guess
        exchange=_meta_text(meta, "fullExchangeName") or _meta_text(meta, "exchangeName"),
        instrument_type=_meta_text(meta, "instrumentType"),
        price=float(bars["close"].iloc[-1]),
        previous_close=float(bars["close"].iloc[-2]),
        bars=bars,
        source=Source(f"Yahoo Finance via yfinance ({sym})", f"https://finance.yahoo.com/quote/{sym}", datetime.now(), str(bars.index[-1].date())),
        dividends=dividends.astype(float),
        splits=splits.astype(float),
    )


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if np.isfinite(f) else None


def default_expiry(expiries: list[str], today: date | None = None, target_days: int = 30) -> str:
    """The listed expiry closest to about a month out.

    First Version: the nearest expiry, often tomorrow's weekly, where every
    probability collapses to a coin toss around the strike. Current Version:
    the one closest to 30 calendar days, a more typical holding period.
    """
    today = today or date.today()

    def gap(text: str) -> int:
        try:
            return abs((date.fromisoformat(text) - today).days - target_days)
        except ValueError:
            return 10**6

    return min(expiries, key=gap)


def option_chain(symbol: str, expiry: str | None = None, underlying: float | None = None) -> OptionChain:
    """Calls and puts for one expiry (about a month out if none is given)."""
    key = (symbol.upper(), expiry or "")
    with _lock:
        hit = _chains.get(key)
        if hit and time.time() - hit[0] < CHAIN_TTL_S:
            return hit[1]
    yf = _yf()
    try:
        ticker = yf.Ticker(symbol)
        expiries = list(ticker.options or [])
    except Exception as exc:
        raise DataError(f"Yahoo did not return option expiries for {symbol} ({exc.__class__.__name__}). Enter the contract manually.") from None
    if not expiries:
        raise DataError(f"No listed options found for {symbol}. Enter the contract manually.")
    chosen = expiry if expiry in expiries else default_expiry(expiries)
    try:
        chain = ticker.option_chain(chosen)
    except Exception as exc:
        raise DataError(f"Yahoo did not return the {chosen} option chain ({exc.__class__.__name__}). Enter the contract manually.") from None

    def rows(frame, kind):
        out = []
        for r in frame.to_dict("records"):
            out.append(
                OptionQuote(
                    contract=str(r.get("contractSymbol", "")),
                    kind=kind,
                    strike=float(r["strike"]),
                    expiry=chosen,
                    bid=_num(r.get("bid")),
                    ask=_num(r.get("ask")),
                    last=_num(r.get("lastPrice")),
                    implied_vol=_num(r.get("impliedVolatility")),
                    volume=int(r["volume"]) if _num(r.get("volume")) is not None else None,
                    open_interest=int(r["openInterest"]) if _num(r.get("openInterest")) is not None else None,
                )
            )
        return out

    result = OptionChain(
        symbol=symbol.upper(),
        expiries=expiries,
        expiry=chosen,
        calls=rows(chain.calls, "call"),
        puts=rows(chain.puts, "put"),
        underlying_price=underlying,
        # First Version: as_of was the expiry, so the label read "as of 2026-11-20" for
        # quotes fetched on 2026-10-21. Current Version: as_of is the day the quotes
        # describe (today); the expiry is named in the detail.
        source=Source(
            "Yahoo Finance options via yfinance",
            OPTIONS_PAGE.format(symbol=symbol.upper()),
            datetime.now(),
            date.today().isoformat(),
            detail=f"Expiry {chosen}; quotes may be delayed 15 minutes or more",
        ),
    )
    with _lock:
        _chains[key] = (time.time(), result)
    return result
