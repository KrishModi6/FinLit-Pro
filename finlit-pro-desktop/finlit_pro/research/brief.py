"""The research brief: every figure the analysis may use, each tagged with its source ID.

The brief is plain text. Numbers are pre-formatted so the engine reads
exactly what is on screen and has no arithmetic of its own to get wrong.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np

from finlit_pro.analytics.montecarlo import DRIFT_MODES, MODELS
from finlit_pro.fmt import money, num, pct
from finlit_pro.research.sources import SourceRegistry
from finlit_pro.workspace import Workspace

ROW_FIELDS = [
    ("revenue", "revenue", "money"),
    ("gross_profit", "gross profit", "money"),
    ("operating_income", "operating income", "money"),
    ("net_income", "net income", "money"),
    ("eps_diluted", "diluted EPS", "eps"),
    ("operating_cash_flow", "operating cash flow", "money"),
    ("capex", "capex", "money"),
    ("buybacks", "buybacks", "money"),
    ("dividends_paid", "dividends paid", "money"),
    ("cash", "cash", "money"),
    ("total_debt", "total debt", "money"),
    ("equity", "equity", "money"),
    ("diluted_shares", "diluted shares", "shares"),
]


def _value(v, kind: str) -> str:
    if v is None or not np.isfinite(v):
        return "n/a"
    if kind == "eps":
        return num(v)
    if kind == "shares":
        return f"{v / 1e6:,.0f}M"
    return money(v)


def _tags(ids) -> str:
    ids = [i for i in dict.fromkeys(ids) if i]
    return f" [{', '.join(ids)}]" if ids else ""


def build(ws: Workspace) -> tuple[str, SourceRegistry]:
    reg = SourceRegistry()
    lines: list[str] = []
    h = ws.history
    if h is None:
        return "No data loaded.", reg

    s_price = reg.dataset(h.source)
    lines.append(f"# Research brief: {h.symbol} ({h.name}), prepared {datetime.now():%Y-%m-%d %H:%M}")
    if ws.is_demo:
        lines.append("NOTE: simulated demonstration data, not a real security. State this in the summary.")

    # Market data
    lines += ["", "## Market data"]
    lines.append(f"Last price {num(h.price)} {h.currency} as of {h.bars.index[-1].date()}; change on the day {pct(h.day_change, 2, True)}{_tags([s_price])}")
    rets = []
    for label, days in (("1M", 21), ("3M", 63), ("6M", 126), ("1Y", 252), ("3Y", 756), ("5Y", 1260)):
        if len(h.closes) > days:
            rets.append(f"{label} {pct(h.closes.iloc[-1] / h.closes.iloc[-days - 1] - 1, 1, True)}")
    lines.append("Total returns (dividends reinvested): " + ", ".join(rets) + _tags([s_price]))
    year = h.bars.iloc[-252:]
    lines.append(f"52-week range {num(year['low'].min())} to {num(year['high'].max())}; {pct(h.price / year['high'].max() - 1, 1, True)} from the high{_tags([s_price])}")
    if h.trailing_dividends():
        lines.append(f"Trailing 12-month dividends {num(h.trailing_dividends())} per share{_tags([s_price])}")

    if ws.risk:
        m = ws.risk.metrics
        ids = [s_price]
        if ws.benchmark:
            ids.append(reg.dataset(ws.benchmark.source))
        if ws.risk_free_source:
            ids.append(reg.dataset(ws.risk_free_source))
        span = (ws.risk.growth.index[-1] - ws.risk.growth.index[0]).days / 365.25
        calc = reg.computation("risk statistics", f"Daily returns over {span:.1f} years, risk-free {ws.risk_free:.2%}")
        lines.append(
            f"Risk over {span:.1f} years: CAGR {pct(m.get('cagr'))}, volatility {pct(m.get('volatility'))}, Sharpe {num(m.get('sharpe'))}, "
            f"max drawdown {pct(-m.get('max_drawdown', np.nan))}, 1-day VaR 95% {pct(m.get('var95_1d'), 2)}, excess kurtosis {num(m.get('excess_kurtosis'), 1)}{_tags(ids + [calc])}"
        )
        if "beta" in m:
            lines.append(f"Against {ws.risk.benchmark}: beta {num(m['beta'])}, annual alpha {pct(m['alpha'], 1, True)}, correlation {num(m['correlation'])}, benchmark CAGR {pct(m.get('bench_cagr'))}{_tags(ids + [calc])}")

    # Fundamentals
    f, r = ws.fundamentals, ws.ratios
    lines += ["", "## Financial statements (SEC EDGAR XBRL)"]
    if f is None:
        lines.append(f"Not available: {ws.fundamentals_error or 'not loaded'}")
    else:
        s_facts = reg.dataset(f.sources[0]) if f.sources else ""
        lines.append(f"{f.name}, CIK {f.cik}, {f.sic_description or 'industry n/a'}, fiscal year end {f.fiscal_year_end or 'n/a'}, latest balance sheet {f.latest_period}{_tags([s_facts])}")
        lines += f.split_notes
        for end, row in f.annual.tail(6).iterrows():
            ids = [s_facts]
            for key, _, _ in ROW_FIELDS:
                ref = f.refs.get(key, {}).get(end)
                if ref and ref.accession:
                    ids.append(reg.filing(ref, f.name))
            values = "; ".join(f"{label} {_value(row.get(key), kind)}" for key, label, kind in ROW_FIELDS if key in row)
            lines.append(f"Fiscal year ended {end.date()}: {values}{_tags(ids)}")
        if f.ttm:
            ids = [s_facts] + [reg.filing(ref, f.name) for k, ref in f.ttm_refs.items() if k in ("revenue", "net_income", "operating_cash_flow") and ref.accession]
            lines.append(
                f"Trailing twelve months: revenue {money(f.ttm.get('revenue'))}, net income {money(f.ttm.get('net_income'))}, "
                f"operating cash flow {money(f.ttm.get('operating_cash_flow'))}, capex {money(f.ttm.get('capex'))}{_tags(ids)}"
            )
        if r:
            latest = [reg.filing(ref, f.name) for k, ref in f.ttm_refs.items() if k in ("total_assets", "shares_outstanding") and ref.accession]
            calc = reg.computation("valuation ratios", "Live price x latest share count; TTM flows; latest balance sheet")
            ids = [s_price, s_facts] + latest + [calc]
            lines.append(
                f"Valuation at the live price: market cap {money(r.get('market_cap'))}, EV {money(r.get('enterprise_value'))}, P/E {num(r.get('pe'), 1)}, "
                f"EV/EBIT {num(r.get('ev_ebit'), 1)}, P/S {num(r.get('ps'), 1)}, FCF yield {pct(r.get('fcf_yield'))}, dividend yield {pct(r.get('dividend_yield'))}{_tags(ids)}"
            )
            lines.append(
                f"Profitability: gross margin {pct(r.get('gross_margin'))}, operating margin {pct(r.get('operating_margin'))}, net margin {pct(r.get('net_margin'))}, "
                f"ROE {pct(r.get('roe'))}, ROIC {pct(r.get('roic'))}{_tags([s_facts, calc])}"
            )
            lines.append(
                f"Growth: revenue CAGR 3y {pct(r.get('revenue_cagr_3y'))}, 5y {pct(r.get('revenue_cagr_5y'))}; EPS CAGR 5y {pct(r.get('eps_cagr_5y'))}; "
                f"FCF CAGR 5y {pct(r.get('fcf_cagr_5y'))}; diluted share count change per year (3y) {pct(r.get('share_change_3y'), 2, True)}{_tags([s_facts, calc])}"
            )
            lines.append(
                f"Balance sheet: net debt {money(r.get('net_debt'))}, debt/equity {num(r.get('debt_to_equity'))}, current ratio {num(r.get('current_ratio'))}, "
                f"interest coverage {num(r.get('interest_coverage'), 1)}x; stock-based compensation {pct(r.get('sbc_to_revenue'))} of revenue{_tags([s_facts, calc])}"
            )
        if ws.piotroski and ws.piotroski[1]:
            score, runnable, checks = ws.piotroski
            failed = [c.name for c in checks if c.passed is False]
            calc = reg.computation("Piotroski F-score", "Nine tests on the last two fiscal years")
            lines.append(f"Piotroski F-score {score}/{runnable}" + (f"; failed: {', '.join(failed)}" if failed else "") + _tags([s_facts, calc]))
        if ws.altman:
            calc = reg.computation("Altman Z-score", "Original public-manufacturer weights")
            lines.append(f"Altman Z-score {num(ws.altman[0])} ({ws.altman[1]}){_tags([s_facts, s_price, calc])}")
        if ws.dcf and ws.dcf_inputs:
            d, i = ws.dcf, ws.dcf_inputs
            calc = reg.computation("discounted cash flow", f"Base FCF {money(i.base_fcf)}, growth {pct(i.growth)} for {i.years_high}y fading to {pct(i.terminal_growth)}, discount {pct(i.discount)}")
            lines.append(f"DCF value {num(d.per_share)} per share ({pct(d.per_share / h.price - 1, 0, True)} vs price); terminal value is {pct(d.pv_terminal / d.enterprise_value, 0)} of EV{_tags([s_facts, calc])}")
            if ws.implied_growth is not None:
                lines.append(f"Reverse DCF: the price implies {pct(ws.implied_growth)} annual FCF growth for {i.years_high} years at the same discount rate{_tags([s_price, calc])}")
        key = f.key_filings()[:8]
        if key:
            lines += ["", "## Recent filings"]
            for fl in key:
                ref_id = reg.filing_record(fl, f.name)
                lines.append(f"{fl.filed} {fl.form} {fl.description} (period {fl.report_date or 'n/a'}){_tags([ref_id])}")
            lines.append(f"Insider (Form 4) filings in the last 90 days: {f.insider_filings(90)}{_tags([reg.dataset(f.sources[1]) if len(f.sources) > 1 else s_facts])}")

    # Model
    fc = ws.forecast
    if fc:
        calc = reg.computation(f"{fc.model} v{fc.version}", f"Horizon {fc.horizon_days} trading days, inputs from the price history")
        lines += ["", f"## {fc.model} v{fc.version} (the owner's prediction model)"]
        lines.append(f"Verdict {fc.verdict}, signal score {fc.score:+d} of +/-{fc.score_range[1]}; composite target {num(fc.target)} ({pct(fc.expected_return, 1, True)}) over {fc.horizon_days} trading days{_tags([s_price, calc])}")
        lines.append("Components: " + ", ".join(f"{k} {num(v)} (weight {fc.weights.get(k, 0):.0%})" for k, v in fc.components.items()) + _tags([calc]))
        lines.append("Signals: " + "; ".join(f"{sg.name} {sg.reading} ({sg.score:+d})" for sg in fc.signals) + _tags([calc]))
        lines.append("Simulated percentiles at horizon: " + ", ".join(f"P{q} {num(v)}" for q, v in fc.quantiles.items()) + f"; probability of a rise {pct(fc.prob_up, 0)}{_tags([calc])}")
    ev = ws.evaluation
    if ev:
        calc = reg.computation("walk-forward evaluation", f"{len(ev.records)} point-in-time forecasts at a {ev.horizon}-day horizon")
        lines.append("Out-of-sample evaluation: " + "; ".join(f"{m.name} {m.display}" + (f" ({m.benchmark})" if m.benchmark else "") + (f" [{m.flag}]" if m.flag else "") for m in ev.metrics[:9]) + _tags([s_price, calc]))
        strat = [m for m in ev.metrics if m.name.startswith(("Long/flat", "Buy and hold")) and ("CAGR" in m.name or "Sharpe" in m.name)]
        lines.append("Verdict-based strategy vs buy and hold over the same periods: " + "; ".join(f"{m.name} {m.display}" for m in strat) + _tags([calc]))

    if ws.mc:
        s, c = ws.mc.stats, ws.mc.config
        calc = reg.computation("Monte Carlo simulation", f"{c.n_paths:,} paths, {c.horizon_days} days, {MODELS[c.model]}, {DRIFT_MODES[c.drift_mode]}")
        lines += ["", "## Monte Carlo simulation"]
        lines.append(f"Inputs: volatility {pct(ws.mc.est.vol_annual)}, expected return {pct(ws.mc.est.drift_annual)}/yr, lookback {ws.mc.est.samples} days{_tags([s_price, calc])}")
        lines.append(f"Terminal percentiles: P5 {num(s['p5'])}, P25 {num(s['p25'])}, P50 {num(s['p50'])}, P75 {num(s['p75'])}, P95 {num(s['p95'])}; P(above today) {pct(s['prob_up'], 0)}; VaR 95 {pct(s['var95'], 0)}; expected max drawdown {pct(s['expected_max_dd'], 0)}{_tags([calc])}")
        if ws.calibration:
            lines.append(f"Calibration on this stock's history: {ws.calibration.verdict}{_tags([calc])}")

    # Filing text
    if ws.filing_texts:
        lines += ["", "## Filing excerpts"]
        for ft in ws.filing_texts:
            for name, body in ft.sections.items():
                sid = reg.filing_section(ft.source, name)
                cut = f", truncated to {len(body):,} of {ft.full_chars[name]:,} characters" if ft.truncated.get(name) else ""
                lines += ["", f"### [{sid}] {ft.filing.form} filed {ft.filing.filed}, period {ft.filing.report_date}: {name}{cut}", body]
    for problem in ws.filing_problems:
        lines.append(f"Filing text unavailable: {problem}")

    if ws.news:
        lines += ["", "## Headlines (titles only, not verified)"]
        for n in ws.news[:8]:
            sid = reg.headline(n.title, n.url, n.publisher, n.published)
            lines.append(f"{n.published:%Y-%m-%d} {n.publisher}: {n.title}{_tags([sid])}" if n.published else f"{n.publisher}: {n.title}{_tags([sid])}")

    header = ["", "## Source list"] + [f"{e.id}: {e.title}" + (f", as of {e.as_of}" if e.as_of else "") + (f", {e.detail}" if e.detail else "") for e in reg.entries]
    return "\n".join(lines + header), reg
