"""Monte Carlo predictor: the FinLit Pro AI Predictor, rebuilt for the desktop."""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_quant import validation
from finlit_quant.analysis import Analysis
from finlit_quant.analytics.montecarlo import DRIFT_MODES, MODELS, PERCENTILES, MCConfig
from finlit_quant.ui import theme
from finlit_quant.ui.charts import Chart, index_date_formatter, price_formatter
from finlit_quant.ui.widgets import Banner, CardGrid, Field, Table, chip, label, panel, scroll_page, tone_for

HORIZONS = [("1M", 21), ("3M", 63), ("6M", 126), ("1Y", 252), ("2Y", 504)]


class PredictorTab(QWidget):
    run_requested = Signal(object)  # MCConfig

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        note = Banner()
        note.close_btn.hide()
        note.show_message(
            "Not a forecast. This runs thousands of random walks built from the stock's own volatility. "
            "The spread is the point, and the calibration panel shows how honest that spread has been on this stock before.",
            "info",
        )
        lay.addWidget(note)

        form_frame, form = panel("Simulation settings")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        self.horizon = Field("Horizon (trading days)", "252", tip="252 trading days is about one calendar year.")
        self.paths = Field("Paths", "10000", tip="More paths give smoother percentiles. 10,000 is plenty.")
        self.lookback = Field("Lookback (years)", "3", tip="How many years of history to estimate volatility and drift from.")
        self.custom = Field("Custom expected return (%/yr)", "8", tip="Only used when drift is set to Custom.")
        self.seed = Field("Seed (blank = random)", "42", tip="The same seed reproduces the same paths exactly.")
        self.model = QComboBox()
        for key, name in MODELS.items():
            self.model.addItem(name, key)
        self.drift = QComboBox()
        for key, name in DRIFT_MODES.items():
            self.drift.addItem(name, key)
        self.drift.currentIndexChanged.connect(lambda _: self.custom.setEnabled(self.drift.currentData() == "custom"))
        self.custom.setEnabled(False)
        model_box, drift_box = QWidget(), QWidget()
        for box, title, combo in ((model_box, "Shock model", self.model), (drift_box, "Drift", self.drift)):
            v = QVBoxLayout(box)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(3)
            v.addWidget(label(title, "Muted"))
            v.addWidget(combo)
            v.addStretch(1)
        for i, w in enumerate((self.horizon, self.paths, self.lookback, model_box, drift_box, self.custom, self.seed)):
            grid.addWidget(w, i // 4, i % 4)
        form.addLayout(grid)
        quick = QHBoxLayout()
        quick.addWidget(label("Quick horizon:", "Muted"))
        for name, days in HORIZONS:
            b = chip(name, checkable=False)
            b.clicked.connect(lambda _=False, d=days: self.horizon.set_text(str(d)))
            quick.addWidget(b)
        quick.addStretch(1)
        self.run_btn = QPushButton("Run simulation")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._submit)
        quick.addWidget(self.run_btn)
        form.addLayout(quick)
        lay.addWidget(form_frame)

        self.banner = Banner()
        lay.addWidget(self.banner)

        self.cards = CardGrid(4)
        for key, title, tip in (
            ("median", "Median outcome", "Half the simulated paths end above this, half below."),
            ("prob_up", "Paths above today", "Share of paths that finish above the current price."),
            ("band", "10th to 90th percentile", "Four in five paths finish inside this range."),
            ("var", "VaR 95 / CVaR 95", "Loss at the 5th percentile, and the average loss beyond it."),
            ("dd", "Typical drawdown on the way", "Average worst peak-to-trough fall inside each path."),
            ("tails", "Big moves", "Chance of finishing 20% up or more, or 20% down or worse."),
            ("inputs", "Volatility used", "Annualised, from the lookback window."),
            ("drift", "Expected return used", "Annualised arithmetic return implied by the drift setting."),
        ):
            self.cards.card(key, title, tip)
        lay.addWidget(self.cards)

        fan_frame, fan = panel("Projected spread", "Shaded bands are the 5-95, 10-90 and 25-75 percentiles; thin lines are individual paths.")
        self.fan = Chart(height=380, toolbar=True)
        fan.addWidget(self.fan)
        lay.addWidget(fan_frame)

        row = QHBoxLayout()
        hist_frame, hist = panel("Where the paths end")
        self.hist = Chart(height=280)
        hist.addWidget(self.hist)
        pct_frame, pct_lay = panel("Percentile table")
        self.pct_table = Table(["Percentile", "Price", "Change"])
        pct_lay.addWidget(self.pct_table)
        row.addWidget(hist_frame, 3)
        row.addWidget(pct_frame, 2)
        lay.addLayout(row)

        sig_frame, sig = panel(
            "Signal engine (from the original FinLit Pro AI Predictor)",
            "Six technical signals scored -2 to +2, and a composite target that blends the Monte Carlo median (40%), "
            "a 120-day regression trend (30%) and EMA momentum (30%). One weak input, never a thesis.",
        )
        self.verdict = label("", "H2")
        sig.addWidget(self.verdict)
        self.sig_table = Table(["Signal", "Reading", "Score"])
        sig.addWidget(self.sig_table)
        self.targets = Table(["Model", "Target", "Change"])
        sig.addWidget(self.targets)
        lay.addWidget(sig_frame)

        cal_frame, cal = panel(
            "Calibration: has this model been honest about this stock?",
            "Walk-forward test: at regular past dates the model is fitted on the data available then, and we check where the price really ended up.",
        )
        self.cal_text = label("", wrap=True)
        cal.addWidget(self.cal_text)
        cal_row = QHBoxLayout()
        self.cal_table = Table(["Band", "Promised", "Actually caught"])
        self.cal_chart = Chart(height=220)
        cal_row.addWidget(self.cal_table, 2)
        cal_row.addWidget(self.cal_chart, 3)
        cal.addLayout(cal_row)
        lay.addWidget(cal_frame)
        lay.addStretch(1)

    # ------------------------------------------------------------------
    def config(self) -> MCConfig | None:
        """Validate every field, mark the bad ones, and return a config or None."""
        ok = True
        values = {}
        checks = (
            ("horizon", self.horizon, lambda t: validation.positive_int(t, "Horizon", 1, 2520)),
            ("paths", self.paths, lambda t: validation.positive_int(t, "Paths", 100, 200_000)),
            ("lookback", self.lookback, lambda t: validation.number(t, "Lookback", 0.5, 10, allow_zero=False)),
        )
        for key, field, fn in checks:
            try:
                values[key] = fn(field.text())
                field.clear_error()
            except validation.ValidationError as exc:
                field.set_error(str(exc))
                ok = False
        values["custom"] = 0.08
        if self.drift.currentData() == "custom":
            try:
                values["custom"] = validation.number(self.custom.text(), "Expected return", -90, 200, allow_negative=True) / 100
                self.custom.clear_error()
            except validation.ValidationError as exc:
                self.custom.set_error(str(exc))
                ok = False
        seed_text = self.seed.text().strip()
        values["seed"] = None
        if seed_text:
            try:
                values["seed"] = validation.positive_int(seed_text, "Seed", 1, 2**31 - 1)
                self.seed.clear_error()
            except validation.ValidationError as exc:
                self.seed.set_error(str(exc))
                ok = False
        if not ok:
            self.banner.show_message("Some settings need fixing. The fields marked in red say what to change.", "error")
            return None
        cfg = MCConfig(
            horizon_days=values["horizon"],
            n_paths=values["paths"],
            model=self.model.currentData(),
            drift_mode=self.drift.currentData(),
            custom_return=values["custom"],
            lookback_days=int(round(values["lookback"] * 252)),
            seed=values["seed"],
        )
        try:
            cfg.validate()
        except validation.ValidationError as exc:
            self.banner.show_message(str(exc), "error")
            return None
        self.banner.hide()
        return cfg

    def _submit(self) -> None:
        cfg = self.config()
        if cfg:
            self.run_requested.emit(cfg)

    def set_busy(self, busy: bool) -> None:
        self.run_btn.setEnabled(not busy)
        self.run_btn.setText("Simulating..." if busy else "Run simulation")

    def show_error(self, message: str) -> None:
        self.banner.show_message(message, "error")

    # ------------------------------------------------------------------
    def render(self, a: Analysis) -> None:
        if not a.history:
            self.fan.message("Load a ticker to run the simulation.")
            return
        if not a.mc:
            self.fan.message("Press Run simulation.")
            return
        r, h, s = a.mc, a.history, a.mc.stats
        s0 = r.start_price
        cur = h.currency
        fmt = price_formatter(cur)

        def p(v):
            return fmt(v, None)

        self.cards.card("median", "").set(p(s["median"]), f"{s['median'] / s0 - 1:+.1%} after {r.config.horizon_days} days", tone_for(s["median"] / s0 - 1))
        self.cards.card("prob_up", "").set(f"{s['prob_up']:.0%}", "of paths finish above today", "good" if s["prob_up"] >= 0.5 else "warn")
        self.cards.card("band", "").set(f"{p(s['p10'])} to {p(s['p90'])}", f"{(s['p90'] - s['p10']) / s0:.0%} of today's price wide")
        self.cards.card("var", "").set(f"-{s['var95']:.0%} / -{s['cvar95']:.0%}", "1 in 20 paths lose at least the first figure", "bad")
        self.cards.card("dd", "").set(f"-{s['expected_max_dd']:.0%}", f"{s['prob_dd_20']:.0%} of paths fall 20%+ at some point", "warn")
        self.cards.card("tails", "").set(f"{s['prob_gain_20']:.0%} up / {s['prob_loss_20']:.0%} down", "chance of a 20%+ move either way")
        self.cards.card("inputs", "").set(f"{r.est.vol_annual:.0%}", f"tail df {r.est.t_df:.1f}, excess kurtosis {r.est.excess_kurtosis:.1f}", "warn" if r.est.vol_annual > 0.4 else "neutral")
        self.cards.card("drift", "").set(f"{r.est.drift_annual:+.1%}/yr", DRIFT_MODES[r.config.drift_mode], tone_for(r.est.drift_annual))

        # Fan chart: one year of history, then the projection.
        fig = self.fan.clear()
        ax = fig.add_subplot()
        hist_closes = h.bars["close"].iloc[-252:]
        n_hist = len(hist_closes)
        x_hist = np.arange(n_hist)
        x_proj = n_hist - 1 + r.days
        ax.plot(x_hist, hist_closes.to_numpy(), color=theme.TEXT, linewidth=1.3, label="History")
        for path in r.sample_paths[:40]:
            ax.plot(x_proj, path, color=theme.SKY, linewidth=0.5, alpha=0.18)
        for lo, hi, alpha in ((5, 95, 0.10), (10, 90, 0.14), (25, 75, 0.22)):
            ax.fill_between(x_proj, r.bands[lo], r.bands[hi], color=theme.ACCENT, alpha=alpha, linewidth=0, label=f"{lo}-{hi}%")
        ax.plot(x_proj, r.bands[50], color=theme.ACCENT, linewidth=1.8, label="Median")
        ax.axhline(s0, color=theme.MUTED, linewidth=0.7, linestyle=":")
        ax.axvline(n_hist - 1, color=theme.MUTED, linewidth=0.7)
        ax.yaxis.set_major_formatter(fmt)
        ax.yaxis.tick_right()
        dates = list(hist_closes.index)
        future = [dates[-1] + np.timedelta64(int(d * 365 / 252), "D") for d in range(1, r.config.horizon_days + 1)]
        ax.xaxis.set_major_formatter(index_date_formatter(pd.DatetimeIndex(dates + future)))
        ax.set_title(f"{h.symbol}: {r.config.n_paths:,} paths, {MODELS[r.config.model]}" + ("  (simulated data)" if a.is_demo else ""))
        ax.legend(loc="upper left", ncols=5)
        self.fan.draw()

        # Terminal distribution.
        fig = self.hist.clear()
        ax = fig.add_subplot()
        clip_hi = np.percentile(r.terminal, 99.5)
        data = r.terminal[r.terminal <= clip_hi]
        ax.hist(data[data < s0], bins=60, color=theme.RED, alpha=0.75, range=(data.min(), clip_hi))
        ax.hist(data[data >= s0], bins=60, color=theme.ACCENT, alpha=0.75, range=(data.min(), clip_hi))
        for q, style in ((5, ":"), (50, "-"), (95, ":")):
            ax.axvline(s[f"p{q}"], color=theme.TEXT, linewidth=0.9, linestyle=style)
        ax.axvline(s0, color=theme.AMBER, linewidth=1.2, label="Today")
        ax.xaxis.set_major_formatter(fmt)
        ax.set_yticks([])
        ax.legend(loc="upper right")
        ax.set_title("Final price of each path (top 0.5% trimmed for scale)")
        self.hist.draw()

        rows, tones = [], []
        for q in PERCENTILES:
            v = s[f"p{q}"]
            ch = v / s0 - 1
            name = {5: "5th (bad)", 50: "50th (median)", 95: "95th (good)"}.get(q, f"{q}th")
            rows.append([name, p(v), f"{ch:+.1%}"])
            tones.append([None, None, tone_for(ch)])
        self.pct_table.fill(rows, tones)
        self.pct_table.fit_height()

        if a.predictor:
            pr = a.predictor
            color = theme.ACCENT if pr.score >= 2 else (theme.RED if pr.score <= -2 else theme.AMBER)
            self.verdict.setText(f"{pr.verdict}   score {pr.score:+d} of +/-{pr.max_score}   model agreement: {pr.agreement} ({pr.model_spread_pct:.1f}% spread)")
            self.verdict.setStyleSheet(f"color: {color};")
            self.sig_table.fill([[sg.name, sg.reading, f"{sg.score:+d}"] for sg in pr.signals], [[None, None, tone_for(sg.score)] for sg in pr.signals], align_right_from=2, stretch_col=1)
            self.sig_table.fit_height()
            tr = [
                ("Monte Carlo median (40%)", pr.mc_median),
                (f"Regression trend, R² {pr.trend_r2:.2f} (30%)", pr.trend_target),
                ("EMA momentum (30%)", pr.ema_target),
                ("Composite target", pr.composite_target),
            ]
            self.targets.fill([[n, p(v), f"{v / s0 - 1:+.1%}"] for n, v in tr], [[None, None, tone_for(v / s0 - 1)] for _, v in tr])
            self.targets.fit_height()

        cal = a.calibration
        if cal is None:
            self.cal_text.setText("Not enough history to back-test this horizon. It needs the lookback plus the horizon plus about a year of origins.")
            self.cal_table.setRowCount(0)
            self.cal_chart.message("No calibration test")
        else:
            self.cal_text.setText(f"{cal.verdict}  ({cal.tests} overlapping tests at a {cal.horizon_days}-day horizon, normal model.)")
            rows, tones = [], []
            for band, (nominal, observed) in cal.coverage.items():
                rows.append([band, f"{nominal:.0%}", f"{observed:.0%}"])
                tones.append([None, None, "good" if abs(observed - nominal) <= 0.1 else "warn"])
            self.cal_table.fill(rows, tones)
            self.cal_table.fit_height()
            fig = self.cal_chart.clear()
            ax = fig.add_subplot()
            ax.hist(cal.pit, bins=10, range=(0, 1), color=theme.SKY, alpha=0.8)
            ax.axhline(len(cal.pit) / 10, color=theme.AMBER, linewidth=1, linestyle="--", label="Perfectly calibrated")
            ax.set_title("Where outcomes fell inside the forecast (0 = far below, 1 = far above)")
            ax.legend(loc="upper center")
            self.cal_chart.draw()
