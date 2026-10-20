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
from finlit_pro.validation import ValidationError

NAN = float("nan")


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
    s = series.dropna()
    if len(s) < years + 1:
        return NAN
    start, end = float(s.iloc[-years - 1]), float(s.iloc[-1])
    if start <= 0 or end <= 0:
        return NAN
    return (end / start) ** (1 / years) - 1


def flow(fund: Fundamentals, key: str) -> float:
    """TTM if available, else the latest fiscal year."""
    if key in fund.ttm and np.isfinite(fund.ttm[key]):
        return float(fund.ttm[key])
    col = fund.annual.get(key)
    return float(col.dropna().iloc[-1]) if col is not None and col.notna().any() else NAN


def balance(fund: Fundamentals, key: str) -> float:
    if key in fund.latest and np.isfinite(fund.latest[key]):
        return float(fund.latest[key])
    col = fund.annual.get(key)
    return float(col.dropna().iloc[-1]) if col is not None and col.notna().any() else NAN


def ratios(fund: Fundamentals, price: float, dividends_ttm: float = 0.0) -> dict[str, float]:
    a = fund.annual
    shares = _f(fund.shares_outstanding)
    mcap = price * shares if np.isfinite(shares) else NAN
    cash = _f(balance(fund, "cash"))
    st_inv = balance(fund, "short_investments")
    liquid = cash + (0 if np.isnan(st_inv) else st_inv)
    debt = balance(fund, "total_debt")
    ev = mcap + (0 if np.isnan(debt) else debt) - (0 if np.isnan(liquid) else liquid)

    revenue, net_income = flow(fund, "revenue"), flow(fund, "net_income")
    op_income, gross = flow(fund, "operating_income"), flow(fund, "gross_profit")
    ocf, capex = flow(fund, "operating_cash_flow"), flow(fund, "capex")
    fcf = ocf - (0 if np.isnan(capex) else capex)
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
    invested = (0 if np.isnan(debt) else debt) + equity - (0 if np.isnan(liquid) else liquid)

    # Averages of opening and closing balances, as ROE should be.
    def avg(key: str) -> float:
        col = a.get(key)
        if col is None or col.dropna().size < 2:
            return balance(fund, key)
        c = col.dropna()
        return float((c.iloc[-1] + c.iloc[-2]) / 2)

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
        "roe": _div(net_income, avg("equity")) if avg("equity") > 0 else NAN,
        "roa": _div(net_income, avg("total_assets")),
        "roic": _div(op_income * (1 - tax_rate), invested) if invested > 0 else NAN,
        "current_ratio": _div(balance(fund, "current_assets"), balance(fund, "current_liabilities")),
        "debt_to_equity": _div(debt, equity) if np.isfinite(equity) and equity > 0 else NAN,
        "net_debt": (0 if np.isnan(debt) else debt) - (0 if np.isnan(liquid) else liquid),
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
    return out


# ---------------------------------------------------------------------------
# Quality scores
# ---------------------------------------------------------------------------


@dataclass
class Check:
    name: str
    passed: bool | None  # None = could not be computed from the filings
    detail: str


def piotroski(annual: pd.DataFrame) -> tuple[int, int, list[Check]]:
    """Piotroski F-score: nine pass/fail tests of profitability, leverage and efficiency.

    Uses the last two fiscal years. Returns (score, tests that could be run, checks).
    """
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

    Not meaningful for banks and insurers, whose balance sheets are mostly
    financial assets and liabilities; the zone label says so where it can.
    """
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
    sic = (fund.sic_description or "").lower()
    if any(word in sic for word in ("bank", "insurance", "savings", "finance", "reit", "real estate investment")):
        return z, "Not meaningful for financial companies"
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

    def validate(self) -> None:
        if not np.isfinite(self.base_fcf) or self.base_fcf <= 0:
            raise ValidationError(
                "Free cash flow is zero or negative, so a cash-flow DCF cannot value this company. "
                "Enter a positive base free cash flow you expect it to reach, or use the multiples instead."
            )
        if not np.isfinite(self.shares) or self.shares <= 0:
            raise ValidationError("The share count is missing, so there is no per-share value. Check the SEC data loaded.")
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
    return DCFInputs(
        base_fcf=_f(ratio.get("fcf")),
        growth=float(np.clip(growth, -0.05, 0.15)),
        discount=0.09,
        terminal_growth=0.025,
        net_cash=-_f(ratio.get("net_debt")) if np.isfinite(_f(ratio.get("net_debt"))) else 0.0,
        shares=_f(ratio.get("shares")),
    )
