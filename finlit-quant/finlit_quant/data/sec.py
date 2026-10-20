"""SEC EDGAR: the primary source for fundamentals.

Three free, keyless endpoints:

  company_tickers.json   ticker -> CIK (the SEC's company id)
  submissions/CIK*.json  company profile and the filing index
  companyfacts/CIK*.json every XBRL number the company has ever filed

The SEC requires a User-Agent naming the app and a contact email, and limits
clients to 10 requests a second. We make at most three requests per company
and cache them for hours, so the limit is never close.

Turning company facts into a clean table is the hard part, and the reasons are
documented where they bite: companies switch XBRL tags over the years, every
10-K repeats prior years as comparatives, restatements arrive in later
filings, and 10-Qs report year-to-date rather than quarterly figures.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import NamedTuple

import numpy as np
import pandas as pd

from finlit_quant import __version__, validation
from finlit_quant.data import demo
from finlit_quant.data.http import get_json
from finlit_quant.data.models import DataError, Filing, Fundamentals

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn}/{doc}"
SERVICE = "SEC EDGAR"

ANNUAL_FORMS = {"10-K", "10-K/A", "10-KT", "20-F", "40-F"}
QUARTER_FORMS = {"10-Q", "10-Q/A"}

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
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
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
    "debt_long_total": ["LongTermDebt"],
    "debt_noncurrent": ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations"],
    "debt_current_portion": ["LongTermDebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent"],
    "debt_current_all": ["DebtCurrent"],
    "short_borrowings": ["ShortTermBorrowings", "CommercialPaper"],
}

UNIT_FOR = {"eps_diluted": "USD/shares", "diluted_shares": "shares"}

# Per-share figures change meaning at a stock split. Filings made after a
# split restate the comparatives they repeat, but older years that only ever
# appeared in pre-split filings are never restated, so each value's filing
# date is kept to tell the two apart.
SPLIT_SENSITIVE = ("eps_diluted", "diluted_shares")


def _headers(email: str) -> dict[str, str]:
    contact = validation.email(email) if email else ""
    if not contact:
        raise DataError(
            "SEC EDGAR needs a contact email before it will answer. Open Settings, "
            "enter your email under SEC EDGAR, then press Analyze again."
        )
    return {"User-Agent": f"FinLitQuant/{__version__} {contact}", "Accept": "application/json"}


def _to_date(text: str | None) -> date | None:
    if not text:
        return None
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


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
        f"{sym} is not in the SEC's list of company filers. ETFs, indices, mutual funds, crypto and "
        "most non-US listings have no SEC company facts. The price, risk and Monte Carlo tabs still work."
    )


def parse_filings(cik: int, submissions: dict, limit: int = 300) -> list[Filing]:
    recent = ((submissions or {}).get("filings") or {}).get("recent") or {}
    forms = recent.get("form") or []
    out = []
    for i, form in enumerate(forms):
        try:
            accn = recent["accessionNumber"][i]
            doc = recent["primaryDocument"][i]
        except (KeyError, IndexError):
            continue
        url = ARCHIVE_URL.format(cik=cik, accn=accn.replace("-", ""), doc=doc) if doc else ""
        out.append(
            Filing(
                form=form,
                filed=(recent.get("filingDate") or [""] * (i + 1))[i] or "",
                report_date=(recent.get("reportDate") or [""] * (i + 1))[i] or "",
                description=(recent.get("primaryDocDescription") or [""] * (i + 1))[i] or "",
                url=url,
            )
        )
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------------
# Company facts -> tables
# ---------------------------------------------------------------------------


def _entries(facts: dict, tag: str, unit: str) -> list[dict]:
    for taxonomy in ("us-gaap", "dei"):
        node = ((facts or {}).get("facts") or {}).get(taxonomy, {}).get(tag)
        if node:
            return list((node.get("units") or {}).get(unit) or [])
    return []


def _annual_duration(entries: list[dict]) -> dict[date, float]:
    return {k: float(v["val"]) for k, v in _annual_entries(entries).items()}


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
        if not start or not end or not 340 <= (end - start).days <= 390:
            continue
        if end not in best or (e.get("filed") or "") > (best[end].get("filed") or ""):
            best[end] = e
    return best


def _instants(entries: list[dict], forms: set[str]) -> dict[date, float]:
    best: dict[date, dict] = {}
    for e in entries:
        if e.get("form") not in forms or e.get("start"):
            continue
        end = _to_date(e.get("end"))
        if not end:
            continue
        if end not in best or (e.get("filed") or "") > (best[end].get("filed") or ""):
            best[end] = e
    return {k: float(v["val"]) for k, v in best.items()}


def _merge(series_by_priority: list[dict[date, float]]) -> dict[date, float]:
    merged: dict[date, float] = {}
    for series in reversed(series_by_priority):
        merged.update(series)  # higher priority overwrites
    return merged


def _ttm(entries: list[dict]) -> tuple[float, date] | None:
    """Trailing twelve months from one tag, or None.

    TTM = last fiscal year + this year's year-to-date - last year's same
    year-to-date. 10-Qs report year-to-date figures, so this is the one
    formula that works for Q1, Q2 and Q3 alike without reconstructing
    individual quarters.
    """
    annual = _annual_duration(entries)
    if not annual:
        return None
    fy_end = max(annual)
    fy_value = annual[fy_end]

    ytd: list[tuple[date, int, dict]] = []
    for e in entries:
        if e.get("form") not in QUARTER_FORMS:
            continue
        start, end = _to_date(e.get("start")), _to_date(e.get("end"))
        if not start or not end or end <= fy_end or start <= fy_end - timedelta(days=5):
            continue
        ytd.append((end, (end - start).days, e))
    if not ytd:
        return fy_value, fy_end

    latest_end = max(item[0] for item in ytd)
    cur_end, cur_days, cur = max((i for i in ytd if i[0] == latest_end), key=lambda i: i[1])
    target = cur_end - timedelta(days=364)
    for e in entries:
        start, end = _to_date(e.get("start")), _to_date(e.get("end"))
        if not start or not end:
            continue
        if abs((end - target).days) <= 10 and abs((end - start).days - cur_days) <= 10:
            return fy_value + float(cur["val"]) - float(e["val"]), cur_end
    return fy_value, fy_end


def _shares_outstanding(facts: dict) -> tuple[float, str] | None:
    """Latest cover-page share count and its as-of date, summing share classes in one filing."""
    entries = _entries(facts, "EntityCommonStockSharesOutstanding", "shares")
    if not entries:
        entries = _entries(facts, "CommonStockSharesOutstanding", "shares")
    if not entries:
        return None
    groups: dict[tuple[str, str], set[float]] = defaultdict(set)
    for e in entries:
        if e.get("end") and e.get("val"):
            groups[(e["end"], e.get("accn", ""))].add(float(e["val"]))
    if not groups:
        return None
    latest = max(groups, key=lambda k: (k[0], k[1]))
    return float(sum(groups[latest])), latest[0]


def total_debt(row: dict) -> float:
    """Combine the debt tags without double counting the current portion.

    LongTermDebt already includes its current maturities, so only true
    short-term borrowings are added to it. DebtCurrent already includes the
    current portion of long-term debt, so it pairs with the non-current tag.
    """

    def get(key: str) -> float | None:
        v = row.get(key)
        return None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)

    if get("debt_long_total") is not None:
        return get("debt_long_total") + (get("short_borrowings") or 0.0)
    if get("debt_current_all") is not None:
        return (get("debt_noncurrent") or 0.0) + get("debt_current_all")
    return (get("debt_noncurrent") or 0.0) + (get("debt_current_portion") or 0.0) + (get("short_borrowings") or 0.0)


class Extracted(NamedTuple):
    table: pd.DataFrame
    ttm: dict[str, float]
    latest: dict[str, float]
    latest_period: str | None
    shares: float | None
    shares_date: str | None
    filed: dict[str, dict[pd.Timestamp, str]]


def extract(facts: dict, years: int = 10) -> Extracted:
    """Company facts -> annual table, TTM flows, latest balance sheet and share count."""
    annual_series: dict[str, dict[date, float]] = {}
    ttm: dict[str, float] = {}
    filed: dict[str, dict[pd.Timestamp, str]] = {}

    for metric, tags in DURATION_TAGS.items():
        unit = UNIT_FOR.get(metric, "USD")
        per_tag = [_entries(facts, tag, unit) for tag in tags]
        chosen = _merge([_annual_entries(e) for e in per_tag])
        annual_series[metric] = {k: float(v["val"]) for k, v in chosen.items()}
        if metric in SPLIT_SENSITIVE:
            filed[metric] = {pd.Timestamp(k): v.get("filed") or "" for k, v in chosen.items()}
        # For TTM the tag must be consistent across the three figures, so pick
        # the tag whose TTM is most recent, breaking ties by priority.
        best: tuple[date, int, float] | None = None
        for priority, entries in enumerate(per_tag):
            result = _ttm(entries)
            if result is None:
                continue
            value, end = result
            if best is None or end > best[0]:
                best = (end, priority, value)
        if best is not None:
            ttm[metric] = best[2]

    # Fiscal year ends come from the flow statements. Balance sheet instants
    # are then read at those dates; 10-Ks also carry instants for older dates
    # (equity roll-forwards) that would otherwise add half-empty rows.
    fy_ends = sorted(set().union(*(annual_series[m].keys() for m in ("revenue", "net_income", "operating_cash_flow"))))
    fy_ends = fy_ends[-years:]

    instant_annual: dict[str, dict[date, float]] = {}
    latest_assets = _merge([_instants(_entries(facts, t, "USD"), ANNUAL_FORMS | QUARTER_FORMS) for t in INSTANT_TAGS["total_assets"]])
    latest_period = max(latest_assets) if latest_assets else None
    latest: dict[str, float] = {}

    for metric, tags in INSTANT_TAGS.items():
        per_tag_annual = [_instants(_entries(facts, t, "USD"), ANNUAL_FORMS) for t in tags]
        merged = _merge(per_tag_annual)
        aligned = {}
        for fy in fy_ends:
            match = [d for d in merged if abs((d - fy).days) <= 7]
            if match:
                aligned[fy] = merged[min(match, key=lambda d: abs((d - fy).days))]
        instant_annual[metric] = aligned
        if latest_period:
            any_form = _merge([_instants(_entries(facts, t, "USD"), ANNUAL_FORMS | QUARTER_FORMS) for t in tags])
            if latest_period in any_form:
                latest[metric] = any_form[latest_period]

    columns = {m: pd.Series(annual_series[m]) for m in DURATION_TAGS}
    columns.update({m: pd.Series(instant_annual[m]) for m in INSTANT_TAGS})
    table = pd.DataFrame(columns)
    if fy_ends:
        table = table.reindex(fy_ends)
    else:
        table = table.iloc[0:0]
    table.index = pd.to_datetime(table.index)
    table = table.sort_index()

    if "gross_profit" in table and "revenue" in table and "cost_of_revenue" in table:
        table["gross_profit"] = table["gross_profit"].fillna(table["revenue"] - table["cost_of_revenue"])
    table["total_debt"] = [total_debt(row) for row in table.to_dict("records")] if len(table) else []

    if latest:
        latest["total_debt"] = total_debt(latest)
    elif len(table):
        latest = {k: float(v) for k, v in table.iloc[-1].items() if pd.notna(v)}
        latest_period = str(table.index[-1].date())

    # Companies with several share classes report each class with a
    # dimension, which companyfacts omits, so the cover count can be missing.
    # Diluted weighted shares are then the best available stand-in.
    cover = _shares_outstanding(facts)
    shares, shares_date = cover if cover else (None, None)
    if shares is None and len(table) and pd.notna(table["diluted_shares"].iloc[-1]):
        shares = float(table["diluted_shares"].iloc[-1])
        shares_date = filed.get("diluted_shares", {}).get(table.index[-1])

    return Extracted(table, ttm, latest, (str(latest_period) if latest_period else None), shares, shares_date, filed)


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
    notes = []
    for when, factor in splits.sort_index().items():
        if not np.isfinite(factor) or factor <= 0 or factor == 1:
            continue
        cutoff = when.strftime("%Y-%m-%d")
        changed = 0
        for metric in SPLIT_SENSITIVE:
            if metric not in fund.annual:
                continue
            for row_end, filed_on in fund.filed_dates.get(metric, {}).items():
                if filed_on and filed_on < cutoff and row_end in fund.annual.index and pd.notna(fund.annual.at[row_end, metric]):
                    if metric == "eps_diluted":
                        fund.annual.at[row_end, metric] /= factor
                    else:
                        fund.annual.at[row_end, metric] *= factor
                    changed += 1
        if fund.shares_outstanding and fund.shares_date and fund.shares_date < cutoff:
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
    ttl = 0 if force else 12 * 3600
    facts = get_json(
        FACTS_URL.format(cik=cik),
        headers=headers,
        ttl_s=ttl,
        service=SERVICE,
        not_found_message=f"{title} has no XBRL financial data on EDGAR. Very new or very small filers sometimes do not.",
    )
    subs = get_json(SUBMISSIONS_URL.format(cik=cik), headers=headers, ttl_s=0 if force else 6 * 3600, service=SERVICE)

    if not (facts.value.get("facts") or {}).get("us-gaap"):
        raise DataError(
            f"{title} does not report US GAAP numbers to the SEC (foreign filers often use IFRS). "
            "The price, risk and Monte Carlo tabs still work."
        )

    ex = extract(facts.value)
    if ex.table.empty:
        raise DataError(f"EDGAR has no annual (10-K) figures for {title} yet, so there is nothing to tabulate.")

    profile = subs.value or {}
    return Fundamentals(
        cik=cik,
        name=profile.get("name") or facts.value.get("entityName") or title,
        annual=ex.table,
        ttm=ex.ttm,
        latest=ex.latest,
        latest_period=ex.latest_period,
        shares_outstanding=ex.shares,
        shares_date=ex.shares_date,
        filed_dates=ex.filed,
        sic_description=profile.get("sicDescription"),
        fiscal_year_end=profile.get("fiscalYearEnd"),
        exchanges=list(profile.get("exchanges") or []),
        filings=parse_filings(cik, profile),
        source="stale" if "stale" in (facts.source, subs.source) else facts.source,
    )
