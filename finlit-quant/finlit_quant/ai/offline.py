"""The offline analyst: a rule-based memo for when no AI key is configured.

It reads the same Analysis the language models do and applies fixed,
documented rules, so it is transparent about exactly why it says what it
says. Each rule adds or subtracts points in one of five pillars; the pillars
decide the stance. It cannot reason about the business, only the numbers,
and the memo says so.
"""

from __future__ import annotations

import numpy as np

from finlit_quant.ai.brief import money, num, pct
from finlit_quant.analysis import Analysis
from finlit_quant.analytics import indicators as ind


def _ok(v) -> bool:
    return v is not None and np.isfinite(v)


def memo(a: Analysis) -> str:
    h = a.history
    if h is None:
        return "Load a ticker first."
    r = a.ratios
    pillars: dict[str, list[tuple[int, str]]] = {"Quality": [], "Growth": [], "Valuation": [], "Balance sheet": [], "Price and risk": []}

    def add(pillar: str, points: int, text: str) -> None:
        pillars[pillar].append((points, text))

    # Quality
    if _ok(r.get("roic")):
        v = r["roic"]
        add("Quality", 2 if v > 0.15 else (1 if v > 0.08 else -1), f"ROIC of {pct(v)} {'is excellent' if v > 0.15 else ('clears a typical cost of capital' if v > 0.08 else 'is below a typical cost of capital')}.")
    if _ok(r.get("operating_margin")):
        v = r["operating_margin"]
        add("Quality", 1 if v > 0.2 else (0 if v > 0.05 else -1), f"Operating margin is {pct(v)}.")
    if a.piotroski and a.piotroski[1] >= 6:
        score, runnable, _ = a.piotroski
        frac = score / runnable
        add("Quality", 1 if frac >= 0.7 else (-1 if frac <= 0.35 else 0), f"Piotroski F-score {score}/{runnable}: {'improving fundamentals' if frac >= 0.7 else ('deteriorating fundamentals' if frac <= 0.35 else 'mixed')}.")
    if _ok(r.get("sbc_to_revenue")) and r["sbc_to_revenue"] > 0.1:
        add("Quality", -1, f"Stock-based compensation is {pct(r['sbc_to_revenue'])} of revenue, a real cost that GAAP cash flow adds back.")

    # Growth
    if _ok(r.get("revenue_cagr_3y")):
        v = r["revenue_cagr_3y"]
        add("Growth", 2 if v > 0.15 else (1 if v > 0.05 else (-1 if v < 0 else 0)), f"Revenue has compounded {pct(v)} a year over three years.")
    if _ok(r.get("eps_cagr_5y")):
        v = r["eps_cagr_5y"]
        add("Growth", 1 if v > 0.1 else (-1 if v < 0 else 0), f"Diluted EPS grew {pct(v)} a year over five years.")
    if _ok(r.get("share_change_3y")):
        v = r["share_change_3y"]
        if v < -0.01:
            add("Growth", 1, f"The share count is shrinking {pct(-v)} a year, so buybacks add to per-share growth.")
        elif v > 0.02:
            add("Growth", -1, f"The share count is growing {pct(v)} a year, diluting holders.")

    # Valuation
    if _ok(r.get("fcf_yield")):
        v = r["fcf_yield"]
        add("Valuation", 2 if v > 0.06 else (1 if v > 0.04 else (-1 if v < 0.02 else 0)), f"Free cash flow yield is {pct(v)}.")
    if _ok(r.get("pe")):
        v = r["pe"]
        add("Valuation", 1 if v < 15 else (-1 if v > 35 else 0), f"P/E is {num(v, 1)}.")
    if a.implied_growth is not None and _ok(r.get("fcf_cagr_5y")):
        gap = a.implied_growth - r["fcf_cagr_5y"]
        add("Valuation", -1 if gap > 0.05 else (1 if gap < -0.05 else 0), f"The price implies {pct(a.implied_growth)} FCF growth against {pct(r['fcf_cagr_5y'])} delivered over five years.")
    if a.dcf:
        up = a.dcf.per_share / h.price - 1
        add("Valuation", 1 if up > 0.25 else (-1 if up < -0.25 else 0), f"The DCF with the current assumptions gives {num(a.dcf.per_share)}, {pct(up, 0, True)} from the price.")

    # Balance sheet
    if _ok(r.get("net_debt")) and _ok(r.get("market_cap")) and r["market_cap"] > 0:
        v = r["net_debt"] / r["market_cap"]
        add("Balance sheet", 1 if v < 0 else (-1 if v > 0.5 else 0), f"Net {'cash' if v < 0 else 'debt'} of {money(abs(r['net_debt']))}, {pct(abs(v), 1)} of market cap.")
    if _ok(r.get("interest_coverage")):
        v = r["interest_coverage"]
        add("Balance sheet", -2 if v < 2 else (0 if v < 6 else 1), f"Operating income covers interest {num(v, 1)} times.")
    if a.altman and _ok(a.altman[0]) and "meaningful" not in a.altman[1]:
        add("Balance sheet", -2 if "Distress" in a.altman[1] else (1 if "Safe" in a.altman[1] else 0), f"Altman Z of {num(a.altman[0])}: {a.altman[1].lower()}.")

    # Price and risk
    closes = h.closes
    if len(closes) > 200:
        sma200 = float(ind.sma(closes, 200).iloc[-1])
        add("Price and risk", 1 if closes.iloc[-1] > sma200 else -1, f"Price is {'above' if closes.iloc[-1] > sma200 else 'below'} its 200-day average ({pct(closes.iloc[-1] / sma200 - 1, 1, True)}).")
    if a.risk:
        m = a.risk.metrics
        add("Price and risk", 1 if m.get("sharpe", 0) > 0.8 else (-1 if m.get("sharpe", 0) < 0 else 0), f"Sharpe ratio of {num(m.get('sharpe'))} over the window, with volatility of {pct(m.get('volatility'))}.")
        if m.get("max_drawdown", 0) > 0.5:
            add("Price and risk", -1, f"It has fallen {pct(m['max_drawdown'], 0)} peak to trough in this window; the holder needs a strong stomach.")
    if a.predictor:
        add("Price and risk", int(np.sign(a.predictor.score)) if abs(a.predictor.score) >= 2 else 0, f"The technical signal engine reads {a.predictor.verdict.lower()} ({a.predictor.score:+d}).")

    totals = {k: sum(p for p, _ in v) for k, v in pillars.items() if v}
    total = sum(totals.values())
    stance = "Bullish" if total >= 4 else ("Bearish" if total <= -3 else "Neutral")
    conviction = "medium" if abs(total) >= 7 else "low"

    out = []
    if a.is_demo:
        out.append("> **Simulated demo data.** Nothing below describes a real company.\n")
    out.append("## Verdict")
    out.append(f"**{stance}**, {conviction} conviction, on a 6 to 12 month view. Rule score {total:+d} across {len(totals)} pillars: " + ", ".join(f"{k} {v:+d}" for k, v in totals.items()) + ".")
    out.append("")
    for pillar, items in pillars.items():
        if not items:
            continue
        out.append(f"## {pillar} ({totals[pillar]:+d})")
        out += [f"- {text}" for _, text in items]
        out.append("")
    if a.mc:
        s = a.mc.stats
        out.append("## Monte Carlo read")
        out.append(
            f"Over {a.mc.config.horizon_days} trading days, half the simulated paths end below {num(s['p50'])} and one in twenty below {num(s['p5'])}. "
            f"{pct(s['prob_loss_20'], 0)} of paths lose 20% or more, and the typical path suffers a {pct(s['expected_max_dd'], 0)} drawdown along the way, "
            "which matters more for sizing than where it ends."
        )
        if a.calibration:
            out.append("")
            out.append(a.calibration.verdict)
        out.append("")
    if a.fundamentals is None and a.fundamentals_error:
        out.append(f"*Fundamentals were not available: {a.fundamentals_error}*\n")
    out.append("## What to check next")
    out.append("- Read the latest 10-K risk factors and MD&A: these rules cannot see the business, only the numbers.")
    out.append("- Compare the margins and growth here against two direct competitors in the Compare tab.")
    out.append("- Stress the DCF: what growth does the price need, and is that believable?")
    out.append("")
    out.append("*Offline rule-based analyst. Add an Anthropic or OpenAI key in Settings for a written AI memo. Research, not personal financial advice.*")
    return "\n".join(out)
