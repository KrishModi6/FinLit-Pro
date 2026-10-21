"""Regression tests for the price-data defects found by live testing.

Every payload is hand-built in Yahoo's or yfinance's documented shape; sessions
and the yfinance module are replaced by fakes, so nothing here goes online.
"""

import json
import threading
from collections.abc import Mapping
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
import pytest
import requests
from conftest import bars_from, gbm_closes

from finlit_pro.analytics import risk
from finlit_pro.data import http, prices, yahoo, yf_provider
from finlit_pro.data.cache import DiskCache
from finlit_pro.data.models import CACHE, LIVE, STALE, DataError, NetworkError, NotFoundError

DAY = 86400
NY = -14400  # New York in October (EDT)


def utc(text: str) -> int:
    return int(datetime.fromisoformat(text).replace(tzinfo=timezone.utc).timestamp())


def chart(symbol="TEST", closes=(250.0, 262.45, None), first="2026-10-16T13:30", gaps=(0, 3, 4), meta=None, offset=NY, adj=True):
    """A v8 chart payload: one bar per entry of `closes`, `gaps` days after `first` (UTC)."""
    t0 = utc(first)
    stamps = [t0 + g * DAY for g in gaps[: len(closes)]]
    m = {"symbol": symbol, "currency": "USD", "gmtoffset": offset, "longName": "Test Inc", "instrumentType": "EQUITY"}
    m.update(meta or {})
    quote = {
        "open": [c if c is None else c - 1 for c in closes],
        "high": [c if c is None else c + 2 for c in closes],
        "low": [c if c is None else c - 2 for c in closes],
        "close": list(closes),
        "volume": [None if c is None else 1000 for c in closes],
    }
    result = {"meta": m, "timestamp": stamps, "indicators": {"quote": [quote]}}
    if adj:
        result["indicators"]["adjclose"] = [{"adjclose": list(closes)}]
    return {"chart": {"result": [result], "error": None}}


AMZN_AFTER_CLOSE = {
    "regularMarketPrice": 262.63,
    "regularMarketTime": utc("2026-10-20T20:00:01"),
    "regularMarketDayHigh": 265.34,
    "regularMarketDayLow": 260.42,
    "regularMarketVolume": 34498734,
}


class FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status_code = status
        self._payload = payload
        self.text = json.dumps(payload) if payload is not None else ""
        self.encoding = "utf-8"

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class Router:
    """A fake requests.Session: maps the chart symbol in each URL to a response or an exception."""

    def __init__(self, routes):
        self.routes = routes
        self.urls: list[str] = []

    def get(self, url, headers=None, timeout=None):
        self.urls.append(url)
        symbol = url.split("/v8/finance/chart/")[1].split("?")[0] if "/v8/finance/chart/" in url else url
        result = self.routes.get(symbol, FakeResponse(404, {"chart": {"result": None, "error": {"code": "Not Found"}}}))
        result = result() if callable(result) else result
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def no_rate_limit(monkeypatch):
    monkeypatch.setattr(http, "limiter_for", lambda url: None)


# ------------------------------------------- day change against the right session


def test_null_close_for_the_latest_session_is_rebuilt_from_meta():
    # Live at 2026-10-21 01:00 UTC: Yahoo sent the 10-20 bar with close=None while
    # regularMarketPrice already held the 10-20 close. AMZN showed +5.05% (vs 10-16).
    h = yahoo.parse_chart(chart("AMZN", meta=AMZN_AFTER_CLOSE), "AMZN")
    assert h.price == 262.63
    assert h.previous_close == 262.45  # 10-19, the session before the price, not 10-16
    assert h.day_change == pytest.approx(262.63 / 262.45 - 1)  # +0.07%, not +5.05%
    assert h.source.as_of == "2026-10-20" and str(h.bars.index[-1].date()) == "2026-10-20"
    last = h.bars.iloc[-1]
    assert last["close"] == last["adjclose"] == h.price  # the model's last price matches the Monte Carlo's
    assert (last["high"], last["low"], last["volume"]) == (265.34, 260.42, 34498734)
    assert last["open"] == 262.45  # no open in meta: the previous close stands in
    assert h.bars.index.is_monotonic_increasing and not h.bars.index.has_duplicates
    assert h.bars.index.dtype == h.bars.index[:-1].dtype  # same resolution as Yahoo's own bars


def test_rebuilt_session_open_stays_inside_the_days_range():
    meta = dict(AMZN_AFTER_CLOSE, regularMarketDayHigh=240.0, regularMarketDayLow=230.0, regularMarketPrice=235.0)
    last = yahoo.parse_chart(chart("AMZN", meta=meta), "AMZN").bars.iloc[-1]
    assert last["low"] <= last["open"] <= last["high"] and last["open"] == 240.0  # gap down: open clipped to the high
    bare = {"regularMarketPrice": 263.0, "regularMarketTime": utc("2026-10-20T20:00:00")}
    last = yahoo.parse_chart(chart("AMZN", meta=bare), "AMZN").bars.iloc[-1]
    assert (last["open"], last["high"], last["low"], last["volume"]) == (262.45, 263.0, 262.45, 0)


def test_no_extra_session_when_meta_is_on_the_last_bars_date():
    meta = {"regularMarketPrice": 262.5, "regularMarketTime": utc("2026-10-19T20:00:00")}
    h = yahoo.parse_chart(chart("AMZN", closes=(250.0, 262.45), meta=meta), "AMZN")
    assert len(h.bars) == 2 and h.previous_close == 250.0 and h.source.as_of == "2026-10-19"


def test_session_date_uses_the_exchange_offset_not_utc():
    # 00:30 UTC on 10-20 is still 10-19 in New York: the 10-19 bar is the latest session.
    meta = {"regularMarketPrice": 262.5, "regularMarketTime": utc("2026-10-20T00:30:00")}
    h = yahoo.parse_chart(chart("AMZN", closes=(250.0, 262.45), meta=meta), "AMZN")
    assert len(h.bars) == 2 and h.source.as_of == "2026-10-19"
    # Tokyo: 00:30 UTC on 10-21 is 09:30 on 10-21, a new session after the 10-20 bar.
    tokyo = {"regularMarketPrice": 3095.0, "regularMarketTime": utc("2026-10-21T00:30:00")}
    h = yahoo.parse_chart(chart("7203.T", closes=(3102.0, 3102.0), first="2026-10-19T00:00", gaps=(0, 1), meta=tokyo, offset=32400), "7203.T")
    assert h.source.as_of == "2026-10-21" and h.previous_close == 3102.0


def test_quote_and_watchlist_use_the_same_session(monkeypatch, no_rate_limit):
    monkeypatch.setattr(http, "_session", lambda: Router({"AMZN": FakeResponse(200, chart("AMZN", meta=AMZN_AFTER_CLOSE))}))
    price, change = yahoo.quote("AMZN")
    assert price == 262.63 and change == pytest.approx(262.63 / 262.45 - 1)


# -------------------------------------------------- history before 1970, stable key


def test_history_asks_for_everything_since_1900_under_a_stable_cache_key(monkeypatch):
    seen = {}

    def fake_get_json(url, **kw):
        seen["url"], seen["key"] = url, kw.get("cache_key")
        return http.Fetched(chart("KO", closes=(0.263, 0.262, 0.265), first="1962-01-02T14:30", gaps=(0, 1, 2), meta={"regularMarketPrice": 0.265}), LIVE, 0, url)

    monkeypatch.setattr(yahoo, "get_json", fake_get_json)
    h = yahoo.history("KO")
    assert "period1=-2208994789" in seen["url"] and "period1=0&" not in seen["url"]
    assert seen["key"] == "yahoo:history:KO"
    assert str(h.bars.index[0].date()) == "1962-01-02"  # negative timestamps parse


def test_offline_copy_is_found_after_the_clock_hour_changes(monkeypatch, no_rate_limit):
    up = Router({"AAPL": FakeResponse(200, chart("AAPL", closes=(250.0, 262.45, 263.0), meta={"regularMarketPrice": 263.0}))})
    monkeypatch.setattr(http, "_session", lambda: up)
    assert yahoo.history("AAPL").source.status == LIVE
    real_time = yahoo.time.time
    monkeypatch.setattr(yahoo.time, "time", lambda: real_time() + 3 * 3600)  # period2 in the URL moves on
    down = Router({"AAPL": requests.exceptions.ConnectionError()})
    monkeypatch.setattr(http, "_session", lambda: down)
    monkeypatch.setattr(yf_provider, "history", lambda s: (_ for _ in ()).throw(DataError("yfinance failed")))
    h = prices.load_history("AAPL")
    assert h.source.status == STALE and h.price == 263.0 and len(h.attempts) == 2
    assert "Offline copy" in h.source.label()
    assert len(down.urls) == 1  # one host, once; step 3 read the disk without going online


def test_history_cache_does_not_grow_with_each_hour(monkeypatch, tmp_path, no_rate_limit):
    store = DiskCache(tmp_path / "grow")
    http.set_cache(store)
    monkeypatch.setattr(http, "_session", lambda: Router({"AAPL": FakeResponse(200, chart("AAPL", closes=(1.0, 2.0, 3.0)))}))
    real_time = yahoo.time.time
    for hours in range(4):
        monkeypatch.setattr(yahoo.time, "time", lambda h=hours: real_time() + h * 3600)
        yahoo.history("AAPL", force=True)
    assert len(list(store.root.glob("*.json"))) == 1
    assert not list(store.root.glob("*.tmp"))


def test_cached_history_never_goes_online(monkeypatch):
    monkeypatch.setattr(http, "_session", lambda: (_ for _ in ()).throw(AssertionError("network used")))
    assert yahoo.cached_history("AAPL") is None
    http.cache().put(yahoo.history_key("AAPL"), chart("AAPL", closes=(1.0, 2.0, 3.0)))
    h = yahoo.cached_history("aapl")
    assert h.source.status == STALE and h.price == 3.0
    http.cache().put(yahoo.history_key("BAD"), {"chart": {"result": None}})
    assert yahoo.cached_history("BAD") is None  # an unreadable copy is no copy


# ------------------------------------------------------------- class-share spelling


def test_brk_dot_b_is_retried_with_yahoos_dash_spelling(monkeypatch, no_rate_limit):
    session = Router({"BRK-B": FakeResponse(200, chart("BRK-B", closes=(532.02, 532.23, 539.82)))})
    monkeypatch.setattr(http, "_session", lambda: session)
    h = yahoo.history("brk.b")
    assert h.symbol == "BRK-B"  # the spelling Yahoo knows
    assert yahoo.quote("BRK.B")[0] == 539.82
    assert yahoo.cached_history("BRK.B").symbol == "BRK-B"
    assert prices.load_history("BRK.B").symbol == "BRK-B"


def test_exchange_suffixes_are_never_rewritten(monkeypatch, no_rate_limit):
    assert yahoo.spellings("SAP.DE") == ["SAP.DE"] and yahoo.spellings("7203.T") == ["7203.T"]
    assert yahoo.spellings("SHOP.TO") == ["SHOP.TO"] and yahoo.spellings("BF.B") == ["BF.B", "BF-B"]
    session = Router({"BP.L": FakeResponse(200, chart("BP.L", closes=(4.0, 4.1)))})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.history("BP.L").symbol == "BP.L"  # found first time: no dash retry
    assert not any("BP-L" in u for u in session.urls)
    with pytest.raises(NotFoundError, match='"SAP.DE"'):
        yahoo.history("SAP.DE")
    assert not any("SAP-DE" in u for u in session.urls)


def test_unknown_class_share_names_both_spellings(monkeypatch, no_rate_limit):
    monkeypatch.setattr(http, "_session", lambda: Router({}))
    with pytest.raises(NotFoundError, match='"BRK.Q" or "BRK-Q"'):
        yahoo.history("BRK.Q")


# ---------------------------------------------------------- not-found and delisted


def test_not_found_covers_delisting_and_stops_the_chain(monkeypatch, no_rate_limit):
    session = Router({})
    monkeypatch.setattr(http, "_session", lambda: session)
    monkeypatch.setattr(yf_provider, "history", lambda s: (_ for _ in ()).throw(AssertionError("chain continued")))
    with pytest.raises(NotFoundError) as caught:
        prices.load_history("TWTR")
    message = str(caught.value)
    assert "misspelled" in message and "delisted or acquired" in message and "search by company name" in message
    assert len(session.urls) == 1  # the second host is not asked about a symbol Yahoo does not know
    with pytest.raises(NotFoundError, match="delisted or acquired"):
        yahoo.quote("TWTR")  # the watchlist gets the same message, not "HTTP 404"


def test_http_404_with_a_message_is_a_not_found_error(monkeypatch):
    monkeypatch.setattr(http, "_session", lambda: Router({"https://www.sec.gov/x.htm": FakeResponse(404)}))
    with pytest.raises(NotFoundError, match="gone"):
        http.get_text("https://www.sec.gov/x.htm", not_found_message="gone")
    with pytest.raises(DataError, match="HTTP 404") as caught:
        http.get_text("https://www.sec.gov/x.htm")
    assert not isinstance(caught.value, NotFoundError)


# ------------------------------------------------------------ hanging or offline Yahoo


def test_timeouts_are_split_and_retries_do_not_multiply_a_hang():
    assert http.TIMEOUT == (5.0, 15.0)
    http._local.__dict__.pop("session", None)
    retry = http._session().get_adapter("https://query1.finance.yahoo.com").max_retries
    assert (retry.connect, retry.read, retry.status) == (1, 1, 3)
    assert 429 in retry.status_forcelist and 503 in retry.status_forcelist


@pytest.mark.parametrize("error", [requests.exceptions.ReadTimeout(), requests.exceptions.ConnectTimeout(), requests.exceptions.ConnectionError()])
def test_network_failures_are_network_errors_and_skip_the_second_host(monkeypatch, no_rate_limit, error):
    session = Router({"AAPL": error})
    monkeypatch.setattr(http, "_session", lambda: session)
    with pytest.raises(NetworkError, match="internet connection"):
        yahoo.history("AAPL", allow_stale=False)
    assert len(session.urls) == 1


def test_server_errors_still_try_the_second_host(monkeypatch, no_rate_limit):
    session = Router({"AAPL": FakeResponse(500)})
    monkeypatch.setattr(http, "_session", lambda: session)
    with pytest.raises(DataError, match="HTTP 500"):
        yahoo.history("AAPL", allow_stale=False)
    assert [u.split("/v8")[0] for u in session.urls] == list(yahoo.HOSTS)


def test_exhausted_5xx_retries_are_not_called_rate_limiting(monkeypatch):
    error = requests.exceptions.RetryError("Max retries exceeded (Caused by ResponseError('too many 503 error responses'))")
    monkeypatch.setattr(http, "_session", lambda: Router({"https://example.test/x": error}))
    with pytest.raises(DataError, match="server errors"):
        http.get_json("https://example.test/x", service="Yahoo Finance")


def test_cache_key_replaces_the_url_as_the_cache_name(monkeypatch):
    session = Router({"https://example.test/a?t=1": FakeResponse(200, {"n": 1})})
    monkeypatch.setattr(http, "_session", lambda: session)
    http.get_json("https://example.test/a?t=1", ttl_s=60, cache_key="logical")
    again = http.get_json("https://example.test/a?t=2", ttl_s=60, cache_key="logical")
    assert again.status == CACHE and again.value == {"n": 1} and len(session.urls) == 1


def test_concurrent_writes_of_one_key_leave_a_readable_entry(tmp_path):
    store = DiskCache(tmp_path / "race")
    value = {"rows": list(range(20000))}
    threads = [threading.Thread(target=lambda: [store.put("k", value) for _ in range(5)]) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert store.get("k", None)[0] == value


# --------------------------------------------------------------- yfinance fallback


class FakeMetadata(Mapping):
    """Like yfinance's HistoryMetadata: touching the lazy key would go online."""

    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        if key == "tradingPeriods":
            raise AssertionError("lazy key fetched")
        return self.data[key]

    def __iter__(self):
        return iter([*self.data, "tradingPeriods"])

    def __len__(self):
        return len(self.data) + 1


def fake_yf(frames: dict, metadata: dict, options=None):
    class Ticker:
        def __init__(self, symbol):
            self.symbol = symbol
            self.options = options or []

        def history(self, **_k):
            return frames.get(self.symbol, pd.DataFrame())

        @property
        def history_metadata(self):
            return FakeMetadata(metadata.get(self.symbol, {}))

        def option_chain(self, expiry):
            row = {"contractSymbol": "X", "strike": 100.0, "bid": 1.0, "ask": 1.2, "lastPrice": 1.1, "impliedVolatility": 0.3, "volume": 5, "openInterest": 7}
            return type("Chain", (), {"calls": pd.DataFrame([row]), "puts": pd.DataFrame([row])})()

    return type("yf", (), {"Ticker": Ticker})


def yf_frame(n=5):
    index = pd.date_range("2026-10-13", periods=n, freq="B", tz="Asia/Tokyo")
    close = np.linspace(3000, 3100, n)
    return pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close, "Adj Close": close, "Volume": 1000.0, "Dividends": 0.0, "Stock Splits": 0.0}, index=index)


def test_yfinance_fallback_takes_currency_name_and_exchange_from_metadata(monkeypatch):
    meta = {"7203.T": {"symbol": "7203.T", "currency": "JPY", "longName": "Toyota Motor Corporation", "fullExchangeName": "Tokyo", "instrumentType": "EQUITY"}}
    monkeypatch.setattr(yf_provider, "_yf", lambda: fake_yf({"7203.T": yf_frame()}, meta))
    h = yf_provider.history("7203.T")
    assert (h.currency, h.name, h.exchange, h.instrument_type) == ("JPY", "Toyota Motor Corporation", "Tokyo", "EQUITY")
    assert h.bars.index.tz is None and str(h.bars.index[-1].date()) == "2026-10-19"


def test_yfinance_fallback_never_assumes_usd(monkeypatch):
    monkeypatch.setattr(yf_provider, "_yf", lambda: fake_yf({"SAP.DE": yf_frame()}, {"SAP.DE": {"shortName": "SAP SE   "}}))
    h = yf_provider.history("SAP.DE")
    assert h.currency is None and h.name == "SAP SE" and h.exchange is None


def test_yfinance_fallback_finds_class_shares_by_dash(monkeypatch):
    meta = {"BRK-B": {"symbol": "BRK-B", "currency": "USD", "longName": "Berkshire Hathaway Inc."}}
    monkeypatch.setattr(yf_provider, "_yf", lambda: fake_yf({"BRK-B": yf_frame()}, meta))
    h = yf_provider.history("BRK.B")
    assert h.symbol == "BRK-B" and h.currency == "USD"


def test_option_chain_source_is_as_of_today_with_the_expiry_in_detail(monkeypatch):
    yf_provider._chains.clear()
    monkeypatch.setattr(yf_provider, "_yf", lambda: fake_yf({}, {}, options=["2099-11-20", "2099-12-18"]))
    chain = yf_provider.option_chain("TESTOPT", "2099-11-20", 100.0)
    assert chain.source.as_of == date.today().isoformat()
    assert "Expiry 2099-11-20" in chain.source.detail and "delayed 15 minutes" in chain.source.detail
    assert "as of 2099" not in chain.source.label()


# ---------------------------------------------------------------------- CSV import


def yf_default_export(start="2026-01-02", n=300, tz="America/New_York") -> str:
    """Ticker.history().to_csv() as yfinance writes it: dates with a UTC offset that changes at DST."""
    index = pd.bdate_range(start, periods=n, tz=tz)
    closes = gbm_closes(n).to_numpy()
    frame = pd.DataFrame({"Open": closes, "High": closes, "Low": closes, "Close": closes, "Adj Close": closes, "Volume": 1000, "Dividends": 0.0, "Stock Splits": 0.0}, index=index)
    frame.index.name = "Date"
    return frame.to_csv()


def test_yfinance_export_spanning_dst_imports_with_naive_dates(tmp_path):
    text = yf_default_export()
    assert "-05:00" in text and "-04:00" in text  # mixed offsets: the case that raised before
    path = tmp_path / "msft.csv"
    path.write_text(text)
    h = prices.import_csv(str(path), "MSFT")
    assert h.bars.index.tz is None and len(h.bars) == 300
    assert str(h.bars.index[0].date()) == "2026-01-02" and (h.bars.index == h.bars.index.normalize()).all()
    bench = bars_from(gbm_closes(400, seed=5).set_axis(pd.bdate_range("2025-11-03", periods=400)))
    risk.report(h.closes, bench["adjclose"], 0.04, 1, "SPY")  # the Returns view: no tz comparison error


def test_a_positive_offset_keeps_the_exchanges_own_date():
    h = prices.parse_csv(yf_default_export("2026-03-02", 40, "Asia/Tokyo"), "7203.T")
    assert str(h.bars.index[0].date()) == "2026-03-02"  # not shifted to the previous UTC day
    assert h.bars.index.tz is None


def test_yf_download_layout_with_three_header_rows():
    rows = [f"2026-02-{d:02d},{100 + d},{100 + d},{101 + d},{99 + d},{100 + d},5000" for d in range(1, 29)] + [f"2026-03-{d:02d},{130 + d},{130 + d},{131 + d},{129 + d},{130 + d},5000" for d in range(1, 6)]
    text = "Price,Adj Close,Close,High,Low,Open,Volume\nTicker,MSFT,MSFT,MSFT,MSFT,MSFT,MSFT\nDate,,,,,,\n" + "\n".join(rows)
    h = prices.parse_csv(text, "MSFT")
    assert len(h.bars) == 33 and h.bars["close"].iloc[0] == 101


def test_mixed_offsets_in_a_non_iso_layout_take_each_rows_own_date():
    rows = [f"01/{d:02d}/2026 00:00:00{'-05:00' if d % 2 else '+09:00'},{100 + d}" for d in range(1, 32)]
    h = prices.parse_csv("Date,Close\n" + "\n".join(rows), "TEST")
    assert h.bars.index.tz is None and str(h.bars.index[0].date()) == "2026-01-01" and len(h.bars) == 31


def test_windows_1252_csv_with_a_pound_sign_imports(tmp_path):
    path = tmp_path / "excel.csv"
    path.write_bytes(b"Date,Close\n" + b"\n".join(f"2024-01-{i:02d},\xa3{100 + i}".encode("latin-1") for i in range(1, 32)))
    h = prices.import_csv(str(path), "TEST")
    assert h.bars["close"].iloc[-1] == 131
    assert prices.load_imported("TEST").bars["close"].iloc[-1] == 131  # the saved copy reads back


def test_utf16_tab_separated_export_imports():
    text = "Date\tClose\n" + "\n".join(f"2024-01-{i:02d}\t{100 + i}" for i in range(1, 32))
    assert prices.parse_csv(text.encode("utf-16"), "TEST").bars["close"].iloc[0] == 101


@pytest.mark.parametrize(
    "data,message",
    [
        (b"PK\x03\x04\x14\x00\x06\x00" * 20, "Excel workbook or a zip archive"),
        (b"Date,Close\n\x00\x01\x02\x03", "not a text CSV"),
        (b"Date,Close\n\x81\x8d\x8f\x90", "not a text CSV"),  # undefined in Windows-1252 too
        (b"", "not a readable CSV"),
        (b"Date,Close\n" + b"\n".join(b"someday,%d" % i for i in range(40)), "None of the dates"),
        (b"Date,Close\n" + b"\n".join(b"2024-01-01,%d" % i for i in range(40)), "more than one row for some days"),
    ],
)
def test_unreadable_files_get_a_data_error_that_says_what_to_do(tmp_path, data, message):
    path = tmp_path / "bad.csv"
    path.write_bytes(data)
    with pytest.raises(DataError, match=message):
        prices.import_csv(str(path), "TEST")


def test_a_missing_file_is_a_data_error(tmp_path):
    with pytest.raises(DataError, match="Could not open nope.csv"):
        prices.import_csv(str(tmp_path / "nope.csv"), "TEST")


def test_semicolon_csv_with_decimal_commas():
    text = "Date;Open;Close;Volume\n" + "\n".join(f"{d:02d}.01.2024;1.2{d:02d},50;1.2{d:02d},75;1.000" for d in range(1, 32))
    h = prices.parse_csv(text, "SAP.DE")
    assert h.bars["close"].iloc[0] == pytest.approx(1201.75) and h.bars["open"].iloc[-1] == pytest.approx(1231.50)
    assert str(h.bars.index[0].date()) == "2024-01-01" and str(h.bars.index[-1].date()) == "2024-01-31"
    plain = "sep=;\nDate;Close\n" + "\n".join(f"2024-01-{d:02d};{100 + d}.5" for d in range(1, 32))
    assert prices.parse_csv(plain, "TEST").bars["close"].iloc[0] == 101.5


def test_parser_errors_become_data_errors(monkeypatch):
    def boom(*_a, **_k):
        raise TypeError("unexpected")

    monkeypatch.setattr(prices, "_dates", boom)
    with pytest.raises(DataError, match="Date column"):
        prices.parse_csv("Date,Close\n" + "\n".join(f"2024-01-{d:02d},{d}" for d in range(1, 32)), "TEST")
