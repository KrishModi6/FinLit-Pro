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

import csv
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


def _layout(text: str, symbol: str) -> tuple[str, str]:
    """(text, delimiter): drops an Excel "sep=" line, sniffs ',' ';' or tab, and reduces yfinance's three header rows to one."""
    lines = text.lstrip("\ufeff").splitlines()
    sep = None
    if lines and re.fullmatch(r"sep=.", lines[0].strip(), re.IGNORECASE):
        sep, lines = lines[0].strip()[4], lines[1:]
    if sep is None:
        header = next((line for line in lines if line.strip()), "")
        counts = {c: header.count(c) for c in (",", ";", "\t")}
        sep = max(counts, key=lambda c: counts[c]) if any(counts.values()) else ","
    # yf.download(...).to_csv() writes "Price,Close,...", "Ticker,AAPL,...", "Date,,,..." before the rows
    # (with group_by="ticker" the Ticker row comes first).
    if len(lines) > 2 and {lines[0].split(sep)[0].strip(), lines[1].split(sep)[0].strip()} == {"Price", "Ticker"} and lines[2].startswith("Date"):
        lines = _one_ticker(lines, sep, symbol)
    return "\n".join(lines), sep


def _one_ticker(lines: list[str], sep: str, symbol: str) -> list[str]:
    """yfinance's three header rows as one, keeping only the columns of `symbol`.

    First Version: the Ticker row was dropped and the first Close column used, so a
    yf.download(["AAPL", "MSFT"]) file imported as MSFT got AAPL's prices (off by up
    to 273 a share), with no warning. Current Version: only the columns whose Ticker
    is the symbol being imported are kept (BRK.B also matches BRK-B), and a file with
    no column for that symbol is refused, naming the tickers it does have.
    """
    first, second = (next(csv.reader([line], delimiter=sep)) for line in lines[:2])
    fields, tickers = (first, second) if first[0].strip() == "Price" else (second, first)
    names = [t.strip().upper() for t in tickers]
    present = list(dict.fromkeys(n for n in names[1:] if n))
    wanted = {symbol.upper(), symbol.upper().replace(".", "-"), symbol.upper().replace("-", ".")}
    keep = [0] + [i for i in range(1, len(fields)) if not present or (i < len(names) and names[i] in wanted)]
    if len(keep) == 1:
        listed = " and ".join(present) if len(present) <= 2 else ", ".join(present[:-1]) + " and " + present[-1]
        raise DataError(
            f"That file has prices for {listed}, not {symbol}. Import it under {'that symbol' if len(present) == 1 else 'one of those symbols'}, "
            f"or download {symbol} on its own and import that file."
        )
    out = io.StringIO()
    writer = csv.writer(out, delimiter=sep, lineterminator="\n")
    writer.writerow(["Date", *(fields[i] for i in keep[1:])])
    for row in csv.reader(lines[3:], delimiter=sep):
        if row:
            writer.writerow([row[i] if i < len(row) else "" for i in keep])
    return out.getvalue().splitlines()


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


CURRENCY_AND_SPACE = r"[\s$\u00a3\u20ac\u00a0]"
NUMBER = re.compile(r"[-+]?(\d[\d.,]*|[.,]\d+)")


def _style(number: str) -> str | None:
    """How one number writes its decimals: "point" (1,234.56), "comma" (1.234,56), "either", or None.

    "either" is one separator followed by exactly three digits after a short whole
    part, such as 3.010 or 1,234, which is a thousands separator in one convention
    and a decimal mark in the other. None means the number has no separator.
    """
    digits = number.lstrip("-+")
    dots, commas = digits.count("."), digits.count(",")
    if not dots and not commas:
        return None
    if dots and commas:  # the later mark is the decimal one
        return "point" if digits.rfind(".") > digits.rfind(",") else "comma"
    mark = "." if dots else ","
    if dots + commas > 1:  # 1.234.567 or 1,234,567: a repeated mark groups thousands
        return "comma" if mark == "." else "point"
    whole, frac = digits.split(mark)
    if len(frac) != 3 or whole in ("", "0") or len(whole) > 3:
        return "point" if mark == "." else "comma"
    return "either"


def _number_style(frame: pd.DataFrame, sep: str) -> str:
    """"point" or "comma" for the whole file, from every price and volume column.

    First Version: a semicolon file was read with decimal commas column by column,
    whenever a column had a digit-comma-digit. "2,007.00" became 1.9414, "3.010" (a
    dot grouping thousands, as in yen prices) became 3.01, and a volume of 1.234.567
    in a decimal-comma file became 0, all with no warning. Current Version: the
    convention is decided once for the file from the numbers that show it (both
    marks, a repeated mark, or a mark not followed by three digits). A file that
    shows both conventions is refused, and so is a semicolon or tab file whose
    numbers could be read either way. Comma-separated files keep the decimal point
    unless their numbers show otherwise.
    """
    seen: dict[str, str] = {}
    for c in NUMERIC:
        if c not in frame:
            continue
        for value in pd.unique(frame[c].dropna().astype(str).str.replace(CURRENCY_AND_SPACE, "", regex=True)):
            if NUMBER.fullmatch(value) and (style := _style(value)):
                seen.setdefault(style, value)
    if "point" in seen and "comma" in seen:
        raise DataError(
            f'The numbers in that file are written two ways ("{seen["point"]}" and "{seen["comma"]}"), so their size cannot be read reliably. '
            "Save it with a decimal point and no thousands separators (like 2007.50), then import it again."
        )
    if "point" in seen or "comma" in seen:
        return "point" if "point" in seen else "comma"
    if "either" in seen and sep != ",":
        example = seen["either"]
        whole, frac = example.lstrip("-+").replace(",", ".").split(".")
        small, big = f"{float(whole + '.' + frac):g}", str(int(whole + frac))
        raise DataError(
            f'Some numbers in that file can be read two ways: "{example}" could be {small} or {big}. '
            f"Save it with a decimal point and no thousands separators (like {big} or {small}), then import it again."
        )
    return "point"


def _numbers(values: pd.Series, style: str) -> pd.Series:
    """Numbers as broker exports write them: currency signs, thousands separators, or decimal commas."""
    text = values.astype(str).str.replace(CURRENCY_AND_SPACE, "", regex=True)
    if style == "comma":
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
    except (ValueError, TypeError, OverflowError, csv.Error) as exc:
        raise DataError(f"Could not read daily prices from that file ({exc.__class__.__name__}). {HOW_TO_FIX}") from None


def _parse_csv(text: str, symbol: str) -> PriceHistory:
    body, sep = _layout(text, symbol)
    try:
        frame = pd.read_csv(io.StringIO(body), sep=sep, dtype=str, skipinitialspace=True)
    except (ValueError, pd.errors.ParserError) as exc:
        raise DataError(f"That file is not a readable CSV ({exc.__class__.__name__}). {HOW_TO_FIX}") from None
    cols = {c: ALIASES.get(str(c).strip().lower()) for c in frame.columns}
    frame = frame.rename(columns={k: v for k, v in cols.items() if v})
    if "date" not in frame or "close" not in frame:
        # First Version: "The CSV needs at least a Date column and a Close column." with no
        # word on what the file had or what to do. Current Version: it names the file's
        # columns and says how to fix the file, like the other import messages.
        found = ", ".join(str(c).strip() for c in list(cols)[:8]) + (", ..." if len(cols) > 8 else "")
        raise DataError(
            f"The CSV needs at least a Date column and a Close column; this file has {found or 'no column names'}. "
            "Name the date column Date and the closing price column Close, with one row per trading day, then import it again."
        )
    frame = frame.loc[:, ~frame.columns.duplicated()]
    frame["date"] = _dates(frame["date"])
    frame = frame.dropna(subset=["date"])
    if frame.empty:
        raise DataError(f"None of the dates in that CSV could be read. Use dates like 2024-01-31 or 01/31/2024. {HOW_TO_FIX}")
    style = _number_style(frame, sep)
    for c in NUMERIC:
        if c in frame:
            frame[c] = _numbers(frame[c], style)
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
        # First Version: every imported file was labelled USD, so a 7203.T or SAP.DE
        # file showed yen or euro prices as dollars. Current Version: a CSV states no
        # currency, so it is left blank (""), never assumed.
        currency="",
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
