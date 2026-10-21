"""Fundamentals from SEC EDGAR: ratios, ten years of statements with per-value provenance, quality scores."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTabWidget, QVBoxLayout, QWidget

from finlit_pro import glossary, validation
from finlit_pro.fmt import money, num, pct
from finlit_pro.ui import theme
from finlit_pro.ui.charts import Chart, compact_formatter, percent_formatter
from finlit_pro.ui.views.valuation_view import ValuationView
from finlit_pro.ui.widgets import Field, KpiStrip, Notice, SourceLine, Table, hrow, label, panel, scroll_page, tone
from finlit_pro.workspace import Workspace

ROWS = [
    ("revenue", "Revenue", "money"),
    ("gross_profit", "Gross profit", "money"),
    ("operating_income", "Operating income", "money"),
    ("net_income", "Net income", "money"),
    ("eps_diluted", "Diluted EPS", "eps"),
    ("operating_cash_flow", "Operating cash flow", "money"),
    ("capex", "Capital expenditure", "money"),
    ("fcf", "Free cash flow", "money"),
    ("rnd", "Research and development", "money"),
    ("sbc", "Stock-based compensation", "money"),
    ("dividends_paid", "Dividends paid", "money"),
    ("buybacks", "Share repurchases", "money"),
    ("cash", "Cash and equivalents", "money"),
    ("total_debt", "Total debt", "money"),
    ("equity", "Shareholders' equity", "money"),
    ("total_assets", "Total assets", "money"),
    ("diluted_shares", "Diluted shares", "shares"),
]


class FundamentalsView(QWidget):
    email_saved = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.inner = QTabWidget()
        self.inner.setDocumentMode(True)
        root.addWidget(self.inner)
        self.valuation = ValuationView()

        area, lay = scroll_page()
        self.inner.addTab(area, "Statements and ratios")
        self.inner.addTab(self.valuation, "Valuation (DCF)")

        self.setup, setup_lay = panel("SEC EDGAR access", "The SEC requires a contact email in the User-Agent header of every EDGAR request. It is sent only to sec.gov and stored in your settings.")
        self.email = Field("Contact email", placeholder="name@example.com", width=280)
        save = QPushButton("Save")
        save.setObjectName("Primary")
        save.clicked.connect(self._save_email)
        setup_lay.addLayout(hrow(self.email, save))
        lay.addWidget(self.setup)
        self.setup.hide()
        self.notice = Notice()
        lay.addWidget(self.notice)
        self.header = label("", "Title", wrap=True)
        self.sub = label("", "Small", wrap=True)
        lay.addWidget(self.header)
        lay.addWidget(self.sub)

        self.kpis = KpiStrip(8)
        for key, cap, tip in (
            ("market_cap", "Market cap", "Live price x shares outstanding from the latest filing cover page."),
            ("enterprise_value", "Enterprise value", "Market cap + debt - cash and short-term investments."),
            ("pe", "P/E (TTM)", "Market cap / trailing twelve months net income."),
            ("ev_ebit", "EV / EBIT", "Enterprise value / TTM operating income."),
            ("fcf_yield", "FCF yield", "TTM operating cash flow less capex, over market cap."),
            ("dividend_yield", "Dividend yield", "Trailing 12-month dividends per share / price."),
            ("gross_margin", "Gross margin", ""),
            ("operating_margin", "Operating margin", ""),
            ("roic", "ROIC", "After-tax operating income / (debt + equity - cash)."),
            ("roe", "ROE", "Net income / average shareholders' equity."),
            ("revenue_cagr_5y", "Revenue CAGR 5y", ""),
            ("eps_cagr_5y", "EPS CAGR 5y", ""),
            ("net_debt", "Net debt", "Debt less cash and short-term investments."),
            ("debt_to_equity", "Debt / equity", ""),
            ("interest_coverage", "Interest coverage", "Operating income / interest expense."),
            ("share_change_3y", "Share count / yr", "Annual change in diluted shares over three years."),
        ):
            self.kpis.kpi(key, cap, tip)
        lay.addWidget(self.kpis)

        chart_frame, chart_lay = panel("Results by fiscal year")
        self.chart = Chart(height=300)
        chart_lay.addWidget(self.chart)
        lay.addWidget(chart_frame)

        t_frame, t_lay = panel("Annual statements", "Hover over a value for the filing it was taken from; double-click to open that filing on sec.gov. Restated years show the latest filed figure.")
        self.table = Table()
        self.table.cellDoubleClicked.connect(self._open_cell)
        t_lay.addWidget(self.table)
        lay.addWidget(t_frame)

        quality = QHBoxLayout()
        f_frame, f_lay = panel("Piotroski F-score", "Nine pass/fail tests over the last two fiscal years.")
        self.f_score = label("", "Kpi")
        f_lay.addWidget(self.f_score)
        self.f_table = Table(["Test", "Result", "Detail"])
        f_lay.addWidget(self.f_table)
        z_frame, z_lay = panel("Altman Z-score", "Five-ratio distress score. Built for manufacturers; not meaningful for banks and insurers.")
        self.z_value = label("", "Kpi")
        self.z_zone = label("", "Small", wrap=True)
        z_lay.addWidget(self.z_value)
        z_lay.addWidget(self.z_zone)
        quality.addWidget(f_frame, 3)
        quality.addWidget(z_frame, 2)
        lay.addLayout(quality)
        self.source = SourceLine()
        lay.addWidget(self.source)
        lay.addStretch(1)
        self._cell_urls: dict[tuple[int, int], str] = {}

    def _save_email(self) -> None:
        try:
            value = validation.email(self.email.text())
        except validation.ValidationError as exc:
            self.email.set_error(str(exc))
            return
        self.email.clear_error()
        self.email_saved.emit(value)

    def _open_cell(self, row: int, col: int) -> None:
        url = self._cell_urls.get((row, col))
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def need_email(self, show: bool) -> None:
        self.setup.setVisible(show)

    def show_loading(self) -> None:
        self.notice.show_message("Loading SEC EDGAR company facts and filing index.")

    def render(self, ws: Workspace) -> None:
        self.valuation.render(ws)
        f = ws.fundamentals
        if f is None:
            if ws.fundamentals_error:
                self.notice.show_message(ws.fundamentals_error, "warn")
            self.header.setText(ws.history.name if ws.history else "")
            self.sub.setText("")
            self.chart.message("No SEC financial statements for this security.")
            return
        self.notice.clear()
        if f.notes:
            # Caveats such as a derived figure, a share count fallback or XBRL lagging the latest filing.
            self.notice.show_message("Data notes: " + " ".join(dict.fromkeys(f.notes)), "warn")
        self.setup.hide()
        r = ws.ratios
        self.header.setText(f.name)
        fye = f"{f.fiscal_year_end[:2]}/{f.fiscal_year_end[2:]}" if f.fiscal_year_end else "n/a"
        self.sub.setText(f"CIK {f.cik}  |  {f.sic_description or 'industry n/a'}  |  fiscal year ends {fye}  |  latest balance sheet {f.latest_period or 'n/a'}" + "".join(f"  |  {n}" for n in f.split_notes))

        def k(key, text, sub="", t=None):
            self.kpis.kpi(key).set(text, sub, t)

        k("market_cap", money(r.get("market_cap")), f"{f.shares_outstanding / 1e6:,.0f}M shares" if f.shares_outstanding else "")
        k("enterprise_value", money(r.get("enterprise_value")))
        k("pe", num(r.get("pe"), 1), "" if np.isfinite(r.get("pe", np.nan)) else "no positive earnings")
        k("ev_ebit", num(r.get("ev_ebit"), 1))
        k("fcf_yield", pct(r.get("fcf_yield")), f"FCF {money(r.get('fcf'))}", tone(r.get("fcf_yield")))
        k("dividend_yield", pct(r.get("dividend_yield"), 2))
        k("gross_margin", pct(r.get("gross_margin")))
        k("operating_margin", pct(r.get("operating_margin")), "", tone(r.get("operating_margin")))
        k("roic", pct(r.get("roic")), "", tone(r.get("roic")))
        k("roe", pct(r.get("roe")), "", tone(r.get("roe")))
        k("revenue_cagr_5y", pct(r.get("revenue_cagr_5y")), f"3y {pct(r.get('revenue_cagr_3y'))}", tone(r.get("revenue_cagr_5y")))
        k("eps_cagr_5y", pct(r.get("eps_cagr_5y")), "", tone(r.get("eps_cagr_5y")))
        nd = r.get("net_debt")
        k("net_debt", money(nd), "net cash" if nd is not None and nd < 0 else "")
        k("debt_to_equity", num(r.get("debt_to_equity")))
        k("interest_coverage", f"{num(r.get('interest_coverage'), 1)}x", "", "down" if r.get("interest_coverage", 99) < 3 else None)
        k("share_change_3y", pct(r.get("share_change_3y"), 2, True), "", tone(r.get("share_change_3y"), positive_is_good=False))

        ann = f.annual.copy()
        ann["fcf"] = ann["operating_cash_flow"] - ann["capex"].fillna(0)
        years = [d.strftime("FY%Y") for d in ann.index]

        fig = self.chart.clear()
        ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [3, 2]})
        x = np.arange(len(ann))
        w = 0.27
        for i, (col, name, color) in enumerate((("revenue", "Revenue", theme.ACCENT), ("net_income", "Net income", theme.UP), ("fcf", "Free cash flow", "#f0883e"))):
            ax1.bar(x + (i - 1) * w, ann[col].fillna(0), w, label=name, color=color)
        ax1.set_xticks(x, [y[2:] for y in years])
        ax1.yaxis.set_major_formatter(compact_formatter())
        ax1.set_title("Revenue, net income and free cash flow (USD)")
        ax1.legend(loc="upper left")
        for col, name, color in (("gross_profit", "Gross", theme.ACCENT), ("operating_income", "Operating", theme.UP), ("net_income", "Net", "#f0883e"), ("fcf", "FCF", "#a371f7")):
            ax2.plot(x, ann[col] / ann["revenue"], marker="o", markersize=3, label=name, color=color, linewidth=1.2)
        ax2.set_xticks(x, [y[2:] for y in years])
        ax2.yaxis.set_major_formatter(percent_formatter())
        ax2.set_title("Margins")
        ax2.legend(loc="best", ncols=2)
        self.chart.draw()

        self.table.set_headers(["Metric"] + years)
        rows, tips = [], []
        self._cell_urls = {}
        for key, name, kind in ROWS:
            if key not in ann or ann[key].isna().all():
                continue
            vals, cell_tips = [], [""]
            for j, (end, v) in enumerate(ann[key].items()):
                if kind == "eps":
                    vals.append(num(v))
                elif kind == "shares":
                    vals.append(f"{v / 1e6:,.0f}M" if np.isfinite(v) else "n/a")
                else:
                    vals.append(money(v))
                ref = f.refs.get(key, {}).get(end)
                if ref and ref.accession:
                    cell_tips.append(f"{ref.form} filed {ref.filed}, accession {ref.accession}")
                    self._cell_urls[(len(rows), j + 1)] = ref.url
                else:
                    cell_tips.append("Derived" if key in ("fcf", "total_debt") else "")
            rows.append([name] + vals)
            tips.append(cell_tips)
        self.table.fill(rows, tips=tips)
        self.table.fit_height(40)

        if ws.piotroski:
            score, runnable, checks = ws.piotroski
            self.f_score.setText(f"{score} / {runnable}")
            self.f_score.setStyleSheet(f"color: {theme.UP if score >= 7 else (theme.DOWN if score <= 3 else theme.WARN)};")
            self.f_table.fill(
                [[c.name, "Pass" if c.passed else ("Fail" if c.passed is False else "n/a"), c.detail] for c in checks],
                [[None, "up" if c.passed else ("down" if c.passed is False else "muted"), None] for c in checks],
                align_right_from=99,
                stretch_col=2,
            )
            self.f_table.fit_height()
        if ws.altman:
            z, zone = ws.altman
            self.z_value.setText(num(z))
            self.z_value.setStyleSheet(f"color: {theme.UP if 'Safe' in zone else (theme.DOWN if 'Distress' in zone else theme.WARN)};")
            self.z_zone.setText(zone)
            self.z_value.setToolTip(glossary.tip("Altman Z-score"))
            self.z_zone.setToolTip(glossary.tip("Altman Z-score"))
        self.source.set_sources(f.sources)
