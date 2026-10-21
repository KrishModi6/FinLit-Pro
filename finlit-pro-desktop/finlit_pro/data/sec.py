"""SEC EDGAR: the primary source for fundamentals.

Three free, keyless endpoints:

  company_tickers.json   ticker -> CIK (the SEC's company id)
  submissions/CIK*.json  company profile and the filing index
  companyfacts/CIK*.json every XBRL number the company has ever filed

The SEC requires a User-Agent naming the app and a contact email, and its
fair-access policy allows 10 requests a second. `http.py` holds us to 5, we
make three requests per company (four for a heavy filer whose latest annual
report has scrolled off the first page of its filing index), and they are
cached for hours.

Turning company facts into a clean table is the hard part, and the reasons are
documented where they bite: companies switch XBRL tags over the years, every
10-K repeats prior years as comparatives, restatements arrive in later
filings, and 10-Qs report year-to-date rather than quarterly figures.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import NamedTuple

import numpy as np
import pandas as pd

from finlit_pro import __version__, validation
from finlit_pro.data import demo
from finlit_pro.data.http import get_json
from finlit_pro.data.models import DataError, FactRef, Filing, Fundamentals, Source
from finlit_pro.fmt import money
from finlit_pro.validation import ValidationError

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
OLDER_SUBMISSIONS_URL = "https://data.sec.gov/submissions/{name}"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn}/{doc}"
INDEX_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn_nodash}/{accn}-index.htm"
COMPANY_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik:010d}&type=&dateb=&owner=include&count=40"
SERVICE = "SEC EDGAR"

ANNUAL_FORMS = {"10-K", "10-K/A", "10-KT", "20-F", "40-F"}
QUARTER_FORMS = {"10-Q", "10-Q/A"}
# Periodic reports that carry financial statements, newest first in the filing index.
PERIODIC_FORMS = ("10-K", "10-Q", "20-F", "40-F")

# A share count dated more than about 15 months before the latest balance
# sheet describes a company that no longer exists in that form.
STALE_DAYS = 456

# Commodity pools and grantor trusts (gold, silver, bitcoin ETFs) file 10-Ks
# under this SIC code; their "net income" is the change in value of what they hold.
COMMODITY_POOL_SIC = "6221"
# Forms only investment companies file (unit investment trusts such as SPY, mutual and closed-end funds).
FUND_FORMS = {"N-CSR", "N-CSRS", "NPORT-P", "N-30D", "N-CEN", "485BPOS", "24F-2NT", "NSAR-U", "NSAR-B"}

# Flow metrics, measured over a period. Tags are in priority order: the first
# one that has a value for a given year wins, so a company that switched from
# SalesRevenueNet to the post-2018 ASC 606 tags still gets one unbroken line.
DURATION_TAGS: dict[str, list[str]] = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "RevenuesNetOfInterestExpense",
    ],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "pretax_income": [
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    ],
    "income_tax": ["IncomeTaxExpenseBenefit"],
    "net_income": ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"],
    "eps_diluted": ["EarningsPerShareDiluted", "EarningsPerShareBasic"],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "rnd": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
    "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
    "interest_expense": ["InterestExpense", "InterestExpenseNonoperating"],
    "dividends_paid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    # Companies with nothing dilutive report one count for both, under the second tag.
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"],
}

# Balance sheet metrics, measured at a point in time.
INSTANT_TAGS: dict[str, list[str]] = {
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "short_investments": ["MarketableSecuritiesCurrent", "ShortTermInvestments", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"],
    "current_assets": ["AssetsCurrent"],
    "total_assets": ["Assets"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "total_liabilities": ["Liabilities"],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "retained_earnings": ["RetainedEarningsAccumulatedDeficit"],
    # Debt comes in priority groups that `total_debt` combines. Each group gives one figure per date, from its
    # first tag with a value there, so one tag of a group is never added to another.
    # First Version: only LongTermDebt counted as total long-term debt, so JPM's $460B, tagged
    # LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, was missed and its debt
    # read as short-term borrowings alone. Current Version: that tag is a second choice. Both
    # include current maturities, so only short-term borrowings are added to them.
    "debt_long_total": ["LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"],
    # First Version: only the LongTermDebt family of tags was read, so ORCL's $122B of LongTermNotesPayable (its
    # 10-Qs: LongTermNotesAndLoans), DASH's $2.7B ConvertibleLongTermNotesPayable and PINS's $981M
    # ConvertibleDebtNoncurrent were missed. Current Version: notes, convertible notes, long-term lines of credit and
    # other long-term debt are later choices in the same groups. Finance lease liabilities are left out on purpose:
    # they are leases, not borrowings, and companies that count them as debt already fold them into
    # LongTermDebtAndCapitalLeaseObligations, so adding FinanceLeaseLiability* would count those leases twice.
    "debt_noncurrent": [
        "LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations", "LongTermNotesPayable", "LongTermNotesAndLoans",
        "ConvertibleLongTermNotesPayable", "ConvertibleDebtNoncurrent", "LongTermLineOfCreditNoncurrent", "OtherLongTermDebtNoncurrent",
    ],
    # ORCL tags its current debt as DebtCurrent in its 10-K and as NotesPayableCurrent in its 10-Qs. NotesPayableCurrent
    # is a current portion, not all current debt: CVNA tags it beside LongTermDebtCurrent and a drawn credit line.
    "debt_current_portion": [
        "LongTermDebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent", "NotesPayableCurrent", "ConvertibleNotesPayableCurrent", "ConvertibleDebtCurrent",
    ],
    # All current debt: the current portion of long-term debt plus short-term borrowings.
    "debt_current_all": ["DebtCurrent"],
    "short_borrowings": ["ShortTermBorrowings", "CommercialPaper", "LinesOfCreditCurrent"],
    # Long- and short-term debt as one figure, from the debt note. It is not always complete (WMT's leaves out
    # short-term borrowings), so it is used only when no total or part above is tagged: GS tags only this, $437.9B.
    "debt_combined_total": ["DebtLongtermAndShorttermCombinedAmount"],
    # Debt tagged only by instrument (notes, convertible notes, unsecured or secured long-term debt, loans, a
    # long-term credit line), current and non-current together. Instruments often appear in the notes as parts of
    # a total, so these are used only when no total or part above is tagged: CME's only debt line is
    # UnsecuredLongTermDebt, and O's largest is NotesPayable.
    "debt_instrument_total": [
        "NotesPayable", "ConvertibleNotesPayable", "ConvertibleDebt", "UnsecuredLongTermDebt", "SecuredLongTermDebt", "LongTermLoansPayable",
        "LoansPayable", "LongTermLineOfCredit",
    ],
}

DEBT_KEYS = ("debt_long_total", "debt_noncurrent", "debt_current_portion", "debt_current_all", "short_borrowings", "debt_combined_total", "debt_instrument_total")

# Debt figures from the notes and the cash flow statement. They never enter the total, but one above zero in the
# last ~15 months shows the company has debt, so a missing total is then n/a rather than zero. BRK and F tag their
# borrowings only by segment, which SEC company facts leave out; BRK still tags its debt maturities and F its
# proceeds from new long-term debt. Repayments and interest expense are left out: they also appear at companies
# that have repaid their debt (HUBS) or pay only credit-line fees (TTD, DOCU, ROKU).
DEBT_DISCLOSURE_TAGS = (
    "DebtInstrumentCarryingAmount", "DebtInstrumentFaceAmount", "LongTermDebtFairValue", "DebtInstrumentFairValue",
    "SeniorNotes", "SeniorLongTermNotes", "SecuredDebt", "UnsecuredDebt", "LineOfCredit",
    "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths", "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo",
    "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree", "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour",
    "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive", "LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive",
    "ProceedsFromIssuanceOfLongTermDebt", "ProceedsFromIssuanceOfDebt", "ProceedsFromIssuanceOfSeniorLongTermDebt",
    "ProceedsFromConvertibleDebt", "ProceedsFromBankDebt", "ProceedsFromNotesPayable",
)

NO_DEBT_NOTE = "No debt is reported in the filings; treated as zero."

# Inputs to derived balance sheet figures only; they are not columns of the table.
HELPER_INSTANT_TAGS: dict[str, list[str]] = {
    "liabilities_and_equity": ["LiabilitiesAndStockholdersEquity"],
    "equity_with_nci": ["StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "minority_interest": ["MinorityInterest"],
}

# Start of the note that says TTM figures are simply the last fiscal year.
TTM_IS_FISCAL_YEAR = "No quarterly figures have been filed since the fiscal year ended"

# Share counts reported at a date: the cover page first, then the balance sheet.
SHARE_COUNT_TAGS = ("EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding")

UNIT_FOR = {"eps_diluted": "USD/shares", "diluted_shares": "shares"}

# Per-share figures change meaning at a stock split. Filings made after a
# split restate the comparatives they repeat, but older years that only ever
# appeared in pre-split filings are never restated, so each value's filing
# date is kept to tell the two apart.
SPLIT_SENSITIVE = ("eps_diluted", "diluted_shares")


def _headers(email: str) -> dict[str, str]:
    text = (email or "").strip()
    if not text:
        raise DataError("SEC EDGAR requires a contact email in each request. Enter it in Settings > Data, then refresh.")
    # First Version: a malformed email raised the generic ValidationError, which said nothing about the
    # SEC or where the email is set. Current Version: a DataError naming the SEC contact email and Settings > Data.
    try:
        contact = validation.email(text)
    except ValidationError:
        raise DataError(f'The SEC contact email "{text}" does not look like an email address. Fix it in Settings > Data (use the form name@example.com), then refresh.') from None
    return {"User-Agent": f"FinLitPro/{__version__} {contact}", "Accept": "application/json"}


def _to_date(text: str | None) -> date | None:
    if not text:
        return None
    try:
        return datetime.strptime(str(text)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _current(day: date | None, reference: date | None) -> bool:
    """True when `day` is no more than STALE_DAYS before `reference` (always true without a reference)."""
    return reference is None or (day is not None and (reference - day).days <= STALE_DAYS)


def index_url(cik: int, accession: str) -> str:
    return INDEX_URL.format(cik=cik, accn_nodash=accession.replace("-", ""), accn=accession) if accession else ""


def _ref(cik: int, entry: dict) -> FactRef:
    accn = entry.get("accn") or ""
    return FactRef(form=entry.get("form") or "", filed=entry.get("filed") or "", accession=accn, url=index_url(cik, accn))


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------


def lookup_cik(symbol: str, email: str) -> tuple[int, str]:
    fetched = get_json(TICKERS_URL, headers=_headers(email), ttl_s=7 * 86400, service=SERVICE)
    table = {}
    for row in (fetched.value or {}).values():
        try:
            table[str(row["ticker"]).upper()] = (int(row["cik_str"]), str(row["title"]))
        except (KeyError, TypeError, ValueError):
            continue
    sym = symbol.upper()
    for candidate in (sym, sym.replace(".", "-"), sym.replace("-", ".")):
        if candidate in table:
            return table[candidate]
    raise DataError(
        f"{sym} is not in the SEC's company list. ETFs, indices, funds, crypto and most non-US listings "
        "do not file XBRL financial statements. Price, model, Monte Carlo and options views still work."
    )


def _parse_columns(cik: int, columns: dict) -> list[Filing]:
    """One page of the filing index (parallel lists, newest first) -> filings."""
    forms = columns.get("form") or []

    def at(key: str, i: int) -> str:
        values = columns.get(key) or []
        return (values[i] if i < len(values) else "") or ""

    out = []
    for i, form in enumerate(forms):
        accn, doc = at("accessionNumber", i), at("primaryDocument", i)
        if not accn:
            continue
        out.append(
            Filing(
                form=form,
                filed=at("filingDate", i),
                report_date=at("reportDate", i),
                description=at("primaryDocDescription", i),
                url=ARCHIVE_URL.format(cik=cik, accn=accn.replace("-", ""), doc=doc) if doc else "",
                accession=accn,
                index_url=index_url(cik, accn),
            )
        )
    return out


def parse_filings(cik: int, submissions: dict, limit: int | None = None) -> list[Filing]:
    """The filing index in submissions.recent, newest first.

    First Version: only the newest 300 entries were kept. JPM files hundreds of
    424B2 prospectus supplements a week, so its 10-K and 10-Q fell outside them
    and the app said it had none. Current Version: every entry of
    submissions.recent is parsed (JPM: about 26,000); `limit` is optional.
    """
    recent = ((submissions or {}).get("filings") or {}).get("recent") or {}
    out = _parse_columns(cik, recent)
    return out[:limit] if limit else out


def _older_filings(cik: int, submissions: dict, headers: dict[str, str], force: bool = False) -> list[Filing]:
    """The first older page of the filing index (filings.files), or nothing if there is none or it cannot be read."""
    files = ((submissions or {}).get("filings") or {}).get("files") or []
    name = (files[0] or {}).get("name") if files else None
    if not name:
        return []
    try:
        page = get_json(OLDER_SUBMISSIONS_URL.format(name=name), headers=headers, ttl_s=0 if force else 7 * 86400, service=SERVICE)
    except DataError:
        return []
    return _parse_columns(cik, page.value or {})


def _fund_reason(profile: dict, title: str, filings: list[Filing]) -> str | None:
    """Why company statements do not apply to this filer, when it is a commodity pool, trust ETF or fund.

    First Version: GLD and IBIT file 10-Ks with US GAAP XBRL, so their unrealised gains on gold and
    bitcoin became "net income" and the app showed a P/E of 5.7 and a DCF value. SPY and DIA reached
    the companyfacts 404 and were called "very new or very small filers". Current Version: SIC 6221
    (commodity contracts), "ETF" in the registrant's name, or an index of investment company forms
    with no 10-K or 10-Q is refused with the same wording as `not_a_company`.
    """
    name = profile.get("name") or title
    sic = str(profile.get("sic") or "")
    forms = {f.form for f in filings}
    is_fund = (
        sic == COMMODITY_POOL_SIC
        or re.search(r"\bETF\b", name, flags=re.IGNORECASE) is not None
        or (bool(forms & FUND_FORMS) and not forms & set(PERIODIC_FORMS))
    )
    return not_a_company("ETF", name) if is_fund else None


def _accessions(facts: dict) -> set[str]:
    """Every filing (accession number) that contributed at least one fact."""
    out: set[str] = set()
    for taxonomy in ((facts or {}).get("facts") or {}).values():
        for node in (taxonomy or {}).values():
            for entries in ((node or {}).get("units") or {}).values():
                out.update(e.get("accn") for e in entries if e.get("accn"))
    return out


def _lag_note(facts: dict, filings: list[Filing], as_of: str | None) -> str | None:
    """A note when the newest 10-K or 10-Q in the filing index has no facts in companyfacts yet.

    First Version: KO's figures stopped at its Q1 10-Q while the Filings view read the Q2 10-Q,
    and nothing said the numbers trailed the latest filing. Current Version: the newest
    periodic filing's accession is looked up among the facts' accessions.
    """
    known = _accessions(facts)
    missing = []
    for f in filings:
        if f.form in PERIODIC_FORMS and f.accession:
            if f.accession in known:
                break
            missing.append(f)
    if not missing:
        return None
    # First Version: only the newest filing was named, so C's note named its August 10-Q although its May 10-Q was
    # missing from company facts too. Current Version: every periodic filing newer than the last one with facts.
    names = [f"the {f.form} filed {f.filed}" for f in reversed(missing)]
    which = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return f"SEC has not yet published XBRL data for {which}; figures are as of {as_of or 'the previous filing'}."


# ---------------------------------------------------------------------------
# Company facts -> tables
# ---------------------------------------------------------------------------


def _entries(facts: dict, tag: str, unit: str) -> list[dict]:
    for taxonomy in ("us-gaap", "dei"):
        node = ((facts or {}).get("facts") or {}).get(taxonomy, {}).get(tag)
        if node:
            return list((node.get("units") or {}).get(unit) or [])
    return []


def _latest_filed(best: dict[date, dict], key: date, e: dict) -> None:
    if key not in best or (e.get("filed") or "") > (best[key].get("filed") or ""):
        best[key] = e


def _annual_entries(entries: list[dict]) -> dict[date, dict]:
    """One fact per fiscal year, from annual filings, latest filing winning.

    A 10-K repeats the two prior years as comparatives, and a later 10-K's
    comparative is the restated figure, so for each fiscal year end we keep
    the value from the most recently filed document. Durations of 340 to 390
    days admit 52- and 53-week fiscal years and reject the quarterly and
    year-to-date values that also appear in some 10-Ks.
    """
    best: dict[date, dict] = {}
    for e in entries:
        if e.get("form") not in ANNUAL_FORMS:
            continue
        start, end = _to_date(e.get("start")), _to_date(e.get("end"))
        if start and end and 340 <= (end - start).days <= 390:
            _latest_filed(best, end, e)
    return best


def _instant_entries(entries: list[dict], forms: set[str]) -> dict[date, dict]:
    best: dict[date, dict] = {}
    for e in entries:
        if e.get("form") in forms and not e.get("start"):
            end = _to_date(e.get("end"))
            if end:
                _latest_filed(best, end, e)
    return best


def _merge(by_priority: list[dict]) -> dict:
    merged: dict = {}
    for series in reversed(by_priority):
        merged.update(series)  # higher priority overwrites
    return merged


def _ttm(entries: list[dict]) -> tuple[float, date, dict] | None:
    """Trailing twelve months from one tag: (value, period end, newest fact used).

    TTM = last fiscal year + this year's year-to-date - last year's same
    year-to-date. 10-Qs report year-to-date figures, so this one formula
    works after Q1, Q2 and Q3 without reconstructing single quarters.
    """
    annual = _annual_entries(entries)
    if not annual:
        return None
    fy_end = max(annual)
    fy = annual[fy_end]
    fy_value = float(fy["val"])

    # First Version: any 10-Q period starting after this tag's last fiscal year counted as
    # year-to-date, so a tag whose annual figures stopped years ago mixed that old year with this
    # year's quarters. Current Version: the year-to-date must start right after that fiscal year end.
    ytd: list[tuple[date, int, dict]] = []
    for e in entries:
        if e.get("form") not in QUARTER_FORMS:
            continue
        start, end = _to_date(e.get("start")), _to_date(e.get("end"))
        if start and end and end > fy_end and fy_end - timedelta(days=5) < start <= fy_end + timedelta(days=10):
            ytd.append((end, (end - start).days, e))
    if not ytd:
        return fy_value, fy_end, fy

    latest_end = max(item[0] for item in ytd)
    cur_end, cur_days, cur = max((i for i in ytd if i[0] == latest_end), key=lambda i: i[1])
    target = cur_end - timedelta(days=364)
    # First Version: the first matching prior-year figure in file order won, which is usually the
    # original filing. Current Version: the latest filed one, the comparative in the current 10-Q,
    # restated on the same basis as the current figure.
    prior = []
    for e in entries:
        start, end = _to_date(e.get("start")), _to_date(e.get("end"))
        if start and end and abs((end - target).days) <= 10 and abs((end - start).days - cur_days) <= 10:
            prior.append(e)
    if prior:
        last_year = max(prior, key=lambda e: e.get("filed") or "")
        return fy_value + float(cur["val"]) - float(last_year["val"]), cur_end, cur
    return fy_value, fy_end, fy


def _shares_outstanding(facts: dict, tag: str = "EntityCommonStockSharesOutstanding") -> tuple[float, str, dict] | None:
    """Latest share count reported under one tag, its as-of date and fact, summing share classes in one filing."""
    groups: dict[tuple[str, str], dict[float, dict]] = defaultdict(dict)
    for e in _entries(facts, tag, "shares"):
        if e.get("end") and e.get("val"):
            groups[(e["end"], e.get("accn", ""))][float(e["val"])] = e
    if not groups:
        return None
    latest = max(groups, key=lambda k: (k[0], k[1]))
    return float(sum(groups[latest])), latest[0], next(iter(groups[latest].values()))


# Earnings to common shareholders first: the numerator of EPS.
IMPLIED_SHARES_INCOME_TAGS = ("NetIncomeLossAvailableToCommonStockholdersDiluted", "NetIncomeLossAvailableToCommonStockholdersBasic", "NetIncomeLoss", "ProfitLoss")


def _implied_shares(facts: dict) -> dict[tuple[str, str], float]:
    """Net income divided by diluted EPS for each period (start, end): about the diluted share count, in shares."""
    found: dict[str, dict[tuple[str, str], float]] = {}
    for metric, tags, unit in (("ni", IMPLIED_SHARES_INCOME_TAGS, "USD"), ("eps", [*DURATION_TAGS["eps_diluted"], "EarningsPerShareBasicAndDiluted"], "USD/shares")):
        by_period: dict[tuple[str, str], dict] = {}
        for tag in tags:
            latest: dict[tuple[str, str], dict] = {}
            for e in _entries(facts, tag, unit):
                key = (e.get("start") or "", e.get("end") or "")
                if key[0] and key not in by_period and (key not in latest or (e.get("filed") or "") > (latest[key].get("filed") or "")):
                    latest[key] = e
            by_period.update(latest)  # earlier tags keep their periods
        found[metric] = {k: float(v["val"]) for k, v in by_period.items() if v.get("val") is not None}
    out = {}
    for key, eps in found["eps"].items():
        ni = found["ni"].get(key)
        # Cents of rounding make a small EPS useless as a check.
        if ni is not None and abs(eps) >= 0.05 and ni / eps > 0:
            out[key] = ni / eps
    return out


def _diluted_counts(facts: dict) -> list[tuple[float, date, dict, float | None]]:
    """Every diluted weighted-average share count in 10-Ks and 10-Qs, newest period first, quarter before year to date.

    Each comes with net income over diluted EPS for the same period where that can be computed: (count, period end,
    fact, implied count).
    """
    implied = _implied_shares(facts)
    rows = []
    for tag in DURATION_TAGS["diluted_shares"]:
        for e in _entries(facts, tag, "shares"):
            start, end = _to_date(e.get("start")), _to_date(e.get("end"))
            if e.get("form") in ANNUAL_FORMS | QUARTER_FORMS and start and end and e.get("val"):
                rows.append(((end, -(end - start).days, e.get("filed") or ""), float(e["val"]), end, e, implied.get((e["start"], e["end"]))))
    rows.sort(key=lambda r: r[0], reverse=True)
    return [r[1:] for r in rows]


def _scale_ok(counts: list) -> list[bool]:
    """For each diluted count, False when it looks tagged in thousands or millions of shares.

    A count is off scale when net income over diluted EPS for its period is more than 50 times larger or smaller
    (a unit error is a factor of 1,000; minority interests or preferred dividends move it far less). A count
    whose period has no usable EPS is judged like the newest count that can be checked.
    """
    checked = [None if i is None else 0.02 <= c / i <= 50 for c, _, _, i in counts]
    default = next((ok for ok in checked if ok is not None), True)
    return [default if ok is None else ok for ok in checked]


def _latest_diluted(facts: dict, counts: list | None = None) -> tuple[float, date, dict] | None:
    """The diluted weighted-average share count for the most recent period reported, quarter before year to date.

    First Version: the newest count was used as tagged. MCD tags its diluted count in millions (711.1) and TEM in
    thousands (182,397), so TEM's market cap was computed from 182,397 shares. Current Version: a count that net
    income over diluted EPS shows to be in thousands or millions is skipped.
    """
    counts = _diluted_counts(facts) if counts is None else counts
    return next(((c, end, e) for (c, end, e, _), ok in zip(counts, _scale_ok(counts)) if ok), None)


def _misscaled_note(counts: list) -> str:
    """Why no diluted count is usable, when every count in the filings fails the scale check; else empty."""
    if not counts or any(_scale_ok(counts)):
        return ""
    count, end, _, implied = next((c for c in counts if c[3] is not None), counts[0])
    return (f" The diluted weighted-average count for the period ended {end} is tagged as {count:,.0f} shares, while net income "
            f"divided by diluted EPS gives about {implied / 1e6:,.0f}M, so it is not used.")


def _same_filing_diluted(counts: list, entry: dict) -> float | None:
    """The newest scale-checked diluted count reported in the same filing as `entry`, which shares its split basis."""
    for (count, _, e, _), ok in zip(counts, _scale_ok(counts)):
        if ok and e.get("accn") == entry.get("accn") and e.get("filed") == entry.get("filed"):
            return count
    return None


def _share_count(facts: dict, reference: date | None, cik: int) -> tuple[float | None, str | None, FactRef | None, list[str]]:
    """Shares outstanding, the date that decides split restatement, the fact used, and notes.

    First Version: the newest cover-page count was used however old it was. BRK's newest
    untagged-by-class count is 941,481 from 2011 and SHOP's is 39.3M from a 2014 20-F, which gave
    BRK-B a market cap of $508M instead of about $1.1T. When no cover count existed at all, the
    last annual diluted count was used, also however old.
    Current Version: a cover or balance-sheet count dated more than about 15 months before the
    latest balance sheet is rejected. The diluted weighted-average count for the latest reported
    period is used instead when it is current, and the substitution is noted. Otherwise the count
    is left empty with a note, never filled with an old figure.

    First Version: a current count was used however far it was from the diluted count. HEI tags only
    one of its two classes, 55.1M shares, against 141.3M diluted, so its market cap read $16.8B
    instead of about $42.7B. Current Version: a current cover or balance-sheet count is checked
    against the diluted weighted-average count in the same filing (same basis for any stock split);
    outside 0.5 to 2 times it, the latest diluted count is used and the note says why.
    """
    stale, off = [], None
    counts = _diluted_counts(facts)
    diluted = _latest_diluted(facts, counts)
    diluted_current = diluted if diluted and _current(diluted[1], reference) else None
    for tag in SHARE_COUNT_TAGS:
        found = _shares_outstanding(facts, tag)
        if found and _current(_to_date(found[1]), reference):
            same = _same_filing_diluted(counts, found[2])
            ratio = found[0] / same if same else 1.0
            if 0.5 <= ratio <= 2 or diluted_current is None:
                return found[0], found[1], _ref(cik, found[2]), []
            off = off or (found, ratio)
        elif found:
            stale.append(found[1])
    if off:
        (count, as_of, _), ratio = off
        value, end, entry = diluted_current
        filed = entry.get("filed") or str(end)
        likely = "it probably counts only one share class" if ratio < 0.5 else "the two counts probably cover different share classes"
        return value, filed, _ref(cik, entry), [
            f"Shares outstanding: the reported count of {count / 1e6:,.1f}M at {as_of} is {ratio:.2f} times the diluted weighted-average count "
            f"in the same filing, outside the 0.5 to 2 range, so {likely}. The diluted count for the period ended {end} "
            f"({value / 1e6:,.1f}M shares, filed {filed}) is used for market cap and per-share values."
        ]
    why = (f"the newest reported share count is dated {max(stale)}, more than 15 months before the latest balance sheet"
           if stale else "the filings tag no cover-page share count (companies with several share classes often tag each class separately)")
    if diluted and _current(diluted[1], reference):
        value, end, entry = diluted
        # Split restatement goes by filing date: a company restates weighted counts for a split made before it files.
        filed = entry.get("filed") or str(end)
        note = f"Shares outstanding: {why}, so the diluted weighted-average count for the period ended {end} ({value / 1e6:,.0f}M shares, filed {filed}) is used."
        return value, filed, _ref(cik, entry), [note]
    newest = max(stale + ([str(diluted[1])] if diluted else []), default=None)
    misscaled = _misscaled_note(counts)
    found_text = (f"the newest share count in the XBRL data is dated {newest}, too old to use" if newest
                  else "the XBRL data has no usable share count" if misscaled else "the XBRL data has no share count")
    return None, None, None, [
        f"Shares outstanding are n/a: {found_text}, so market cap and per-share values are left blank.{misscaled} "
        "Companies with several share classes (Class A and B) often tag each class separately, which SEC company facts leave out."
    ]


def total_debt(row: dict) -> float:
    """Combine the debt groups without double counting.

    In priority order: a comprehensive long-term total (LongTermDebt includes
    its current maturities, so only true short-term borrowings are added to
    it); else the non-current part plus the current part, where DebtCurrent
    already includes the current portion of long-term debt and short-term
    borrowings and so stands alone; else long- and short-term debt combined
    in one figure; else debt tagged only by instrument, plus short-term
    borrowings.

    First Version: with no debt tag at all the result was 0.0, so BRK, which
    tags its borrowings under its own names, showed no debt and net cash.
    Current Version: NaN when no debt concept is present; n/a, not zero.
    Whether that means "no debt" is decided once, for the latest balance
    sheet, in `_debt_decision`.

    First Version: any comprehensive total won, even zero, so ORCL's FY2022
    LongTermDebt of 0 (tagged beside $72B of notes) made its total debt 0,
    and MAR's LongTermDebt of $23M hid $16.9B of debt. Current Version: a
    total smaller than the non-current part it should contain is not used.
    """

    def get(key: str) -> float | None:
        v = row.get(key)
        return None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)

    if all(get(k) is None for k in DEBT_KEYS):
        return float("nan")
    short = get("short_borrowings") or 0.0
    long_total = get("debt_long_total")
    if long_total and long_total >= (get("debt_noncurrent") or 0.0):
        return long_total + short
    if any(get(k) is not None for k in ("debt_noncurrent", "debt_current_all", "debt_current_portion")):
        noncurrent = get("debt_noncurrent") or 0.0
        if get("debt_current_all"):
            return noncurrent + get("debt_current_all")
        return noncurrent + (get("debt_current_portion") or 0.0) + short
    if get("debt_combined_total") is not None:
        return get("debt_combined_total")
    if get("debt_instrument_total") is not None:
        return get("debt_instrument_total") + short
    return (long_total or 0.0) + short


def _debt_evidence(facts: dict, period: date, balance_floor: date) -> tuple[str, float, date, bool] | None:
    """The newest debt figure above zero near the latest balance sheet: (tag, value, date, is a flow), or None.

    Debt disclosures and debt proceeds count when dated within about 15 months before `period` (or a few months
    after it: debt issued after the balance sheet). Balance sheet debt tags count from `balance_floor`, the last
    fiscal year end, on: a debt line that last year's annual balance sheet no longer shows has been repaid
    (HUBS's convertible notes, last tagged at 2025-03-31). For each tag only its newest figure counts, so debt
    reported as repaid (SHOP's convertible notes: $920M at 2025-09-30, 0 at 2025-12-31) is not current debt.
    """
    balance_tags = {t for k in DEBT_KEYS for t in INSTANT_TAGS[k]}
    best = None
    for tag in [*balance_tags, *DEBT_DISCLOSURE_TAGS]:
        oldest = balance_floor if tag in balance_tags else period - timedelta(days=STALE_DAYS)
        newest = None
        for e in _entries(facts, tag, "USD"):
            day = _to_date(e.get("end"))
            if e.get("form") in ANNUAL_FORMS | QUARTER_FORMS and day and oldest <= day <= period + timedelta(days=120):
                key = (day, e.get("filed") or "")
                if newest is None or key > newest[0]:
                    newest = (key, e)
        if newest and float(newest[1].get("val") or 0) > 0:
            day = newest[0][0]
            if best is None or day > best[2]:
                best = (tag, float(newest[1]["val"]), day, bool(newest[1].get("start")))
    return best


def _debt_decision(facts: dict, latest: dict, period: date, fy_last: date | None, debt_any: dict[str, dict]) -> tuple[str, float, str | None]:
    """Total debt for the latest balance sheet: (status, value, note), decided once here for every view.

    "reported": a total is built from the debt tags at `period`. When that balance sheet tags no debt line but
    an earlier one in the same fiscal year does (CAT's 10-Qs tag debt only by segment), that total is used and
    the note says from which date. "none": no debt tag, debt disclosure or debt proceeds above zero in the last
    ~15 months, so total debt is 0.0. "unknown": the filings show debt that no standard total captures (BRK and
    F tag their borrowings only by segment), so it is NaN.
    """
    value = total_debt(latest)
    if np.isfinite(value):
        return "reported", value, None
    floor = min(fy_last - timedelta(days=7), period) if fy_last else period
    evidence = _debt_evidence(facts, period, floor)
    if evidence is None:
        return "none", 0.0, NO_DEBT_NOTE
    earlier = sorted({d for series in debt_any.values() for d in series if floor <= d < period}, reverse=True)
    for day in earlier:
        value = total_debt({k: float(debt_any[k][day]["val"]) for k in DEBT_KEYS if day in debt_any.get(k, {})})
        if np.isfinite(value):
            return "reported", value, (
                f"The latest balance sheet ({period}) tags no standard debt line, so total debt is the {money(value)} "
                f"reported at {day}. Check the latest filing's balance sheet if the company has borrowed or repaid since."
            )
    tag, amount, day, flow = evidence
    return "unknown", float("nan"), (
        f"Total debt is n/a: the filings show debt (XBRL {tag}, {money(amount)} {'for the period ended' if flow else 'at'} {day}) "
        f"but no standard debt total for the balance sheet of {period}, so enterprise value, EV/EBIT, EV/Sales, net debt, "
        "debt/equity, ROIC and the DCF's net cash are not shown. To value the company, read total debt from the filing's "
        "balance sheet and enter net cash in the DCF."
    )


def _derived_liabilities(total: float | None, equity_with_nci: float | None, equity: float | None, nci: float | None) -> float | None:
    """Total liabilities = total liabilities and equity (or assets) - total equity including noncontrolling interests."""
    if total is None or (equity_with_nci is None and equity is None):
        return None
    return total - (equity_with_nci if equity_with_nci is not None else equity + (nci or 0.0))


class Extracted(NamedTuple):
    table: pd.DataFrame
    ttm: dict[str, float]
    latest: dict[str, float]
    latest_period: str | None
    shares: float | None
    shares_date: str | None
    refs: dict[str, dict[pd.Timestamp, FactRef]]
    ttm_refs: dict[str, FactRef]
    notes: list[str]
    debt_status: str = "reported"
    year_ago: dict[str, float] = {}
    year_ago_period: str | None = None


def extract(facts: dict, years: int = 10) -> Extracted:
    """Company facts -> annual table, TTM flows, latest balance sheet, share count, provenance and caveats."""
    cik = int(facts.get("cik") or 0)
    annual_series: dict[str, dict[date, float]] = {}
    refs: dict[str, dict[pd.Timestamp, FactRef]] = {}
    found_ttm: dict[str, tuple[date, float, dict]] = {}
    notes: list[str] = []

    for metric, tags in DURATION_TAGS.items():
        unit = UNIT_FOR.get(metric, "USD")
        per_tag = [_entries(facts, tag, unit) for tag in tags]
        chosen = _merge([_annual_entries(e) for e in per_tag])
        annual_series[metric] = {k: float(v["val"]) for k, v in chosen.items()}
        refs[metric] = {pd.Timestamp(k): _ref(cik, v) for k, v in chosen.items()}
        # The tag must be consistent across the three TTM figures, so take
        # the tag whose TTM is most recent, breaking ties by priority.
        best = None
        for entries in per_tag:
            result = _ttm(entries)
            if result and (best is None or result[1] > best[0]):
                best = (result[1], result[0], result[2])
        if best is not None:
            found_ttm[metric] = best

    # Fiscal year ends come from the flow statements. Balance sheet instants
    # are then read at those dates; 10-Ks also carry instants for older dates
    # (equity roll-forwards) that would otherwise add half-empty rows.
    fy_ends = sorted(set().union(*(annual_series[m].keys() for m in ("revenue", "net_income", "operating_cash_flow"))))[-years:]
    fy_last = fy_ends[-1] if fy_ends else None

    # First Version: a tag the company stopped using still produced a "TTM" from its last fiscal
    # year, however old, and it outranked the current annual figure: AMZN's gross profit was FY2009's
    # $5.5B (gross margin 0.7%) and BRK's operating income came from a 2013 10-Q.
    # Current Version: a TTM is kept only if its period ends on or after the latest fiscal year end.
    ttm: dict[str, float] = {}
    ttm_refs: dict[str, FactRef] = {}
    ttm_ends: dict[str, date] = {}
    for metric, (end, value, entry) in found_ttm.items():
        if fy_last is None or end >= fy_last:
            ttm[metric], ttm_refs[metric], ttm_ends[metric] = value, _ref(cik, entry), end

    instant_annual: dict[str, dict[date, float]] = {}
    any_form = ANNUAL_FORMS | QUARTER_FORMS
    assets_any = _merge([_instant_entries(_entries(facts, t, "USD"), any_form) for t in INSTANT_TAGS["total_assets"]])
    latest_period = max(assets_any) if assets_any else None
    latest: dict[str, float] = {}
    helpers: dict[str, tuple[dict[date, float], float | None]] = {}
    # Every balance sheet figure by date, from 10-Ks and 10-Qs: the year-ago balance sheet and the debt decision read it.
    any_dates: dict[str, dict[date, dict]] = {}

    for metric, tags in {**INSTANT_TAGS, **HELPER_INSTANT_TAGS}.items():
        merged = _merge([_instant_entries(_entries(facts, t, "USD"), ANNUAL_FORMS) for t in tags])
        aligned, aligned_refs = {}, {}
        for fy in fy_ends:
            match = [d for d in merged if abs((d - fy).days) <= 7]
            if match:
                e = merged[min(match, key=lambda d: abs((d - fy).days))]
                aligned[fy] = float(e["val"])
                aligned_refs[pd.Timestamp(fy)] = _ref(cik, e)
        newest = None
        if latest_period:
            merged_any = any_dates[metric] = _merge([_instant_entries(_entries(facts, t, "USD"), any_form) for t in tags])
            if latest_period in merged_any:
                newest = float(merged_any[latest_period]["val"])
                if metric in INSTANT_TAGS:
                    latest[metric] = newest
                    ttm_refs.setdefault(metric, _ref(cik, merged_any[latest_period]))
        if metric in INSTANT_TAGS:
            instant_annual[metric], refs[metric] = aligned, aligned_refs
        else:
            helpers[metric] = (aligned, newest)

    # First Version: AMZN and KO tag no total liabilities line, so Altman Z had no input.
    # Current Version: derived from the balance sheet identity, and noted as derived.
    derived_at = []
    for fy in fy_ends:
        if fy not in instant_annual["total_liabilities"]:
            value = _derived_liabilities(
                helpers["liabilities_and_equity"][0].get(fy, instant_annual["total_assets"].get(fy)),
                helpers["equity_with_nci"][0].get(fy), instant_annual["equity"].get(fy), helpers["minority_interest"][0].get(fy))
            if value is not None:
                instant_annual["total_liabilities"][fy] = value
                derived_at.append(str(fy))
    if latest and "total_liabilities" not in latest:
        value = _derived_liabilities(
            helpers["liabilities_and_equity"][1] if helpers["liabilities_and_equity"][1] is not None else latest.get("total_assets"),
            helpers["equity_with_nci"][1], latest.get("equity"), helpers["minority_interest"][1])
        if value is not None:
            latest["total_liabilities"] = value
            derived_at.append(str(latest_period))

    # First Version: only the latest balance sheet and the fiscal year ends were kept, so ROE and ROA could not
    # average the trailing twelve months they divide into. Current Version: the balance sheet closest to 12 months
    # before the latest one (within 45 days), from 10-K or 10-Q facts, with the same figures as the latest.
    year_ago: dict[str, float] = {}
    year_ago_period = None
    near = [d for d in assets_any if latest_period and abs((d - (latest_period - timedelta(days=365))).days) <= 45]
    if near:
        year_ago_period = min(near, key=lambda d: abs((d - (latest_period - timedelta(days=365))).days))

        def at(metric: str) -> float | None:
            e = any_dates.get(metric, {}).get(year_ago_period)
            return float(e["val"]) if e else None

        year_ago = {m: at(m) for m in INSTANT_TAGS if at(m) is not None}
        if "total_liabilities" not in year_ago:
            value = _derived_liabilities(
                at("liabilities_and_equity") if at("liabilities_and_equity") is not None else year_ago.get("total_assets"),
                at("equity_with_nci"), year_ago.get("equity"), at("minority_interest"))
            if value is not None:
                year_ago["total_liabilities"] = value
                derived_at.append(str(year_ago_period))
        year_ago["total_debt"] = total_debt(year_ago)
    if derived_at:
        dates = sorted(set(derived_at))
        when = f"{len(dates)} balance sheets from {dates[0]} to {dates[-1]}" if len(dates) > 3 else ", ".join(dates)
        notes.append(f"Total liabilities ({when}) are derived as total liabilities and equity minus total equity including noncontrolling interests, because the filings do not tag a total liabilities line there.")

    columns = {m: pd.Series(annual_series[m], dtype="float64") for m in DURATION_TAGS}
    columns.update({m: pd.Series(instant_annual[m], dtype="float64") for m in INSTANT_TAGS})
    table = pd.DataFrame(columns)
    table = table.reindex(fy_ends) if fy_ends else table.iloc[0:0]
    table.index = pd.to_datetime(table.index)
    table = table.sort_index()

    # First Version: TTM gross profit came only from the GrossProfit tag, which AMZN last used in 2009.
    # Current Version: where gross profit is not tagged, it is revenue minus cost of revenue for the
    # same period, annual and TTM, and noted as derived.
    derived_gross = bool((table["gross_profit"].isna() & table["revenue"].notna() & table["cost_of_revenue"].notna()).any())
    table["gross_profit"] = table["gross_profit"].fillna(table["revenue"] - table["cost_of_revenue"])
    rev_end = ttm_ends.get("revenue")
    if rev_end is not None and ttm_ends.get("gross_profit") != rev_end and ttm_ends.get("cost_of_revenue") == rev_end:
        ttm["gross_profit"] = ttm["revenue"] - ttm["cost_of_revenue"]
        ttm_refs.pop("gross_profit", None)
        derived_gross = True
    if derived_gross:
        notes.append("Gross profit is derived as revenue minus cost of revenue, because the filings do not tag a gross profit line.")
    table["total_debt"] = [total_debt(row) for row in table.to_dict("records")] if len(table) else []

    if not latest and len(table):
        latest = {k: float(v) for k, v in table.iloc[-1].items() if pd.notna(v)}
        latest_period = table.index[-1].date()
    # First Version: sec.py noted "Total debt is n/a" whenever the latest balance sheet tagged no standard debt line,
    # while valuation.py separately treated missing debt as zero unless interest expense was tagged. SHOP, PLTR and
    # ARM carried both notes at once; DASH and PINS, whose convertible notes went unread, were called debt-free; CAT
    # and ORCL showed "n/a" beside ratios computed from an older debt figure.
    # Current Version: debt is decided once, here, for the latest balance sheet, with one note at most, and
    # valuation.py uses it as given: "reported" (a total from the debt tags), "none" (no debt figure of any kind
    # above zero in the last ~15 months: 0.0) or "unknown" (debt shown but no standard total: NaN).
    debt_status = "reported"
    if latest:
        debt_status, latest["total_debt"], debt_note = _debt_decision(facts, latest, latest_period, fy_last, {k: any_dates.get(k, {}) for k in DEBT_KEYS})
        if debt_note:
            notes.append(debt_note)

    if ttm and fy_last and max(ttm_ends.values()) <= fy_last:
        notes.append(f"{TTM_IS_FISCAL_YEAR} {fy_last}, so trailing-twelve-month figures equal that fiscal year.")

    shares, shares_date, shares_ref, share_notes = _share_count(facts, latest_period or fy_last, cik)
    if shares_ref:
        ttm_refs["shares_outstanding"] = shares_ref
    notes.extend(share_notes)

    return Extracted(table, ttm, latest, str(latest_period) if latest_period else None, shares, shares_date, refs, ttm_refs, notes,
                     debt_status, year_ago, str(year_ago_period) if year_ago_period else None)


def apply_splits(fund: Fundamentals, splits: pd.Series) -> list[str]:
    """Restate per-share history for stock splits, using Yahoo's split events.

    First Version: EPS and share counts were tabulated as filed. Apple's
    FY2016-17 figures only ever appeared in filings made before its 2020
    4-for-1 split, so EPS read 9.21 in 2017 and 2.98 in 2018, which wrecked
    the EPS growth rate and failed the F-score's dilution test.
    Current Version: any per-share value whose filing predates a split is
    restated by the split ratio. Values filed after a split are already
    restated by the company and are left alone. Safe to call twice.
    """
    if fund.splits_applied or splits is None or splits.empty:
        fund.splits_applied = True
        return fund.split_notes
    # First Version: a share count years out of date (SHOP's 2014 count) was multiplied by every split
    # since. Current Version: a stale count is never restated (extract no longer returns one either).
    shares_current = _current(_to_date(fund.shares_date), _to_date(fund.latest_period))
    notes = []
    for when, factor in splits.sort_index().items():
        if not np.isfinite(factor) or factor <= 0 or factor == 1:
            continue
        cutoff = when.strftime("%Y-%m-%d")
        changed = 0
        for metric in SPLIT_SENSITIVE:
            if metric not in fund.annual:
                continue
            for row_end, ref in fund.refs.get(metric, {}).items():
                if ref.filed and ref.filed < cutoff and row_end in fund.annual.index and pd.notna(fund.annual.at[row_end, metric]):
                    fund.annual.at[row_end, metric] = fund.annual.at[row_end, metric] / factor if metric == "eps_diluted" else fund.annual.at[row_end, metric] * factor
                    changed += 1
        if fund.shares_outstanding and fund.shares_date and shares_current and fund.shares_date < cutoff:
            fund.shares_outstanding *= factor
            changed += 1
        if changed:
            ratio = f"{factor:g}-for-1" if factor >= 1 else f"1-for-{1 / factor:g}"
            notes.append(f"Per-share figures filed before {cutoff} restated for the {ratio} split.")
    fund.split_notes = notes
    fund.splits_applied = True
    return notes


def fundamentals(symbol: str, email: str, force: bool = False) -> Fundamentals:
    symbol = validation.ticker(symbol)
    if demo.is_demo(symbol):
        return demo.fundamentals(symbol)

    headers = _headers(email)
    cik, title = lookup_cik(symbol, email)
    # The filing index comes first: it tells a fund from a company before the (large) company facts are fetched.
    subs = get_json(SUBMISSIONS_URL.format(cik=cik), headers=headers, ttl_s=0 if force else 6 * 3600, service=SERVICE)
    profile = subs.value or {}
    filings = parse_filings(cik, profile)
    reason = _fund_reason(profile, title, filings)
    if reason:
        raise DataError(reason)
    if not any(f.form in PERIODIC_FORMS for f in filings):
        filings += _older_filings(cik, profile, headers, force)

    facts = get_json(
        FACTS_URL.format(cik=cik),
        headers=headers,
        ttl_s=0 if force else 12 * 3600,
        service=SERVICE,
        not_found_message=f"{title} has no XBRL financial statements on EDGAR (ETFs, funds and trusts usually do not). Price, model, Monte Carlo and options views still work.",
    )
    if not (facts.value.get("facts") or {}).get("us-gaap"):
        # First Version: TSM was told only that it "does not report US GAAP figures", which did not say where its
        # statements are. Current Version: the refusal names the annual form it files (20-F or 40-F) and IFRS.
        annual = next((f.form for f in filings if f.form.split("/")[0] in ("20-F", "40-F")), None)
        basis = "IFRS figures" if (facts.value.get("facts") or {}).get("ifrs-full") else "figures that are not US GAAP"
        if annual:
            raise DataError(f"{title} files its annual reports on Form {annual.split('/')[0]} with {basis}, and FinLit Pro reads US GAAP statements only. "
                            f"Read its financial statements in the Form {annual.split('/')[0]} on sec.gov. Price, model, Monte Carlo and options views still work.")
        raise DataError(f"{title} does not report US GAAP figures in XBRL (foreign filers often use IFRS). Price, model, Monte Carlo and options views still work.")

    ex = extract(facts.value)
    if ex.table.empty:
        raise DataError(f"EDGAR has no annual (10-K) figures for {title} yet. Price, model, Monte Carlo and options views still work.")

    name = profile.get("name") or facts.value.get("entityName") or title
    notes = list(ex.notes)
    lag = _lag_note(facts.value, filings, ex.latest_period)
    if lag:
        notes.insert(0, lag)
    forms = {f.form for f in filings}
    fy_last = str(ex.table.index[-1].date())
    quarters_since = [f for f in filings if f.form in QUARTER_FORMS and (f.report_date or f.filed) > fy_last]
    if "6-K" in forms and not forms & QUARTER_FORMS:
        # A foreign issuer: say why there are no quarters instead of the general note.
        notes = [n for n in notes if not n.startswith(TTM_IS_FISCAL_YEAR)]
        notes.append(f"{name} reports quarters on Form 6-K, which FinLit Pro does not read, so trailing-twelve-month figures and the balance sheet come from its annual reports (latest {ex.latest_period}).")
    elif quarters_since and any(n.startswith(TTM_IS_FISCAL_YEAR) for n in notes):
        # First Version: C carried "No quarterly figures have been filed since the fiscal year ended 2025-12-31" beside
        # the lag note, although it had filed 10-Qs in May and August that SEC company facts did not include yet.
        # Current Version: when the filing index has 10-Qs after the fiscal year, the note says why they are not used.
        if lag:
            which = f"the {len(quarters_since)} 10-Qs filed since (the newest filed {quarters_since[0].filed})" if len(quarters_since) > 1 else f"the 10-Q filed {quarters_since[0].filed}"
            why = f"until SEC publishes XBRL data for {which}; refresh later to update them"
        else:
            why = "because SEC company facts hold no year-to-date figures from the 10-Qs filed since that match the annual ones"
        notes = [f"Trailing-twelve-month figures equal the fiscal year ended {fy_last} {why}." if n.startswith(TTM_IS_FISCAL_YEAR) else n for n in notes]

    company = COMPANY_URL.format(cik=cik)
    return Fundamentals(
        cik=cik,
        name=name,
        annual=ex.table,
        ttm=ex.ttm,
        latest=ex.latest,
        latest_period=ex.latest_period,
        shares_outstanding=ex.shares,
        sources=[
            Source("SEC EDGAR XBRL company facts", FACTS_URL.format(cik=cik), datetime.fromtimestamp(facts.saved_at), ex.latest_period, facts.status, f"CIK {cik}"),
            Source("SEC EDGAR filing index", company, datetime.fromtimestamp(subs.saved_at), status=subs.status),
        ],
        sic_description=profile.get("sicDescription"),
        fiscal_year_end=profile.get("fiscalYearEnd"),
        exchanges=list(profile.get("exchanges") or []),
        filings=filings,
        refs=ex.refs,
        ttm_refs=ex.ttm_refs,
        shares_date=ex.shares_date,
        notes=notes,
        debt_status=ex.debt_status,
        year_ago=ex.year_ago,
        year_ago_period=ex.year_ago_period,
    )


FUND_TYPES = ("ETF", "MUTUALFUND", "MONEYMARKET", "INDEX", "CRYPTOCURRENCY", "CURRENCY", "FUTURE")


def not_a_company(instrument_type: str | None, name: str = "") -> str | None:
    """A friendly reason SEC fundamentals do not apply, when Yahoo says the symbol is a fund, index or similar.

    Grantor trusts such as gold and bitcoin ETFs do file 10-Ks with XBRL, but their 'net income' is the
    change in value of what they hold, so statement ratios would be nonsense.
    """
    kind = (instrument_type or "").upper()
    if kind not in FUND_TYPES:
        return None
    label = {"ETF": "an exchange-traded fund", "MUTUALFUND": "a mutual fund", "MONEYMARKET": "a money market fund", "INDEX": "an index",
             "CRYPTOCURRENCY": "a cryptocurrency", "CURRENCY": "a currency", "FUTURE": "a futures contract"}[kind]
    who = name or "This symbol"
    return f"{who} is {label}, not an operating company, so company financial statements do not apply. Price, model, Monte Carlo and options views still work."
