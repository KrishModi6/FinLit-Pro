"""Valuation: two-stage DCF, sensitivity grid, reverse DCF and a Monte Carlo DCF."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_pro import validation
from finlit_pro.analytics import valuation as val
from finlit_pro.fmt import money, pct
from finlit_pro.ui import theme
from finlit_pro.ui.charts import Chart, price_formatter
from finlit_pro.ui.widgets import Field, KpiStrip, Notice, Table, label, panel, scroll_page, tone
from finlit_pro.workspace import Workspace


class ValuationView(QWidget):
    inputs_changed = Signal(object)  # DCFInputs

    def __init__(self) -> None:
        super().__init__()
        self.analysis: Workspace | None = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        form_frame, form = panel(
            "Discounted cash flow assumptions",
            "Prefilled from the filings: TTM free cash flow, the lower of five-year revenue and FCF growth (capped at 15%), a 9% discount rate and 2.5% terminal growth. Change anything and press Calculate.",
        )
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        self.f_fcf = Field("Base free cash flow ($M)", tip="Operating cash flow minus capex, trailing twelve months.")
        self.f_growth = Field("Growth, years 1-5 (%)", tip="Annual FCF growth in the high-growth stage.")
        self.f_high = Field("High-growth years", "5")
        self.f_fade = Field("Fade years", "5", tip="Years over which growth slides linearly to the terminal rate.")
        self.f_disc = Field("Discount rate (%)", tip="Your required return. 8-10% is typical for a large company.")
        self.f_term = Field("Terminal growth (%)", tip="Growth forever after the forecast. Keep it at or below long-run GDP growth.")
        self.f_cash = Field("Net cash ($M)", tip="Cash minus debt. Negative for a net-debt company.")
        self.f_shares = Field("Shares (M)")
        for i, w in enumerate((self.f_fcf, self.f_growth, self.f_high, self.f_fade, self.f_disc, self.f_term, self.f_cash, self.f_shares)):
            grid.addWidget(w, i // 4, i % 4)
        form.addLayout(grid)
        btns = QHBoxLayout()
        reset = QPushButton("Reset to filing defaults")
        reset.clicked.connect(self._reset)
        calc = QPushButton("Calculate")
        calc.setObjectName("Primary")
        calc.clicked.connect(self._calculate)
        btns.addStretch(1)
        btns.addWidget(reset)
        btns.addWidget(calc)
        form.addLayout(btns)
        lay.addWidget(form_frame)

        self.banner = Notice()
        lay.addWidget(self.banner)

        self.cards = KpiStrip(6)
        for key, title, tip in (
            ("value", "Intrinsic value / share", "Present value of the projected cash flows plus net cash, per share."),
            ("upside", "vs current price", ""),
            ("implied", "Growth the price implies", "Reverse DCF: the stage-one growth that makes the DCF equal today's price."),
            ("terminal", "Terminal value share of EV", "How much of the value sits beyond the forecast. Above 75% means the answer is mostly the terminal assumptions."),
            ("mc_prob", "Monte Carlo: P(value > price)", "Share of 20,000 DCFs with uncertain growth, discount rate and terminal growth that exceed the price."),
            ("mc_band", "Monte Carlo 10th to 90th", ""),
        ):
            self.cards.kpi(key, title, tip)
        lay.addWidget(self.cards)

        row = QHBoxLayout()
        sens_frame, sens = panel("Sensitivity: value per share", "Rows: discount rate. Columns: terminal growth. Green is above the current price.")
        self.sens = Table()
        sens.addWidget(self.sens)
        mc_frame, mc = panel("Monte Carlo DCF", "Growth +/-4 points, discount +/-1 point, terminal +/-0.5 point (one standard deviation).")
        self.mc_chart = Chart(height=260)
        mc.addWidget(self.mc_chart)
        row.addWidget(sens_frame, 1)
        row.addWidget(mc_frame, 1)
        lay.addLayout(row)

        fl_frame, fl = panel("Projected cash flows")
        self.flows = Table(["Year", "Growth", "Free cash flow", "Present value"])
        fl.addWidget(self.flows)
        lay.addWidget(fl_frame)
        self.note = label("", "Muted", wrap=True)
        lay.addWidget(self.note)
        lay.addStretch(1)

    def _fill_fields(self, inp: val.DCFInputs) -> None:
        def m(v):
            return f"{v / 1e6:,.1f}" if np.isfinite(v) else ""

        self.f_fcf.set_text(m(inp.base_fcf))
        self.f_growth.set_text(f"{inp.growth * 100:.1f}")
        self.f_high.set_text(str(inp.years_high))
        self.f_fade.set_text(str(inp.years_fade))
        self.f_disc.set_text(f"{inp.discount * 100:.1f}")
        self.f_term.set_text(f"{inp.terminal_growth * 100:.1f}")
        self.f_cash.set_text(m(inp.net_cash))
        self.f_shares.set_text(f"{inp.shares / 1e6:,.1f}" if np.isfinite(inp.shares) else "")

    def _reset(self) -> None:
        a = self.analysis
        if a and a.fundamentals and a.ratios:
            self._fill_fields(val.default_inputs(a.fundamentals, a.ratios))
            self._calculate()

    def read_inputs(self) -> val.DCFInputs | None:
        ok = True
        out = {}
        specs = (
            ("fcf", self.f_fcf, lambda t: validation.number(t, "Base free cash flow", allow_zero=False, allow_negative=True) * 1e6),
            ("growth", self.f_growth, lambda t: validation.number(t, "Growth", -50, 100, allow_negative=True) / 100),
            ("high", self.f_high, lambda t: validation.positive_int(t, "High-growth years", 1, 20)),
            ("fade", self.f_fade, lambda t: validation.positive_int(t, "Fade years", 1, 20)),
            ("disc", self.f_disc, lambda t: validation.number(t, "Discount rate", 1, 30, allow_zero=False) / 100),
            ("term", self.f_term, lambda t: validation.number(t, "Terminal growth", -3, 5, allow_negative=True) / 100),
            ("cash", self.f_cash, lambda t: validation.number(t, "Net cash", allow_negative=True) * 1e6),
            ("shares", self.f_shares, lambda t: validation.number(t, "Shares", allow_zero=False) * 1e6),
        )
        for key, field, fn in specs:
            try:
                out[key] = fn(field.text())
                field.clear_error()
            except validation.ValidationError as exc:
                field.set_error(str(exc))
                ok = False
        if not ok:
            self.banner.show_message("Some assumptions need fixing. The fields marked in red say what to change.", "error")
            return None
        return val.DCFInputs(out["fcf"], out["growth"], out["disc"], out["term"], out["cash"], out["shares"], out["high"], out["fade"])

    def _calculate(self) -> None:
        inp = self.read_inputs()
        if inp is None:
            return
        try:
            inp.validate()
        except validation.ValidationError as exc:
            self.banner.show_message(str(exc), "error")
            return
        self.banner.clear()
        self.inputs_changed.emit(inp)

    def render(self, a: Workspace) -> None:
        first = self.analysis is None or self.analysis.symbol != a.symbol
        self.analysis = a
        if not a.fundamentals or not a.history:
            self.banner.show_message(a.fundamentals_error or "Valuation needs SEC fundamentals. Load a company that files with the SEC.", "warn")
            self.mc_chart.message("No fundamentals loaded.")
            return
        if a.dcf_inputs is None:
            return
        if first or not self.f_growth.text():
            self._fill_fields(a.dcf_inputs)
        price = a.history.price
        fmt = price_formatter(a.history.currency)
        if a.dcf is None:
            self.banner.show_message(
                "Free cash flow is zero or negative, so a cash-flow DCF cannot value this company as it stands. "
                "Enter the free cash flow you think it can reach in Base free cash flow, then press Calculate.",
                "warn",
            )
            self.mc_chart.message("No DCF")
            return
        d = a.dcf
        up = d.per_share / price - 1
        self.cards.kpi("value", "").set(fmt(d.per_share, None), f"price {fmt(price, None)}", tone(up))
        self.cards.kpi("upside", "").set(f"{up:+.0%}", "undervalued on these assumptions" if up > 0 else "overvalued on these assumptions", tone(up))
        ig = a.implied_growth
        self.cards.kpi("implied", "").set(pct(ig) if ig is not None else "n/a", f"vs {pct(a.ratios.get('fcf_cagr_5y'))} FCF CAGR over 5y" if ig is not None else "outside -50% to 100%")
        ts = d.pv_terminal / d.enterprise_value
        self.cards.kpi("terminal", "").set(f"{ts:.0%}", "assumption-heavy" if ts > 0.75 else "", "warn" if ts > 0.75 else None)

        rows, cols, grid = val.sensitivity(a.dcf_inputs)
        self.sens.set_headers(["Discount \\ Terminal"] + [f"{c:.1%}" for c in cols])
        self.sens.fill(
            [[f"{r:.1%}"] + [fmt(v, None) if np.isfinite(v) else "n/a" for v in grid[i]] for i, r in enumerate(rows)],
            [[None] + [("up" if v > price else "down") if np.isfinite(v) else None for v in grid[i]] for i in range(len(rows))],
        )
        self.sens.fit_height()

        try:
            sims = val.monte_carlo_dcf(a.dcf_inputs)
        except validation.ValidationError:
            sims = np.array([])
        if len(sims):
            p_above = float((sims > price).mean())
            lo, hi = np.percentile(sims, [10, 90])
            self.cards.kpi("mc_prob", "").set(f"{p_above:.0%}", f"of {len(sims):,} valuations", "up" if p_above >= 0.5 else "down")
            self.cards.kpi("mc_band", "").set(f"{fmt(lo, None)} to {fmt(hi, None)}", "per share")
            fig = self.mc_chart.clear()
            ax = fig.add_subplot()
            clip = np.percentile(sims, [0.5, 99.5])
            data = sims[(sims >= clip[0]) & (sims <= clip[1])]
            ax.hist(data, bins=70, color=theme.ACCENT, alpha=0.8)
            ax.axvline(price, color=theme.WARN, linewidth=1.4, label="Price")
            ax.axvline(np.median(sims), color=theme.UP, linewidth=1.2, label="Median value")
            ax.xaxis.set_major_formatter(fmt)
            ax.set_yticks([])
            ax.legend(loc="upper right")
            self.mc_chart.draw()

        self.flows.fill([[f"Year {y}", f"{g:.1%}", money(f), money(pv)] for y, g, f, pv in d.flows])
        self.flows.fit_height()
        self.note.setText(
            f"Enterprise value {money(d.enterprise_value)} = explicit cash flows {money(d.pv_explicit)} + terminal value {money(d.pv_terminal)}; "
            f"plus net cash {money(a.dcf_inputs.net_cash)} gives equity value {money(d.equity_value)}. "
            "A DCF is only as good as its growth and discount assumptions; the sensitivity grid shows how much they matter."
        )


def recompute(a: Workspace, inp: val.DCFInputs) -> None:
    """Refresh the DCF pieces of an Analysis for new inputs."""
    a.dcf_inputs = inp
    try:
        a.dcf = val.dcf(inp)
    except validation.ValidationError:
        a.dcf = None
    a.implied_growth = val.reverse_dcf(replace(inp), a.history.price) if a.dcf else None
