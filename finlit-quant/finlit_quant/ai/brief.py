"""Turn an Analysis into the data brief the AI analyst reads, plus its instructions.

The brief is plain text with every number pre-formatted, so the model reads
the same figures the user sees on screen and has no arithmetic to get wrong.
"""

from __future__ import annotations

from datetime import date

import numpy as np

from finlit_quant.analysis import Analysis
from finlit_quant.analytics.montecarlo import DRIFT_MODES, MODELS


def pct(v, dp: int = 1, sign: bool = False) -> str:
    if v is None or not np.isfinite(v):
        return "n/a"
    return f"{v * 100:+.{dp}f}%" if sign else f"{v * 100:.{dp}f}%"


def num(v, dp: int = 2) -> str:
    if v is None or not np.isfinite(v):
        return "n/a"
    return f"{v:,.{dp}f}"


def money(v, currency: str = "USD") -> str:
    """Compact money: 1.2T, 340.5B, 12.3M."""
    if v is None or not np.isfinite(v):
        return "n/a"
    sign = "-" if v < 0 else ""
    a = abs(v)
    prefix = "$" if currency == "USD" else ""
    suffix = "" if currency == "USD" else f" {currency}"
    for size, unit in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= size:
            return f"{sign}{prefix}{a / size:,.1f}{unit}{suffix}"
    return f"{sign}{prefix}{a:,.2f}{suffix}"


SYSTEM_PROMPT = """You are a senior buy-side equity analyst at a fundamental long/short hedge fund, writing an internal research memo for the portfolio manager.

You receive a data brief assembled by a research workstation: live prices from Yahoo Finance, fundamentals from SEC EDGAR filings, risk statistics against a benchmark, a Monte Carlo simulation with its own walk-forward calibration test, a technical signal score, and a DCF.

How to work:
- Ground every number you cite in the brief. Do not invent figures, estimates, price targets or events. If something important is missing, say what is missing and why it matters.
- You may use general background knowledge about the company's business, industry and competitors, but label it as background and never attach numbers to it that are not in the brief.
- Think like a PM: what is priced in, what would have to be true for the stock to work, where the asymmetry is, and what would prove the thesis wrong.
- Treat the Monte Carlo output as a description of risk, not a forecast. Use the calibration result to say how much to trust its spread for this particular stock.
- Treat the technical signal score as one weak input, never the thesis.
- Be direct and specific. No hype, no hedging boilerplate, no filler.

Format (Markdown):
## Verdict
One line: stance (Bullish, Neutral or Bearish), conviction (low, medium or high), and horizon. Then two sentences on why.
## Thesis
Three bullets.
## Business quality and growth
## Valuation
Include what the reverse DCF implies, if available.
## Balance sheet and capital allocation
## Price action and risk
## Monte Carlo read
## Bull case
## Bear case
## What would change my mind
## What to check next
Specific filings, line items or events to verify.

Keep the memo between 600 and 900 words. Never use em dashes. End with one short line noting this is research, not personal financial advice."""

FOLLOW_UP_NOTE = (
    "Answer the follow-up question as the same analyst, using the brief and your memo. "
    "Be concise unless asked for depth, cite numbers from the brief, and say so when the brief cannot answer it. Never use em dashes."
)


def build(a: Analysis) -> str:
    lines: list[str] = [f"# Data brief: {a.symbol} (prepared {date.today().isoformat()})"]
    h = a.history
    if h is None:
        return "\n".join(lines + ["No price data loaded."])

    cur = h.currency
    if a.is_demo:
        lines.append("NOTE: this is SIMULATED demo data, not a real company. Say so at the top of the memo.")
    lines += [
        "",
        "## Price",
        f"Name: {h.name} | Exchange: {h.exchange or 'n/a'} | Type: {h.instrument_type or 'n/a'} | Currency: {cur}",
        f"Last price: {num(h.price)} ({pct(h.day_change, 2, True)} on the day) | Data as of {h.bars.index[-1].date()} ({h.source})",
    ]
    closes = h.closes
    for label, days in (("1M", 21), ("3M", 63), ("6M", 126), ("1Y", 252), ("3Y", 756), ("5Y", 1260)):
        if len(closes) > days:
            lines.append(f"Return {label}: {pct(closes.iloc[-1] / closes.iloc[-days - 1] - 1, 1, True)}")
    year = h.bars.iloc[-252:] if len(h.bars) >= 252 else h.bars
    lines.append(f"52-week range: {num(year['low'].min())} to {num(year['high'].max())}; price is {pct(h.price / year['high'].max() - 1, 1, True)} from the high")
    if h.trailing_dividends():
        lines.append(f"Trailing 12-month dividends per share: {num(h.trailing_dividends())}")

    f = a.fundamentals
    r = a.ratios
    lines += ["", "## Fundamentals (SEC EDGAR)"]
    if f is None:
        lines.append(f"Unavailable: {a.fundamentals_error or 'not loaded'}")
    else:
        lines.append(f"Company: {f.name} | CIK {f.cik} | Industry: {f.sic_description or 'n/a'} | Fiscal year end: {f.fiscal_year_end or 'n/a'} | Latest balance sheet: {f.latest_period}")
        lines += f.split_notes
        ann = f.annual.tail(6)
        cols = [("revenue", "Revenue"), ("gross_profit", "Gross profit"), ("operating_income", "Operating income"), ("net_income", "Net income"), ("eps_diluted", "Diluted EPS"), ("operating_cash_flow", "Operating cash flow"), ("capex", "Capex"), ("diluted_shares", "Diluted shares")]
        lines.append("Fiscal year | " + " | ".join(label for _, label in cols))
        for idx, row in ann.iterrows():
            vals = []
            for key, _ in cols:
                v = row.get(key)
                if key == "eps_diluted":
                    vals.append(num(v))
                elif key == "diluted_shares":
                    vals.append(f"{v / 1e6:,.0f}M" if v is not None and np.isfinite(v) else "n/a")
                else:
                    vals.append(money(v, "USD"))
            lines.append(f"{idx.date()} | " + " | ".join(vals))
        if f.ttm:
            lines.append(
                "TTM: revenue " + money(f.ttm.get("revenue")) + ", net income " + money(f.ttm.get("net_income"))
                + ", operating cash flow " + money(f.ttm.get("operating_cash_flow"))
            )
    if r:
        lines += [
            "",
            "## Valuation and quality (price-based ratios use the live price)",
            f"Market cap {money(r.get('market_cap'))} | EV {money(r.get('enterprise_value'))} | P/E {num(r.get('pe'), 1)} | P/S {num(r.get('ps'), 1)} | P/B {num(r.get('pb'), 1)} | EV/EBIT {num(r.get('ev_ebit'), 1)} | FCF yield {pct(r.get('fcf_yield'))} | Dividend yield {pct(r.get('dividend_yield'))}",
            f"Margins: gross {pct(r.get('gross_margin'))}, operating {pct(r.get('operating_margin'))}, net {pct(r.get('net_margin'))}, FCF {pct(r.get('fcf_margin'))}",
            f"Returns: ROE {pct(r.get('roe'))}, ROA {pct(r.get('roa'))}, ROIC {pct(r.get('roic'))}",
            f"Growth: revenue CAGR 3y {pct(r.get('revenue_cagr_3y'))}, 5y {pct(r.get('revenue_cagr_5y'))}; EPS CAGR 5y {pct(r.get('eps_cagr_5y'))}; FCF CAGR 5y {pct(r.get('fcf_cagr_5y'))}; diluted share count change per year (3y) {pct(r.get('share_change_3y'), 2, True)}",
            f"Balance sheet: net debt {money(r.get('net_debt'))}, debt/equity {num(r.get('debt_to_equity'))}, current ratio {num(r.get('current_ratio'))}, interest coverage {num(r.get('interest_coverage'), 1)}x",
            f"Stock-based comp / revenue {pct(r.get('sbc_to_revenue'))}; R&D / revenue {pct(r.get('rnd_to_revenue'))}",
        ]
    if a.piotroski:
        score, runnable, checks = a.piotroski
        failed = [c.name for c in checks if c.passed is False]
        lines.append(f"Piotroski F-score: {score}/{runnable} tests passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    if a.altman:
        lines.append(f"Altman Z-score: {num(a.altman[0])} ({a.altman[1]})")
    if a.dcf and a.dcf_inputs:
        d, i = a.dcf, a.dcf_inputs
        lines.append(
            f"DCF (user assumptions): base FCF {money(i.base_fcf)}, growth {pct(i.growth)} for {i.years_high}y fading to {pct(i.terminal_growth)} terminal, discount {pct(i.discount)}"
            f" -> {num(d.per_share)} per share ({pct(d.per_share / h.price - 1, 0, True)} vs price); terminal value is {pct(d.pv_terminal / d.enterprise_value, 0)} of EV"
        )
    if a.implied_growth is not None:
        lines.append(f"Reverse DCF: the current price implies {pct(a.implied_growth)} annual FCF growth for 5 years at the same discount rate")

    rk = a.risk
    if rk:
        m = rk.metrics
        lines += [
            "",
            f"## Risk (last {round((rk.growth.index[-1] - rk.growth.index[0]).days / 365.25, 1)} years, risk-free {pct(a.risk_free, 2)}{' live T-bill' if a.risk_free_live else ' assumed'})",
            f"CAGR {pct(m.get('cagr'))} | Volatility {pct(m.get('volatility'))} | Sharpe {num(m.get('sharpe'))} | Sortino {num(m.get('sortino'))} | Max drawdown {pct(-m.get('max_drawdown', np.nan))} | Longest time under water {int(m.get('longest_drawdown_days', 0))} days",
            f"1-day VaR 95% {pct(m.get('var95_1d'), 2)}, CVaR 95% {pct(m.get('cvar95_1d'), 2)} | Skew {num(m.get('skew'))} | Excess kurtosis {num(m.get('excess_kurtosis'), 1)} | Worst day {pct(m.get('worst_day'), 1)}",
        ]
        if "beta" in m:
            lines.append(
                f"vs {rk.benchmark}: beta {num(m['beta'])}, alpha {pct(m['alpha'], 1, True)}/yr, correlation {num(m['correlation'])}, up capture {num(m['up_capture'])}, down capture {num(m['down_capture'])}, benchmark CAGR {pct(m.get('bench_cagr'))}"
            )

    if a.mc:
        s, c = a.mc.stats, a.mc.config
        lines += [
            "",
            f"## Monte Carlo ({c.n_paths:,} paths, {c.horizon_days} trading days, {MODELS[c.model]}, {DRIFT_MODES[c.drift_mode]})",
            f"Inputs from the last {a.mc.est.samples} days: annualised vol {pct(a.mc.est.vol_annual)}, implied expected return {pct(a.mc.est.drift_annual)}/yr, fitted tail df {num(a.mc.est.t_df, 1)}",
            f"Terminal price percentiles: 5th {num(s['p5'])}, 25th {num(s['p25'])}, median {num(s['p50'])}, 75th {num(s['p75'])}, 95th {num(s['p95'])}",
            f"P(above today) {pct(s['prob_up'], 0)} | P(+20% or more) {pct(s['prob_gain_20'], 0)} | P(-20% or worse) {pct(s['prob_loss_20'], 0)} | VaR 95 {pct(s['var95'], 0)} | CVaR 95 {pct(s['cvar95'], 0)} | Expected max drawdown along the way {pct(s['expected_max_dd'], 0)}",
        ]
    if a.calibration:
        cal = a.calibration
        lines.append(f"Calibration (walk-forward on this stock's own history, {cal.tests} tests at a {cal.horizon_days}-day horizon): " + "; ".join(f"{k} band nominal {pct(v[0], 0)} vs observed {pct(v[1], 0)}" for k, v in cal.coverage.items()))
    if a.predictor:
        p = a.predictor
        lines += [
            "",
            f"## Technical signal engine (legacy FinLit predictor): {p.verdict}, score {p.score:+d} of +/-{p.max_score}",
            *[f"- {sig.name}: {sig.reading} ({sig.score:+d})" for sig in p.signals],
            f"Composite target {num(p.composite_target)} ({pct(p.composite_change, 1, True)}): regression {num(p.trend_target)} (R^2 {num(p.trend_r2)}), EMA momentum {num(p.ema_target)}, Monte Carlo median {num(p.mc_median)}; model agreement {p.agreement}",
        ]
    if a.fundamentals and a.fundamentals.filings:
        recent = a.fundamentals.key_filings()[:8]
        lines += ["", "## Recent SEC filings"] + [f"- {fl.filed} {fl.form} {fl.description}".rstrip() for fl in recent]
        lines.append(f"Insider (Form 4) filings in the last 90 days: {a.fundamentals.insider_filings(90)}")
    if a.news:
        lines += ["", "## Recent headlines (titles only; not verified)"] + [f"- {n.published.date() if n.published else ''} {n.publisher}: {n.title}" for n in a.news[:8]]
    return "\n".join(lines)


def first_message(brief: str) -> dict:
    return {"role": "user", "content": f"{brief}\n\nWrite the research memo."}
