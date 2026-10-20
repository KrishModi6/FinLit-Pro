"""Prediction: the owner's model, its inputs, outputs, and out-of-sample evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QProgressBar, QPushButton, QVBoxLayout, QWidget

from finlit_pro import framing
from finlit_pro.fmt import num, pct
from finlit_pro.model import registry
from finlit_pro.model.evaluation import Evaluation
from finlit_pro.ui import theme
from finlit_pro.ui.pgcharts import epoch, legend, style_plot
from finlit_pro.ui.widgets import KpiStrip, Notice, SourceLine, Table, hrow, label, panel, scroll_page, tone
from finlit_pro.workspace import Workspace

VERDICT_TONE = {"STRONG BUY": "up", "BUY": "up", "HOLD": "warn", "SELL": "down", "STRONG SELL": "down"}


class PredictionView(QWidget):
    run_requested = Signal(str, int, int)  # model key, horizon, simulations
    evaluate_requested = Signal(str, int, int)  # model key, horizon, step
    cancel_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        self.model = QComboBox()
        for key, m in registry.MODELS.items():
            self.model.addItem(f"{m.name} v{m.version}" + (" (original)" if key == registry.DEFAULT else " (corrected)" if "1.1" in key else ""), key)
        self.horizon = QComboBox()
        self.sims = QComboBox()
        self.model.currentIndexChanged.connect(self._model_changed)
        self.run_btn = QPushButton("Run model")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(lambda: self.run_requested.emit(self.model.currentData(), int(self.horizon.currentData()), int(self.sims.currentData())))
        lay.addLayout(hrow(label("Model", "Small"), self.model, 8, label("Horizon", "Small"), self.horizon, label("Simulations", "Small"), self.sims, self.run_btn))
        self.description = label("", "Small", wrap=True)
        lay.addWidget(self.description)
        note = Notice()
        note.show_message(framing.MODEL_NOTE)
        lay.addWidget(note)
        self.notice = Notice()
        lay.addWidget(self.notice)

        self.kpis = KpiStrip(6)
        for key, cap, tip in (
            ("verdict", "Verdict", "The model's recommendation from its six-signal score."),
            ("target", "Composite target", "0.4 x Monte Carlo median + 0.3 x regression trend + 0.3 x EMA projection."),
            ("change", "Expected change", "Composite target versus the last adjusted close."),
            ("prob", "P(rise), simulated", "Share of the model's simulated paths that finish above today."),
            ("score", "Signal score", "Sum of six signals, each -2 to +2."),
            ("agree", "Model agreement", "How closely the three component targets agree."),
        ):
            self.kpis.kpi(key, cap, tip)
        lay.addWidget(self.kpis)

        row = QHBoxLayout()
        in_frame, in_lay = panel("Inputs")
        self.inputs = Table(["Input", "Value", "Notes"])
        in_lay.addWidget(self.inputs)
        comp_frame, comp_lay = panel("Outputs")
        self.components = Table(["Component", "Target", "Change", "Weight"])
        comp_lay.addWidget(self.components)
        self.quantiles = Table(["Percentile", "Price", "Change"])
        comp_lay.addWidget(self.quantiles)
        row.addWidget(in_frame, 1)
        row.addWidget(comp_frame, 1)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        sig_frame, sig_lay = panel("Signals")
        self.signals = Table(["Signal", "Reading", "Score"])
        sig_lay.addWidget(self.signals)
        self.diagnostics = Table(["Diagnostic", "Value"])
        sig_lay.addWidget(self.diagnostics)
        fan_frame, fan_lay = panel("Forecast range", "Last 120 sessions and the model's simulated 10-90 and 25-75 percentile bands to the horizon.")
        self.fan = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        self.fan.setMinimumHeight(330)
        fan_lay.addWidget(self.fan)
        row2.addWidget(sig_frame, 2)
        row2.addWidget(fan_frame, 3)
        lay.addLayout(row2)

        ev_frame, ev_lay = panel(
            "Out-of-sample evaluation",
            "Walk-forward: at each past origin the model sees only the history up to that date, forecasts the horizon, and is scored on what followed. "
            "Origins step by the horizon so outcomes do not overlap. Nothing is fitted to the evaluation period.",
        )
        self.step = QComboBox()
        self.step.addItem("Non-overlapping (step = horizon)", 0)
        self.step.addItem("Every 5 sessions (overlapping)", 5)
        self.eval_btn = QPushButton("Run evaluation")
        self.eval_btn.clicked.connect(lambda: self.evaluate_requested.emit(self.model.currentData(), int(self.horizon.currentData()), int(self.step.currentData())))
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.progress.hide()
        ev_lay.addLayout(hrow(label("Origins", "Small"), self.step, self.eval_btn, self.cancel_btn, self.progress))
        self.ev_notice = Notice()
        ev_lay.addWidget(self.ev_notice)
        ev_row = QHBoxLayout()
        self.ev_metrics = Table(["Metric", "Value", "Compare with", "Assessment"])
        ev_row.addWidget(self.ev_metrics, 3, Qt.AlignTop)
        right = QVBoxLayout()
        self.buckets = Table(["Verdict", "Forecasts", "Mean outcome", "Hit rate", "Mean forecast"])
        right.addWidget(self.buckets)
        self.equity = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        self.equity.setMinimumHeight(260)
        right.addWidget(self.equity)
        ev_row.addLayout(right, 2)
        ev_lay.addLayout(ev_row)
        self.ev_notes = label("", "Small", wrap=True)
        ev_lay.addWidget(self.ev_notes)
        lay.addWidget(ev_frame)
        self.source = SourceLine()
        lay.addWidget(self.source)
        lay.addStretch(1)
        self._model_changed()

    def _model_changed(self) -> None:
        m = registry.get(self.model.currentData())
        cur_h, cur_s = self.horizon.currentData(), self.sims.currentData()
        self.horizon.clear()
        for h in m.horizons:
            self.horizon.addItem(f"{h} trading days", h)
        self.sims.clear()
        for s in m.simulations:
            self.sims.addItem(f"{s:,}", s)
        self.horizon.setCurrentIndex(max(0, self.horizon.findData(cur_h if cur_h else 30)))
        self.sims.setCurrentIndex(max(0, self.sims.findData(cur_s if cur_s else 1000)))
        self.description.setText(m.description)

    def selection(self) -> tuple[str, int, int]:
        return self.model.currentData(), int(self.horizon.currentData()), int(self.sims.currentData())

    def set_busy(self, busy: bool) -> None:
        self.run_btn.setEnabled(not busy)

    def set_eval_busy(self, busy: bool) -> None:
        self.eval_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.progress.setVisible(busy)
        if busy:
            self.progress.setValue(0)

    def set_progress(self, done: int, total: int) -> None:
        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(done)

    def show_error(self, message: str) -> None:
        self.notice.show_message(message, "error")

    def show_eval_error(self, message: str) -> None:
        self.ev_notice.show_message(message, "error")

    def render(self, ws: Workspace) -> None:
        fc = ws.forecast
        if fc is None or ws.history is None:
            return
        self.notice.clear()
        p = fc.price
        self.kpis.kpi("verdict").set(fc.verdict, f"{fc.model} v{fc.version}", VERDICT_TONE.get(fc.verdict))
        self.kpis.kpi("target").set(num(fc.target), f"{fc.horizon_days} trading days")
        self.kpis.kpi("change").set(pct(fc.expected_return, 1, True), f"from {num(p)} on {fc.as_of.date()}", tone(fc.expected_return))
        self.kpis.kpi("prob").set(pct(fc.prob_up, 0), "of simulated paths")
        if fc.score is not None and fc.score_range:
            self.kpis.kpi("score").set(f"{fc.score:+d}", f"range {fc.score_range[0]} to {fc.score_range[1]}", tone(fc.score))
        else:
            self.kpis.kpi("score").set("n/a", "the model reports no score")
        self.kpis.kpi("agree").set(str(fc.diagnostics.get("Model agreement", "n/a")).title(), f"spread {num(fc.diagnostics.get('Model spread (% of price)'), 1)}% of price")

        self.inputs.fill([[i.name, i.value, i.description] for i in fc.inputs], align_right_from=99, stretch_col=2, tips=[[i.description] * 3 for i in fc.inputs])
        self.inputs.fit_height()
        comps = list(fc.components.items()) + [("Composite target", fc.target)]
        self.components.fill([[k, num(v), pct(v / p - 1, 1, True), pct(fc.weights.get(k), 0) if k in fc.weights else ""] for k, v in comps], [[None, None, tone(v / p - 1), None] for _, v in comps])
        self.components.fit_height()
        self.quantiles.fill([[f"P{q}", num(v), pct(v / p - 1, 1, True)] for q, v in fc.quantiles.items()], [[None, None, tone(v / p - 1)] for v in fc.quantiles.values()])
        self.quantiles.fit_height()
        self.signals.fill([[s.name, s.reading, f"{s.score:+d}"] for s in fc.signals], [[None, None, tone(s.score)] for s in fc.signals], align_right_from=2, stretch_col=1)
        self.signals.fit_height()
        diag = []
        for k, v in fc.diagnostics.items():
            if isinstance(v, str):
                diag.append([k, v])
            elif "Volatility" in k:
                diag.append([k, pct(v)])
            elif "%" in k:
                diag.append([k, f"{v:.1f}"])
            elif k == "Sessions used":
                diag.append([k, f"{v:,.0f}"])
            else:
                diag.append([k, num(v, 4 if abs(v) < 1 else 2)])
        self.diagnostics.fill(diag)
        self.diagnostics.fit_height()

        # Fan chart
        self.fan.clear()
        plot = self.fan.getPlotItem()
        style_plot(plot)
        legend(plot)
        hist = ws.history.bars["adjclose"].iloc[-120:]
        x_hist = epoch(hist.index)
        plot.plot(x_hist, hist.to_numpy(), pen=pg.mkPen(theme.TEXT, width=1.2), name="Adjusted close")
        future = pd.bdate_range(hist.index[-1] + pd.Timedelta(days=1), periods=fc.horizon_days)
        xf = np.concatenate([[x_hist[-1]], epoch(future)])

        def band(q):
            return np.concatenate([[p], fc.bands[q]])

        # A connected model may return only a point forecast; draw bands when it provides them.
        has_bands = all(q in fc.bands and len(fc.bands[q]) == fc.horizon_days for q in (10, 25, 50, 75, 90))
        for lo, hi, alpha in ((10, 90, 45), (25, 75, 80)) if has_bands else ():
            # First Version: invisible edges (pen=None) carry no data bounds and the fill
            # reported an empty rect at the origin, so auto-range stretched the x axis
            # back to 1970. Current Version: faint edges, and the fill ignores bounds.
            edge = pg.mkPen(59, 130, 246, alpha + 40, width=0.6)
            a = plot.plot(xf, band(lo), pen=edge)
            b = plot.plot(xf, band(hi), pen=edge)
            plot.addItem(pg.FillBetweenItem(a, b, brush=pg.mkBrush(59, 130, 246, alpha)), ignoreBounds=True)
        if has_bands:
            plot.plot(xf, band(50), pen=pg.mkPen(theme.ACCENT, width=1.5), name="Median")
        plot.addItem(pg.ScatterPlotItem([xf[-1]], [fc.target], symbol="d", size=9, brush=theme.WARN, pen=None))
        lg = plot.legend
        lg.addItem(pg.ScatterPlotItem(symbol="d", brush=theme.WARN, pen=None), "Target")
        self.source.set_sources([ws.history.source])

    def render_evaluation(self, ev: Evaluation) -> None:
        self.ev_notice.clear()
        self.ev_metrics.fill(
            [[m.name, m.display, m.benchmark, m.flag] for m in ev.metrics],
            [[None, None, None, "warn" if m.flag else None] for m in ev.metrics],
            align_right_from=1,
            stretch_col=2,
            tips=[[m.definition, m.definition, "", ""] for m in ev.metrics],
        )
        self.ev_metrics.fit_height(40)
        b = ev.buckets
        self.buckets.fill(
            [[v, f"{int(r.forecasts)}", pct(r.mean_return, 1, True), pct(r.hit_rate, 0), pct(r.mean_forecast, 1, True)] for v, r in b.iterrows()],
            [[VERDICT_TONE.get(v), None, tone(r.mean_return), None, None] for v, r in b.iterrows()],
        )
        self.buckets.fit_height()
        self.equity.clear()
        plot = self.equity.getPlotItem()
        style_plot(plot, y_mode="log10")
        legend(plot)
        x = epoch(ev.equity.index)
        colors = {"Long/flat": theme.ACCENT, "Long/short": "#a371f7", "Buy and hold": theme.MUTED}
        for col in ev.equity.columns:
            plot.plot(x, np.log10(ev.equity[col].clip(lower=1e-6).to_numpy()), pen=pg.mkPen(colors.get(col, theme.TEXT), width=1.3), name=col)
        plot.setLabel("right", "Growth of 1 (log scale)")
        self.ev_notes.setText(" ".join(ev.notes))
