"""Price history through a chain of providers, never assuming any one is up.

Order:
  1. Yahoo chart API, live or fresh cache          (data/yahoo.py)
  2. Yahoo through yfinance                        (data/yf_provider.py)
  3. The last cached copy from route 1, however old ("Offline copy"), read
     from disk without going online
  4. A CSV file the user imported                  (File > Import prices)

Every failed attempt is recorded on the result, so the UI can say which
provider answered and why the others did not. A symbol Yahoo says does not
exist stops the chain at once: no other provider will know it either.
"""

from __future__ import annotations

import io
import re
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

from finlit_pro import validation
from finlit_pro.config import app_dir
from finlit_pro.data import demo, yahoo, yf_provider
from finlit_pro.data.models import IMPORT, DataError, NotFoundError, PriceHistory, Source


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
    except NotFoundError:
        # First Version: matched "does not recognise" in the message, which broke as
        # soon as the wording changed. Current Version: the exception type decides.
        raise
    except DataError as exc:
        attempts.append(f"Yahoo chart API: {exc}")
    try:
        hist = yf_provider.history(symbol)
        hist.attempts = attempts
        return hist
    except DataError as exc:
        attempts.append(f"yfinance: {exc}")
    # First Version: step 3 called yahoo.history(allow_stale=True), which went online
    # again (both hosts, full timeouts) before it looked at the disk. Current Version:
    # the saved copy is read straight from the cache, with no network call.
    hist = yahoo.cached_history(symbol)
    if hist is not None:
        hist.attempts = attempts
        return hist
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


ZIP_MAGIC = b"PK\x03\x04"  # .xlsx workbooks are zip archives
NUMERIC = ("open", "high", "low", "close", "adjclose", "volume")
HOW_TO_FIX = "Save it as a CSV with a Date column (like 2024-01-31) and a Close column, one row per trading day, then import it again."


def decode_csv(data: bytes) -> str:
    """The text of a CSV file: UTF-8 (with or without a BOM), else Windows-1252 as Excel writes it.

    First Version: the file was read as UTF-8 only. An Excel export with a pound
    sign, or an .xlsx renamed to .csv, raised UnicodeDecodeError, which the import
    dialog did not catch, so nothing happened. Current Version: a workbook or zip is
    refused with a clear message, UTF-8 and then Windows-1252 are tried, and anything
    else is refused as not being a text CSV.
    """
    if data.startswith(ZIP_MAGIC):
        raise DataError("That file is an Excel workbook or a zip archive, not a CSV. Open it in Excel, choose File > Save As > CSV UTF-8, then import the .csv file.")
    encodings = ("utf-16",) if data.startswith((b"\xff\xfe", b"\xfe\xff")) else ("utf-8-sig", "cp1252")
    for encoding in encodings:
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        if "\x00" not in text:
            return text
        break
    raise DataError("That file is not a text CSV. Save it as CSV (UTF-8) and import it again.")


def _layout(text: str) -> tuple[str, str]:
    """(text, delimiter): drops an Excel "sep=" line and yfinance's extra header rows, then sniffs ',' or ';'."""
    lines = text.lstrip("\ufeff").splitlines()
    sep = None
    if lines and re.fullmatch(r"sep=.", lines[0].strip(), re.IGNORECASE):
        sep, lines = lines[0].strip()[4], lines[1:]
    # yf.download(...).to_csv() writes "Price,Close,...", "Ticker,AAPL,...", "Date,,,..." before the rows.
    if len(lines) > 2 and lines[0].startswith("Price") and lines[1].startswith("Ticker") and lines[2].startswith("Date"):
        lines = ["Date" + lines[0][len("Price"):]] + lines[3:]
    if sep is None:
        header = next((line for line in lines if line.strip()), "")
        counts = {c: header.count(c) for c in (",", ";", "\t")}
        sep = max(counts, key=lambda c: counts[c]) if any(counts.values()) else ","
    return "\n".join(lines), sep


def _dates(values: pd.Series) -> pd.Series:
    """Naive daily dates. A timestamp carrying a UTC offset keeps its own calendar date.

    First Version: pd.to_datetime on yfinance's own export ("2026-04-21 00:00:00-04:00")
    raised "Mixed timezones detected" for any file spanning a daylight-saving change,
    which the import dialog did not catch; a file with one offset imported with a
    timezone-aware index that later broke the Returns view.
    Current Version: ISO dates are read from their first ten characters (the date on
    the exchange), other layouts are parsed and stripped of any timezone, and the
    result is always naive and at midnight.
    """
    text = values.astype(str).str.strip()
    present = text[(text != "") & (text.str.lower() != "nan")]
    if len(present) and present.str.match(r"^\d{4}-\d{2}-\d{2}").all():
        return pd.to_datetime(text.str[:10], format="%Y-%m-%d", errors="coerce")
    # 31.01.2024 or 31/01/2024: day first when the first field passes 12 and the second never does.
    parts = present.str.extract(r"^(\d{1,2})[./-](\d{1,2})[./-]\d{2,4}").dropna().astype(int)
    dayfirst = bool(len(parts) and parts[0].max() > 12 and parts[1].max() <= 12)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # "could not infer format": each value is then parsed alone
        try:
            parsed = pd.to_datetime(text, errors="coerce", dayfirst=dayfirst)
        except (ValueError, TypeError):  # mixed UTC offsets in a non-ISO layout: one value at a time
            parsed = pd.to_datetime(text.map(lambda v: _one_date(v, dayfirst)), errors="coerce")
    if isinstance(parsed.dtype, pd.DatetimeTZDtype):
        parsed = parsed.dt.tz_localize(None)
    return parsed.dt.normalize()


def _one_date(value: str, dayfirst: bool) -> pd.Timestamp:
    stamp = pd.to_datetime(value, errors="coerce", dayfirst=dayfirst)
    return stamp.tz_localize(None) if isinstance(stamp, pd.Timestamp) and stamp.tz is not None else stamp


def _numbers(values: pd.Series, decimal_comma: bool) -> pd.Series:
    """Numbers as broker exports write them: currency signs, thousands separators, or decimal commas."""
    text = values.astype(str).str.replace(r"[\s$\u00a3\u20ac\u00a0]", "", regex=True)
    if decimal_comma:
        text = text.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    else:
        text = text.str.replace(",", "", regex=False)
    return pd.to_numeric(text, errors="coerce")


def parse_csv(text: str | bytes, symbol: str) -> PriceHistory:
    """Daily OHLCV from a CSV in Yahoo's download layout or any similar one.

    Needs a Date and a Close column; the rest are optional. Dollar signs and
    thousands separators are stripped, as broker exports often include them.
    Semicolon files (European Excel) may use decimal commas. Any parsing problem
    becomes a DataError that says how to fix the file.
    """
    if isinstance(text, bytes):
        text = decode_csv(text)
    try:
        return _parse_csv(text, symbol)
    except DataError:
        raise
    except (ValueError, TypeError, OverflowError) as exc:
        raise DataError(f"Could not read daily prices from that file ({exc.__class__.__name__}). {HOW_TO_FIX}") from None


def _parse_csv(text: str, symbol: str) -> PriceHistory:
    body, sep = _layout(text)
    try:
        frame = pd.read_csv(io.StringIO(body), sep=sep, dtype=str, skipinitialspace=True)
    except (ValueError, pd.errors.ParserError) as exc:
        raise DataError(f"That file is not a readable CSV ({exc.__class__.__name__}). {HOW_TO_FIX}") from None
    cols = {c: ALIASES.get(str(c).strip().lower()) for c in frame.columns}
    frame = frame.rename(columns={k: v for k, v in cols.items() if v})
    if "date" not in frame or "close" not in frame:
        raise DataError("The CSV needs at least a Date column and a Close column.")
    frame = frame.loc[:, ~frame.columns.duplicated()]
    frame["date"] = _dates(frame["date"])
    frame = frame.dropna(subset=["date"])
    if frame.empty:
        raise DataError(f"None of the dates in that CSV could be read. Use dates like 2024-01-31 or 01/31/2024. {HOW_TO_FIX}")
    for c in NUMERIC:
        if c in frame:
            decimal_comma = sep == ";" and bool(frame[c].astype(str).str.contains(r"\d,\d", regex=True).any())
            frame[c] = _numbers(frame[c], decimal_comma)
    frame = frame[frame["close"] > 0]
    frame = frame.drop_duplicates().set_index("date").sort_index()
    if frame.index.has_duplicates:
        day = frame.index[frame.index.duplicated()][0].date()
        raise DataError(f"The CSV has more than one row for some days (for example {day}). Import daily prices, one row per trading day.")
    if len(frame) < 30:
        raise DataError(f"The CSV has {len(frame)} usable rows; at least 30 daily rows are needed.")
    bars = pd.DataFrame(index=frame.index)
    bars["close"] = frame["close"]
    for c in ("open", "high", "low"):
        bars[c] = frame[c].fillna(frame["close"]) if c in frame else frame["close"]
    bars["adjclose"] = frame["adjclose"].fillna(frame["close"]) if "adjclose" in frame else frame["close"]
    bars["volume"] = frame["volume"].fillna(0) if "volume" in frame else 0.0
    bars = bars[["open", "high", "low", "close", "adjclose", "volume"]].astype("float64")
    bars.index = pd.DatetimeIndex(bars.index).normalize()
    bars.index.name = "date"
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
    name = Path(path).name
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise DataError(f"Could not open {name} ({exc.strerror or exc.__class__.__name__}). Check that the file exists and is not open in another program, then try again.") from None
    text = decode_csv(data)
    hist = parse_csv(text, symbol)
    try:
        target = imports_dir() / f"{symbol}.csv"
        target.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise DataError(f"The prices were read, but a copy could not be saved for later ({exc.strerror or exc.__class__.__name__}). Free some disk space, then import again.") from None
    hist.source.url = target.as_uri()
    hist.source.detail = f"Imported from {name}"
    return hist


def load_imported(symbol: str) -> PriceHistory | None:
    target = imports_dir() / f"{symbol}.csv"
    if not target.exists():
        return None
    try:
        hist = parse_csv(target.read_bytes(), symbol)
    except (DataError, OSError):
        return None
    hist.source.url = target.as_uri()
    hist.source.retrieved_at = datetime.fromtimestamp(target.stat().st_mtime)
    return hist
