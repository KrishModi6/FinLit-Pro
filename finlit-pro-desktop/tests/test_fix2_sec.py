"""Regression tests for the second round of SEC fixes: the debt policy, convertible notes and other debt tags,
the year-ago balance sheet, share counts checked against the diluted count, and the notes and filing text found
wrong by live testing (ORCL, CAT, DASH, PINS, SHOP, HUBS, BRK, F, CME, GS, C, HEI, MCD, TEM, TSM, JPM).

Every payload is hand-built in the shape EDGAR serves; nothing here touches the network.
"""

import math

import pandas as pd
import pytest

from finlit_pro.data import filings, http, sec
from finlit_pro.data.models import LIVE, DataError, Filing, Fundamentals

Q = {"form": "10-Q", "filed": "2026-08-05", "accn": "q226"}


def dur(val, start, end, form="10-K", filed="2026-02-10", accn="k25"):
    return {"val": val, "start": start, "end": end, "form": form, "filed": filed, "accn": accn}


def inst(val, end, form="10-K", filed="2026-02-10", accn="k25"):
    return {"val": val, "end": end, "form": form, "filed": filed, "accn": accn}


def usd(*entries):
    return {"units": {"USD": list(entries)}}


def shares(*entries):
    return {"units": {"shares": list(entries)}}


def flows(values, q_ytd=None, q_prior=None):
    out = [dur(values[0], "2024-01-01", "2024-12-31", filed="2025-02-10", accn="k24"), dur(values[1], "2025-01-01", "2025-12-31")]
    if q_ytd is not None:
        out += [dur(q_ytd, "2026-01-01", "2026-06-30", **Q), dur(q_prior, "2025-01-01", "2025-06-30", **Q)]
    return {"USD": out}


def company(us_gaap=None, dei=None, quarter=True, assets=None):
    """Two fiscal years (FY2025 ends 2025-12-31), a Q2 10-Q (2026-06-30) and their balance sheets."""
    gaap = {
        "Revenues": {"units": flows((1000, 1200), 650, 550) if quarter else flows((1000, 1200))},
        "NetIncomeLoss": {"units": flows((100, 120), 70, 60) if quarter else flows((100, 120))},
        "Assets": usd(*(assets or [inst(2000, "2024-12-31", filed="2025-02-10", accn="k24"), inst(2200, "2025-12-31")]
                        + ([inst(2300, "2026-06-30", **Q)] if quarter else []))),
    }
    gaap.update(us_gaap or {})
    return {"cik": 7, "entityName": "Test Co", "facts": {"us-gaap": gaap, "dei": dei or {}}}


def debt_notes(ex):
    return [n for n in ex.notes if "debt" in n.lower()]


# ------------------------------------------------------------------- debt tags


def test_orcl_notes_payable_tags_are_counted():
    # ORCL's 10-K: LongTermNotesPayable $122,342M + DebtCurrent $7,199M; its 10-Q: LongTermNotesAndLoans + NotesPayableCurrent.
    facts = company(us_gaap={
        "LongTermNotesPayable": usd(inst(122_342, "2025-12-31")),
        "DebtCurrent": usd(inst(7_199, "2025-12-31")),
        "LongTermNotesAndLoans": usd(inst(117_712, "2026-06-30", **Q)),
        "NotesPayableCurrent": usd(inst(7_625, "2026-06-30", **Q)),
    })
    ex = sec.extract(facts)
    assert ex.table.loc["2025-12-31", "total_debt"] == 122_342 + 7_199  # equals its DebtLongtermAndShorttermCombinedAmount
    assert ex.latest["total_debt"] == 117_712 + 7_625 and ex.debt_status == "reported"
    assert debt_notes(ex) == []


def test_a_zero_comprehensive_total_does_not_hide_the_parts():
    # ORCL FY2022: LongTermDebt tagged 0 beside $72,110M of notes and $3,749M of current debt.
    facts = company(us_gaap={
        "LongTermDebt": usd(inst(0, "2025-12-31")),
        "LongTermNotesPayable": usd(inst(72_110, "2025-12-31")),
        "DebtCurrent": usd(inst(3_749, "2025-12-31")),
    }, quarter=False)
    assert sec.extract(facts).table.loc["2025-12-31", "total_debt"] == 72_110 + 3_749
    assert sec.total_debt({"debt_long_total": 0.0}) == 0.0  # a real zero with nothing else is still zero


@pytest.mark.parametrize("tag,value", [
    ("ConvertibleLongTermNotesPayable", 2_727),  # DASH
    ("ConvertibleDebtNoncurrent", 981),  # PINS
    ("LongTermLineOfCreditNoncurrent", 300),
    ("OtherLongTermDebtNoncurrent", 40),
])
def test_noncurrent_convertible_and_other_debt_tags_are_read(tag, value):
    ex = sec.extract(company(us_gaap={tag: usd(inst(value, "2026-06-30", **Q))}))
    assert ex.latest["total_debt"] == value and ex.debt_status == "reported" and debt_notes(ex) == []


@pytest.mark.parametrize("tag", ["ConvertibleNotesPayableCurrent", "ConvertibleDebtCurrent"])
def test_current_convertible_notes_pair_with_the_noncurrent_part(tag):
    facts = company(us_gaap={"LongTermDebtNoncurrent": usd(inst(500, "2026-06-30", **Q)), tag: usd(inst(80, "2026-06-30", **Q)),
                             "CommercialPaper": usd(inst(20, "2026-06-30", **Q))})
    assert sec.extract(facts).latest["total_debt"] == 500 + 80 + 20


def test_lines_of_credit_count_as_short_term_borrowings_once():
    facts = company(us_gaap={"LongTermDebtNoncurrent": usd(inst(500, "2026-06-30", **Q)), "LinesOfCreditCurrent": usd(inst(60, "2026-06-30", **Q))})
    assert sec.extract(facts).latest["total_debt"] == 560
    # ShortTermBorrowings comes first in its group, so a line of credit inside it is not added again.
    facts["facts"]["us-gaap"]["ShortTermBorrowings"] = usd(inst(90, "2026-06-30", **Q))
    assert sec.extract(facts).latest["total_debt"] == 590


def test_an_instrument_total_is_used_only_when_nothing_else_is_tagged():
    # CME: UnsecuredLongTermDebt is its only debt line.
    cme = company(us_gaap={"UnsecuredLongTermDebt": usd(inst(3_424, "2026-06-30", **Q))})
    assert sec.extract(cme).latest["total_debt"] == 3_424
    # Beside a balance-sheet total, an instrument from the notes is a part of it and is ignored.
    both = company(us_gaap={"LongTermDebtNoncurrent": usd(inst(9_000, "2026-06-30", **Q)), "LongTermDebtCurrent": usd(inst(1_000, "2026-06-30", **Q)),
                            "ConvertibleNotesPayable": usd(inst(500, "2026-06-30", **Q))})
    assert sec.extract(both).latest["total_debt"] == 10_000


def test_combined_debt_amount_is_a_last_resort():
    # GS tags only DebtLongtermAndShorttermCombinedAmount; WMT's leaves out short-term borrowings, so parts win there.
    gs = company(us_gaap={"DebtLongtermAndShorttermCombinedAmount": usd(inst(437_874, "2026-06-30", **Q)),
                          "UnsecuredLongTermDebt": usd(inst(347_963, "2026-06-30", **Q))})
    assert sec.extract(gs).latest["total_debt"] == 437_874
    wmt = company(us_gaap={"DebtLongtermAndShorttermCombinedAmount": usd(inst(39_930, "2026-06-30", **Q)),
                           "LongTermDebtNoncurrent": usd(inst(35_000, "2026-06-30", **Q)), "DebtCurrent": usd(inst(15_410, "2026-06-30", **Q))})
    assert sec.extract(wmt).latest["total_debt"] == 50_410


def test_finance_leases_are_not_debt():
    facts = company(us_gaap={"LongTermDebtNoncurrent": usd(inst(500, "2026-06-30", **Q)), "FinanceLeaseLiabilityNoncurrent": usd(inst(90, "2026-06-30", **Q))})
    assert sec.extract(facts).latest["total_debt"] == 500


# -------------------------------------------------------------- debt policy


def test_no_debt_figure_of_any_kind_means_zero_with_one_note():
    # PLTR, TTD, DOCU, ROKU: no debt tag, disclosure or proceeds. Interest expense alone (credit-line fees) does not count.
    ex = sec.extract(company(us_gaap={"InterestExpenseNonoperating": usd(dur(1.1, "2026-01-01", "2026-06-30", **Q))}))
    assert ex.debt_status == "none" and ex.latest["total_debt"] == 0.0
    assert debt_notes(ex) == [sec.NO_DEBT_NOTE]


def test_debt_reported_as_repaid_is_not_current_debt():
    # SHOP: convertible notes of $920M at 2025-09-30, tagged 0 at 2025-12-31 after they were settled.
    shop = company(us_gaap={"ConvertibleDebtCurrent": usd(inst(920, "2025-09-30", form="10-Q", filed="2025-11-04", accn="q325"), inst(0, "2025-12-31"))})
    ex = sec.extract(shop)
    assert ex.debt_status == "none" and ex.latest["total_debt"] == 0.0
    # HUBS: notes last tagged at 2025-03-31; the FY2025 balance sheet no longer shows them.
    hubs = company(us_gaap={"ConvertibleNotesPayableCurrent": usd(inst(369, "2025-03-31", form="10-Q", filed="2025-05-04", accn="q125"))})
    assert sec.extract(hubs).debt_status == "none"


@pytest.mark.parametrize("tag,entry,shown", [
    # BRK: borrowings tagged only by segment, but the 10-K still tags its debt maturities.
    ("LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo", inst(6_631, "2025-12-31"), "$6.6K at 2025-12-31"),
    # F: the same, with proceeds from new long-term debt in the 10-Q.
    ("ProceedsFromIssuanceOfLongTermDebt", dur(12_565, "2026-01-01", "2026-06-30", **Q), "for the period ended 2026-06-30"),
    ("DebtInstrumentCarryingAmount", inst(130_105, "2025-12-31"), "at 2025-12-31"),
    ("LongTermDebtFairValue", inst(144_703, "2026-06-30", **Q), "at 2026-06-30"),
])
def test_debt_that_no_standard_total_captures_is_unknown(tag, entry, shown):
    ex = sec.extract(company(us_gaap={tag: usd(entry)}))
    assert ex.debt_status == "unknown" and math.isnan(ex.latest["total_debt"])
    notes = debt_notes(ex)
    assert len(notes) == 1 and notes[0].startswith("Total debt is n/a: the filings show debt (XBRL " + tag)
    assert shown in notes[0] and "debt/equity" in notes[0] and "enter net cash in the DCF" in notes[0]
    assert sec.NO_DEBT_NOTE not in ex.notes


def test_debt_disclosures_older_than_15_months_do_not_count():
    old = company(us_gaap={"DebtInstrumentFaceAmount": usd(inst(500, "2025-03-15", form="10-Q", filed="2025-05-01", accn="q125"))})
    assert sec.extract(old).debt_status == "none"


def test_latest_balance_sheet_without_debt_lines_uses_the_fiscal_year_end_total():
    # CAT: its 10-Qs tag debt only by segment; the 10-K tags LongTermDebtNoncurrent and ShortTermBorrowings.
    facts = company(us_gaap={"LongTermDebtNoncurrent": usd(inst(30_696, "2025-12-31")), "ShortTermBorrowings": usd(inst(5_514, "2025-12-31"))})
    ex = sec.extract(facts)
    assert ex.debt_status == "reported" and ex.latest["total_debt"] == 30_696 + 5_514
    notes = debt_notes(ex)
    assert notes == ["The latest balance sheet (2026-06-30) tags no standard debt line, so total debt is the $36.2K reported at 2025-12-31. "
                     "Check the latest filing's balance sheet if the company has borrowed or repaid since."]
    assert not any(n.startswith("Total debt is n/a") for n in ex.notes)  # the CAT/ORCL contradiction


def test_a_debt_total_from_an_earlier_fiscal_year_is_not_carried_forward():
    # The only debt total predates the last fiscal year end; the FY2025 10-K shows debt only in a disclosure.
    facts = company(us_gaap={"LongTermDebtNoncurrent": usd(inst(800, "2024-12-31", filed="2025-02-10", accn="k24")),
                             "DebtInstrumentFaceAmount": usd(inst(800, "2025-12-31"))})
    ex = sec.extract(facts)
    assert ex.debt_status == "unknown" and math.isnan(ex.latest["total_debt"])


def test_debt_status_and_year_ago_reach_fundamentals(monkeypatch):
    fake_edgar(monkeypatch, submissions([("10-Q", "2026-08-05", "q226"), ("10-K", "2026-02-10", "k25")]), company())
    f = sec.fundamentals("TEST", "me@example.com")
    assert f.debt_status == "none" and f.latest["total_debt"] == 0.0 and f.notes.count(sec.NO_DEBT_NOTE) == 1
    assert f.year_ago_period is None and f.year_ago == {}  # no balance sheet near 2025-06-30 in this company


# ------------------------------------------------------------ year-ago balance


def test_year_ago_balance_sheet_is_the_instant_closest_to_twelve_months_earlier():
    q25 = {"form": "10-Q", "filed": "2025-08-05", "accn": "q225"}
    facts = company(
        assets=[inst(2000, "2024-12-31", filed="2025-02-10", accn="k24"), inst(2100, "2025-06-28", **q25), inst(2150, "2025-09-27", form="10-Q", filed="2025-11-04", accn="q325"),
                inst(2200, "2025-12-31"), inst(2300, "2026-06-30", **Q)],
        us_gaap={
            "StockholdersEquity": usd(inst(700, "2025-06-28", **q25), inst(900, "2026-06-30", **Q)),
            "LiabilitiesAndStockholdersEquity": usd(inst(2100, "2025-06-28", **q25)),
            "CashAndCashEquivalentsAtCarryingValue": usd(inst(50, "2025-06-28", **q25), inst(60, "2026-06-30", **Q)),
            "LongTermDebtNoncurrent": usd(inst(400, "2025-06-28", **q25), inst(380, "2026-06-30", **Q)),
        })
    ex = sec.extract(facts)
    assert ex.year_ago_period == "2025-06-28"  # two days from 2025-06-30, not the 2025-09-27 10-Q
    assert ex.year_ago["total_assets"] == 2100 and ex.year_ago["equity"] == 700 and ex.year_ago["cash"] == 50
    assert ex.year_ago["total_debt"] == 400
    assert ex.year_ago["total_liabilities"] == 2100 - 700  # derived, like the latest balance sheet
    assert any("2025-06-28" in n and n.startswith("Total liabilities") for n in ex.notes)
    assert set(ex.year_ago) <= set(ex.latest)  # the same figures as the latest balance sheet


def test_no_year_ago_balance_sheet_beyond_45_days():
    facts = company(assets=[inst(2000, "2024-12-31", filed="2025-02-10", accn="k24"), inst(2100, "2025-05-10", form="10-Q", filed="2025-06-01", accn="q125"),
                            inst(2200, "2025-12-31"), inst(2300, "2026-06-30", **Q)])
    ex = sec.extract(facts)
    assert ex.year_ago == {} and ex.year_ago_period is None


def test_year_ago_for_an_annual_filer_is_the_previous_fiscal_year_end():
    ex = sec.extract(company(quarter=False))
    assert ex.latest_period == "2025-12-31" and ex.year_ago_period == "2024-12-31" and ex.year_ago["total_assets"] == 2000


# ---------------------------------------------------------------- share count


def diluted(val, start="2026-04-01", end="2026-06-30", **kw):
    return dur(val, start, end, **{**Q, **kw})


def eps_and_income(shares_count, start="2026-04-01", end="2026-06-30"):
    """Net income and diluted EPS for the quarter, consistent with `shares_count` shares."""
    return {"NetIncomeLoss": usd(dur(2.0 * shares_count, start, end, **Q)),
            "EarningsPerShareDiluted": {"units": {"USD/shares": [dur(2.0, start, end, **Q)]}}}


def test_a_one_class_count_far_below_the_diluted_count_is_replaced():
    # HEI: CommonStockSharesOutstanding counts one of two classes, 55.1M, against 141.3M diluted in the same 10-Q.
    facts = company(us_gaap={
        "CommonStockSharesOutstanding": shares(inst(55_143_000, "2025-10-31", **Q)),
        "WeightedAverageNumberOfDilutedSharesOutstanding": shares(diluted(141_269_000)),
        **eps_and_income(141_269_000),
    })
    ex = sec.extract(facts)
    assert ex.shares == 141_269_000 and ex.shares_date == "2026-08-05"
    note = next(n for n in ex.notes if n.startswith("Shares outstanding"))
    assert "55.1M at 2025-10-31 is 0.39 times" in note and "one share class" in note and "141.3M shares, filed 2026-08-05" in note


def test_a_count_within_half_to_twice_the_diluted_count_is_kept():
    facts = company(
        us_gaap={"WeightedAverageNumberOfDilutedSharesOutstanding": shares(diluted(1_000)), **eps_and_income(1_000)},
        dei={"EntityCommonStockSharesOutstanding": shares(inst(830, "2026-07-20", **Q))},  # MSTR-like: 0.83 times
    )
    ex = sec.extract(facts)
    assert ex.shares == 830 and not any(n.startswith("Shares outstanding") for n in ex.notes)


def test_counts_from_different_filings_are_not_compared():
    # A cover count filed before a 4-for-1 split and a diluted count restated after it differ by 4 times; the
    # count is kept and restated later by apply_splits.
    facts = company(
        us_gaap={"WeightedAverageNumberOfDilutedSharesOutstanding": shares(diluted(4_000)), **eps_and_income(4_000)},
        dei={"EntityCommonStockSharesOutstanding": shares(inst(1_000, "2026-04-20", form="10-Q", filed="2026-05-05", accn="q126"))},
    )
    assert sec.extract(facts).shares == 1_000


def test_a_diluted_count_tagged_in_millions_is_not_used():
    # MCD tags its diluted count in millions (711.1); its cover count of 707.6M is right.
    facts = company(
        us_gaap={"WeightedAverageNumberOfDilutedSharesOutstanding": shares(diluted(711.1)), **eps_and_income(711_100_000)},
        dei={"EntityCommonStockSharesOutstanding": shares(inst(707_600_000, "2026-06-30", **Q))},
    )
    ex = sec.extract(facts)
    assert ex.shares == 707_600_000 and not any(n.startswith("Shares outstanding") for n in ex.notes)


def test_a_misscaled_diluted_count_is_never_the_share_count():
    # TEM: no cover count, and a diluted count in thousands (179,404 for about 179.5M). The quarter's EPS of 0.03 is
    # too small to check, so it is judged like the year to date.
    facts = company(us_gaap={
        "WeightedAverageNumberOfDilutedSharesOutstanding": shares(diluted(182_397), diluted(179_404, start="2026-01-01")),
        "NetIncomeLoss": usd(dur(5_642_000, "2026-04-01", "2026-06-30", **Q), dur(-120_277_000, "2026-01-01", "2026-06-30", **Q)),
        "EarningsPerShareDiluted": {"units": {"USD/shares": [dur(0.03, "2026-04-01", "2026-06-30", **Q), dur(-0.67, "2026-01-01", "2026-06-30", **Q)]}},
    })
    ex = sec.extract(facts)
    assert ex.shares is None
    note = next(n for n in ex.notes if n.startswith("Shares outstanding are n/a"))
    assert "tagged as 179,404 shares" in note and "about 180M" in note


# -------------------------------------------------------- fundamentals() notes


def columns(rows):
    return {"form": [r[0] for r in rows], "filingDate": [r[1] for r in rows], "accessionNumber": [r[2] for r in rows],
            "reportDate": [r[3] if len(r) > 3 else "" for r in rows], "primaryDocument": ["doc.htm" for _ in rows], "primaryDocDescription": ["" for _ in rows]}


def submissions(rows, sic="7372", name="TEST CO"):
    return {"cik": "7", "name": name, "sic": sic, "sicDescription": "Software", "fiscalYearEnd": "1231", "exchanges": ["NYSE"],
            "filings": {"recent": columns(rows), "files": []}}


def fake_edgar(monkeypatch, subs, facts, title="Test Co"):
    def get_json(url, **kwargs):
        if url == sec.TICKERS_URL:
            value = {"0": {"cik_str": 7, "ticker": "TEST", "title": title}}
        elif url == sec.SUBMISSIONS_URL.format(cik=7):
            value = subs
        elif url == sec.FACTS_URL.format(cik=7):
            value = facts
        else:
            raise AssertionError(f"unexpected request {url}")
        return http.Fetched(value, LIVE, 1_760_000_000, url)

    monkeypatch.setattr(sec, "get_json", get_json)


def test_no_false_no_quarterly_figures_note_when_10qs_lag(monkeypatch):
    # C: the 10-Qs of May and August are in the index but company facts stop at the FY2025 10-K.
    rows = [("10-Q", "2026-08-06", "c-q2", "2026-06-30"), ("10-Q", "2026-05-07", "c-q1", "2026-03-31"), ("10-K", "2026-02-20", "k25", "2025-12-31")]
    fake_edgar(monkeypatch, submissions(rows), company(quarter=False))
    notes = sec.fundamentals("TEST", "me@example.com").notes
    assert notes[0] == "SEC has not yet published XBRL data for the 10-Q filed 2026-05-07 and the 10-Q filed 2026-08-06; figures are as of 2025-12-31."
    assert not any(n.startswith(sec.TTM_IS_FISCAL_YEAR) for n in notes)
    assert ("Trailing-twelve-month figures equal the fiscal year ended 2025-12-31 until SEC publishes XBRL data for the 2 10-Qs filed since "
            "(the newest filed 2026-08-06); refresh later to update them.") in notes
    # With one 10-Q since, the note names it.
    fake_edgar(monkeypatch, submissions(rows[1:]), company(quarter=False))
    notes = sec.fundamentals("TEST", "me@example.com").notes
    assert notes[0] == "SEC has not yet published XBRL data for the 10-Q filed 2026-05-07; figures are as of 2025-12-31."
    assert ("Trailing-twelve-month figures equal the fiscal year ended 2025-12-31 until SEC publishes XBRL data for the 10-Q filed 2026-05-07; "
            "refresh later to update them.") in notes


def test_ttm_note_when_the_10q_facts_have_no_year_to_date(monkeypatch):
    facts = company(quarter=False)
    facts["facts"]["us-gaap"]["Assets"]["units"]["USD"].append(inst(2300, "2026-03-31", form="10-Q", filed="2026-05-07", accn="c-q1"))
    rows = [("10-Q", "2026-05-07", "c-q1", "2026-03-31"), ("10-K", "2026-02-20", "k25", "2025-12-31")]
    fake_edgar(monkeypatch, submissions(rows), facts)
    notes = sec.fundamentals("TEST", "me@example.com").notes
    assert not any("not yet published" in n or n.startswith(sec.TTM_IS_FISCAL_YEAR) for n in notes)
    assert any(n.startswith("Trailing-twelve-month figures equal the fiscal year ended 2025-12-31 because SEC company facts hold no year-to-date") for n in notes)


def test_the_original_note_stays_when_no_10q_was_filed_since(monkeypatch):
    fake_edgar(monkeypatch, submissions([("10-K", "2026-02-20", "k25", "2025-12-31")]), company(quarter=False))
    assert any(n.startswith(sec.TTM_IS_FISCAL_YEAR) for n in sec.fundamentals("TEST", "me@example.com").notes)


def test_ifrs_filer_refusal_names_form_20f(monkeypatch):
    # TSM files a 20-F with IFRS figures: company facts has ifrs-full but no us-gaap.
    facts = {"cik": 7, "entityName": "TSMC", "facts": {"ifrs-full": {"Revenue": {"units": {"TWD": []}}}, "dei": {}}}
    fake_edgar(monkeypatch, submissions([("6-K", "2026-10-10", "s1"), ("20-F", "2026-04-15", "a1")], name="TAIWAN SEMICONDUCTOR"), facts, title="TSMC")
    with pytest.raises(DataError) as err:
        sec.fundamentals("TEST", "me@example.com")
    assert str(err.value) == ("TSMC files its annual reports on Form 20-F with IFRS figures, and FinLit Pro reads US GAAP statements only. "
                              "Read its financial statements in the Form 20-F on sec.gov. Price, model, Monte Carlo and options views still work.")


def test_non_us_gaap_filer_without_a_20f_keeps_the_general_message(monkeypatch):
    facts = {"cik": 7, "entityName": "X", "facts": {"dei": {}}}
    fake_edgar(monkeypatch, submissions([("10-K", "2026-02-20", "k25")]), facts, title="X Corp")
    with pytest.raises(DataError, match="does not report US GAAP figures"):
        sec.fundamentals("TEST", "me@example.com")


# -------------------------------------------------------------- filing text


def test_bad_email_is_reported_once_for_both_reports(monkeypatch):
    calls = []
    monkeypatch.setattr(filings, "read", lambda *a, **k: calls.append(a) or None)
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[
        Filing("10-Q", "2026-08-01", "2026-06-30", "10-Q", "https://www.sec.gov/q.htm", "a2"),
        Filing("10-K", "2026-02-01", "2025-12-31", "10-K", "https://www.sec.gov/k.htm", "a1")])
    texts, problems = filings.latest_reports(fund, "bad-email")
    assert texts == [] and len(problems) == 1 and "Settings > Data" in problems[0] and calls == []


def test_foreign_issuer_note_is_unchanged_by_a_bad_email():
    fund = Fundamentals(1, "ARM", None, {}, {}, None, None, filings=[Filing("20-F", "2026-05-26", "2026-03-31", "20-F", "https://www.sec.gov/f.htm", "a1")])
    assert filings.latest_reports(fund, "bad-email") == ([], ["ARM files annual reports on Form 20-F; FinLit Pro reads 10-K and 10-Q text only."])


RISKS = ("We face many risks. " * 200).strip()


def test_heading_sharing_a_line_with_the_part_heading_is_found():
    text = ("Table of Contents\nItem 1A. Risk Factors\n45\nItem 2. Unregistered Sales\n46\n"
            "PART II. OTHER INFORMATION Item 1A. Risk Factors\n" + RISKS + "\nItem 2. Unregistered Sales of Equity Securities\nNone.\n")
    _, start, end = filings.SECTIONS["10-Q"][1]
    body = filings.extract_section(text, start, end)
    assert body.startswith("Item 1A. Risk Factors\nWe face many risks.") and body.endswith("We face many risks.")


def test_a_mid_line_cross_reference_never_replaces_a_short_real_section():
    # JPM's 10-Q: the real heading, then "Refer to Part I, Item 1A: Risk Factors on pages 9-31" on the same line.
    real = "Item 1A. Risk Factors. |  | Refer to Part I, Item 1A: Risk Factors on pages 9-31 of the 2025 Form 10-K for the risks. " + "No material changes. " * 10
    text = "Item 1A. Risk Factors\n45\nItem 2. Unregistered\n46\n" + real + "\nItem 2. Unregistered Sales of Equity Securities\n" + "Body. " * 5000
    _, start, end = filings.SECTIONS["10-Q"][1]
    body = filings.extract_section(text, start, end)
    assert body == real.strip()


def page(sections_html):
    return f"<html><body>{sections_html}</body></html>"


def test_short_10q_risk_factors_are_kept_but_short_10k_sections_are_not(monkeypatch):
    short = "There have been no material changes to the risk factors disclosed in our Annual Report on Form 10-K for 2025, which describe the risks."
    q_html = page(f"<p>Item 2. Management&#8217;s Discussion and Analysis</p><p>{'Revenue rose. ' * 60}</p><p>Item 4. Controls</p><p>PART II</p>"
                  f"<p>Item 1A. Risk Factors</p><p>{short}</p><p>Item 2. Unregistered Sales of Equity Securities</p><p>None.</p>")
    k_html = page(f"<p>Item 1. Business</p><p>{'We sell widgets. ' * 60}</p><p>Item 1A. Risk Factors</p><p>{short}</p><p>Item 1B. Unresolved</p>")
    monkeypatch.setattr(filings, "get_text", lambda url, **k: http.Fetched(q_html if "q.htm" in url else k_html, LIVE, 1_760_000_000, url))
    q = filings.read(Filing("10-Q", "2026-08-01", "2026-06-30", "10-Q", "https://www.sec.gov/q.htm", "a2"), "me@example.com")
    assert q.sections["Risk Factors"].startswith("Item 1A. Risk Factors") and "no material changes" in q.sections["Risk Factors"]
    assert 150 <= q.full_chars["Risk Factors"] < 500
    k = filings.read(Filing("10-K", "2026-02-01", "2025-12-31", "10-K", "https://www.sec.gov/k.htm", "a1"), "me@example.com")
    assert "Risk Factors" not in k.sections and "Risk Factors not found in the 10-K; the filing may incorporate it by reference." in k.notes
    # A contents entry is still not a section.
    toc = page("<p>Item 1A. Risk Factors</p><p>45</p><p>Item 2. Unregistered Sales</p><p>46</p>")
    monkeypatch.setattr(filings, "get_text", lambda url, **k: http.Fetched(toc, LIVE, 1_760_000_000, url))
    assert "Risk Factors" not in filings.read(Filing("10-Q", "2026-08-01", "2026-06-30", "10-Q", "https://www.sec.gov/q.htm", "a2"), "me@example.com").sections


def test_debt_notes_never_contradict_each_other():
    # Every policy outcome adds at most one debt note, and never both "n/a" and "treated as zero".
    cases = [company(), company(us_gaap={"LongTermDebtNoncurrent": usd(inst(5, "2026-06-30", **Q))}),
             company(us_gaap={"DebtInstrumentFaceAmount": usd(inst(5, "2026-06-30", **Q))}),
             company(us_gaap={"LongTermDebtNoncurrent": usd(inst(5, "2025-12-31"))})]
    for facts in cases:
        notes = debt_notes(sec.extract(facts))
        assert len(notes) <= 1
    assert pd.isna(sec.total_debt({}))
