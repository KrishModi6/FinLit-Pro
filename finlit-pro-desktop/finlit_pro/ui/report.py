"""Export: a self-contained HTML research report and the price history as CSV."""

from __future__ import annotations

import base64
import html
from datetime import datetime

from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtWidgets import QWidget

from finlit_pro import APP_NAME, __version__, framing
from finlit_pro.data.models import STATUS_LABEL, Source
from finlit_pro.fmt import money, num, pct
from finlit_pro.workspace import Workspace


def widget_png(widget: QWidget) -> str:
    data = QByteArray()
    buf = QBuffer(data)
    buf.open(QIODevice.WriteOnly)
    widget.grab().save(buf, "PNG")
    return base64.b64encode(bytes(data)).decode("ascii")


def all_sources(ws: Workspace, extra: list[Source] | None = None) -> list[Source]:
    out = []
    if ws.history:
        out.append(ws.history.source)
    if ws.benchmark:
        out.append(ws.benchmark.source)
    if ws.risk_free_source:
        out.append(ws.risk_free_source)
    if ws.fundamentals:
        out += ws.fundamentals.sources
    out += [ft.source for ft in ws.filing_texts]
    return out + (extra or [])


def build_html(ws: Workspace, charts: dict[str, str], note_html: str) -> str:
    e = html.escape
    h = ws.history
    rows = []
    if h:
        rows += [("Last price", f"{num(h.price)} {h.currency} ({h.bars.index[-1].date()})"), ("Change on the day", pct(h.day_change, 2, True))]
    r = ws.ratios
    if r:
        rows += [("Market cap", money(r.get("market_cap"))), ("P/E (TTM)", num(r.get("pe"), 1)), ("EV/EBIT", num(r.get("ev_ebit"), 1)), ("FCF yield", pct(r.get("fcf_yield"))), ("ROIC", pct(r.get("roic")))]
    if ws.risk:
        m = ws.risk.metrics
        rows += [("Volatility", pct(m.get("volatility"))), ("Sharpe", num(m.get("sharpe"))), ("Max drawdown", pct(-m.get("max_drawdown", float("nan"))))]
    fc = ws.forecast
    if fc:
        rows += [(f"{fc.model} v{fc.version}", f"{fc.verdict}, target {num(fc.target)} ({pct(fc.expected_return, 1, True)}) in {fc.horizon_days} trading days")]
    if ws.mc:
        s = ws.mc.stats
        rows += [(f"Monte Carlo P10-P90 ({ws.mc.config.horizon_days} days)", f"{num(s['p10'])} to {num(s['p90'])}")]
    key = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in rows)
    ev = ""
    if ws.evaluation:
        ev = "<table>" + "".join(f"<tr><th>{e(m.name)}</th><td>{e(m.display)}</td><td>{e(m.benchmark)}</td><td>{e(m.flag)}</td></tr>" for m in ws.evaluation.metrics) + "</table>"
        ev += f"<p class='muted'>{e(' '.join(ws.evaluation.notes))}</p>"
    def link(s: Source) -> str:
        return f'<a href="{e(s.url)}">{e(s.name)}</a>' if s.url else e(s.name)

    src = "".join(
        f"<tr><td>{link(s)}</td><td>{e(STATUS_LABEL.get(s.status, s.status))}</td>"
        f"<td>{e(s.as_of or '')}</td><td>{s.retrieved_at:%Y-%m-%d %H:%M}</td><td>{e(s.detail)}</td></tr>"
        for s in all_sources(ws)
    )
    figs = "".join(f'<figure><img alt="{e(c)}" src="data:image/png;base64,{b}"><figcaption>{e(c)}</figcaption></figure>' for c, b in charts.items())
    title = f"{h.symbol} research report" if h else "Research report"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<style>
body {{ margin:0; background:#ffffff; color:#1f2328; font:14px/1.5 "Segoe UI",system-ui,sans-serif; }}
main {{ max-width:1000px; margin:0 auto; padding:28px 16px 48px; }}
h1 {{ font-size:22px; margin:0 0 2px; }} h2 {{ font-size:15px; margin:24px 0 8px; border-bottom:1px solid #d1d9e0; padding-bottom:4px; }}
table {{ border-collapse:collapse; width:100%; }} th,td {{ text-align:left; padding:4px 8px 4px 0; border-bottom:1px solid #eaeef2; vertical-align:top; }}
th {{ color:#59636e; font-weight:600; }} .muted {{ color:#59636e; }} a {{ color:#0969da; text-decoration:none; }}
img {{ max-width:100%; border:1px solid #d1d9e0; }} figure {{ margin:14px 0; }} figcaption {{ color:#59636e; font-size:12px; }}
.note {{ background:#f6f8fa; border-left:3px solid #0969da; padding:8px 12px; }}
</style></head><body><main>
<h1>{e(title)}</h1>
<p class="muted">{e(h.name if h else '')} | generated {datetime.now():%Y-%m-%d %H:%M} | {APP_NAME} {__version__}</p>
<p class="note">{e(framing.PERSONAL_USE)}</p>
<h2>Summary</h2><table>{key}</table>
<h2>Model evaluation (out of sample)</h2>{ev or '<p class="muted">Not run.</p>'}
<h2>Research note</h2>{note_html or '<p class="muted">No note generated.</p>'}
<h2>Charts</h2>{figs or '<p class="muted">None.</p>'}
<h2>Data sources</h2><table><tr><th>Source</th><th>Status</th><th>As of</th><th>Retrieved</th><th>Detail</th></tr>{src}</table>
<p class="muted">{e(framing.SIMULATION_NOTE)}</p>
</main></body></html>"""


def price_csv(ws: Workspace) -> str:
    return ws.history.bars.to_csv(index_label="date", float_format="%.6g") if ws.history else ""
