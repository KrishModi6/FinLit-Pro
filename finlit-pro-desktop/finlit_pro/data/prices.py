"""Price history through a chain of providers, never assuming any one is up.

Order:
  1. Yahoo chart API, live or fresh cache          (data/yahoo.py)
  2. Yahoo through yfinance                        (data/yf_provider.py)
  3. The last cached copy from route 1, however old ("Offline copy")
  4. A CSV file the user imported                  (File > Import prices)

Every failed attempt is recorded on the result, so the UI can say which
provider answered and why the others did not.
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import pandas as pd

from finlit_pro import validation
from finlit_pro.config import app_dir
from finlit_pro.data import demo, yahoo, yf_provider
from finlit_pro.data.models import IMPORT, DataError, PriceHistory, Source


def imports_dir() -> Path:
    path = app_dir("data") / "imports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_history(symbol: str, force: bool = False) -> PriceHistory:
    symbol = validation.ticker(symbol)
    if demo.is_demo(symbol):
        return demo.history(symbol)
    attempts: list[str] = []
    try:
        return yahoo.history(symbol, force=force, allow_stale=False)
    except DataError as exc:
        if "does not recognise" in str(exc):
            raise
        attempts.append(f"Yahoo chart API: {exc}")
    try:
        hist = yf_provider.history(symbol)
        hist.attempts = attempts
        return hist
    except DataError as exc:
        attempts.append(f"yfinance: {exc}")
    try:
        hist = yahoo.history(symbol, allow_stale=True)
        hist.attempts = attempts
        return hist
    except DataError:
        pass
    imported = load_imported(symbol)
    if imported is not None:
        imported.attempts = attempts
        return imported
    raise DataError(
        f"No price data for {symbol}. " + " ".join(attempts) + " Try again later, or import a CSV with File > Import prices."
    )


# ----------------------------------------------------------------- CSV import

ALIASES = {
    "date": "date", "timestamp": "date",
    "open": "open", "high": "high", "low": "low", "close": "close", "close/last": "close",
    "adj close": "adjclose", "adj_close": "adjclose", "adjclose": "adjclose", "adjusted close": "adjclose",
    "volume": "volume",
}


def parse_csv(text: str, symbol: str) -> PriceHistory:
    """Daily OHLCV from a CSV in Yahoo's download layout or any similar one.

    Needs a Date and a Close column; the rest are optional. Dollar signs and
    thousands separators are stripped, as broker exports often include them.
    """
    try:
        frame = pd.read_csv(io.StringIO(text))
    except (ValueError, pd.errors.ParserError) as exc:
        raise DataError(f"That file is not a readable CSV ({exc.__class__.__name__}).") from None
    cols = {c: ALIASES.get(str(c).strip().lower()) for c in frame.columns}
    frame = frame.rename(columns={k: v for k, v in cols.items() if v})
    if "date" not in frame or "close" not in frame:
        raise DataError("The CSV needs at least a Date column and a Close column.")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"]).set_index("date").sort_index()
    for c in ("open", "high", "low", "close", "adjclose", "volume"):
        if c in frame:
            frame[c] = pd.to_numeric(frame[c].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")
    frame = frame[frame["close"] > 0]
    if len(frame) < 30:
        raise DataError(f"The CSV has {len(frame)} usable rows; at least 30 daily rows are needed.")
    bars = pd.DataFrame(index=frame.index)
    bars["close"] = frame["close"]
    for c in ("open", "high", "low"):
        bars[c] = frame[c] if c in frame else frame["close"]
    bars["adjclose"] = frame["adjclose"] if "adjclose" in frame else frame["close"]
    bars["volume"] = frame["volume"].fillna(0) if "volume" in frame else 0.0
    bars = bars[["open", "high", "low", "close", "adjclose", "volume"]]
    bars.index = bars.index.normalize()
    return PriceHistory(
        symbol=symbol,
        name=symbol,
        currency="USD",
        exchange=None,
        instrument_type=None,
        price=float(bars["close"].iloc[-1]),
        previous_close=float(bars["close"].iloc[-2]),
        bars=bars,
        source=Source(f"Imported CSV ({symbol})", "", datetime.now(), str(bars.index[-1].date()), status=IMPORT),
    )


def import_csv(path: str, symbol: str) -> PriceHistory:
    symbol = validation.ticker(symbol)
    text = Path(path).read_text(encoding="utf-8-sig")
    hist = parse_csv(text, symbol)
    target = imports_dir() / f"{symbol}.csv"
    target.write_text(text, encoding="utf-8")
    hist.source.url = target.as_uri()
    hist.source.detail = f"Imported from {Path(path).name}"
    return hist


def load_imported(symbol: str) -> PriceHistory | None:
    target = imports_dir() / f"{symbol}.csv"
    if not target.exists():
        return None
    try:
        hist = parse_csv(target.read_text(encoding="utf-8"), symbol)
    except DataError:
        return None
    hist.source.url = target.as_uri()
    hist.source.retrieved_at = datetime.fromtimestamp(target.stat().st_mtime)
    return hist
