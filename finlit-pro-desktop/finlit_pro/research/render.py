"""Render a research note as HTML for the panel and the exported report."""

from __future__ import annotations

import html
from datetime import datetime

from finlit_pro.research.note import Note
from finlit_pro.research.sources import SourceRegistry

TONE = {"Buy": "#1a7f37", "Accumulate": "#1a7f37", "Hold": "#9a6700", "Reduce": "#cf222e", "Sell": "#cf222e", "No recommendation": "#57606a"}


def _cite(ids: list[str], reg: SourceRegistry) -> str:
    out = []
    for sid in ids:
        e = reg.get(sid)
        if e and e.url:
            out.append(f'<a href="{html.escape(e.url)}" title="{html.escape(e.title)}">{sid}</a>')
        else:
            out.append(f'<span title="{html.escape(e.title if e else "unknown")}">{sid}</span>')
    return f'<span class="cite">[{", ".join(out)}]</span>' if out else '<span class="warn">[unverified]</span>'


def to_html(note: Note, reg: SourceRegistry, symbol: str, colors: dict[str, str] | None = None) -> str:
    c = {"text": "#1f2328", "muted": "#59636e", "border": "#d1d9e0", "link": "#0969da", "bg": "transparent"} | (colors or {})
    e = html.escape
    parts = [
        f"""<style>
        body {{ color: {c['text']}; }}
        h2 {{ font-size: 15px; margin: 14px 0 4px 0; }}
        h3 {{ font-size: 13px; margin: 12px 0 4px 0; color: {c['muted']}; text-transform: uppercase; }}
        td, th {{ padding: 3px 8px 3px 0; vertical-align: top; }}
        th {{ text-align: left; color: {c['muted']}; font-weight: 600; }}
        a {{ color: {c['link']}; text-decoration: none; }}
        .cite {{ color: {c['muted']}; font-size: 11px; }}
        .warn {{ color: #cf222e; font-size: 11px; }}
        .muted {{ color: {c['muted']}; }}
        </style>""",
        f"<h2>Research note: {e(symbol)}</h2>",
        f'<p class="muted">{e(note.engine)} | generated {datetime.now():%Y-%m-%d %H:%M}</p>',
        f'<p><b style="color:{TONE.get(note.recommendation, c["text"])}">{e(note.recommendation)}</b> | conviction {e(note.conviction)} | horizon {e(note.horizon)}</p>',
        f"<p>{e(note.summary)}</p>",
    ]
    if note.warnings:
        parts.append("".join(f'<p class="warn">{e(w)}</p>' for w in note.warnings))

    parts.append("<h3>Facts</h3>")
    topics = list(dict.fromkeys(f.topic for f in note.facts))
    parts.append("<table>")
    for topic in topics:
        rows = [f for f in note.facts if f.topic == topic]
        for i, f in enumerate(rows):
            label = e(topic) if i == 0 else ""
            mark = "" if f.verified else ' <span class="warn">unverified</span>'
            parts.append(f'<tr><th width="150">{label}</th><td>{e(f.statement)} {_cite(f.sources, reg)}{mark}</td></tr>')
    parts.append("</table>")

    parts.append("<h3>Interpretation</h3><table>")
    for i in note.interpretation:
        parts.append(f'<tr><th width="70">{e(i.confidence)}</th><td>{e(i.statement)} {_cite(i.based_on, reg) if i.based_on else ""}</td></tr>')
    parts.append("</table>")

    if note.risks:
        parts.append("<h3>Risks</h3><ul>" + "".join(f"<li>{e(r.risk)} {_cite(r.sources, reg) if r.sources else ''}</li>" for r in note.risks) + "</ul>")
    if note.uncertainties or note.data_gaps:
        parts.append("<h3>Uncertainty and data gaps</h3><ul>")
        parts += [f"<li><b>{e(u.issue)}</b> {e(u.effect)}</li>" for u in note.uncertainties]
        parts += [f"<li>Data gap: {e(g)}</li>" for g in note.data_gaps]
        parts.append("</ul>")

    used = {sid for f in note.facts for sid in f.sources} | {sid for i in note.interpretation for sid in i.based_on} | {sid for r in note.risks for sid in r.sources}
    parts.append("<h3>Sources</h3><table><tr><th>ID</th><th>Source</th><th>As of</th><th>Retrieved</th></tr>")
    for s in reg.entries:
        if s.id not in used:
            continue
        title = f'<a href="{e(s.url)}">{e(s.title)}</a>' if s.url else e(s.title)
        retrieved = s.retrieved.strftime("%Y-%m-%d %H:%M") if s.retrieved else ""
        parts.append(f'<tr><td>{s.id}</td><td>{title}<br><span class="muted">{e(s.detail)}</span></td><td>{e(s.as_of or "")}</td><td>{retrieved}</td></tr>')
    parts.append("</table>")
    return "\n".join(parts)
