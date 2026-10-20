"""Export: a self-contained HTML research report, and the raw price data as CSV."""

from __future__ import annotations

import html
from datetime import datetime

from PySide6.QtGui import QTextDocument

from finlit_quant import APP_NAME, __version__
from finlit_quant.ai.brief import money, num, pct
from finlit_quant.analysis import Analysis


def _markdown_to_html(md: str) -> str:
    if not md.strip():
        return "<p><em>No memo written yet. Use the AI Analyst tab first.</em></p>"
    doc = QTextDocument()
    doc.setMarkdown(md)
    body = doc.toHtml()
    start, end = body.find("<body"), body.rfind("</body>")
    if start == -1 or end == -1:
        return body
    return body[body.find(">", start) + 1 : end]


def build_html(a: Analysis, charts: dict[str, str], memo_markdown: str) -> str:
    """`charts` maps a caption to a base64 PNG."""
    h = a.history
    r = a.ratios
    rows = []
    if h:
        rows += [("Price", f"{num(h.price)} {h.currency}"), ("Day change", pct(h.day_change, 2, True)), ("Data as of", str(h.bars.index[-1].date()))]
    if r:
        rows += [
            ("Market cap", money(r.get("market_cap"))),
            ("P/E (TTM)", num(r.get("pe"), 1)),
            ("EV / EBIT", num(r.get("ev_ebit"), 1)),
            ("FCF yield", pct(r.get("fcf_yield"))),
            ("Operating margin", pct(r.get("operating_margin"))),
            ("ROIC", pct(r.get("roic"))),
            ("Revenue CAGR 5y", pct(r.get("revenue_cagr_5y"))),
        ]
    if a.risk:
        m = a.risk.metrics
        rows += [("Volatility", pct(m.get("volatility"))), ("Sharpe", num(m.get("sharpe"))), ("Max drawdown", pct(-m.get("max_drawdown", float("nan"))))]
        if "beta" in m:
            rows.append((f"Beta vs {a.risk.benchmark}", num(m["beta"])))
    if a.mc:
        s = a.mc.stats
        rows += [
            (f"Monte Carlo median ({a.mc.config.horizon_days}d)", num(s["median"])),
            ("Monte Carlo 10th to 90th", f"{num(s['p10'])} to {num(s['p90'])}"),
            ("Paths finishing above today", pct(s["prob_up"], 0)),
        ]
    if a.dcf:
        rows.append(("DCF value per share", num(a.dcf.per_share)))
    if a.implied_growth is not None:
        rows.append(("Growth implied by price", pct(a.implied_growth)))

    table = "".join(f"<tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>" for k, v in rows)
    figures = "".join(
        f'<figure><img alt="{html.escape(cap)}" src="data:image/png;base64,{b64}"><figcaption>{html.escape(cap)}</figcaption></figure>'
        for cap, b64 in charts.items()
    )
    title = f"{h.symbol} research report" if h else "Research report"
    demo = '<p class="warn">Simulated demo data. Nothing here describes a real company.</p>' if a.is_demo else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{ --bg:#0b1220; --panel:#111a2e; --border:#24314f; --text:#e6ebf5; --muted:#8a97b1; --accent:#10b981; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
main {{ max-width:980px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ margin:0 0 4px; font-size:28px; }} .muted {{ color:var(--muted); }}
.warn {{ background:#3a2a0a; border:1px solid #6b4e10; color:#f59e0b; padding:10px 14px; border-radius:8px; }}
section {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:18px 20px; margin-top:18px; }}
table {{ border-collapse:collapse; width:100%; }} th,td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--border); }}
th {{ color:var(--muted); font-weight:600; width:45%; }}
figure {{ margin:18px 0 0; }} img {{ max-width:100%; border-radius:8px; border:1px solid var(--border); }}
figcaption {{ color:var(--muted); font-size:13px; }}
.memo * {{ color:var(--text) !important; background:transparent !important; }}
</style></head><body><main>
<h1>{html.escape(title)}</h1>
<p class="muted">{html.escape(h.name if h else "")} &middot; generated {datetime.now():%Y-%m-%d %H:%M} by {APP_NAME} {__version__}</p>
{demo}
<section><h2>Key numbers</h2><table>{table}</table></section>
<section class="memo"><h2>Analyst memo</h2>{_markdown_to_html(memo_markdown)}</section>
<section><h2>Charts</h2>{figures or '<p class="muted">No charts rendered.</p>'}</section>
<p class="muted">Prices: Yahoo Finance. Fundamentals: SEC EDGAR XBRL company facts. Monte Carlo output describes risk, not a forecast. Research, not personal financial advice.</p>
</main></body></html>"""


def price_csv(a: Analysis) -> str:
    if not a.history:
        return ""
    return a.history.bars.to_csv(index_label="date", float_format="%.6g")
