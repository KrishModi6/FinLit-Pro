"""Regression tests for the second round of price-data fixes (verify_prices.md and the data-layer audit).

Every payload is hand-built in Yahoo's or yfinance's documented shape, with the
values seen live on 2026-10-20/21 where they matter; sessions and the yfinance
module are replaced by fakes, so nothing here goes online.
"""

import json
import time
from datetime import datetime, timezone

import pandas as pd
import pytest
import requests

from finlit_pro.data import http, prices, yahoo, yf_provider
from finlit_pro.data.cache import DiskCache
from finlit_pro.data.models import CACHE, LIVE, STALE, DataError, NetworkError, NotFoundError

DAY = 86400


def utc(text: str) -> int:
    return int(datetime.fromisoformat(text).replace(tzinfo=timezone.utc).timestamp())


def payload(symbol="TEST", stamps=(), closes=(), meta=None, quote=None, events=None, tz="America/New_York", offset=-14400):
    """A v8 chart payload with explicit timestamps; `quote` overrides the generated OHLCV lists."""
    m = {"symbol": symbol, "currency": "USD", "gmtoffset": offset, "exchangeTimezoneName": tz, "longName": "Test Inc", "instrumentType": "EQUITY"}
    m.update(meta or {})
    if tz is None:
        m.pop("exchangeTimezoneName")
    q = {
        "open": [None if c is None else c - 1 for c in closes],
        "high": [None if c is None else c + 2 for c in closes],
        "low": [None if c is None else c - 2 for c in closes],
        "close": list(closes),
        "volume": [None if c is None else 1000 for c in closes],
    }
    q.update(quote or {})
    result = {"meta": m, "timestamp": list(stamps), "indicators": {"quote": [q], "adjclose": [{"adjclose": list(closes)}]}}
    if events:
        result["events"] = events
    return {"chart": {"result": [result], "error": None}}


def daily(first: str, n: int, closes=None):
    """n consecutive UTC timestamps a day apart, starting at `first`."""
    t0 = utc(first)
    return [t0 + i * DAY for i in range(n)], list(closes) if closes is not None else [100.0 + i for i in range(n)]


class FakeResponse:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body
        self.text = json.dumps(body) if body is not None else ""
        self.encoding = "utf-8"

    def json(self):
        if self._body is None:
            raise ValueError("no json")
        return self._body


class Hosts:
    """A fake requests.Session keyed by (host, symbol); logs every URL. A value may be a callable, an exception or a response."""

    def __init__(self, routes):
        self.routes = routes
        self.urls: list[str] = []

    def get(self, url, headers=None, timeout=None):
        self.urls.append(url)
        host = url.split("//")[1].split(".")[0]
        symbol = url.split("/v8/finance/chart/")[1].split("?")[0] if "/v8/finance/chart/" in url else url
        result = self.routes.get((host, symbol), self.routes.get(symbol, FakeResponse(404, {"chart": {"result": None, "error": {"code": "Not Found"}}})))
        result = result() if callable(result) else result
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def no_rate_limit(monkeypatch):
    monkeypatch.setattr(http, "limiter_for", lambda url: None)


def later(monkeypatch, seconds):
    """Move every clock the cache and Yahoo read forward by `seconds`."""
    real = time.time
    monkeypatch.setattr(time, "time", lambda: real() + seconds)


# ------------------------------------------------- bug 1: the rebuilt latest session


def null_close_session(open_, high, low, volume, price, day_high=None, day_low=None):
    """Two finished sessions, then 2026-10-20 sent with close=None and the session's price in meta (as SAP.DE and ASML.AS were live)."""
    stamps = [utc("2026-10-16T07:00"), utc("2026-10-19T07:00"), utc("2026-10-20T07:00")]
    meta = {"regularMarketPrice": price, "regularMarketTime": utc("2026-10-20T15:38"), "regularMarketDayHigh": day_high, "regularMarketDayLow": day_low}
    quote = {"open": [1440.0, 1450.0, open_], "high": [1460.0, 1470.0, high], "low": [1430.0, 1445.0, low], "close": [1450.0, 1469.4, None], "volume": [1000, 1000, volume]}
    return payload("ASML.AS", stamps, (1450.0, 1469.4, None), meta=meta, quote=quote, tz="Europe/Amsterdam", offset=7200)


def test_latest_session_keeps_the_open_high_low_and_volume_yahoo_sent():
    # ASML.AS live: open 1452.6, close 1455.4 (an up day); the first fix used the previous close 1469.4 as the open.
    h = yahoo.parse_chart(null_close_session(1452.6, 1469.4, 1436.6, 476981, 1455.4, 1469.4, 1436.6), "ASML.AS")
    last = h.bars.iloc[-1]
    assert str(h.bars.index[-1].date()) == "2026-10-20" and h.previous_close == 1469.4
    assert (last["open"], last["high"], last["low"], last["close"], last["volume"]) == (1452.6, 1469.4, 1436.6, 1455.4, 476981)
    assert last["close"] >= last["open"]  # drawn as the up day it was


def test_unknown_open_high_low_are_the_close_not_a_made_up_range():
    # VOD.L live: the null bar and meta both sent 0.0 for open, high and low; volume 9,356,395 was real.
    h = yahoo.parse_chart(null_close_session(0.0, 0.0, 0.0, 9356395, 119.4, 0.0, 0.0), "VOD.L")
    last = h.bars.iloc[-1]
    assert (last["open"], last["high"], last["low"], last["close"]) == (119.4, 119.4, 119.4, 119.4)
    assert last["volume"] == 9356395


def test_rebuilt_range_always_includes_the_open_and_the_close():
    # The bar's high and low were captured before the last trade; the close is still a price traded that day.
    last = yahoo.parse_chart(null_close_session(1452.6, 1454.0, 1450.0, 10, 1455.4), "ASML.AS").bars.iloc[-1]
    assert last["high"] == 1455.4 and last["low"] == 1450.0 and last["open"] == 1452.6
    # Meta fills what the bar did not send.
    last = yahoo.parse_chart(null_close_session(None, None, None, None, 1455.4, 1469.4, 1436.6), "ASML.AS").bars.iloc[-1]
    assert (last["open"], last["high"], last["low"], last["volume"]) == (1455.4, 1469.4, 1436.6, 0)


# --------------------------------------------- audit: dates from the exchange's clock


def us_midnight_stamps():
    """GC=F style: bars stamped at New York midnight on both sides of a DST change (04:00 UTC in summer, 05:00 UTC in winter)."""
    days = pd.bdate_range("2026-10-26", "2026-11-06")
    return [int(pd.Timestamp(d, tz="America/New_York").timestamp()) for d in days], [d.date() for d in days]


def test_bars_on_both_sides_of_dst_keep_their_own_dates():
    stamps, days = us_midnight_stamps()
    closes = [4000.0 + i for i in range(len(stamps))]
    # After 2026-11-01 Yahoo's gmtoffset is New York's winter offset; the summer bars must not move to the previous day.
    h = yahoo.parse_chart(payload("GC=F", stamps, closes, offset=-18000), "GC=F")
    assert [d.date() for d in h.bars.index] == days
    assert not (h.bars.index.dayofweek >= 5).any()  # no weekend-dated bars


def test_london_fx_dates_survive_the_clock_change():
    # EURUSD=X: stamped at London midnight, 23:00 UTC the evening before in summer time.
    days = pd.bdate_range("2026-10-19", "2026-10-30")
    stamps = [int(pd.Timestamp(d, tz="Europe/London").timestamp()) for d in days]
    h = yahoo.parse_chart(payload("EURUSD=X", stamps, [1.12 + i / 1000 for i in range(len(days))], tz="Europe/London", offset=0), "EURUSD=X")
    assert [d.date() for d in h.bars.index] == [d.date() for d in days]


def test_dividends_splits_and_the_latest_session_use_the_exchanges_clock():
    stamps, days = us_midnight_stamps()
    summer = stamps[2]  # 2026-10-28 00:00 New York
    events = {"dividends": {str(summer): {"amount": 0.5, "date": summer}}, "splits": {str(summer): {"date": summer, "numerator": 2, "denominator": 1}}}
    meta = {"regularMarketPrice": 5000.0, "regularMarketTime": utc("2026-11-09T05:00")}  # 2026-11-09 00:00 New York (winter)
    h = yahoo.parse_chart(payload("GC=F", stamps, [4000.0 + i for i in range(len(stamps))], meta=meta, events=events, offset=-18000), "GC=F")
    assert str(h.dividends.index[0].date()) == "2026-10-28" and str(h.splits.index[0].date()) == "2026-10-28"
    assert str(h.bars.index[-1].date()) == "2026-11-09" and h.price == 5000.0


def test_gmtoffset_is_used_when_meta_names_no_time_zone():
    # 09:30 New York stamps give the same date with any offset; the fallback must still work without a name.
    stamps, closes = daily("2026-10-19T13:30", 3)
    for tz in (None, "Not/A_Zone"):
        h = yahoo.parse_chart(payload("AAPL", stamps, closes, tz=tz), "AAPL")
        assert [str(d.date()) for d in h.bars.index] == ["2026-10-19", "2026-10-20", "2026-10-21"]


# ------------------------------------------------ audit: malformed payloads are DataErrors


def good():
    stamps, closes = daily("2026-10-12T13:30", 5)
    return payload("AAPL", stamps, closes)


def broken(change):
    p = good()
    change(p["chart"]["result"][0])
    return p


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["indicators"].update(quote=[None]),
        lambda r: r["indicators"].update(adjclose=[None]),
        lambda r: r["indicators"]["quote"][0].update(close=[1.0, 2.0, 3.0, 4.0]),  # shorter than the timestamps
        lambda r: r["timestamp"].__setitem__(2, None),
        lambda r: r.update(meta="not a mapping"),
        lambda r: r.update(timestamp="soon"),
    ],
)
def test_malformed_chart_payloads_raise_data_error(change):
    with pytest.raises(DataError, match="could not be read"):
        yahoo.parse_chart(broken(change), "AAPL")
    with pytest.raises(DataError):
        yahoo.parse_chart([1, 2], "AAPL")


def test_events_without_a_date_or_a_value_are_skipped():
    p = broken(lambda r: r.update(events={"dividends": {"a": {"amount": 0.2}, "b": {"date": utc("2026-10-13T13:30"), "amount": 0.3}, "c": {"date": utc("2026-10-14T13:30")}},
                                          "splits": {"x": {"date": utc("2026-10-13T13:30"), "numerator": 4, "denominator": 0}}}))
    h = yahoo.parse_chart(p, "AAPL")
    assert list(h.dividends.values) == [0.3] and h.splits.empty


def test_a_malformed_payload_moves_the_chain_on_to_yfinance(monkeypatch, no_rate_limit):
    session = Hosts({"AAPL": FakeResponse(200, broken(lambda r: r["indicators"].update(adjclose=[None])))})
    monkeypatch.setattr(http, "_session", lambda: session)
    tried = []

    def yf_history(symbol):
        tried.append(symbol)
        raise DataError("yfinance failed")

    monkeypatch.setattr(yf_provider, "history", yf_history)
    with pytest.raises(DataError, match="No price data") as caught:
        prices.load_history("AAPL")
    assert tried == ["AAPL"] and "could not be read" in str(caught.value)
    assert not isinstance(caught.value, (AttributeError, NotFoundError))


# ------------------------------------------------ bug 4: a bad answer never replaces a good copy


def test_an_unreadable_200_never_replaces_the_offline_copy(monkeypatch, no_rate_limit):
    stamps, closes = daily("2026-10-12T13:30", 5)
    good_payload = payload("AAPL", stamps, closes)
    session = Hosts({"AAPL": FakeResponse(200, good_payload)})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.history("AAPL").price == 104.0
    empty = {"chart": {"result": [{"meta": {"symbol": "AAPL"}, "timestamp": [], "indicators": {"quote": [{}]}}], "error": None}}
    later(monkeypatch, 3600)
    session.routes["AAPL"] = FakeResponse(200, empty)
    monkeypatch.setattr(yf_provider, "history", lambda s: (_ for _ in ()).throw(DataError("yfinance failed")))
    h = prices.load_history("AAPL")
    assert h.source.status == STALE and h.price == 104.0  # the good copy, labelled Offline copy
    assert http.cache().get(yahoo.history_key("AAPL"), None)[0] == good_payload
    session.routes["AAPL"] = requests.exceptions.ConnectionError()
    assert prices.load_history("AAPL").price == 104.0  # and it is still there offline


def test_get_json_check_rejects_before_saving(monkeypatch):
    monkeypatch.setattr(http, "_session", lambda: Hosts({"https://example.test/a": FakeResponse(200, {"n": 1})}))
    http.get_json("https://example.test/a", ttl_s=60)

    def refuse(value):
        raise DataError("unusable")

    monkeypatch.setattr(http, "_session", lambda: Hosts({"https://example.test/a": FakeResponse(200, {"n": 2})}))
    with pytest.raises(DataError, match="unusable"):
        http.get_json("https://example.test/a", ttl_s=0, allow_stale=False, check=refuse)
    stale = http.get_json("https://example.test/a", ttl_s=0, check=refuse)
    assert stale.status == STALE and stale.value == {"n": 1}


# ------------------------------------------------ bug 5: BRK.B stops asking for BRK.B


def test_the_spelling_yahoo_answered_to_is_asked_for_first(monkeypatch, no_rate_limit):
    stamps, closes = daily("2026-10-15T13:30", 4, (532.02, 532.23, 535.0, 539.82))
    session = Hosts({"BRK-B": FakeResponse(200, payload("BRK-B", stamps, closes))})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.quote("BRK.B")[0] == 539.82
    assert [u.split("/chart/")[1].split("?")[0] for u in session.urls] == ["BRK.B", "BRK-B"]  # once, to learn the spelling
    session.urls.clear()
    assert yahoo.quote("BRK.B")[0] == 539.82 and session.urls == []  # fresh copy: no request at all
    later(monkeypatch, 600)
    yahoo.quote("BRK.B")
    assert [u.split("/chart/")[1].split("?")[0] for u in session.urls] == ["BRK-B"]  # no 404 first


def test_brk_dot_b_offline_inside_the_window_is_cached_not_an_offline_copy(monkeypatch, no_rate_limit):
    stamps, closes = daily("2026-10-15T13:30", 4, (532.02, 532.23, 535.0, 539.82))
    monkeypatch.setattr(http, "_session", lambda: Hosts({"BRK-B": FakeResponse(200, payload("BRK-B", stamps, closes))}))
    prices.load_history("BRK.B")
    down = Hosts({"BRK.B": requests.exceptions.ConnectionError(), "BRK-B": requests.exceptions.ConnectionError()})
    monkeypatch.setattr(http, "_session", lambda: down)
    monkeypatch.setattr(yf_provider, "history", lambda s: (_ for _ in ()).throw(AssertionError("yfinance tried")))
    h = prices.load_history("BRK.B")
    assert h.source.status == CACHE and h.attempts == [] and down.urls == []


def test_a_remembered_spelling_that_disappears_still_tries_the_other(monkeypatch, no_rate_limit):
    stamps, closes = daily("2026-10-15T13:30", 3)
    http.cache().put(yahoo.spelling_key("BRK.B"), "BRK-B")
    session = Hosts({"BRK.B": FakeResponse(200, payload("BRK.B", stamps, closes))})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.quote("BRK.B")[0] == 102.0
    assert [u.split("/chart/")[1].split("?")[0] for u in session.urls] == ["BRK-B", "BRK.B"]


# ------------------------------------------------ audit: watchlist quotes are never old


def test_watchlist_quote_never_returns_an_old_copy_as_current(monkeypatch, no_rate_limit):
    stamps, closes = daily("2026-10-15T13:30", 3, (98.0, 98.0, 100.0))
    session = Hosts({"AAPL": FakeResponse(200, payload("AAPL", stamps, closes))})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.quote("AAPL") == (100.0, pytest.approx(100 / 98 - 1))
    session.routes["AAPL"] = requests.exceptions.ConnectionError()
    assert yahoo.quote("AAPL")[0] == 100.0  # under two minutes old: still a cached quote
    later(monkeypatch, 3 * DAY)
    with pytest.raises(NetworkError):
        yahoo.quote("AAPL")  # the watchlist row stays blank
    session.routes["AAPL"] = FakeResponse(503)
    with pytest.raises(DataError, match="HTTP 503"):
        yahoo.quote("AAPL")


# ------------------------------------------------ audit: query1 5xx asks query2


def irx(rate):
    stamps, closes = daily("2026-10-15T13:30", 3, (rate, rate, rate))
    return payload("^IRX", stamps, closes, meta={"regularMarketPrice": rate})


def test_query1_server_errors_ask_query2_before_using_an_old_copy(monkeypatch, no_rate_limit):
    session = Hosts({"%5EIRX": FakeResponse(200, irx(3.9))})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.risk_free_rate()[0] == pytest.approx(0.039)
    later(monkeypatch, 3 * DAY)
    session.routes = {("query1", "%5EIRX"): FakeResponse(503), ("query2", "%5EIRX"): FakeResponse(200, irx(5.2))}
    session.urls.clear()
    rate, source = yahoo.risk_free_rate()
    assert rate == pytest.approx(0.052) and source.status == LIVE
    assert [u.split("//")[1].split(".")[0] for u in session.urls] == ["query1", "query2"]


def test_an_old_copy_is_used_only_when_every_host_fails(monkeypatch, no_rate_limit):
    session = Hosts({"%5EIRX": FakeResponse(200, irx(3.9))})
    monkeypatch.setattr(http, "_session", lambda: session)
    yahoo.risk_free_rate()
    later(monkeypatch, 3 * DAY)
    session.routes = {"%5EIRX": FakeResponse(503)}
    session.urls.clear()
    rate, source = yahoo.risk_free_rate()
    assert rate == pytest.approx(0.039) and source.status == STALE and len(session.urls) == 2
    session.routes = {"%5EIRX": requests.exceptions.ConnectionError()}
    session.urls.clear()
    assert yahoo.risk_free_rate()[1].status == STALE and len(session.urls) == 1  # network down: one host, then the copy


def test_a_fresh_copy_from_query2_is_used_without_a_request(monkeypatch, no_rate_limit):
    session = Hosts({("query1", "%5EIRX"): FakeResponse(503), ("query2", "%5EIRX"): FakeResponse(200, irx(4.1))})
    monkeypatch.setattr(http, "_session", lambda: session)
    assert yahoo.risk_free_rate()[0] == pytest.approx(0.041)
    session.urls.clear()
    rate, source = yahoo.risk_free_rate()
    assert source.status == CACHE and session.urls == []


def test_not_found_is_never_hidden_by_an_old_copy(monkeypatch, no_rate_limit):
    stamps, closes = daily("2026-10-15T13:30", 3)
    session = Hosts({"TWTR": FakeResponse(200, payload("TWTR", stamps, closes))})
    monkeypatch.setattr(http, "_session", lambda: session)
    yahoo.history("TWTR")
    session.routes = {}
    with pytest.raises(NotFoundError):
        yahoo.history("TWTR", force=True)


# ------------------------------------------------ bug 6: no "None" or assumed currency


def test_a_missing_currency_is_blank_never_usd(monkeypatch):
    stamps, closes = daily("2026-10-15T13:30", 3)
    p = payload("TEST", stamps, closes)
    p["chart"]["result"][0]["meta"].pop("currency")
    assert yahoo.parse_chart(p, "TEST").currency == ""
    text = "Date,Close\n" + "\n".join(f"2024-01-{d:02d},{100 + d}" for d in range(1, 32))
    h = prices.parse_csv(text, "7203.T")
    assert h.currency == "" and "None" not in f"{h.price} {h.currency}"


# ------------------------------------------------ bug 2: multi-ticker yfinance downloads


def yf_download(tickers, group_by="column", n=35):
    """yf.download(tickers).to_csv(): two header rows naming the field and the ticker, then a Date row."""
    fields = ["Adj Close", "Close", "High", "Low", "Open", "Volume"]
    cols = [(f, t) for f in fields for t in tickers] if group_by == "column" else [(f, t) for t in tickers for f in fields]
    base = {t: 100.0 * (i + 1) for i, t in enumerate(tickers)}
    rows = []
    for d in pd.bdate_range("2026-01-02", periods=n):
        rows.append(",".join([str(d.date())] + [str(1000 if f == "Volume" else base[t] + d.day) for f, t in cols]))
    price_row = "Price," + ",".join(f for f, _ in cols)
    ticker_row = "Ticker," + ",".join(t for _, t in cols)
    head = [price_row, ticker_row] if group_by == "column" else [ticker_row, price_row]
    return "\n".join(head + ["Date" + "," * len(cols)] + rows)


def test_multi_ticker_download_imports_the_requested_symbols_columns():
    text = yf_download(["AAPL", "MSFT"])
    msft = prices.parse_csv(text, "MSFT")
    aapl = prices.parse_csv(text, "AAPL")
    assert msft.bars["close"].iloc[0] == 202.0 and aapl.bars["close"].iloc[0] == 102.0
    assert prices.parse_csv(yf_download(["AAPL", "MSFT"], group_by="ticker"), "MSFT").bars["close"].iloc[-1] == msft.bars["close"].iloc[-1]
    assert prices.parse_csv(yf_download(["BRK-B", "AAPL"]), "BRK.B").bars["close"].iloc[0] == 102.0


def test_a_download_without_the_symbol_is_refused():
    with pytest.raises(DataError, match="prices for AAPL and MSFT, not TSLA"):
        prices.parse_csv(yf_download(["AAPL", "MSFT"]), "TSLA")
    with pytest.raises(DataError, match="prices for AAPL, not MSFT. Import it under that symbol"):
        prices.parse_csv(yf_download(["AAPL"]), "MSFT")


# ------------------------------------------------ bug 3: thousands separators in semicolon files


def semi(values, header="Date;Close"):
    return header + "\n" + "\n".join(f"{d.date()};{v}" for d, v in zip(pd.bdate_range("2025-01-02", periods=len(values)), values))


def test_semicolon_file_with_comma_thousands_and_a_decimal_point():
    h = prices.parse_csv(semi([f"2,{i:03d}.50" for i in range(40)]), "TEST")
    assert h.bars["close"].iloc[0] == 2000.5 and h.bars["close"].iloc[-1] == 2039.5


def test_decimal_comma_file_reads_dotted_volumes_as_thousands():
    text = semi([f"100,{i:02d};1.234.567" for i in range(40)], "Date;Close;Volume")
    h = prices.parse_csv(text, "SAP.DE")
    assert h.bars["close"].iloc[1] == 100.01 and h.bars["volume"].iloc[0] == 1234567


def test_numbers_that_read_two_ways_are_refused_with_what_to_do():
    with pytest.raises(DataError, match='"3.010" could be 3.01 or 3010. Save it with a decimal point'):
        prices.parse_csv(semi([f"3.{i:03d}" for i in range(10, 50)]), "7203.T")
    with pytest.raises(DataError, match="written two ways"):
        prices.parse_csv(semi(["1.234,50"] * 20 + ["1,234.50"] * 20), "TEST")


def test_comma_files_keep_the_decimal_point():
    text = "Date,Close\n" + "\n".join(f"{d.date()},3.{i:03d}" for i, d in enumerate(pd.bdate_range("2025-01-02", periods=40), start=10))
    assert prices.parse_csv(text, "TEST").bars["close"].iloc[0] == 3.01


def test_missing_columns_message_names_them_and_says_what_to_do():
    with pytest.raises(DataError, match="Date column and a Close column; this file has Day, Price. Name the date column Date"):
        prices.parse_csv("Day,Price\n2024-01-01,1", "TEST")


# ------------------------------------------------ minor: cache temp files, option as-of


def test_clear_removes_leftover_temporary_files(tmp_path):
    store = DiskCache(tmp_path / "c")
    store.put("a", 1)
    store.put("b", 2)
    (store.root / "deadbeef.123.456.tmp").write_text("{")
    assert store.clear() == 2  # responses removed, as the Settings message says
    assert list(store.root.iterdir()) == []


def option_yf(last_trades, underlying=None):
    rows = [{"contractSymbol": f"X{i}", "strike": 100.0 + i, "bid": 1.0, "ask": 1.2, "lastPrice": 1.1, "impliedVolatility": 0.3, "volume": 5, "openInterest": 7,
             "lastTradeDate": pd.Timestamp(t, tz="UTC") if t else pd.NaT} for i, t in enumerate(last_trades)]

    class Ticker:
        options = ["2099-11-20"]

        def __init__(self, symbol):
            pass

        def option_chain(self, expiry):
            frame = pd.DataFrame(rows)
            return type("Chain", (), {"calls": frame, "puts": frame.iloc[:1], "underlying": underlying})()

    return type("yf", (), {"Ticker": Ticker})


def test_option_as_of_is_the_newest_trade_on_the_exchanges_clock(monkeypatch):
    yf_provider._chains.clear()
    trades = ["2026-10-16 15:00", "2026-10-20 19:59:59", None]
    monkeypatch.setattr(yf_provider, "_yf", lambda: option_yf(trades, {"exchangeTimezoneName": "America/New_York"}))
    chain = yf_provider.option_chain("OPTA", "2099-11-20", 100.0)
    assert chain.source.as_of == "2026-10-20" and "as of 2026-10-20" in chain.source.label()
    yf_provider._chains.clear()
    # 00:30 UTC on 10-21 is still 10-20 in New York.
    monkeypatch.setattr(yf_provider, "_yf", lambda: option_yf(["2026-10-21 00:30"], {"exchangeTimezoneName": "America/New_York"}))
    assert yf_provider.option_chain("OPTB", "2099-11-20", 100.0).source.as_of == "2026-10-20"


def test_option_as_of_is_blank_when_no_trade_time_is_reported(monkeypatch):
    yf_provider._chains.clear()
    monkeypatch.setattr(yf_provider, "_yf", lambda: option_yf([None, None]))
    chain = yf_provider.option_chain("OPTC", "2099-11-20", 100.0)
    assert chain.source.as_of is None and "date of these quotes is not known" in chain.source.detail
