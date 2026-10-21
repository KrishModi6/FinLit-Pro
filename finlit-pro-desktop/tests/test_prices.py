"""The price provider chain and CSV import. Providers are replaced by stubs; nothing goes online."""

import pandas as pd
import pytest
from conftest import bars_from, gbm_closes

from finlit_pro.data import prices, yahoo, yf_provider
from finlit_pro.data.models import IMPORT, LIVE, STALE, DataError, NotFoundError, PriceHistory, Source


def history(name: str, status: str = LIVE) -> PriceHistory:
    bars = bars_from(gbm_closes(300))
    return PriceHistory("TEST", "Test Inc", "USD", None, None, float(bars["close"].iloc[-1]), float(bars["close"].iloc[-2]), bars, Source(name, "", pd.Timestamp.now().to_pydatetime(), status=status))


def fail(message):
    def raiser(*_a, **_k):
        raise DataError(message)

    return raiser


def test_live_yahoo_answers_first(monkeypatch):
    monkeypatch.setattr(yahoo, "history", lambda s, force=False, allow_stale=True: history("chart"))
    monkeypatch.setattr(yf_provider, "history", fail("should not be called"))
    h = prices.load_history("test")
    assert h.source.name == "chart" and h.attempts == []


def test_falls_back_to_yfinance_and_records_why(monkeypatch):
    monkeypatch.setattr(yahoo, "history", fail("Yahoo Finance is rate limiting requests."))
    monkeypatch.setattr(yf_provider, "history", lambda s: history("yfinance"))
    h = prices.load_history("TEST")
    assert h.source.name == "yfinance"
    assert h.attempts == ["Yahoo chart API: Yahoo Finance is rate limiting requests."]


def test_then_to_the_stale_copy(monkeypatch):
    # Step 3 reads the saved copy from disk (yahoo.cached_history); it no longer calls yahoo.history again.
    monkeypatch.setattr(yahoo, "history", fail("Could not reach Yahoo Finance."))
    monkeypatch.setattr(yahoo, "cached_history", lambda s: history("chart", STALE))
    monkeypatch.setattr(yf_provider, "history", fail("yfinance failed"))
    h = prices.load_history("TEST")
    assert h.source.status == STALE and len(h.attempts) == 2


def test_then_to_an_imported_csv(monkeypatch, tmp_path):
    monkeypatch.setattr(yahoo, "history", fail("Could not reach Yahoo Finance."))
    monkeypatch.setattr(yf_provider, "history", fail("yfinance failed"))
    with pytest.raises(DataError, match="import a CSV"):
        prices.load_history("TEST")
    csv = tmp_path / "test.csv"
    rows = ["Date,Open,High,Low,Close,Adj Close,Volume"] + [f"2024-01-{d:02d},10,11,9,{10 + d / 10:.2f},{10 + d / 10:.2f},1000" for d in range(1, 32)]
    csv.write_text("\n".join(rows))
    prices.import_csv(str(csv), "test")
    h = prices.load_history("TEST")
    assert h.source.status == IMPORT and len(h.bars) == 31 and len(h.attempts) == 2


def test_an_unknown_symbol_is_not_retried_elsewhere(monkeypatch):
    def unknown(*_a, **_k):
        raise NotFoundError('Yahoo Finance has no data for "ZZZZ".')

    def never(*_a, **_k):
        raise AssertionError("should not be called")

    monkeypatch.setattr(yahoo, "history", unknown)
    monkeypatch.setattr(yf_provider, "history", never)
    monkeypatch.setattr(yahoo, "cached_history", never)
    with pytest.raises(NotFoundError, match="has no data"):
        prices.load_history("ZZZZ")


def test_parse_csv_accepts_broker_layouts():
    text = "Date,Close/Last,Volume,Open,High,Low\n" + "\n".join(f"01/{d:02d}/2024,$1{d:02d}.50,\"1,000\",$100,$101,$99" for d in range(31, 0, -1))
    h = prices.parse_csv(text, "TEST")
    assert h.bars.index.is_monotonic_increasing
    assert h.bars["close"].iloc[0] == 101.5 and h.bars["volume"].iloc[0] == 1000
    assert (h.bars["adjclose"] == h.bars["close"]).all()  # no adjusted column: closes are used


@pytest.mark.parametrize(
    "text,message",
    [
        ("a,b\n1,2", "Date column and a Close column"),
        ("Date,Close\n2024-01-01,10", "at least 30"),
        ("Date,Close\n" + "\n".join(f"2024-02-{d:02d},-5" for d in range(1, 29)), "at least 30"),  # negative prices are dropped
    ],
)
def test_parse_csv_explains_what_is_wrong(text, message):
    with pytest.raises(DataError, match=message):
        prices.parse_csv(text, "TEST")


def test_default_option_expiry_is_about_a_month_out():
    from datetime import date

    expiries = ["2026-10-21", "2026-10-23", "2026-11-20", "2026-12-18"]
    assert yf_provider.default_expiry(expiries, today=date(2026, 10, 20)) == "2026-11-20"
