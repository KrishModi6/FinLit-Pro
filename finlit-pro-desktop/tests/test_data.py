"""Data layer tests against hand-built payloads in the providers' documented shapes.

No test here touches the network: sessions are replaced by fakes.
"""

import pandas as pd
import pytest
import requests

from finlit_pro.data import demo, http, sec, yahoo
from finlit_pro.data.models import CACHE, DEMO, LIVE, STALE, DataError, FactRef

# ---------------------------------------------------------------- Yahoo chart

T0 = 1709559000  # 2024-03-04 13:30 UTC = 09:30 New York


def chart_payload():
    day = 86400
    return {
        "chart": {
            "result": [
                {
                    "meta": {"symbol": "TEST", "longName": "Test Inc", "currency": "USD", "regularMarketPrice": 12.5, "gmtoffset": -18000, "fullExchangeName": "NasdaqGS", "instrumentType": "EQUITY"},
                    "timestamp": [T0, T0 + day, T0 + 2 * day, T0 + 3 * day],
                    "events": {"dividends": {str(T0 + day): {"amount": 0.2, "date": T0 + day}}},
                    "indicators": {
                        "quote": [{"open": [10, None, 11, 12], "high": [10.5, None, 11.5, None], "low": [9.5, None, 10.5, 11.5], "close": [10, None, 11, 12], "volume": [100, None, 300, None]}],
                        "adjclose": [{"adjclose": [9.5, None, 10.6, 12]}],
                    },
                }
            ],
            "error": None,
        }
    }


def test_parse_chart_drops_null_bars_and_fills_partial_ones():
    h = yahoo.parse_chart(chart_payload(), "TEST")
    assert list(h.bars.index.strftime("%Y-%m-%d")) == ["2024-03-04", "2024-03-06", "2024-03-07"]
    assert h.price == 12.5
    assert h.previous_close == 11  # the previous daily bar, not the close before the range
    last = h.bars.iloc[-1]
    assert last["high"] == 12 and last["volume"] == 0  # missing high falls back to the close
    assert h.closes.iloc[0] == 9.5  # adjusted closes for returns
    assert h.dividends.iloc[0] == 0.2
    assert h.exchange == "NasdaqGS" and h.name == "Test Inc"
    # Provenance: provider, a link to the quote page, the date of the last bar.
    assert h.source.name == "Yahoo Finance chart API (TEST)"
    assert h.source.url == "https://finance.yahoo.com/quote/TEST"
    assert h.source.as_of == "2024-03-07" and h.source.status == LIVE


def test_parse_chart_reads_split_ratios():
    payload = chart_payload()
    payload["chart"]["result"][0]["events"]["splits"] = {"1": {"date": T0 + 86400, "numerator": 4.0, "denominator": 1.0, "splitRatio": "4:1"}}
    h = yahoo.parse_chart(payload, "TEST")
    assert list(h.splits.values) == [4.0]
    assert h.splits.index[0].strftime("%Y-%m-%d") == "2024-03-05"


def test_parse_chart_error_envelope_is_friendly():
    payload = {"chart": {"result": None, "error": {"code": "Not Found", "description": "No data found, symbol may be delisted"}}}
    with pytest.raises(DataError, match="Check the ticker"):
        yahoo.parse_chart(payload, "ZZZZ")


def test_demo_tickers_never_touch_the_network(monkeypatch):
    from finlit_pro.data import prices

    monkeypatch.setattr(http, "_session", lambda: (_ for _ in ()).throw(AssertionError("network used")))
    h = prices.load_history("demo")
    assert h.source.status == DEMO and "Simulated" in h.source.name and len(h.bars) > 2000
    f = sec.fundamentals("DEMO", "")
    assert f.status == DEMO and "simulated" in f.name.lower() and len(f.annual) == 10


def test_demo_is_reproducible():
    a, b = demo.history("DEMO"), demo.history("DEMO")
    assert a.bars.equals(b.bars)


# ------------------------------------------------------------- HTTP + cache


class FakeResponse:
    def __init__(self, status=200, payload=None, text=""):
        self.status_code = status
        self._payload = payload
        self.text = text
        self.encoding = "utf-8"

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeSession:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.calls = 0

    def get(self, url, headers=None, timeout=None):
        self.calls += 1
        result = self.behaviour(self.calls)
        if isinstance(result, Exception):
            raise result
        return result


def test_get_json_caches_then_falls_back_to_stale_copy(monkeypatch):
    session = FakeSession(lambda n: FakeResponse(200, {"n": n}) if n == 1 else requests.exceptions.ConnectionError())
    monkeypatch.setattr(http, "_session", lambda: session)
    first = http.get_json("https://example.test/a", ttl_s=60)
    assert first.status == LIVE and first.value == {"n": 1} and first.url == "https://example.test/a"
    assert http.get_json("https://example.test/a", ttl_s=60).status == CACHE
    stale = http.get_json("https://example.test/a", ttl_s=0)
    assert stale.status == STALE and stale.value == {"n": 1}
    with pytest.raises(DataError, match="Could not reach"):
        http.get_json("https://example.test/a", ttl_s=0, allow_stale=False)


def test_get_json_without_cache_raises_actionable_errors(monkeypatch):
    monkeypatch.setattr(http, "_session", lambda: FakeSession(lambda n: requests.exceptions.Timeout()))
    with pytest.raises(DataError, match="took too long"):
        http.get_json("https://example.test/slow", service="Yahoo Finance")
    monkeypatch.setattr(http, "_session", lambda: FakeSession(lambda n: requests.exceptions.RetryError()))
    with pytest.raises(DataError, match="rate limiting"):
        http.get_json("https://example.test/busy", service="Yahoo Finance")
    monkeypatch.setattr(http, "_session", lambda: FakeSession(lambda n: FakeResponse(404)))
    with pytest.raises(DataError, match="does not recognise"):
        http.get_json("https://example.test/missing", not_found_message="Yahoo Finance does not recognise it")
    monkeypatch.setattr(http, "_session", lambda: FakeSession(lambda n: FakeResponse(403)))
    with pytest.raises(DataError, match="contact email"):
        http.get_json("https://data.sec.gov/forbidden", service="SEC EDGAR")
    monkeypatch.setattr(http, "_session", lambda: FakeSession(lambda n: FakeResponse(200, None)))
    with pytest.raises(DataError, match="could not be read"):
        http.get_json("https://example.test/html")


def test_a_not_found_answer_is_never_hidden_by_a_stale_copy(monkeypatch):
    session = FakeSession(lambda n: FakeResponse(200, {"ok": 1}) if n == 1 else FakeResponse(404))
    monkeypatch.setattr(http, "_session", lambda: session)
    http.get_json("https://example.test/gone", ttl_s=0, not_found_message="gone")
    with pytest.raises(DataError, match="gone"):
        http.get_json("https://example.test/gone", ttl_s=0, not_found_message="gone")


def test_get_text_caches_documents(monkeypatch):
    session = FakeSession(lambda n: FakeResponse(200, text="<html>filing</html>"))
    monkeypatch.setattr(http, "_session", lambda: session)
    assert http.get_text("https://www.sec.gov/doc.htm").value == "<html>filing</html>"
    again = http.get_text("https://www.sec.gov/doc.htm")
    assert again.status == CACHE and session.calls == 1


def test_rate_limiter_spaces_requests(monkeypatch):
    clock = {"t": 100.0}
    sleeps = []
    monkeypatch.setattr(http.time, "monotonic", lambda: clock["t"])
    monkeypatch.setattr(http.time, "sleep", lambda s: sleeps.append(s))
    limiter = http.RateLimiter(5.0)
    for _ in range(3):
        limiter.wait()
    assert sleeps == pytest.approx([0.2, 0.4])  # the 2nd and 3rd calls wait their turn
    assert http.limiter_for("https://data.sec.gov/x").interval == pytest.approx(0.2)
    assert http.limiter_for("https://query1.finance.yahoo.com/x").interval == pytest.approx(0.5)
    assert http.limiter_for("https://example.com/") is None


# ----------------------------------------------------------- SEC extraction


def dur(val, start, end, form="10-K", filed="2021-02-01", accn="k"):
    return {"val": val, "start": start, "end": end, "form": form, "filed": filed, "accn": accn}


def inst(val, end, form="10-K", filed="2021-02-01", accn="k"):
    return {"val": val, "end": end, "form": form, "filed": filed, "accn": accn}


def year(y):
    return f"{y}-01-01", f"{y}-12-31"


def company_facts():
    rev_old = [
        dur(100, *year(2016), filed="2017-02-01"),
        dur(110, *year(2017), filed="2018-02-01"),
        # The 2018 10-K restates 2016 as a comparative: the later filing wins.
        dur(101, *year(2016), filed="2018-02-01"),
        # A quarterly figure inside a 10-K must not be mistaken for a year.
        dur(30, "2017-10-01", "2017-12-31", filed="2018-02-01"),
    ]
    rev_new = [dur(v, *year(y), filed=f"{y + 1}-02-01") for y, v in ((2018, 121), (2019, 133), (2020, 146))]
    rev_new += [
        dur(80, "2021-01-01", "2021-06-30", form="10-Q", filed="2021-08-01", accn="q2"),  # year to date
        dur(41, "2021-04-01", "2021-06-30", form="10-Q", filed="2021-08-01", accn="q2"),  # the quarter alone
        dur(70, "2020-01-01", "2020-06-30", form="10-Q", filed="2021-08-01", accn="q2"),  # last year's YTD
    ]
    ni = [dur(v, *year(y), filed=f"{y + 1}-02-01") for y, v in ((2016, 10), (2017, 11), (2018, 12), (2019, 13), (2020, 15))]
    ocf = [dur(v, *year(y), filed=f"{y + 1}-02-01") for y, v in ((2016, 14), (2017, 15), (2018, 16), (2019, 18), (2020, 20))]
    assets = [inst(v, f"{y}-12-31", filed=f"{y + 1}-02-01") for y, v in ((2016, 200), (2017, 210), (2018, 220), (2019, 230), (2020, 240))]
    assets.append(inst(250, "2021-06-30", form="10-Q", filed="2021-08-01", accn="q2"))
    # 10-Ks also carry older instants (equity roll-forwards); these must not add rows.
    assets.append(inst(190, "2014-12-31", filed="2016-02-01"))
    return {
        "cik": 1,
        "entityName": "Test Co",
        "facts": {
            "us-gaap": {
                "Revenues": {"units": {"USD": rev_old}},
                "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": rev_new}},
                "NetIncomeLoss": {"units": {"USD": ni}},
                "NetCashProvidedByUsedInOperatingActivities": {"units": {"USD": ocf}},
                "Assets": {"units": {"USD": assets}},
                "LongTermDebtNoncurrent": {"units": {"USD": [inst(50, "2020-12-31"), inst(48, "2021-06-30", form="10-Q", accn="q2")]}},
                "LongTermDebtCurrent": {"units": {"USD": [inst(5, "2020-12-31"), inst(6, "2021-06-30", form="10-Q", accn="q2")]}},
                "EarningsPerShareDiluted": {"units": {"USD/shares": [dur(1.5, *year(2020))]}},
            },
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {"shares": [inst(990, "2021-01-25", accn="k20"), inst(600, "2021-07-20", form="10-Q", accn="q2"), inst(400, "2021-07-20", form="10-Q", accn="q2")]}
                }
            },
        },
    }


def test_extract_merges_tags_prefers_restatements_and_rejects_quarters():
    table = sec.extract(company_facts()).table
    assert list(table.index.year) == [2016, 2017, 2018, 2019, 2020]
    assert list(table["revenue"]) == [101, 110, 121, 133, 146]
    assert table.loc["2020-12-31", "total_assets"] == 240
    assert table.loc["2020-12-31", "total_debt"] == 55


def test_extract_ttm_uses_year_to_date_arithmetic():
    ex = sec.extract(company_facts())
    assert ex.ttm["revenue"] == 146 + 80 - 70
    assert ex.ttm["net_income"] == 15  # no 10-Q data: falls back to the fiscal year
    assert ex.ttm_refs["revenue"].form == "10-Q"  # cited to the quarterly filing


def test_every_annual_value_names_its_filing():
    ex = sec.extract(company_facts())
    ref = ex.refs["revenue"][pd.Timestamp("2016-12-31")]
    assert isinstance(ref, FactRef)
    assert ref.filed == "2018-02-01"  # the restating filing, not the original
    assert ref.form == "10-K"


def test_extract_latest_balance_sheet_and_share_classes():
    ex = sec.extract(company_facts())
    assert ex.latest_period == "2021-06-30"
    assert ex.latest["total_assets"] == 250
    assert ex.latest["total_debt"] == 48 + 6
    assert ex.shares == 1000  # two share classes in the same filing are summed
    assert ex.shares_date == "2021-07-20"


@pytest.mark.parametrize(
    "row,expected",
    [
        ({"debt_long_total": 100, "short_borrowings": 10, "debt_current_portion": 20}, 110),
        ({"debt_noncurrent": 80, "debt_current_all": 30, "debt_current_portion": 20}, 110),
        ({"debt_noncurrent": 80, "debt_current_portion": 20, "short_borrowings": 5}, 105),
        ({}, 0),
    ],
)
def test_total_debt_never_double_counts(row, expected):
    assert sec.total_debt(row) == expected


def test_sec_requires_contact_email():
    with pytest.raises(DataError, match="contact email"):
        sec.fundamentals("AAPL", "")


def test_lookup_cik_and_filings(monkeypatch):
    tickers = {"0": {"cik_str": 1067983, "ticker": "BRK-B", "title": "Berkshire Hathaway Inc"}}
    monkeypatch.setattr(sec, "get_json", lambda *a, **k: http.Fetched(tickers, LIVE, 0, sec.TICKERS_URL))
    assert sec.lookup_cik("brk.b", "me@example.com") == (1067983, "Berkshire Hathaway Inc")
    with pytest.raises(DataError, match="ETFs"):
        sec.lookup_cik("SPY", "me@example.com")
    subs = {"filings": {"recent": {"form": ["10-K", "4"], "accessionNumber": ["0000950170-24-000001", "0000950170-24-000002"], "primaryDocument": ["brk.htm", ""], "filingDate": ["2024-02-26", "2024-02-27"], "reportDate": ["2023-12-31", ""], "primaryDocDescription": ["10-K", ""]}}}
    filings = sec.parse_filings(1067983, subs)
    assert filings[0].url == "https://www.sec.gov/Archives/edgar/data/1067983/000095017024000001/brk.htm"
    assert filings[0].accession == "0000950170-24-000001" and "000095017024000001" in filings[0].index_url
    assert filings[1].url == ""


def split_company():
    """Shaped like Apple around its 2020 4-for-1 split.

    FY2016 and FY2017 only appear in pre-split 10-Ks. FY2018 and FY2019 were
    repeated, restated, in the post-split FY2020 10-K.
    """
    eps, shares, ni = [], [], []
    for y, e, s, filed in ((2016, 8.31, 5500, "2016-10-26"), (2017, 9.21, 5252, "2017-11-03"), (2018, 2.98, 20000, "2020-10-30"), (2019, 2.97, 18596, "2020-10-30"), (2020, 3.28, 17528, "2020-10-30")):
        eps.append(dur(e, *year(y), filed=filed))
        shares.append(dur(s, *year(y), filed=filed))
        ni.append(dur(e * s, *year(y), filed=filed))
    # The pre-split FY2018 10-K also reported FY2018, at pre-split values.
    eps.append(dur(11.91, *year(2018), filed="2018-11-05"))
    shares.append(dur(5000, *year(2018), filed="2018-11-05"))
    return {
        "facts": {
            "us-gaap": {
                "EarningsPerShareDiluted": {"units": {"USD/shares": eps}},
                "WeightedAverageNumberOfDilutedSharesOutstanding": {"units": {"shares": shares}},
                "NetIncomeLoss": {"units": {"USD": ni}},
            },
            "dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": [inst(4400, "2020-07-17", form="10-Q", filed="2020-07-31")]}}},
        }
    }


def fund_from(ex):
    from finlit_pro.data.models import Fundamentals

    return Fundamentals(1, "Split Co", ex.table, ex.ttm, ex.latest, ex.latest_period, ex.shares, refs=ex.refs, shares_date=ex.shares_date)


def test_apply_splits_restates_only_pre_split_filings():
    f = fund_from(sec.extract(split_company()))
    assert list(f.annual["eps_diluted"]) == [8.31, 9.21, 2.98, 2.97, 3.28]
    notes = sec.apply_splits(f, pd.Series({pd.Timestamp("2020-08-31"): 4.0}))
    eps = f.annual["eps_diluted"].round(4).tolist()
    assert eps == [round(8.31 / 4, 4), round(9.21 / 4, 4), 2.98, 2.97, 3.28]
    assert f.annual["diluted_shares"].tolist() == [22000, 21008, 20000, 18596, 17528]
    assert f.shares_outstanding == 4400 * 4  # the cover count predates the split too
    assert notes and "4-for-1" in notes[0]
    # Idempotent: a second call must not divide again.
    sec.apply_splits(f, pd.Series({pd.Timestamp("2020-08-31"): 4.0}))
    assert f.annual["eps_diluted"].iloc[0] == pytest.approx(8.31 / 4)


def test_apply_splits_handles_two_splits_and_none():
    f = fund_from(sec.extract(split_company()))
    sec.apply_splits(f, pd.Series({pd.Timestamp("2017-06-01"): 2.0, pd.Timestamp("2020-08-31"): 4.0}))
    assert f.annual["eps_diluted"].iloc[0] == pytest.approx(8.31 / 8)  # filed before both
    assert f.annual["eps_diluted"].iloc[1] == pytest.approx(9.21 / 4)  # filed between them
    g = fund_from(sec.extract(split_company()))
    assert sec.apply_splits(g, pd.Series(dtype=float)) == []
    assert g.annual["eps_diluted"].iloc[0] == 8.31
