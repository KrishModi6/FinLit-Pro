"""Fundamental ratios, quality scores, and discounted cash flow valuation.

Everything takes a Fundamentals (from SEC EDGAR) plus the live price, so the
multiples always use today's market value against the latest filed numbers.
Missing inputs give NaN rather than a guess: a ratio that cannot be computed
from what the company filed is shown as blank.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from finlit_pro.data.models import Fundamentals
from finlit_pro.fmt import money
from finlit_pro.validation import ValidationError

NAN = float("nan")

# SEC industry (SIC) descriptions of banks, savings institutions, insurers, brokers, exchanges and lenders, e.g.
# "National Commercial Banks", "Savings Institution, Federally Chartered", "Fire, Marine & Casualty Insurance",
# "Security Brokers, Dealers & Flotation Companies" (GS, SCHW), "Security & Commodity Brokers, Dealers, Exchanges &
# Services" (CME, ICE), "Commodity Contracts Brokers & Dealers", "Loan Brokers", "Mortgage Bankers & Loan
# Correspondents", "Personal Credit Institutions", "Finance Services" (AXP, COIN), "Finance Lessors".
# First Version: "security brokers" missed CME's "Security & Commodity Brokers, ...", and altman_z kept its own wider
# list ("finance", "insurance"), so AON was "Not meaningful" there but scored everywhere else. Current Version: one
# list, used by ratios, the DCF, Piotroski and Altman alike. ("Dealers" alone would match "Retail-Auto Dealers", and
# "credit" alone "Services-Consumer Credit Reporting", so neither is used.)
FINANCIAL_SIC_WORDS = ("bank", "savings", "insurance", "brokers", "exchanges", "finance services", "finance lessors", "credit institution", "credit agencies")
# Insurance agents and brokers (AON, AJG, WTW) sell policies without carrying the risk, so their cash flow means what it does elsewhere.
NOT_FINANCIAL_SIC_WORDS = ("insurance agents",)
# Real estate investment trusts are not financial companies, but the Altman Z (built for manufacturers) does not describe them.
REIT_SIC_WORDS = ("real estate investment",)

FINANCIAL_KIND = "financial companies (banks, insurers, brokers and lenders)"
FINANCIAL_NOTE = (
    "Free cash flow, enterprise value, net debt, debt/equity, ROIC, the DCF and the Piotroski and Altman scores are not shown "
    f"for {FINANCIAL_KIND} (SEC industry: {{sic}}). Cash-flow and leverage measures do not describe their business: "
    "deposits, loans, policy reserves, customer balances and trading positions are its operations rather than its financing. "
    "P/E, P/B, ROE and dividend yield still apply."
)
FINANCIAL_DCF = (
    f"A cash-flow DCF does not value {FINANCIAL_KIND}: their cash flow swings with deposits, loans, customer balances and "
    "trading positions, and borrowing is part of the business rather than its financing. Compare it on P/E, P/B, ROE and dividend yield instead."
)
NOT_MEANINGFUL = "Not meaningful for financial companies"
NOT_MEANINGFUL_REIT = "Not meaningful for REITs"


def is_financial(sic_description: str | None) -> bool:
    """A bank, savings institution, insurer, broker-dealer, exchange or lender, from its SEC industry description."""
    sic = (sic_description or "").lower()
    return any(w in sic for w in FINANCIAL_SIC_WORDS) and not any(w in sic for w in NOT_FINANCIAL_SIC_WORDS)


def _note(fund: Fundamentals, text: str) -> None:
    """Add a caveat once; ratios are recomputed whenever the price or the inputs change."""
    if text not in fund.notes:
        fund.notes.append(text)


def _f(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return NAN
    return v if np.isfinite(v) else NAN


def _div(a, b) -> float:
    a, b = _f(a), _f(b)
    if np.isnan(a) or np.isnan(b) or b == 0:
        return NAN
    return a / b


def cagr(series: pd.Series, years: int) -> float:
    """Annual growth from the value `years` fiscal years before the latest reported one to that latest value.

    First Version: the start was the value `years` reported values back, so a fiscal year missing in between
    stretched the period: DELL's "5-year" EPS CAGR (23.2%) ran over six years (19.0% over the real span).
    Current Version: the start is the fiscal year `years` rows back, NaN if it is not reported or if the dates
    do not span about `years` years (a fiscal year row missing altogether).
    """
    valid = np.flatnonzero(series.notna().to_numpy())
    if not len(valid) or valid[-1] < years:
        return NAN
    pos = int(valid[-1])
    start, end = _f(series.iloc[pos - years]), _f(series.iloc[pos])
    if isinstance(series.index, pd.DatetimeIndex):
        elapsed = (series.index[pos] - series.index[pos - years]).days / 365.25
        if abs(elapsed - years) > 0.15:
            return NAN
    if np.isnan(start) or start <= 0 or end <= 0:
        return NAN
    return (end / start) ** (1 / years) - 1


def flow(fund: Fundamentals, key: str) -> float:
    """TTM if available, else the last fiscal year's value; NaN rather than an older year's.

    First Version: with no TTM value, the newest fiscal year that reported the item was used, however old, so
    PLTR's interest coverage of 759x and SHOP's 527x came from interest expense of years ago, and AAPL's 39x from
    FY2023. Current Version: TTM or the last fiscal year only (see _last_year), and NaN otherwise.
    """
    v = _f(fund.ttm.get(key))
    return v if np.isfinite(v) else _last_year(fund, key)


def balance(fund: Fundamentals, key: str) -> float:
    """The latest balance sheet's value, else the last fiscal year end's; NaN rather than an older year's.

    First Version: fell back to the newest fiscal year with any value. Current Version: see _current.
    """
    return _current(fund, key)


def _last_year(fund: Fundamentals, key: str) -> float:
    """The value in the last fiscal year's row, NaN if that year does not report it (never an older year)."""
    a = fund.annual
    return _f(a[key].iloc[-1]) if key in a and len(a) else NAN


def _current(fund: Fundamentals, key: str) -> float:
    """The latest balance sheet's value, else the last fiscal year end's; NaN rather than an older year's."""
    return _f(fund.latest[key]) if np.isfinite(_f(fund.latest.get(key))) else _last_year(fund, key)


def _returns_base(fund: Fundamentals, key: str) -> tuple[float, float]:
    """(net income, average balance) over matching periods, for ROE (equity) and ROA (total assets).

    First Version: TTM net income through the latest 10-Q over the average of the last two fiscal-year-end
    balances, which can be up to 18 months older. NVDA's equity doubled in that time, so its ROE read 163% and
    its ROA 121%. Second Version: the average of the latest 10-Q and the last fiscal year end, which often falls
    mid-way through the trailing year, so a growing company's ROE read low (NVDA 99.9% against 117.2%).
    Current Version: TTM net income over the average of the latest balance sheet and the one about twelve months
    before it (fund.year_ago), so both span the same trailing year (NVDA 117%). Without a year-ago balance sheet,
    the second version's rule applies.
    """
    latest, year_ago, ttm_income = _f(fund.latest.get(key)), _f((fund.year_ago or {}).get(key)), _f(fund.ttm.get("net_income"))
    if np.isfinite(latest) and np.isfinite(year_ago) and np.isfinite(ttm_income):
        return ttm_income, (latest + year_ago) / 2
    a = fund.annual
    fy_end = a.index[-1] if len(a) else None
    fy_value, latest, ttm_income = _last_year(fund, key), _f(fund.latest.get(key)), _f(fund.ttm.get("net_income"))
    after_fy = bool(fund.latest_period) and fy_end is not None and pd.Timestamp(fund.latest_period) > fy_end + pd.Timedelta(days=7)
    if after_fy and np.isfinite(latest) and np.isfinite(fy_value) and np.isfinite(ttm_income):
        # The latest balance sheet is a 10-Q after the last fiscal year end: TTM income (which ends at that
        # quarter) over the average of the quarter's balance and the fiscal-year-end balance inside the TTM period.
        return ttm_income, (latest + fy_value) / 2
    previous = _f(a[key].iloc[-2]) if key in a and len(a) >= 2 else NAN
    income = _last_year(fund, "net_income")
    if np.isfinite(fy_value) and np.isfinite(previous) and np.isfinite(income):
        # Otherwise the last fiscal year: its income over the average of its opening and closing balances.
        return income, (fy_value + previous) / 2
    # One fiscal year of history: the latest income over the latest balance.
    return flow(fund, "net_income"), balance(fund, key)


def ratios(fund: Fundamentals, price: float, dividends_ttm: float = 0.0) -> dict[str, float]:
    a = fund.annual
    financial = is_financial(fund.sic_description)
    shares = _f(fund.shares_outstanding)
    mcap = price * shares if np.isfinite(shares) else NAN
    cash = _f(balance(fund, "cash"))
    st_inv = balance(fund, "short_investments")
    liquid = cash + (0 if np.isnan(st_inv) else st_inv)
    liquid0 = 0 if np.isnan(liquid) else liquid

    revenue, net_income = flow(fund, "revenue"), flow(fund, "net_income")
    op_income, gross = flow(fund, "operating_income"), flow(fund, "gross_profit")
    ocf, capex = flow(fund, "operating_cash_flow"), flow(fund, "capex")
    fcf = ocf - (0 if np.isnan(capex) else capex)

    # First Version: missing debt counted as zero, and balance() fell back to the newest year with any debt
    # tag, so PLTR's zero from 2021 stood in for today and BRK, which tags its borrowings under its own names,
    # showed no debt and net cash. Second Version: with no debt tag, zero unless interest expense was reported,
    # else NaN; DASH and PINS (convertible notes, no interest tag) were called debt-free, while TTD, DOCU and ROKU
    # (no debt, small interest expense) lost EV and the DCF, and both notes could sit beside sec.py's own.
    # Current Version: sec.py decides debt once (fund.debt_status) and notes it; here total debt is used as given:
    # 0.0 for "none", NaN for "unknown", which leaves EV, EV/EBIT, EV/Sales, net debt, D/E, ROIC and the DCF's
    # net cash NaN. Interest expense plays no part.
    if fund.debt_status == "none":
        debt = 0.0
    elif fund.debt_status == "unknown":
        debt = NAN
    else:
        debt = _current(fund, "total_debt")
    ev = mcap + debt - liquid0
    # P/E as market cap over TTM net income. Summing reported EPS across a
    # 10-K and a 10-Q mixes pre- and post-split figures when a split lands
    # in between; net income has no such problem.
    eps = _div(net_income, shares)
    equity = balance(fund, "equity")
    assets = balance(fund, "total_assets")

    pretax, tax = flow(fund, "pretax_income"), flow(fund, "income_tax")
    tax_rate = _div(tax, pretax)
    if np.isnan(tax_rate) or not 0 <= tax_rate <= 0.5:
        tax_rate = 0.21  # US statutory rate when the effective one is unusable

    # First Version: invested capital was debt + equity - all cash, so PLTR, whose cash and short-term
    # investments are 96% of its equity, showed a ROIC of 712%. Current Version: when invested capital is
    # under 10% of debt plus equity, the ratio is NaN and a note says why.
    capital = debt + equity
    invested = capital - liquid0
    roic = _div(op_income * (1 - tax_rate), invested) if invested > 0 else NAN
    if np.isfinite(capital) and capital > 0 and invested < 0.1 * capital:
        roic = NAN
        if not financial:
            _note(fund, f"ROIC is not shown: cash and short-term investments ({money(liquid0)}) exceed most of the capital "
                        f"(debt plus equity of {money(capital)}), so invested capital is under 10% of it and the ratio would not be meaningful.")

    equity_avg_income, equity_avg = _returns_base(fund, "equity")
    assets_avg_income, assets_avg = _returns_base(fund, "total_assets")
    pe = _div(mcap, net_income) if np.isfinite(net_income) and net_income > 0 else NAN

    out = {
        "market_cap": mcap,
        "enterprise_value": ev,
        "pe": pe,
        "earnings_yield": _div(eps, price),
        "ps": _div(mcap, revenue),
        "pb": _div(mcap, equity) if np.isfinite(equity) and equity > 0 else NAN,
        "ev_sales": _div(ev, revenue),
        "ev_ebit": _div(ev, op_income) if np.isfinite(op_income) and op_income > 0 else NAN,
        "fcf": fcf,
        "fcf_yield": _div(fcf, mcap),
        "fcf_per_share": _div(fcf, shares),
        "dividend_yield": _div(dividends_ttm, price) if dividends_ttm else 0.0,
        "gross_margin": _div(gross, revenue),
        "operating_margin": _div(op_income, revenue),
        "net_margin": _div(net_income, revenue),
        "fcf_margin": _div(fcf, revenue),
        "roe": _div(equity_avg_income, equity_avg) if equity_avg > 0 else NAN,
        "roa": _div(assets_avg_income, assets_avg),
        "roic": roic,
        "current_ratio": _div(balance(fund, "current_assets"), balance(fund, "current_liabilities")),
        "debt_to_equity": _div(debt, equity) if np.isfinite(equity) and equity > 0 else NAN,
        "net_debt": debt - liquid0,  # NaN when debt is NaN
        "interest_coverage": _div(op_income, flow(fund, "interest_expense")),
        "asset_turnover": _div(revenue, assets),
        "sbc_to_revenue": _div(flow(fund, "sbc"), revenue),
        "rnd_to_revenue": _div(flow(fund, "rnd"), revenue),
        "revenue_cagr_3y": cagr(a.get("revenue", pd.Series(dtype=float)), 3),
        "revenue_cagr_5y": cagr(a.get("revenue", pd.Series(dtype=float)), 5),
        "eps_cagr_5y": cagr(a.get("eps_diluted", pd.Series(dtype=float)), 5),
        "fcf_cagr_5y": cagr((a.get("operating_cash_flow", pd.Series(dtype=float)) - a.get("capex", pd.Series(dtype=float)).fillna(0)), 5),
        "share_change_3y": cagr(a.get("diluted_shares", pd.Series(dtype=float)), 3),
        "tax_rate": tax_rate,
        "revenue": revenue,
        "net_income": net_income,
        "eps": eps,
        "shares": shares,
    }
    if financial:
        # First Version: JPM showed FCF of -$162.5B and an FCF yield of -18.2%, because a bank's operating
        # cash flow swings with its trading and lending balances. Current Version: cash-flow and leverage
        # measures are NaN for banks and insurers, with one note; P/E, P/B, ROE and dividend yield stay.
        for key in ("fcf", "fcf_yield", "fcf_per_share", "fcf_margin", "fcf_cagr_5y", "enterprise_value", "ev_sales", "ev_ebit", "net_debt", "debt_to_equity", "roic"):
            out[key] = NAN
        _note(fund, FINANCIAL_NOTE.format(sic=fund.sic_description))
    return out


# ---------------------------------------------------------------------------
# Quality scores
# ---------------------------------------------------------------------------


@dataclass
class Check:
    name: str
    passed: bool | None  # None = could not be computed from the filings
    detail: str


def piotroski(annual: pd.DataFrame, sic_description: str | None = None) -> tuple[int, int, list[Check]]:
    """Piotroski F-score: nine pass/fail tests of profitability, leverage and efficiency.

    Uses the last two fiscal years. Returns (score, tests that could be run, checks).
    """
    # First Version: JPM scored 2/7 and BRK 2/6 on tests of cash flow, leverage and current ratio that do
    # not apply to banks and insurers. Current Version: not meaningful for financial companies, with no tests run.
    if is_financial(sic_description):
        return 0, 0, [Check(NOT_MEANINGFUL, None, f"The F-score's cash-flow, leverage and current-ratio tests do not describe {FINANCIAL_KIND}. Judge it on ROE, P/B and dividend yield instead.")]
    if len(annual) < 3:
        return 0, 0, [Check("Not enough history", None, "The F-score needs three fiscal years of filings.")]
    cur, prev, prev2 = annual.iloc[-1], annual.iloc[-2], annual.iloc[-3]

    def g(row, key):
        return _f(row.get(key))

    roa = _div(g(cur, "net_income"), g(prev, "total_assets"))
    roa_prev = _div(g(prev, "net_income"), g(prev2, "total_assets"))
    cfo = g(cur, "operating_cash_flow")
    lev = _div(g(cur, "total_debt"), (g(cur, "total_assets") + g(prev, "total_assets")) / 2)
    lev_prev = _div(g(prev, "total_debt"), (g(prev, "total_assets") + g(prev2, "total_assets")) / 2)
    cr = _div(g(cur, "current_assets"), g(cur, "current_liabilities"))
    cr_prev = _div(g(prev, "current_assets"), g(prev, "current_liabilities"))
    gm = _div(g(cur, "gross_profit"), g(cur, "revenue"))
    gm_prev = _div(g(prev, "gross_profit"), g(prev, "revenue"))
    at = _div(g(cur, "revenue"), g(prev, "total_assets"))
    at_prev = _div(g(prev, "revenue"), g(prev2, "total_assets"))
    sh, sh_prev = g(cur, "diluted_shares"), g(prev, "diluted_shares")

    def test(name, ok_expr, values, detail):
        if any(np.isnan(v) for v in values):
            return Check(name, None, "Not reported in the filings")
        return Check(name, bool(ok_expr), detail)

    checks = [
        test("Positive return on assets", roa > 0, [roa], f"ROA {roa:.1%}" if np.isfinite(roa) else ""),
        test("Positive operating cash flow", cfo > 0, [cfo], f"CFO {cfo / 1e6:,.0f}M" if np.isfinite(cfo) else ""),
        test("ROA improved", roa > roa_prev, [roa, roa_prev], f"{roa_prev:.1%} to {roa:.1%}" if np.isfinite(roa) and np.isfinite(roa_prev) else ""),
        test("Cash flow exceeds net income", cfo > g(cur, "net_income"), [cfo, g(cur, "net_income")], f"CFO {cfo / 1e6:,.0f}M vs net income {g(cur, 'net_income') / 1e6:,.0f}M"),
        test("Leverage fell", lev < lev_prev, [lev, lev_prev], f"Debt/assets {lev_prev:.2f} to {lev:.2f}" if np.isfinite(lev) and np.isfinite(lev_prev) else ""),
        test("Current ratio improved", cr > cr_prev, [cr, cr_prev], f"{cr_prev:.2f} to {cr:.2f}" if np.isfinite(cr) and np.isfinite(cr_prev) else ""),
        test("No share dilution", sh <= sh_prev * 1.001, [sh, sh_prev], f"Diluted shares {sh_prev / 1e6:,.0f}M to {sh / 1e6:,.0f}M" if np.isfinite(sh) and np.isfinite(sh_prev) else ""),
        test("Gross margin improved", gm > gm_prev, [gm, gm_prev], f"{gm_prev:.1%} to {gm:.1%}" if np.isfinite(gm) and np.isfinite(gm_prev) else ""),
        test("Asset turnover improved", at > at_prev, [at, at_prev], f"{at_prev:.2f}x to {at:.2f}x" if np.isfinite(at) and np.isfinite(at_prev) else ""),
    ]
    runnable = [c for c in checks if c.passed is not None]
    return sum(1 for c in runnable if c.passed), len(runnable), checks


def altman_z(fund: Fundamentals, market_cap: float) -> tuple[float, str]:
    """Altman Z-score (original public-manufacturer weights).

    Not meaningful for financial companies, whose balance sheets are mostly
    financial assets and liabilities, nor for REITs; the zone label says so.
    """
    # First Version: the missing-data check ran first, so JPM read "Not enough balance sheet data" and the
    # financial-company label was never reached. Current Version: the industry is checked first.
    # First Version: its own word list ("finance", "insurance", ...) called AON financial here only, and missed CME.
    # Current Version: is_financial() decides, as everywhere else; REITs keep their own label.
    if is_financial(fund.sic_description):
        return NAN, NOT_MEANINGFUL
    if any(word in (fund.sic_description or "").lower() for word in REIT_SIC_WORDS):
        return NAN, NOT_MEANINGFUL_REIT
    ta = balance(fund, "total_assets")
    tl = balance(fund, "total_liabilities")
    wc = balance(fund, "current_assets") - balance(fund, "current_liabilities")
    re_ = balance(fund, "retained_earnings")
    ebit = flow(fund, "operating_income")
    sales = flow(fund, "revenue")
    parts = [_div(wc, ta), _div(re_, ta), _div(ebit, ta), _div(market_cap, tl), _div(sales, ta)]
    if any(np.isnan(p) for p in parts):
        return NAN, "Not enough balance sheet data"
    z = 1.2 * parts[0] + 1.4 * parts[1] + 3.3 * parts[2] + 0.6 * parts[3] + 1.0 * parts[4]
    if z > 2.99:
        return z, "Safe zone (above 2.99)"
    if z >= 1.81:
        return z, "Grey zone (1.81 to 2.99)"
    return z, "Distress zone (below 1.81)"


# ---------------------------------------------------------------------------
# Discounted cash flow
# ---------------------------------------------------------------------------


@dataclass
class DCFInputs:
    base_fcf: float
    growth: float  # stage-one annual growth, decimal
    discount: float
    terminal_growth: float
    net_cash: float
    shares: float
    years_high: int = 5
    years_fade: int = 5
    refusal: str = ""  # why a DCF does not apply to this company at all (banks and insurers)

    def validate(self) -> None:
        if self.refusal:
            raise ValidationError(self.refusal)
        if not np.isfinite(self.base_fcf) or self.base_fcf <= 0:
            raise ValidationError(
                "Free cash flow is zero or negative, so a cash-flow DCF cannot value this company. "
                "Enter a positive base free cash flow you expect it to reach, or use the multiples instead."
            )
        if not np.isfinite(self.shares) or self.shares <= 0:
            raise ValidationError("The share count is missing, so there is no per-share value. Check the SEC data loaded.")
        if not np.isfinite(self.net_cash):
            # First Version: blamed interest expense, which no longer decides debt. Current Version: names the actual reason.
            raise ValidationError(
                "Net cash is unknown because the filings show debt that no standard XBRL total captures (see the notes). "
                "Enter net cash (cash and short-term investments minus debt, negative for net debt) from the latest balance sheet."
            )
        if self.discount <= self.terminal_growth:
            raise ValidationError(
                f"The discount rate ({self.discount:.1%}) must be higher than terminal growth "
                f"({self.terminal_growth:.1%}), or the terminal value is infinite. Raise the discount rate or lower terminal growth."
            )
        if self.discount <= 0:
            raise ValidationError("The discount rate must be greater than zero. Typical values are 7% to 12%.")
        if self.terminal_growth > 0.05:
            raise ValidationError("Terminal growth above 5% forever implies the company outgrows the economy. Use 2% to 3%.")


@dataclass
class DCFResult:
    per_share: float
    enterprise_value: float
    equity_value: float
    pv_explicit: float
    pv_terminal: float
    flows: list[tuple[int, float, float, float]]  # (year, growth, fcf, present value)


def dcf(inp: DCFInputs) -> DCFResult:
    """Two-stage DCF: `years_high` at `growth`, then a linear fade to terminal growth."""
    inp.validate()
    fcf = inp.base_fcf
    flows = []
    pv_total = 0.0
    n = inp.years_high + inp.years_fade
    for year in range(1, n + 1):
        if year <= inp.years_high:
            g = inp.growth
        else:
            step = (year - inp.years_high) / (inp.years_fade + 1)
            g = inp.growth + (inp.terminal_growth - inp.growth) * step
        fcf *= 1 + g
        pv = fcf / (1 + inp.discount) ** year
        pv_total += pv
        flows.append((year, g, fcf, pv))
    terminal = fcf * (1 + inp.terminal_growth) / (inp.discount - inp.terminal_growth)
    pv_terminal = terminal / (1 + inp.discount) ** n
    ev = pv_total + pv_terminal
    equity = ev + inp.net_cash
    return DCFResult(equity / inp.shares, ev, equity, pv_total, pv_terminal, flows)


def sensitivity(inp: DCFInputs, discount_steps=(-0.02, -0.01, 0, 0.01, 0.02), tg_steps=(-0.01, -0.005, 0, 0.005, 0.01)):
    """Per-share value across discount rate (rows) x terminal growth (columns)."""
    rows = [inp.discount + d for d in discount_steps]
    cols = [inp.terminal_growth + t for t in tg_steps]
    grid = np.full((len(rows), len(cols)), np.nan)
    for i, r in enumerate(rows):
        for j, t in enumerate(cols):
            try:
                grid[i, j] = dcf(replace(inp, discount=r, terminal_growth=t)).per_share
            except ValidationError:
                pass
    return rows, cols, grid


def reverse_dcf(inp: DCFInputs, price: float) -> float | None:
    """The stage-one growth rate the current price implies, by bisection."""
    def value(g: float) -> float:
        return dcf(replace(inp, growth=g)).per_share

    try:
        lo, hi = -0.5, 1.0
        v_lo, v_hi = value(lo), value(hi)
    except ValidationError:
        return None
    if not (v_lo <= price <= v_hi):
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if value(mid) < price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def monte_carlo_dcf(inp: DCFInputs, growth_sd: float = 0.04, discount_sd: float = 0.01, tg_sd: float = 0.005, n: int = 20000, seed: int = 7) -> np.ndarray:
    """Distribution of per-share value when the three key inputs are uncertain.

    Vectorised version of dcf(). Draws where the discount rate is not at
    least one point above terminal growth are discarded, because the
    terminal value is undefined there.
    """
    inp.validate()
    rng = np.random.default_rng(seed)
    g = rng.normal(inp.growth, growth_sd, n)
    r = rng.normal(inp.discount, discount_sd, n)
    tg = np.clip(rng.normal(inp.terminal_growth, tg_sd, n), -0.02, 0.05)
    ok = r > tg + 0.01
    g, r, tg = g[ok], r[ok], tg[ok]

    fcf = np.full(g.shape, inp.base_fcf, dtype=float)
    pv = np.zeros_like(fcf)
    total = inp.years_high + inp.years_fade
    for year in range(1, total + 1):
        if year <= inp.years_high:
            gy = g
        else:
            gy = g + (tg - g) * (year - inp.years_high) / (inp.years_fade + 1)
        fcf = fcf * (1 + gy)
        pv += fcf / (1 + r) ** year
    terminal = fcf * (1 + tg) / (r - tg) / (1 + r) ** total
    return (pv + terminal + inp.net_cash) / inp.shares


def default_inputs(fund: Fundamentals, ratio: dict[str, float]) -> DCFInputs:
    """Sensible starting assumptions, all editable in the UI."""
    # The lower of revenue and FCF growth: FCF CAGRs swing wildly with one
    # good or bad year, and an analyst's default should be the cautious one.
    candidates = [_f(ratio.get("revenue_cagr_5y")), _f(ratio.get("fcf_cagr_5y"))]
    candidates = [g for g in candidates if np.isfinite(g)]
    growth = min(candidates) if candidates else 0.05
    # First Version: unknown net debt became zero net cash, and a bank's DCF was refused as if its cash flow
    # were merely negative. Current Version: unknown net cash stays NaN (validate() asks for it), and banks and
    # insurers carry a refusal that says why a DCF does not apply.
    return DCFInputs(
        base_fcf=_f(ratio.get("fcf")),
        growth=float(np.clip(growth, -0.05, 0.15)),
        discount=0.09,
        terminal_growth=0.025,
        net_cash=-_f(ratio.get("net_debt")),
        shares=_f(ratio.get("shares")),
        refusal=FINANCIAL_DCF if is_financial(fund.sic_description) else "",
    )
