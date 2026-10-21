"""Regression tests for SEC data defects found by live testing (BRK-B, SHOP, AMZN, KO, JPM, NVDA, GLD, IBIT, SPY, ARM).

Every payload is hand-built in the shape EDGAR serves; nothing here touches the network.
"""

import pandas as pd
import pytest

from finlit_pro.data import filings, http, sec
from finlit_pro.data.models import LIVE, DataError, Filing, Fundamentals


def dur(val, start, end, form="10-K", filed="2026-02-10", accn="k25"):
    return {"val": val, "start": start, "end": end, "form": form, "filed": filed, "accn": accn}


def inst(val, end, form="10-K", filed="2026-02-10", accn="k25"):
    return {"val": val, "end": end, "form": form, "filed": filed, "accn": accn}


def flows(values, q_ytd=None, q_prior=None):
    """Annual values for FY2024 and FY2025 and, optionally, the H1 2026 year to date with its prior-year comparative."""
    out = [dur(values[0], "2024-01-01", "2024-12-31", filed="2025-02-10", accn="k24"), dur(values[1], "2025-01-01", "2025-12-31")]
    if q_ytd is not None:
        out += [dur(q_ytd, "2026-01-01", "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226"),
                dur(q_prior, "2025-01-01", "2025-06-30", form="10-Q", filed="2026-08-05", accn="q226")]
    return {"USD": out}


def company(us_gaap=None, dei=None, quarter=True):
    """A company with two fiscal years, a Q2 10-Q and its balance sheets; extra tags are merged in."""
    gaap = {
        "Revenues": {"units": flows((1000, 1200), 650, 550) if quarter else flows((1000, 1200))},
        "NetIncomeLoss": {"units": flows((100, 120), 70, 60) if quarter else flows((100, 120))},
        "Assets": {"units": {"USD": [inst(2000, "2024-12-31", filed="2025-02-10", accn="k24"), inst(2200, "2025-12-31")]
                             + ([inst(2300, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")] if quarter else [])}},
    }
    gaap.update(us_gaap or {})
    return {"cik": 7, "entityName": "Test Co", "facts": {"us-gaap": gaap, "dei": dei or {}}}


def shares(*entries):
    return {"units": {"shares": list(entries)}}


# ------------------------------------------------------------------ share count


def test_stale_cover_count_falls_back_to_a_current_diluted_count():
    # SHOP: the only undimensioned count is 39.3M from a 2014 20-F; diluted weighted shares are 1.3B.
    facts = company(
        us_gaap={"WeightedAverageNumberOfDilutedSharesOutstanding": shares(
            dur(1_290_000_000, "2025-01-01", "2025-12-31"),
            dur(1_298_000_000, "2026-04-01", "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226"),
            dur(1_296_000_000, "2026-01-01", "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226"))},
        dei={"EntityCommonStockSharesOutstanding": shares(inst(39_310_446, "2014-12-31", form="20-F", filed="2016-02-17", accn="old"))},
    )
    ex = sec.extract(facts)
    assert ex.shares == 1_298_000_000  # the latest quarter, not the year to date or the 2014 count
    assert ex.shares_date == "2026-08-05"  # its filing date, which decides split restatement
    assert ex.ttm_refs["shares_outstanding"].accession == "q226"
    assert any("2014-12-31" in n and "diluted weighted-average" in n for n in ex.notes)


def test_no_current_share_count_leaves_shares_empty_with_a_note():
    # BRK: the newest count is from 2011 and no diluted count is tagged at all.
    facts = company(dei={"EntityCommonStockSharesOutstanding": shares(inst(941_481, "2011-04-29", form="10-Q", filed="2011-05-06", accn="old"))})
    ex = sec.extract(facts)
    assert ex.shares is None and ex.shares_date is None and "shares_outstanding" not in ex.ttm_refs
    assert any(n.startswith("Shares outstanding are n/a") and "2011-04-29" in n for n in ex.notes)


def test_a_current_balance_sheet_count_beats_a_stale_cover_count():
    facts = company(
        us_gaap={"CommonStockSharesOutstanding": shares(inst(500, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226"))},
        dei={"EntityCommonStockSharesOutstanding": shares(inst(10, "2012-01-31", filed="2012-02-10", accn="old"))},
    )
    ex = sec.extract(facts)
    assert ex.shares == 500 and ex.shares_date == "2026-06-30"
    assert not any("Shares outstanding" in n for n in ex.notes)


def test_a_current_cover_count_is_used_as_before():
    facts = company(dei={"EntityCommonStockSharesOutstanding": shares(inst(700, "2026-07-20", form="10-Q", filed="2026-08-05", accn="q226"))})
    ex = sec.extract(facts)
    assert ex.shares == 700 and ex.shares_date == "2026-07-20"
    assert not any("Shares outstanding" in n for n in ex.notes)


def _fund(shares_outstanding, shares_date, latest_period="2026-06-30"):
    table = pd.DataFrame({"eps_diluted": [1.0]}, index=pd.to_datetime(["2025-12-31"]))
    return Fundamentals(1, "Split Co", table, {}, {}, latest_period, shares_outstanding, shares_date=shares_date)


def test_a_stale_share_count_is_never_split_restated():
    f = _fund(39_310_446, "2014-12-31")
    sec.apply_splits(f, pd.Series({pd.Timestamp("2022-06-29"): 10.0}))
    assert f.shares_outstanding == 39_310_446  # First Version made this 393M
    current = _fund(1000, "2026-05-01")
    sec.apply_splits(current, pd.Series({pd.Timestamp("2026-07-01"): 2.0}))
    assert current.shares_outstanding == 2000  # a current pre-split count is still restated


# ------------------------------------------------------------------------ TTM


def test_ttm_from_a_tag_the_company_stopped_using_is_dropped():
    # AMZN tagged GrossProfit until FY2009; BRK tagged OperatingIncomeLoss in 10-Qs until 2013.
    facts = company(us_gaap={
        "GrossProfit": {"units": {"USD": [dur(5531, "2009-01-01", "2009-12-31", filed="2010-01-29", accn="k09")]}},
        "OperatingIncomeLoss": {"units": {"USD": [dur(80, "2012-01-01", "2012-12-31", filed="2013-02-25", accn="k12"),
                                                  dur(21, "2013-01-01", "2013-03-31", form="10-Q", filed="2013-05-03", accn="q13"),
                                                  dur(19, "2012-01-01", "2012-03-31", form="10-Q", filed="2013-05-03", accn="q13")]}},
    })
    ex = sec.extract(facts)
    assert "operating_income" not in ex.ttm and "operating_income" not in ex.ttm_refs
    assert "gross_profit" not in ex.ttm  # nothing current, and no cost of revenue to derive it from
    assert ex.ttm["revenue"] == 1200 + 650 - 550


def test_gross_profit_is_derived_from_revenue_and_cost_of_revenue():
    facts = company(us_gaap={
        "GrossProfit": {"units": {"USD": [dur(5531, "2009-01-01", "2009-12-31", filed="2010-01-29", accn="k09")]}},
        "CostOfGoodsAndServicesSold": {"units": flows((500, 590), 320, 270)},
    })
    ex = sec.extract(facts)
    ttm_rev, ttm_cost = 1200 + 650 - 550, 590 + 320 - 270
    assert ex.ttm["gross_profit"] == ttm_rev - ttm_cost  # about 50%, not 5531 / 1300
    assert "gross_profit" not in ex.ttm_refs  # derived, so no single filing to cite
    assert ex.table["gross_profit"].tolist() == [500, 610]
    assert any("Gross profit is derived" in n for n in ex.notes)


def test_year_to_date_must_start_right_after_the_tags_last_fiscal_year():
    # Annual figures stop at FY2023 but the tag reappears in 2026 10-Qs: never FY2023 + 2026 YTD - 2025 YTD.
    entries = [dur(40, "2023-01-01", "2023-12-31", filed="2024-02-10", accn="k23"),
               dur(30, "2026-01-01", "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226"),
               dur(25, "2025-01-01", "2025-06-30", form="10-Q", filed="2026-08-05", accn="q226")]
    value, end, _ = sec._ttm(entries)
    assert (value, str(end)) == (40, "2023-12-31")
    assert "interest_expense" not in sec.extract(company(us_gaap={"InterestExpense": {"units": {"USD": entries}}})).ttm


def test_ttm_uses_the_restated_prior_year_comparative():
    entries = flows((100, 120))["USD"] + [
        dur(50, "2025-01-01", "2025-06-30", form="10-Q", filed="2025-08-05", accn="q225"),  # as first reported
        dur(70, "2026-01-01", "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226"),
        dur(60, "2025-01-01", "2025-06-30", form="10-Q", filed="2026-08-05", accn="q226"),  # restated comparative
    ]
    assert sec._ttm(entries)[0] == 120 + 70 - 60


def test_note_when_ttm_is_just_the_last_fiscal_year():
    ex = sec.extract(company(quarter=False))
    assert ex.ttm["revenue"] == 1200
    assert any(n.startswith(sec.TTM_IS_FISCAL_YEAR) and "2025-12-31" in n for n in ex.notes)
    assert not any(n.startswith(sec.TTM_IS_FISCAL_YEAR) for n in sec.extract(company()).notes)


# ----------------------------------------------------------------------- debt


def test_total_debt_is_nan_without_any_debt_tag():
    assert pd.isna(sec.total_debt({}))
    assert pd.isna(sec.total_debt({"debt_long_total": float("nan"), "cash": 5}))
    ex = sec.extract(company())
    assert pd.isna(ex.latest["total_debt"]) and ex.table["total_debt"].isna().all()
    assert any(n.startswith("Total debt is n/a") for n in ex.notes)


def test_jpm_long_term_debt_tag_is_counted_once():
    facts = company(us_gaap={
        "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities": {"units": {"USD": [inst(460_523, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}},
        "ShortTermBorrowings": {"units": {"USD": [inst(72_430, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}},
        "LongTermDebtAndCapitalLeaseObligationsCurrent": {"units": {"USD": [inst(40_000, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}},
    })
    ex = sec.extract(facts)
    assert ex.latest["total_debt"] == 460_523 + 72_430  # the current portion is already inside the total
    assert not any(n.startswith("Total debt is n/a") for n in ex.notes)


def test_noncurrent_lease_inclusive_debt_pairs_with_its_current_portion():
    # KO: LongTermDebtAndCapitalLeaseObligations (non-current) + ...Current + commercial paper.
    q = {"form": "10-Q", "filed": "2026-08-05", "accn": "q226"}
    facts = company(us_gaap={
        "LongTermDebtAndCapitalLeaseObligations": {"units": {"USD": [inst(39_065, "2026-06-30", **q)]}},
        "LongTermDebtAndCapitalLeaseObligationsCurrent": {"units": {"USD": [inst(4_493, "2026-06-30", **q)]}},
        "CommercialPaper": {"units": {"USD": [inst(250, "2026-06-30", **q)]}},
    })
    assert sec.extract(facts).latest["total_debt"] == 39_065 + 4_493 + 250


# ---------------------------------------------------------------- liabilities


def test_total_liabilities_derived_when_not_tagged():
    # KO: no Liabilities tag; L&E 104,217 and equity including NCI 35,734.
    q = {"form": "10-Q", "filed": "2026-08-05", "accn": "q226"}
    facts = company(us_gaap={
        "LiabilitiesAndStockholdersEquity": {"units": {"USD": [inst(2200, "2025-12-31"), inst(2300, "2026-06-30", **q)]}},
        "StockholdersEquity": {"units": {"USD": [inst(800, "2025-12-31"), inst(900, "2026-06-30", **q)]}},
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest": {"units": {"USD": [inst(850, "2026-06-30", **q)]}},
        "MinorityInterest": {"units": {"USD": [inst(40, "2025-12-31")]}},
    })
    ex = sec.extract(facts)
    assert ex.latest["total_liabilities"] == 2300 - 850  # total equity including NCI
    assert ex.table.loc["2025-12-31", "total_liabilities"] == 2200 - (800 + 40)  # parent equity + NCI
    assert pd.isna(ex.table.loc["2024-12-31", "total_liabilities"])  # no equity tagged: not guessed
    assert any(n.startswith("Total liabilities (2025-12-31, 2026-06-30) are derived") for n in ex.notes)


def test_total_liabilities_from_assets_when_the_total_line_is_missing_too():
    # AMZN: no NCI at all, and no Liabilities tag.
    facts = company(us_gaap={"StockholdersEquity": {"units": {"USD": [inst(900, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}}})
    assert sec.extract(facts).latest["total_liabilities"] == 2300 - 900


def test_tagged_liabilities_are_left_alone():
    facts = company(us_gaap={
        "Liabilities": {"units": {"USD": [inst(1000, "2025-12-31"), inst(1100, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}},
        "LiabilitiesAndStockholdersEquity": {"units": {"USD": [inst(2300, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}},
        "StockholdersEquity": {"units": {"USD": [inst(1, "2026-06-30", form="10-Q", filed="2026-08-05", accn="q226")]}},
    })
    ex = sec.extract(facts)
    assert ex.latest["total_liabilities"] == 1100
    assert not any(n.startswith("Total liabilities") for n in ex.notes)


# --------------------------------------------------- fundamentals(): index, funds


def columns(rows):
    """Filing rows (form, filed, accession) as the parallel lists EDGAR uses."""
    return {"form": [r[0] for r in rows], "filingDate": [r[1] for r in rows], "accessionNumber": [r[2] for r in rows],
            "reportDate": ["" for _ in rows], "primaryDocument": ["doc.htm" for _ in rows], "primaryDocDescription": ["" for _ in rows]}


def submissions(rows, sic="7372", name="TEST CO", files=None, entity="operating"):
    return {"cik": "7", "name": name, "sic": sic, "sicDescription": "Software", "entityType": entity, "fiscalYearEnd": "1231",
            "exchanges": ["NYSE"], "filings": {"recent": columns(rows), "files": files or []}}


def fake_edgar(monkeypatch, subs, facts=None, older=None, title="Test Co"):
    calls = []

    def get_json(url, **kwargs):
        calls.append(url)
        if url == sec.TICKERS_URL:
            value = {"0": {"cik_str": 7, "ticker": "TEST", "title": title}}
        elif url == sec.SUBMISSIONS_URL.format(cik=7):
            value = subs
        elif url.startswith("https://data.sec.gov/submissions/") and older is not None:
            value = older
        elif url == sec.FACTS_URL.format(cik=7):
            if facts is None:
                raise DataError(kwargs["not_found_message"])  # what http.get_json does on a 404
            value = facts
        else:
            raise AssertionError(f"unexpected request {url}")
        return http.Fetched(value, LIVE, 1_760_000_000, url)

    monkeypatch.setattr(sec, "get_json", get_json)
    return calls


def test_every_recent_filing_is_parsed(monkeypatch):
    # JPM: hundreds of 424B2s a week pushed its 10-K and 10-Q past the first 300 entries.
    rows = [("424B2", "2026-10-20", f"0000000007-26-{i:06d}") for i in range(900)]
    rows += [("10-Q", "2026-08-06", "0000000007-26-q00002"), ("10-K", "2026-02-13", "0000000007-26-k00001")]
    fake_edgar(monkeypatch, submissions(rows), company())
    f = sec.fundamentals("TEST", "me@example.com")
    assert len(f.filings) == 902
    assert f.latest_filing("10-K").filed == "2026-02-13" and f.latest_filing("10-Q").filed == "2026-08-06"


def test_older_index_page_is_read_when_no_periodic_report_is_recent(monkeypatch):
    rows = [("424B2", "2026-10-20", f"0000000007-26-{i:06d}") for i in range(5)]
    older = columns([("10-Q", "2026-08-06", "0000000007-26-q00002"), ("10-K", "2026-02-13", "0000000007-26-k00001")])
    files = [{"name": "CIK0000000007-submissions-001.json", "filingCount": 2, "filingFrom": "2026-01-01", "filingTo": "2026-09-01"}]
    calls = fake_edgar(monkeypatch, submissions(rows, files=files), company(), older=older)
    f = sec.fundamentals("TEST", "me@example.com")
    assert "https://data.sec.gov/submissions/CIK0000000007-submissions-001.json" in calls
    assert [x.form for x in f.filings] == ["424B2"] * 5 + ["10-Q", "10-K"]
    # With a periodic report on the first page, no extra request is made.
    calls = fake_edgar(monkeypatch, submissions(rows + [("10-K", "2026-02-13", "0000000007-26-k00001")], files=files), company(), older=older)
    sec.fundamentals("TEST", "me@example.com")
    assert not any("submissions-001" in c for c in calls)


def test_note_when_companyfacts_lags_the_filing_index(monkeypatch):
    # KO: the 10-Q filed 2026-07-29 is in the index but none of its facts are published yet.
    facts = company()
    rows = [("10-Q", "2026-10-29", "0000000007-26-q00003"), ("10-Q", "2026-08-05", "q226"), ("10-K", "2026-02-10", "k25")]
    fake_edgar(monkeypatch, submissions(rows), facts)
    f = sec.fundamentals("TEST", "me@example.com")
    assert f.notes[0] == "SEC has not yet published XBRL data for the 10-Q filed 2026-10-29; figures are as of 2026-06-30."
    fake_edgar(monkeypatch, submissions(rows[1:]), facts)
    assert not any("not yet published" in n for n in sec.fundamentals("TEST", "me@example.com").notes)


@pytest.mark.parametrize(
    "subs,title",
    [
        (submissions([("10-K", "2025-11-20", "k1")], sic="6221", name="SPDR GOLD TRUST"), "SPDR GOLD TRUST"),  # GLD
        (submissions([("10-Q", "2026-08-05", "q1")], sic="6221", name="iShares Bitcoin Trust ETF"), "iShares Bitcoin Trust ETF"),  # IBIT
        (submissions([("NPORT-P", "2026-08-05", "n1"), ("N-30D", "2026-05-05", "n2")], sic="", name="SPDR S&P 500 ETF TRUST", entity="other"), "SPDR S&P 500 ETF TRUST"),  # SPY
        (submissions([("NPORT-P", "2026-08-05", "n1"), ("485BPOS", "2026-05-05", "n2")], sic="", name="SOME INDEX TRUST", entity="other"), "SOME INDEX TRUST"),
    ],
)
def test_funds_and_trusts_are_refused_before_company_facts(monkeypatch, subs, title):
    calls = fake_edgar(monkeypatch, subs, company(), title=title)
    with pytest.raises(DataError) as err:
        sec.fundamentals("TEST", "me@example.com")
    assert str(err.value) == sec.not_a_company("ETF", subs["name"])
    assert sec.FACTS_URL.format(cik=7) not in calls  # refused without downloading the statements


def test_an_operating_company_with_trust_in_its_name_is_not_refused(monkeypatch):
    fake_edgar(monkeypatch, submissions([("10-K", "2026-02-10", "k25")], sic="6022", name="NORTHERN TRUST CORP"), company())
    assert sec.fundamentals("TEST", "me@example.com").name == "NORTHERN TRUST CORP"


def test_companyfacts_404_message_names_funds_and_what_still_works(monkeypatch):
    fake_edgar(monkeypatch, submissions([("8-K", "2026-08-05", "e1")], sic="", name="NEW LISTING INC"), facts=None, title="New Listing Inc")
    with pytest.raises(DataError) as err:
        sec.fundamentals("TEST", "me@example.com")
    assert str(err.value) == ("New Listing Inc has no XBRL financial statements on EDGAR (ETFs, funds and trusts usually do not). "
                              "Price, model, Monte Carlo and options views still work.")


def test_foreign_issuer_on_6k_gets_one_explanatory_note(monkeypatch):
    # ARM: annual 20-F, quarters on 6-K, so TTM is the fiscal year.
    rows = [("6-K", "2026-07-29", "s1"), ("20-F", "2026-05-26", "k25")]
    fake_edgar(monkeypatch, submissions(rows, name="ARM HOLDINGS PLC /UK"), company(quarter=False))
    f = sec.fundamentals("TEST", "me@example.com")
    assert not any(n.startswith(sec.TTM_IS_FISCAL_YEAR) for n in f.notes)
    assert any(n.startswith("ARM HOLDINGS PLC /UK reports quarters on Form 6-K") for n in f.notes)


# ---------------------------------------------------------------------- email


@pytest.mark.parametrize("email", ["not-an-email", "test@example", "a b@example.com"])
def test_invalid_sec_email_is_a_data_error_that_says_where_to_fix_it(email):
    with pytest.raises(DataError) as err:
        sec.fundamentals("AAPL", email)
    assert f'SEC contact email "{email}"' in str(err.value) and "Settings > Data" in str(err.value)


def test_blank_sec_email_asks_for_one():
    with pytest.raises(DataError, match="requires a contact email.*Settings > Data"):
        sec.fundamentals("AAPL", "   ")


def test_invalid_email_while_reading_filings_becomes_a_note():
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[Filing("10-K", "2026-02-01", "2025-12-31", "10-K", "https://www.sec.gov/x.htm", "a1")])
    texts, problems = filings.latest_reports(fund, "bad-email")
    assert texts == [] and "Settings > Data" in problems[0]


# ------------------------------------------------------------- filing sections

FILLER = "The company sells widgets around the world and reports in dollars. "
REAL_BUSINESS = "ITEM 1. BUSINESS\n\n" + FILLER * 30
REAL_RISKS = "ITEM 1A. RISK FACTORS\n\n" + "Demand may fall. " * 150
REAL_MDA = "ITEM 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS\n\n" + "Revenue rose. " * 120

# Shaped like KO's and NVDA's 10-Ks: a contents page, the real headings at line starts, and cross-references
# in sentences, some of them with no end heading after them.
KO_LIKE = "\n\n".join([
    "Part I", "Item 1.", "Business", "2", "Item 1A.", "Risk Factors", "12", "Item 1B.", "Unresolved Staff Comments", "26",
    "Item 7.", "Management’s Discussion and Analysis of Financial Condition and Results of Operations", "35",
    "Item 7A.", "Quantitative and Qualitative Disclosures About Market Risk", "58",
    "Forward-looking risks are described in Part I, “Item 1A. Risk Factors” and elsewhere in this report.",
    "PART I",
    REAL_BUSINESS,
    REAL_RISKS + " Our ability to compete is described in Part I, “Item 1. Business” of this report. " + "More risk. " * 50,
    "ITEM 1B. UNRESOLVED STAFF COMMENTS\n\nNot applicable.",
    REAL_MDA + " See “Item 1A. Risk Factors” in Part I of this report for more. " + "Cash grew. " * 60,
    "This should be read in conjunction with “Item 1A. Risk Factors,” our financial statements and notes.",
    "ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK\n\nRates.",
    "ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA\n\nTables.",
    "Refer to Item 1A. Risk Factors for additional information. " + "Note text. " * 2000,
])


@pytest.mark.parametrize("name,heading", [("Business", "ITEM 1. BUSINESS"), ("Risk Factors", "ITEM 1A. RISK FACTORS"), ("MD&A", "ITEM 7. MANAGEMENT")])
def test_sections_start_at_the_real_heading_not_a_cross_reference(name, heading):
    spec = {n: (s, e) for n, s, e in filings.SECTIONS["10-K"]}
    body = filings.extract_section(KO_LIKE, *spec[name])
    assert body.startswith(heading)
    assert "Note text." not in body and "Tables." not in body  # never runs on to the end of the document
    assert len(body) < 4000


def test_heading_followed_by_a_closing_quote_on_its_own_line_is_a_cross_reference():
    # NVDA: '...read in conjunction with "' then a line starting 'Item 1A. Risk Factors," our ...'
    text = "\n".join(["Item 1A. Risk Factors", "Risks. " * 100, "Item 1B. Unresolved Staff Comments", "None.",
                      "read in conjunction with “", "Item 1A. Risk Factors,” our statements. " + "Filler. " * 3000])
    spec = {n: (s, e) for n, s, e in filings.SECTIONS["10-K"]}
    body = filings.extract_section(text, *spec["Risk Factors"])
    assert body.startswith("Item 1A. Risk Factors\nRisks.") and "Filler." not in body


def test_table_of_contents_is_never_returned_as_a_section():
    # JPM's 10-Q names "Item 2" only in its contents; the MD&A in the body has no item number.
    toc = "\n\n".join(["Item 2.", "Management’s Discussion and Analysis of Financial Condition and Results of Operations."]
                      + [x for i in range(20) for x in (f"Subsection {i}", str(3 + i * 4))] + ["Item 3.", "Quantitative and Qualitative Disclosures", "201"])
    text = toc + "\n\nManagement’s discussion and analysis\n\n" + "Text. " * 500
    spec = {n: (s, e) for n, s, e in filings.SECTIONS["10-Q"]}
    assert filings.extract_section(text, *spec["MD&A"]) == ""


def test_old_rule_still_applies_when_no_heading_starts_a_line():
    text = "Contents. PART I Item 1. Business " + FILLER * 20 + " PART I Item 1A. Risk Factors " + "Risks. " * 50
    spec = {n: (s, e) for n, s, e in filings.SECTIONS["10-K"]}
    body = filings.extract_section(text, *spec["Business"])
    assert body.startswith("Item 1. Business") and "Risks." not in body and len(body) > 500


# --------------------------------------------------------------- latest_reports


def ft_with(filing, sections):
    from finlit_pro.data.models import Source

    return filings.FilingText(filing, dict(sections), {k: False for k in sections}, {k: len(v) for k, v in sections.items()}, Source("x", filing.url, pd.Timestamp("2026-01-01").to_pydatetime()), [])


def filing(form, filed):
    return Filing(form, filed, "2025-12-31", form, f"https://www.sec.gov/{form}-{filed}.htm", f"{form}-{filed}")


def test_part_iii_amendment_falls_back_to_the_original_10k(monkeypatch):
    # SHOP: a 10-K/A filed 2026-04-29 adds only Part III.
    read = []
    monkeypatch.setattr(filings, "read", lambda f, email, limit: read.append(f.form) or ft_with(f, {} if f.form == "10-K/A" else {"Business": "x" * 600}))
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[filing("10-K/A", "2026-04-29"), filing("10-K", "2026-02-11")])
    texts, problems = filings.latest_reports(fund, "me@example.com")
    assert read == ["10-K/A", "10-K"] and problems == []
    assert texts[0].filing.form == "10-K" and "Business" in texts[0].sections
    assert texts[0].notes[0].startswith("The 10-K/A filed 2026-04-29 does not contain these sections")


def test_a_full_amendment_with_the_sections_is_used(monkeypatch):
    monkeypatch.setattr(filings, "read", lambda f, email, limit: ft_with(f, {"Business": "x" * 600}))
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[filing("10-K/A", "2026-04-29"), filing("10-K", "2026-02-11")])
    texts, _ = filings.latest_reports(fund, "me@example.com")
    assert [t.filing.form for t in texts] == ["10-K/A"] and texts[0].notes == []


def test_an_older_amendment_is_ignored(monkeypatch):
    read = []
    monkeypatch.setattr(filings, "read", lambda f, email, limit: read.append(f.form) or ft_with(f, {"Business": "x" * 600}))
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[filing("10-K", "2026-02-11"), filing("10-K/A", "2025-04-29")])
    filings.latest_reports(fund, "me@example.com")
    assert read == ["10-K"]


@pytest.mark.parametrize("forms,expected", [
    (["6-K", "20-F"], "ARM Holdings files annual reports on Form 20-F; FinLit Pro reads 10-K and 10-Q text only."),
    (["40-F"], "ARM Holdings files annual reports on Form 40-F; FinLit Pro reads 10-K and 10-Q text only."),
    (["6-K"], "ARM Holdings files reports on Form 6-K; FinLit Pro reads 10-K and 10-Q text only."),
    (["8-K"], "No 10-K or 10-Q in the company's recent filings."),
])
def test_foreign_annual_forms_are_named(forms, expected):
    fund = Fundamentals(1, "ARM Holdings", None, {}, {}, None, None, filings=[filing(f, "2026-05-26") for f in forms])
    assert filings.latest_reports(fund, "me@example.com") == ([], [expected])
