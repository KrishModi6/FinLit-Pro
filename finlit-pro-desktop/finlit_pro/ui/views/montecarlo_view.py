"""Monte Carlo simulation with adjustable assumptions, distributions and calibration."""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_pro import framing, validation
from finlit_pro.analytics.montecarlo import DRIFT_MODES, MODELS, PERCENTILES, MCConfig
from finlit_pro.fmt import pct
from finlit_pro.ui import theme
from finlit_pro.ui.charts import Chart, index_date_formatter, price_formatter
from finlit_pro.ui.widgets import Field, KpiStrip, Notice, SourceLine, Table, hrow, label, panel, scroll_page, tone
from finlit_pro.workspace import Workspace

HORIZONS = [("1M", 21), ("3M", 63), ("6M", 126), ("1Y", 252), ("2Y", 504)]

ASSUMPTIONS = {
    "student_t": "Daily log returns are Student-t distributed with the stock's own volatility; the degrees of freedom are fitted to its excess kurtosis, so stocks with violent days get fatter tails.",
    "gbm": "Daily log returns are normally distributed (geometric Brownian motion). Normal tails make large daily moves far rarer than markets produce them.",
    "bootstrap": "Each path is assembled from blocks of 10 consecutive real daily returns from the lookback window, preserving actual fat tails and some volatility clustering, but only events that already happened.",
}
DRIFTS = {
    "historical": "Drift is the mean daily log return over the lookback. Past drift is the least reliable input: a strong run inflates every path.",
    "zero": "Drift is set so the expected price equals today's: the simulation shows dispersion only, with no directional view.",
    "custom": "Drift is set from your expected annual return, converted to a log drift once (the sigma squared over two term is applied here and nowhere else).",
}
COMMON = (
    "Volatility is constant for the whole horizon. Days are independent apart from what the bootstrap preserves. "
    "No earnings dates, dividends, gaps, halts or regime changes are modelled. Results depend on the seed only through sampling noise, "
    "which shrinks with more paths."
)


class MonteCarloView(QWidget):
    run_requested = Signal(object)  # MCConfig

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)
        note = Notice()
        note.show_message(framing.SIMULATION_NOTE, "warn")
        lay.addWidget(note)

        form_frame, form = panel("Assumptions")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        self.horizon = Field("Horizon (trading days)", "252", tip="252 trading days is about one calendar year.")
        self.paths = Field("Simulations", "10000", tip="Number of simulated price paths, 100 to 200,000.")
        self.lookback = Field("Lookback (years)", "3", tip="History used to estimate volatility and drift.")
        self.custom = Field("Expected return (% per year)", "8", tip="Used only when drift is Custom.")
        self.vol_override = Field("Volatility override (% per year)", "", placeholder="blank = estimated", tip="Leave blank to use the volatility estimated from the lookback.")
        self.seed = Field("Seed", "42", placeholder="blank = random", tip="The same seed reproduces the same paths.")
        self.model = QComboBox()
        for key, name in MODELS.items():
            self.model.addItem(name, key)
        self.drift = QComboBox()
        for key, name in DRIFT_MODES.items():
            self.drift.addItem(name, key)
        self.drift.currentIndexChanged.connect(lambda _: (self.custom.setEnabled(self.drift.currentData() == "custom"), self._explain()))
        self.model.currentIndexChanged.connect(lambda _: self._explain())
        self.custom.setEnabled(False)
        boxes = []
        for title, combo in (("Return distribution", self.model), ("Drift", self.drift)):
            box = QWidget()
            v = QVBoxLayout(box)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(2)
            v.addWidget(label(title, "Small"))
            v.addWidget(combo)
            v.addStretch(1)
            boxes.append(box)
        for i, w in enumerate((self.horizon, self.paths, self.lookback, boxes[0], boxes[1], self.custom, self.vol_override, self.seed)):
            grid.addWidget(w, i // 4, i % 4)
        form.addLayout(grid)
        quick = [label("Horizon", "Small")]
        for name, days in HORIZONS:
            b = QPushButton(name)
            b.setFixedWidth(42)
            b.clicked.connect(lambda _=False, d=days: self.horizon.set_text(str(d)))
            quick.append(b)
        self.run_btn = QPushButton("Run simulation")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._submit)
        quick += [12, self.run_btn]
        form.addLayout(hrow(*quick))
        lay.addWidget(form_frame)
        self.notice = Notice()
        lay.addWidget(self.notice)

        self.kpis = KpiStrip(4)
        for key, cap, tip in (
            ("median", "Median outcome", "Half the paths finish above this."),
            ("band", "10th to 90th percentile", "Four in five paths finish inside this range."),
            ("prob_up", "Paths above today", ""),
            ("var", "VaR 95 / CVaR 95", "Loss at the 5th percentile, and the average loss beyond it, over the horizon."),
            ("dd", "Mean path drawdown", "Average worst peak-to-trough fall inside each path."),
            ("tails", "P(+20%) / P(-20%)", ""),
            ("vol", "Volatility used", ""),
            ("drift", "Expected return used", ""),
        ):
            self.kpis.kpi(key, cap, tip)
        lay.addWidget(self.kpis)

        fan_frame, fan = panel("Outcome range over the horizon", "Bands: 5-95, 10-90 and 25-75 percentiles. Thin lines: 40 individual paths.")
        self.fan = Chart(height=360, toolbar=True)
        fan.addWidget(self.fan)
        lay.addWidget(fan_frame)

        row = QHBoxLayout()
        hist_frame, hist = panel("Distribution at the horizon")
        self.hist = Chart(height=270)
        hist.addWidget(self.hist)
        pct_frame, pct_lay = panel("Percentiles")
        self.pct_table = Table(["Percentile", "Price", "Change"])
        pct_lay.addWidget(self.pct_table)
        row.addWidget(hist_frame, 3)
        row.addWidget(pct_frame, 2)
        lay.addLayout(row)

        ex_frame, ex_lay = panel("Assumptions and uncertainty")
        self.explain = label("", wrap=True)
        ex_lay.addWidget(self.explain)
        lay.addWidget(ex_frame)

        cal_frame, cal = panel("Calibration on this stock's history", "Walk-forward test of the normal model: at past dates, fit on the data available then and check where the price ended up.")
        self.cal_text = label("", wrap=True)
        cal.addWidget(self.cal_text)
        cal_row = QHBoxLayout()
        self.cal_table = Table(["Band", "Nominal", "Observed"])
        self.cal_chart = Chart(height=200)
        cal_row.addWidget(self.cal_table, 2)
        cal_row.addWidget(self.cal_chart, 3)
        cal.addLayout(cal_row)
        lay.addWidget(cal_frame)
        self.source = SourceLine()
        lay.addWidget(self.source)
        lay.addStretch(1)
        self._explain()

    def _explain(self) -> None:
        self.explain.setText(f"{ASSUMPTIONS[self.model.currentData()]}\n\n{DRIFTS[self.drift.currentData()]}\n\n{COMMON}")

    def config(self) -> MCConfig | None:
        ok, vals = True, {}
        for key, field, fn in (
            ("horizon", self.horizon, lambda t: validation.positive_int(t, "Horizon", 1, 2520)),
            ("paths", self.paths, lambda t: validation.positive_int(t, "Simulations", 100, 200_000)),
            ("lookback", self.lookback, lambda t: validation.number(t, "Lookback", 0.5, 30, allow_zero=False)),
        ):
            try:
                vals[key] = fn(field.text())
                field.clear_error()
            except validation.ValidationError as exc:
                field.set_error(str(exc))
                ok = False
        vals["custom"] = 0.08
        if self.drift.currentData() == "custom":
            try:
                vals["custom"] = validation.number(self.custom.text(), "Expected return", -90, 200, allow_negative=True) / 100
                self.custom.clear_error()
            except validation.ValidationError as exc:
                self.custom.set_error(str(exc))
                ok = False
        vals["vol"] = None
        if self.vol_override.text().strip():
            try:
                vals["vol"] = validation.number(self.vol_override.text(), "Volatility", 1, 300, allow_zero=False) / 100
                self.vol_override.clear_error()
            except validation.ValidationError as exc:
                self.vol_override.set_error(str(exc))
                ok = False
        vals["seed"] = None
        if self.seed.text().strip():
            try:
                vals["seed"] = validation.positive_int(self.seed.text(), "Seed", 1, 2**31 - 1)
                self.seed.clear_error()
            except validation.ValidationError as exc:
                self.seed.set_error(str(exc))
                ok = False
        if not ok:
            self.notice.show_message("Correct the highlighted fields.", "error")
            return None
        cfg = MCConfig(vals["horizon"], vals["paths"], self.model.currentData(), self.drift.currentData(), vals["custom"], int(round(vals["lookback"] * 252)), vals["seed"], vol_override=vals["vol"])
        try:
            cfg.validate()
        except validation.ValidationError as exc:
            self.notice.show_message(str(exc), "error")
            return None
        self.notice.clear()
        return cfg

    def _submit(self) -> None:
        cfg = self.config()
        if cfg:
            self.run_requested.emit(cfg)

    def set_busy(self, busy: bool) -> None:
        self.run_btn.setEnabled(not busy)
        self.run_btn.setText("Running" if busy else "Run simulation")

    def show_error(self, message: str) -> None:
        self.notice.show_message(message, "error")

    def render(self, ws: Workspace) -> None:
        if not ws.history or not ws.mc:
            return
        r, h, s = ws.mc, ws.history, ws.mc.stats
        s0 = r.start_price
        fmt = price_formatter(h.currency)

        def p(v):
            return fmt(v, None)

        k = self.kpis.kpi
        k("median").set(p(s["median"]), f"{s['median'] / s0 - 1:+.1%} after {r.config.horizon_days} days", tone(s["median"] / s0 - 1))
        k("band").set(f"{p(s['p10'])} - {p(s['p90'])}", f"{(s['p90'] - s['p10']) / s0:.0%} of today's price")
        k("prob_up").set(f"{s['prob_up']:.0%}")
        k("var").set(f"-{s['var95']:.0%} / -{s['cvar95']:.0%}", "", "down")
        k("dd").set(f"-{s['expected_max_dd']:.0%}", f"{s['prob_dd_20']:.0%} of paths fall 20% at some point", "warn")
        k("tails").set(f"{s['prob_gain_20']:.0%} / {s['prob_loss_20']:.0%}")
        k("vol").set(pct(r.est.vol_annual, 1), "override" if r.config.vol_override else f"t df {r.est.t_df:.1f}, kurtosis {r.est.excess_kurtosis:.1f}")
        k("drift").set(f"{r.est.drift_annual:+.1%}", DRIFT_MODES[r.config.drift_mode], tone(r.est.drift_annual))

        fig = self.fan.clear()
        ax = fig.add_subplot()
        hist_closes = h.bars["adjclose"].iloc[-252:]
        n = len(hist_closes)
        x_proj = n - 1 + r.days
        ax.plot(np.arange(n), hist_closes.to_numpy(), color=theme.TEXT, linewidth=1.1, label="Adjusted close")
        for path in r.sample_paths[:40]:
            ax.plot(x_proj, path, color=theme.ACCENT, linewidth=0.4, alpha=0.18)
        for lo, hi, alpha in ((5, 95, 0.12), (10, 90, 0.16), (25, 75, 0.24)):
            ax.fill_between(x_proj, r.bands[lo], r.bands[hi], color=theme.ACCENT, alpha=alpha, linewidth=0, label=f"P{lo}-P{hi}")
        ax.plot(x_proj, r.bands[50], color=theme.ACCENT, linewidth=1.6, label="Median")
        ax.axhline(s0, color=theme.MUTED, linewidth=0.6, linestyle=":")
        ax.axvline(n - 1, color=theme.MUTED, linewidth=0.6)
        ax.yaxis.set_major_formatter(fmt)
        ax.yaxis.tick_right()
        dates = list(hist_closes.index) + list(pd.bdate_range(hist_closes.index[-1] + pd.Timedelta(days=1), periods=r.config.horizon_days))
        ax.xaxis.set_major_formatter(index_date_formatter(pd.DatetimeIndex(dates)))
        ax.set_title(f"{h.symbol}: {r.config.n_paths:,} paths, {MODELS[r.config.model]}, {DRIFT_MODES[r.config.drift_mode].lower()}")
        ax.legend(loc="upper left", ncols=5)
        self.fan.draw()

        fig = self.hist.clear()
        ax = fig.add_subplot()
        clip_hi = np.percentile(r.terminal, 99.5)
        data = r.terminal[r.terminal <= clip_hi]
        ax.hist(data[data < s0], bins=60, color=theme.DOWN, alpha=0.8, range=(data.min(), clip_hi))
        ax.hist(data[data >= s0], bins=60, color=theme.UP, alpha=0.8, range=(data.min(), clip_hi))
        for q, style in ((5, ":"), (50, "-"), (95, ":")):
            ax.axvline(s[f"p{q}"], color=theme.TEXT, linewidth=0.8, linestyle=style)
        ax.axvline(s0, color=theme.WARN, linewidth=1.1, label="Today")
        ax.xaxis.set_major_formatter(fmt)
        ax.set_yticks([])
        ax.legend(loc="upper right")
        ax.set_title("Terminal price (top 0.5% trimmed for scale); lines at P5, P50, P95")
        self.hist.draw()

        rows, tones = [], []
        for q in PERCENTILES:
            v = s[f"p{q}"]
            rows.append([f"P{q}", p(v), f"{v / s0 - 1:+.1%}"])
            tones.append([None, None, tone(v / s0 - 1)])
        rows.append(["Mean", p(s["mean"]), f"{s['mean'] / s0 - 1:+.1%}"])
        tones.append([None, None, tone(s["mean"] / s0 - 1)])
        self.pct_table.fill(rows, tones)
        self.pct_table.fit_height()

        cal = ws.calibration
        if cal is None:
            self.cal_text.setText("Not enough history to test this horizon: the test needs the lookback plus the horizon plus about a year of origins.")
            self.cal_table.setRowCount(0)
            self.cal_chart.message("No calibration test at this horizon")
        else:
            self.cal_text.setText(f"{cal.verdict} ({cal.tests} overlapping tests at a {cal.horizon_days}-day horizon.)")
            self.cal_table.fill([[b, f"{n:.0%}", f"{o:.0%}"] for b, (n, o) in cal.coverage.items()], [[None, None, "muted" if abs(o - n) <= 0.1 else "warn"] for n, o in cal.coverage.values()])
            self.cal_table.fit_height()
            fig = self.cal_chart.clear()
            ax = fig.add_subplot()
            ax.hist(cal.pit, bins=10, range=(0, 1), color=theme.ACCENT, alpha=0.85)
            ax.axhline(len(cal.pit) / 10, color=theme.WARN, linewidth=1, linestyle="--", label="Calibrated")
            ax.set_title("Where outcomes fell in the forecast distribution (0 = far below, 1 = far above)")
            ax.legend(loc="upper center")
            self.cal_chart.draw()
        self.source.set_sources([h.source])
