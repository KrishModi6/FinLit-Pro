"""Fundamentals from SEC EDGAR: ratios, ten years of statements, quality scores, filings."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_quant import validation
from finlit_quant.ai.brief import money, num, pct
from finlit_quant.analysis import Analysis
from finlit_quant.ui import theme
from finlit_quant.ui.charts import Chart, compact_formatter, percent_formatter
from finlit_quant.ui.widgets import Banner, CardGrid, Field, Table, label, panel, scroll_page, tone_for

ROWS = [
    ("revenue", "Revenue", "money"),
    ("gross_profit", "Gross profit", "money"),
    ("operating_income", "Operating income", "money"),
    ("net_income", "Net income", "money"),
    ("eps_diluted", "Diluted EPS", "eps"),
    ("operating_cash_flow", "Operating cash flow", "money"),
    ("capex", "Capital expenditure", "money"),
    ("fcf", "Free cash flow", "money"),
    ("rnd", "R&D", "money"),
    ("sbc", "Stock-based comp", "money"),
    ("dividends_paid", "Dividends paid", "money"),
    ("buybacks", "Buybacks", "money"),
    ("cash", "Cash", "money"),
    ("total_debt", "Total debt", "money"),
    ("equity", "Shareholders' equity", "money"),
    ("total_assets", "Total assets", "money"),
    ("diluted_shares", "Diluted shares", "shares"),
]


class FundamentalsTab(QWidget):
    email_saved = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        self.setup, setup_lay = panel(
            "Connect SEC EDGAR (free, one time)",
            "The SEC asks every app that reads EDGAR to identify itself with a contact email, sent in the "
            "request header. It is not an account and nothing is signed up for. It stays on this computer.",
        )
        row = QHBoxLayout()
        self.email = Field("Your email", placeholder="name@example.com", width=320)
        save = QPushButton("Save and load fundamentals")
        save.setObjectName("Primary")
        save.clicked.connect(self._save_email)
        row.addWidget(self.email)
        row.addWidget(save)
        row.addStretch(1)
        setup_lay.addLayout(row)
        lay.addWidget(self.setup)
        self.setup.hide()

        self.banner = Banner()
        lay.addWidget(self.banner)
        self.header = label("", "H2", wrap=True)
        self.sub = label("", "Muted", wrap=True)
        lay.addWidget(self.header)
        lay.addWidget(self.sub)

        self.cards = CardGrid(5)
        for key, title, tip in (
            ("market_cap", "Market cap", "Live price x shares outstanding from the latest filing cover page."),
            ("enterprise_value", "Enterprise value", "Market cap + debt - cash and short-term investments."),
            ("pe", "P/E (TTM)", "Market cap / trailing twelve months net income."),
            ("ev_ebit", "EV / EBIT", "Enterprise value / operating income. Capital-structure neutral."),
            ("fcf_yield", "FCF yield", "Free cash flow (operating cash flow - capex) / market cap."),
            ("gross_margin", "Gross margin", ""),
            ("operating_margin", "Operating margin", ""),
            ("roic", "ROIC", "After-tax operating income / (debt + equity - cash)."),
            ("roe", "ROE", "Net income / average shareholders' equity."),
            ("revenue_cagr_5y", "Revenue CAGR 5y", ""),
            ("net_debt", "Net debt", "Debt minus cash and short-term investments. Negative means net cash."),
            ("debt_to_equity", "Debt / equity", ""),
            ("current_ratio", "Current ratio", "Current assets / current liabilities."),
            ("interest_coverage", "Interest coverage", "Operating income / interest expense."),
            ("share_change_3y", "Share count /yr (3y)", "Negative means buybacks are shrinking the share count."),
        ):
            self.cards.card(key, title, tip)
        lay.addWidget(self.cards)

        chart_frame, chart_lay = panel("Ten years of results")
        self.chart = Chart(height=330)
        chart_lay.addWidget(self.chart)
        lay.addWidget(chart_frame)

        quality = QHBoxLayout()
        f_frame, f_lay = panel("Piotroski F-score", "Nine pass/fail tests of profitability, leverage and efficiency, last two fiscal years.")
        self.f_score = label("", "H2")
        f_lay.addWidget(self.f_score)
        self.f_table = Table(["Test", "Result", "Detail"])
        f_lay.addWidget(self.f_table)
        z_frame, z_lay = panel("Altman Z-score", "Bankruptcy-risk score from five balance sheet ratios. Built for manufacturers; not meaningful for banks.")
        self.z_value = label("", "Price")
        self.z_zone = label("", "Muted", wrap=True)
        z_lay.addWidget(self.z_value)
        z_lay.addWidget(self.z_zone)
        z_lay.addStretch(1)
        quality.addWidget(f_frame, 3)
        quality.addWidget(z_frame, 2)
        lay.addLayout(quality)

        t_frame, t_lay = panel("Annual statements (from 10-K filings)", "Latest filing wins, so restated years show their restated figures.")
        self.table = Table()
        t_lay.addWidget(self.table)
        lay.addWidget(t_frame)

        fl_frame, fl_lay = panel("Recent filings", "Double-click a row to open the document on sec.gov.")
        self.filing_filter = QComboBox()
        self.filing_filter.addItems(["Key filings (10-K, 10-Q, 8-K, proxy, ownership)", "All filings, including insider Form 4"])
        self.filing_filter.currentIndexChanged.connect(lambda _: self._fill_filings())
        self.insiders = label("", "Muted")
        filter_row = QHBoxLayout()
        filter_row.addWidget(self.filing_filter)
        filter_row.addWidget(self.insiders, 1)
        fl_lay.addLayout(filter_row)
        self.filings = Table(["Filed", "Form", "Period", "Description"])
        self.filings.cellDoubleClicked.connect(self._open_filing)
        fl_lay.addWidget(self.filings)
        lay.addWidget(fl_frame)
        lay.addStretch(1)
        self._urls: list[str] = []
        self._fund = None

    def _fill_filings(self) -> None:
        f = self._fund
        if f is None:
            return
        rows = f.key_filings() if self.filing_filter.currentIndex() == 0 else f.filings
        self._urls = [fl.url for fl in rows]
        self.filings.fill([[fl.filed, fl.form, fl.report_date, fl.description] for fl in rows], align_right_from=99, stretch_col=3)
        self.filings.fit_height(15)
        self.insiders.setText(f"{f.insider_filings(90)} insider (Form 4) filings in the last 90 days")

    def _save_email(self) -> None:
        try:
            value = validation.email(self.email.text())
        except validation.ValidationError as exc:
            self.email.set_error(str(exc))
            return
        self.email.clear_error()
        self.email_saved.emit(value)

    def _open_filing(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._urls) and self._urls[row]:
            QDesktopServices.openUrl(QUrl(self._urls[row]))

    def need_email(self, show: bool) -> None:
        self.setup.setVisible(show)

    def show_loading(self) -> None:
        self.banner.show_message("Loading filings from SEC EDGAR...", "info")

    def render(self, a: Analysis) -> None:
        f = a.fundamentals
        if f is None:
            if a.fundamentals_error:
                self.banner.show_message(a.fundamentals_error, "warn")
            self.header.setText(a.history.name if a.history else "")
            self.sub.setText("")
            self.chart.message("No SEC fundamentals for this ticker.")
            return
        self.banner.hide()
        self.setup.hide()
        r = a.ratios
        self.header.setText(f.name)
        self.sub.setText(
            f"CIK {f.cik}   |   {f.sic_description or 'Industry n/a'}   |   Fiscal year ends {f.fiscal_year_end[:2] + '/' + f.fiscal_year_end[2:] if f.fiscal_year_end else 'n/a'}"
            f"   |   Latest balance sheet {f.latest_period or 'n/a'}   |   "
            + ("Source: simulated demo data" if f.source == "demo" else f"Source: SEC EDGAR XBRL ({f.source})")
            + ("".join(f"\n{note}" for note in f.split_notes))
        )

        def card(key, text, tone="neutral", sub=""):
            self.cards.card(key, "").set(text, sub, tone)

        card("market_cap", money(r.get("market_cap")), sub=f"{f.shares_outstanding / 1e6:,.0f}M shares" if f.shares_outstanding else "")
        card("enterprise_value", money(r.get("enterprise_value")))
        card("pe", num(r.get("pe"), 1), "neutral" if np.isfinite(r.get("pe", np.nan)) else "warn", "" if np.isfinite(r.get("pe", np.nan)) else "no positive earnings")
        card("ev_ebit", num(r.get("ev_ebit"), 1))
        card("fcf_yield", pct(r.get("fcf_yield")), tone_for(r.get("fcf_yield")), f"FCF {money(r.get('fcf'))}")
        card("gross_margin", pct(r.get("gross_margin")))
        card("operating_margin", pct(r.get("operating_margin")), tone_for(r.get("operating_margin")))
        card("roic", pct(r.get("roic")), "good" if r.get("roic", 0) > 0.12 else ("bad" if r.get("roic", 0) < 0 else "neutral"))
        card("roe", pct(r.get("roe")), tone_for(r.get("roe")))
        card("revenue_cagr_5y", pct(r.get("revenue_cagr_5y")), tone_for(r.get("revenue_cagr_5y")), f"3y {pct(r.get('revenue_cagr_3y'))}")
        nd = r.get("net_debt")
        card("net_debt", money(nd), "good" if nd is not None and nd < 0 else "neutral", "net cash" if nd is not None and nd < 0 else "")
        card("debt_to_equity", num(r.get("debt_to_equity")))
        card("current_ratio", num(r.get("current_ratio")), "bad" if r.get("current_ratio", 2) < 1 else "neutral")
        card("interest_coverage", f"{num(r.get('interest_coverage'), 1)}x", "bad" if r.get("interest_coverage", 99) < 3 else "neutral")
        card("share_change_3y", pct(r.get("share_change_3y"), 2, True), tone_for(r.get("share_change_3y"), good_if_positive=False))

        ann = f.annual.copy()
        ann["fcf"] = ann["operating_cash_flow"] - ann["capex"].fillna(0)
        years = [d.strftime("FY%Y") if d.month >= 6 else d.strftime("FY%Y (%b)") for d in ann.index]

        fig = self.chart.clear()
        ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [3, 2]})
        x = np.arange(len(ann))
        w = 0.27
        for k, (col, name, color) in enumerate((("revenue", "Revenue", theme.SKY), ("net_income", "Net income", theme.ACCENT), ("fcf", "Free cash flow", theme.AMBER))):
            ax1.bar(x + (k - 1) * w, ann[col].fillna(0), w, label=name, color=color)
        ax1.set_xticks(x, [y[2:6] for y in years])
        ax1.yaxis.set_major_formatter(compact_formatter())
        ax1.set_title("Revenue, net income and free cash flow (USD)")
        ax1.legend(loc="upper left")
        for col, name, color in (("gross_profit", "Gross", theme.SKY), ("operating_income", "Operating", theme.ACCENT), ("net_income", "Net", theme.AMBER), ("fcf", "FCF", theme.PURPLE)):
            ax2.plot(x, ann[col] / ann["revenue"], marker="o", markersize=3, label=name, color=color)
        ax2.set_xticks(x, [y[2:6] for y in years])
        ax2.yaxis.set_major_formatter(percent_formatter())
        ax2.set_title("Margins")
        ax2.legend(loc="best", ncols=2)
        self.chart.draw()

        if a.piotroski:
            score, runnable, checks = a.piotroski
            self.f_score.setText(f"{score} of {runnable} tests passed")
            self.f_score.setStyleSheet(f"color: {theme.ACCENT if score >= 7 else (theme.RED if score <= 3 else theme.AMBER)};")
            self.f_table.fill(
                [[c.name, "Pass" if c.passed else ("Fail" if c.passed is False else "n/a"), c.detail] for c in checks],
                [[None, "good" if c.passed else ("bad" if c.passed is False else "neutral"), None] for c in checks],
                align_right_from=99,
                stretch_col=2,
            )
            self.f_table.fit_height()
        if a.altman:
            z, zone = a.altman
            self.z_value.setText(num(z))
            self.z_value.setStyleSheet(f"color: {theme.ACCENT if 'Safe' in zone else (theme.RED if 'Distress' in zone else theme.AMBER)};")
            self.z_zone.setText(zone)

        self.table.set_headers(["Metric"] + years)
        rows = []
        for key, name, kind in ROWS:
            if key not in ann or ann[key].isna().all():
                continue
            vals = []
            for v in ann[key]:
                if kind == "eps":
                    vals.append(num(v))
                elif kind == "shares":
                    vals.append(f"{v / 1e6:,.0f}M" if np.isfinite(v) else "n/a")
                else:
                    vals.append(money(v))
            rows.append([name] + vals)
        self.table.fill(rows)
        self.table.fit_height(40)

        self._fund = f
        self._fill_filings()
