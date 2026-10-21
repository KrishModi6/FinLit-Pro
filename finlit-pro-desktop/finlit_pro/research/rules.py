"""The rules engine: a research note without a language model.

Facts are read straight from the workspace and cited with the same source
IDs the brief uses. Interpretation comes from fixed, published thresholds,
each scored in one of six pillars; the pillar total sets the
recommendation. The engine cannot read filing text, and says so in the
note's uncertainties.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from finlit_pro.analytics.risk import RANGE_DAYS
from finlit_pro.fmt import money, num, pct
from finlit_pro.research.note import Fact, Interpretation, Note, Risk, Uncertainty
from finlit_pro.research.sources import SourceRegistry
from finlit_pro.workspace import Workspace


def _ok(v) -> bool:
    return v is not None and isinstance(v, (int, float)) and np.isfinite(v)


def build_note(ws: Workspace, reg: SourceRegistry) -> Note:
    h = ws.history
    facts: list[Fact] = []
    interp: list[Interpretation] = []
    risks: list[Risk] = []
    unc: list[Uncertainty] = []
    gaps: list[str] = []
    score = 0

    def judge(points: int, statement: str, confidence: str, ids: list[str]) -> None:
        nonlocal score
        score += points
        interp.append(Interpretation(statement, confidence, [i for i in ids if i]))

    s_price = reg.dataset(h.source)
    cur = f" {h.currency}" if h.currency else ""  # never "None" when the currency is unknown
    facts.append(Fact("Price and risk", f"{h.symbol} last traded at {num(h.price)}{cur} on {h.bars.index[-1].date()}.", [s_price]))
    # One calendar year, matching the 1Y window of the Returns and Risk view
    # (First Version used 252 sessions, which disagreed with that view by a few days).
    year_ago = h.closes[h.closes.index <= h.closes.index[-1] - pd.Timedelta(days=RANGE_DAYS["1Y"])]
    if len(year_ago):
        r1y = h.closes.iloc[-1] / year_ago.iloc[-1] - 1
        facts.append(Fact("Price and risk", f"Total return over the past year was {pct(r1y, 1, True)}.", [s_price]))

    f, r = ws.fundamentals, ws.ratios
    s_facts = reg.dataset(f.sources[0]) if f and f.sources else ""
    calc_ratios = reg.computation("valuation ratios", "Live price x latest share count; TTM flows; latest balance sheet") if r else ""

    if f is not None and len(f.annual) >= 2:
        a = f.annual
        end, prev = a.index[-1], a.index[-2]

        def ref(metric, at):
            rf = f.refs.get(metric, {}).get(at)
            return reg.filing(rf, f.name) if rf and rf.accession else s_facts

        rev, rev_prev = a["revenue"].iloc[-1], a["revenue"].iloc[-2]
        if _ok(rev) and _ok(rev_prev) and rev_prev > 0:
            g = rev / rev_prev - 1
            facts.append(Fact("Financial performance", f"Revenue for the fiscal year ended {end.date()} was {money(rev)}, {pct(g, 1, True)} on the prior year ({money(rev_prev)}).", [ref("revenue", end), ref("revenue", prev)]))
        ni = a["net_income"].iloc[-1]
        if _ok(ni) and _ok(rev) and rev:
            facts.append(Fact("Financial performance", f"Net income for that year was {money(ni)}, a net margin of {pct(ni / rev)}.", [ref("net_income", end), ref("revenue", end)]))
        if r:
            if _ok(r.get("fcf")):
                facts.append(Fact("Cash flow and capital return", f"Trailing free cash flow (operating cash flow less capex) is {money(r['fcf'])}, a {pct(r.get('fcf_yield'))} yield on market value.", [s_facts, s_price, calc_ratios]))
            facts.append(Fact("Valuation", f"At the live price the market value is {money(r.get('market_cap'))}, P/E {num(r.get('pe'), 1)} and EV/EBIT {num(r.get('ev_ebit'), 1)}.", [s_price, s_facts, calc_ratios]))
            nd = r.get("net_debt")
            position = f"Net cash is {money(-nd)} (cash exceeds debt)" if _ok(nd) and nd < 0 else f"Net debt is {money(nd)}"
            facts.append(Fact("Balance sheet", f"{position} and debt to equity is {num(r.get('debt_to_equity'))}.", [s_facts, calc_ratios]))

            roic = r.get("roic")
            if _ok(roic):
                judge(2 if roic > 0.15 else (1 if roic > 0.08 else -1), f"Return on invested capital of {pct(roic)} is {'well above' if roic > 0.15 else ('above' if roic > 0.08 else 'below')} a typical 8% cost of capital.", "High" if abs(roic - 0.08) > 0.07 else "Medium", [s_facts, calc_ratios])
            g3 = r.get("revenue_cagr_3y")
            if _ok(g3):
                judge(2 if g3 > 0.15 else (1 if g3 > 0.05 else (-1 if g3 < 0 else 0)), f"Revenue has compounded {pct(g3)} a year over three years.", "Medium", [s_facts, calc_ratios])
            fy = r.get("fcf_yield")
            # First Version: a negative yield read "A -3.1% free cash flow yield prices in substantial growth".
            # Current Version: a cash-burning company is described as consuming cash (same score).
            if _ok(fy) and fy < 0:
                judge(-1, f"Free cash flow is negative ({pct(fy)} of market value): the company is consuming cash.", "Medium", [s_facts, s_price, calc_ratios])
            elif _ok(fy):
                judge(2 if fy > 0.06 else (1 if fy > 0.04 else (-1 if fy < 0.02 else 0)), f"A {pct(fy)} free cash flow yield {'is attractive' if fy > 0.04 else ('is undemanding' if fy > 0.02 else 'prices in substantial growth')}.", "Medium", [s_facts, s_price, calc_ratios])
            if ws.implied_growth is not None and _ok(r.get("fcf_cagr_5y")):
                gap = ws.implied_growth - r["fcf_cagr_5y"]
                judge(-1 if gap > 0.05 else (1 if gap < -0.05 else 0), f"The price implies {pct(ws.implied_growth)} annual FCF growth against {pct(r['fcf_cagr_5y'])} delivered over five years.", "Medium", [s_price, s_facts, reg.computation("discounted cash flow", "")])
            cov = r.get("interest_coverage")
            # First Version: an operating loss read "Operating income covers interest -3.2 times".
            # Current Version: negative coverage says plainly that there is no earnings cover.
            if _ok(cov) and cov < 0:
                judge(-2, "Operating income is negative, so it does not cover interest expense.", "High", [s_facts, calc_ratios])
                risks.append(Risk("Operating losses leave no earnings cover for interest payments.", [s_facts]))
            elif _ok(cov):
                judge(-2 if cov < 2 else (1 if cov > 8 else 0), f"Operating income covers interest {num(cov, 1)} times.", "High" if cov < 2 or cov > 15 else "Medium", [s_facts, calc_ratios])
                if cov < 3:
                    risks.append(Risk(f"Thin interest coverage ({num(cov, 1)}x) leaves little room if operating income falls.", [s_facts]))
            sbc = r.get("sbc_to_revenue")
            if _ok(sbc) and sbc > 0.08:
                risks.append(Risk(f"Stock-based compensation is {pct(sbc)} of revenue, a real cost added back in cash flow.", [s_facts]))
        else:
            gaps.append("Valuation ratios could not be computed.")
        if ws.piotroski and ws.piotroski[1] >= 6:
            sc, n, _ = ws.piotroski
            judge(1 if sc / n >= 0.7 else (-1 if sc / n <= 0.35 else 0), f"Piotroski F-score {sc}/{n} indicates {'improving' if sc / n >= 0.7 else ('deteriorating' if sc / n <= 0.35 else 'mixed')} fundamentals year on year.", "Medium", [s_facts, reg.computation("Piotroski F-score", "")])
        if ws.altman and _ok(ws.altman[0]) and "meaningful" not in ws.altman[1]:
            if "Distress" in ws.altman[1]:
                risks.append(Risk(f"Altman Z-score of {num(ws.altman[0])} is in the distress zone.", [s_facts]))
    else:
        gaps.append(f"SEC financial statements: {ws.fundamentals_error or 'not loaded'}.")

    if ws.risk:
        m = ws.risk.metrics
        calc = reg.computation("risk statistics", "")
        facts.append(Fact("Price and risk", f"Annualised volatility is {pct(m.get('volatility'))} with a maximum drawdown of {pct(-m.get('max_drawdown', np.nan))} over the risk window.", [s_price, calc]))
        if _ok(m.get("sharpe")):
            judge(1 if m["sharpe"] > 0.8 else (-1 if m["sharpe"] < 0 else 0), f"A Sharpe ratio of {num(m['sharpe'])} over the window is {'strong' if m['sharpe'] > 0.8 else ('negative' if m['sharpe'] < 0 else 'unremarkable')}.", "Low", [s_price, calc])
        if m.get("max_drawdown", 0) > 0.4:
            risks.append(Risk(f"The stock has fallen {pct(m['max_drawdown'], 0)} peak to trough in the window; position size accordingly.", [s_price, calc]))

    fc, ev = ws.forecast, ws.evaluation
    if fc:
        calc = reg.computation(f"{fc.model} v{fc.version}", "")
        facts.append(Fact("Model and simulation", f"{fc.model} v{fc.version} reads {fc.verdict} (score {fc.score:+d}) with a {fc.horizon_days}-day composite target of {num(fc.target)} ({pct(fc.expected_return, 1, True)}).", [s_price, calc]))
        skilled = False
        if ev:
            calc_ev = reg.computation("walk-forward evaluation", "")
            hit, sk, ic = ev.metric("Directional hit rate"), ev.metric("Skill vs no-change"), ev.metric("Information coefficient")
            if hit and sk and ic:
                facts.append(Fact("Model and simulation", f"Out of sample on this ticker the model's direction was right {hit.display} of the time ({hit.benchmark.lower()}), its error skill against a no-change forecast is {sk.display}, and its information coefficient is {ic.display}.", [s_price, calc_ev]))
                skilled = sk.value > 0 and not hit.flag and not ic.flag
            if not skilled:
                unc.append(Uncertainty("The prediction model shows no statistically significant out-of-sample skill on this ticker.", "Its verdict is given little weight in this note."))
        if skilled:
            judge(1 if fc.verdict in ("BUY", "STRONG BUY") else (-1 if fc.verdict in ("SELL", "STRONG SELL") else 0), f"The model's {fc.verdict} verdict has some support from its out-of-sample record.", "Low", [calc])

    if ws.mc:
        s = ws.mc.stats
        calc = reg.computation("Monte Carlo simulation", "")
        facts.append(Fact("Model and simulation", f"The Monte Carlo simulation puts the {ws.mc.config.horizon_days}-day 5th to 95th percentile range at {num(s['p5'])} to {num(s['p95'])}.", [calc]))
        unc.append(Uncertainty("Simulated ranges assume volatility and drift estimated from past prices.", "Regime changes, earnings shocks and crashes can fall outside them."))

    if f is not None:
        latest_k = f.latest_filing("10-K", "10-K/A")
        if latest_k:
            facts.append(Fact("Filings and disclosures", f"The latest annual report is the {latest_k.form} filed {latest_k.filed} for the period ended {latest_k.report_date}.", [reg.filing_record(latest_k, f.name)]))
        for ft in ws.filing_texts:
            if "Risk Factors" in ft.sections:
                risks.append(Risk(f"The {ft.filing.form} filed {ft.filing.filed} lists the company's own risk factors in Item 1A; the rules engine does not read them.", [reg.filing_section(ft.source, "Risk Factors")]))
        unc.append(Uncertainty("The rules engine does not read filing text.", "Management's discussion and stated risk factors are not reflected; add an Anthropic or OpenAI key for an analysis that reads them."))

    if h.status in ("stale", "import"):
        unc.append(Uncertainty(f"Price data is an {h.source.label().split(' | ')[1].lower()} from {h.source.retrieved_at:%Y-%m-%d}.", "Recent moves may be missing."))
    if ws.is_demo:
        unc.append(Uncertainty("This is simulated demonstration data.", "Nothing in this note describes a real company."))

    if not r and not fc:
        rec, conviction = "No recommendation", "Low"
    else:
        rec = "Buy" if score >= 5 else ("Accumulate" if score >= 2 else ("Sell" if score <= -5 else ("Reduce" if score <= -2 else "Hold")))
        conviction = "Medium" if abs(score) >= 6 else "Low"
    summary = (
        f"Rules-based assessment of {h.symbol}: {rec.lower()} with {conviction.lower()} conviction, from a total score of {score:+d} across "
        f"{len(interp)} scored observations on quality, growth, valuation, balance sheet, risk and the prediction model."
    )
    return Note(summary, rec, conviction, "6 to 12 months", facts, interp, risks, unc, gaps, engine="FinLit Pro rules engine")
