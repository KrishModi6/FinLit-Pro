"""Returns and risk over the selected date range, against a benchmark."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_pro import validation
from finlit_pro.fmt import num, pct
from finlit_pro.ui import theme
from finlit_pro.ui.pgcharts import epoch, legend, style_plot
from finlit_pro.ui.widgets import Field, Notice, SourceLine, Table, label, panel, scroll_page
from finlit_pro.workspace import Workspace

ROWS = [
    ("total_return", "Total return", "pct"),
    ("cagr", "CAGR", "pct"),
    ("volatility", "Volatility (annualised)", "pct"),
    ("sharpe", "Sharpe ratio", "num"),
    ("sortino", "Sortino ratio", "num"),
    ("max_drawdown", "Maximum drawdown", "neg"),
    ("longest_drawdown_days", "Longest time below a prior high (days)", "int"),
    ("calmar", "Calmar ratio", "num"),
    ("var95_1d", "1-day VaR 95% (historical)", "neg"),
    ("cvar95_1d", "1-day CVaR 95%", "neg"),
    ("var99_1d", "1-day VaR 99% (historical)", "neg"),
    ("skew", "Skew of daily returns", "num"),
    ("excess_kurtosis", "Excess kurtosis", "num"),
    ("best_day", "Best day", "pct"),
    ("worst_day", "Worst day", "pct"),
    ("positive_days", "Up days", "pct"),
    ("beta", "Beta", "num"),
    ("alpha", "Alpha (Jensen, annualised)", "pct"),
    ("correlation", "Correlation", "num"),
    ("tracking_error", "Tracking error", "pct"),
    ("information_ratio", "Information ratio", "num"),
    ("up_capture", "Up-market capture", "num"),
    ("down_capture", "Down-market capture", "num"),
]
BENCH = {"cagr": "bench_cagr", "total_return": "bench_total_return", "volatility": "bench_volatility", "sharpe": "bench_sharpe", "max_drawdown": "bench_max_drawdown", "var95_1d": "bench_var95_1d", "worst_day": "bench_worst_day"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class ReturnsView(QWidget):
    benchmark_changed = Signal(str)

    def __init__(self, benchmark: str = "SPY") -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        self.bench = Field("Benchmark", benchmark, tip="Any ticker: SPY (S&P 500), QQQ (Nasdaq 100), sector ETFs such as XLK.", width=110)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply)
        self.bench.edit.returnPressed.connect(self._apply)
        top = QHBoxLayout()
        top.addWidget(self.bench)
        top.addWidget(apply_btn)
        self.window_label = label("", "Small")
        top.addSpacing(12)
        top.addWidget(self.window_label, 1)
        lay.addLayout(top)
        self.notice = Notice()
        lay.addWidget(self.notice)

        row = QHBoxLayout()
        g_frame, g_lay = panel("Cumulative return and drawdown")
        self.growth = pg.GraphicsLayoutWidget()
        self.growth.setMinimumHeight(420)
        g_lay.addWidget(self.growth)
        m_frame, m_lay = panel("Statistics")
        self.metrics = Table(["Metric", "Stock", "Benchmark"])
        m_lay.addWidget(self.metrics)
        row.addWidget(g_frame, 3)
        row.addWidget(m_frame, 2)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        d_frame, d_lay = panel("Daily returns", "Histogram against a normal curve with the same mean and volatility. Bars beyond the curve are the tail days a normal model understates.")
        self.dist = pg.PlotWidget()
        self.dist.setMinimumHeight(260)
        d_lay.addWidget(self.dist)
        r_frame, r_lay = panel("Rolling 63-day volatility and 126-day beta")
        self.rolling = pg.GraphicsLayoutWidget()
        self.rolling.setMinimumHeight(260)
        r_lay.addWidget(self.rolling)
        row2.addWidget(d_frame, 1)
        row2.addWidget(r_frame, 1)
        lay.addLayout(row2)

        mo_frame, mo_lay = panel("Monthly returns", "Calendar-month total return; the last column is the calendar year.")
        self.monthly = Table(["Year"] + MONTHS + ["Year"])
        mo_lay.addWidget(self.monthly)
        lay.addWidget(mo_frame)
        self.source = SourceLine()
        lay.addWidget(self.source)
        lay.addStretch(1)

    def _apply(self) -> None:
        try:
            sym = validation.ticker(self.bench.text())
        except validation.ValidationError as exc:
            self.bench.set_error(str(exc))
            return
        self.bench.clear_error()
        self.benchmark_changed.emit(sym)

    def show_error(self, message: str) -> None:
        self.notice.show_message(message, "warn")

    def render(self, ws: Workspace) -> None:
        rk = ws.risk
        if rk is None or ws.history is None:
            return
        self.notice.show_message(" ".join(rk.notes), "warn") if rk.notes else self.notice.clear()
        rf_src = "live 13-week T-bill" if ws.risk_free_source else "Settings fallback"
        self.window_label.setText(f"{rk.growth.index[0].date()} to {rk.growth.index[-1].date()}  |  risk-free {ws.risk_free:.2%} ({rf_src})  |  change the range in the toolbar")
        m = rk.metrics

        def f(v, kind):
            if v is None or not np.isfinite(v):
                return "n/a"
            return {"pct": pct(v), "neg": pct(-v), "num": num(v), "int": f"{v:,.0f}"}[kind]

        rows, tones = [], []
        for key, name, kind in ROWS:
            if key not in m:
                continue
            b = m.get(BENCH[key]) if key in BENCH else None
            rows.append([name, f(m[key], kind), f(b, kind) if b is not None else ""])
            tones.append([None, ("up" if m[key] > 0 else "down") if kind == "pct" and key in ("total_return", "cagr", "alpha") and np.isfinite(m[key]) else None, None])
        self.metrics.fill(rows, tones)
        self.metrics.fit_height(40)

        # Cumulative return and drawdown
        self.growth.clear()
        x = epoch(rk.growth.index)
        p1 = self.growth.addPlot(row=0, col=0, axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        style_plot(p1, show_x=False)
        legend(p1)
        p1.plot(x, (rk.growth.to_numpy() - 1) * 100, pen=pg.mkPen(theme.ACCENT, width=1.4), name=ws.history.symbol)
        if rk.bench_growth is not None:
            p1.plot(epoch(rk.bench_growth.index), (rk.bench_growth.to_numpy() - 1) * 100, pen=pg.mkPen(theme.MUTED, width=1.1), name=rk.benchmark)
        p1.setLabel("right", "Return %")
        p2 = self.growth.addPlot(row=1, col=0, axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        style_plot(p2)
        p2.setXLink(p1)
        dd = rk.drawdown.to_numpy() * 100
        curve = p2.plot(epoch(rk.drawdown.index), dd, pen=pg.mkPen(theme.DOWN, width=1))
        p2.addItem(pg.FillBetweenItem(curve, p2.plot(epoch(rk.drawdown.index), np.zeros_like(dd), pen=None), brush=pg.mkBrush(229, 83, 75, 60)), ignoreBounds=True)
        p2.setLabel("right", "Drawdown %")
        self.growth.ci.layout.setRowStretchFactor(0, 3)
        self.growth.ci.layout.setRowStretchFactor(1, 2)

        # Distribution
        self.dist.clear()
        style_plot(self.dist.getPlotItem())
        r = rk.returns.to_numpy() * 100
        lo, hi = np.percentile(r, [0.2, 99.8])
        bins = int(np.clip(2 * np.sqrt(len(r)), 20, 80))  # about 30 for a year; 80 bins left gaps
        counts, edges = np.histogram(r, bins=bins, range=(lo, hi), density=True)
        self.dist.addItem(pg.BarGraphItem(x0=edges[:-1], x1=edges[1:], height=counts, brush=theme.ACCENT + "aa", pen=None))
        xs = np.linspace(lo, hi, 300)
        mu, sd = r.mean(), r.std(ddof=1)
        self.dist.plot(xs, np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)), pen=pg.mkPen(theme.WARN, width=1.3))
        self.dist.addItem(pg.InfiniteLine(pos=-m["var95_1d"] * 100, angle=90, pen=pg.mkPen(theme.DOWN, style=pg.QtCore.Qt.DashLine)))
        self.dist.getPlotItem().setLabel("bottom", "Daily return %")

        # Rolling
        self.rolling.clear()
        pv = self.rolling.addPlot(row=0, col=0, axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        style_plot(pv, show_x=False)
        rv = rk.rolling_vol.dropna()
        pv.plot(epoch(rv.index), rv.to_numpy() * 100, pen=pg.mkPen("#f0883e", width=1.1))
        pv.setLabel("right", "Vol %")
        pb = self.rolling.addPlot(row=1, col=0, axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        style_plot(pb)
        pb.setXLink(pv)
        if rk.rolling_beta is not None:
            rb = rk.rolling_beta.dropna()
            pb.plot(epoch(rb.index), rb.to_numpy(), pen=pg.mkPen("#79c0ff", width=1.1))
            pb.addItem(pg.InfiniteLine(pos=1, angle=0, pen=pg.mkPen(theme.MUTED, width=0.6, style=pg.QtCore.Qt.DotLine)))
        pb.setLabel("right", "Beta")

        # Monthly table
        closes = ws.history.closes[(ws.history.closes.index >= rk.growth.index[0]) & (ws.history.closes.index <= rk.growth.index[-1])]
        month_end = closes.resample("ME").last()
        monthly = month_end.pct_change()
        first_month = closes.iloc[: closes.index.searchsorted(month_end.index[0], side="right")]
        if len(first_month):
            monthly.iloc[0] = month_end.iloc[0] / first_month.iloc[0] - 1
        year_end = closes.resample("YE").last()
        yearly = year_end.pct_change()
        yearly.iloc[0] = year_end.iloc[0] / closes.iloc[0] - 1
        rows, tones = [], []
        for year in sorted(set(monthly.index.year), reverse=True):
            vals = [monthly.get(pd.Timestamp(year=year, month=mm, day=1) + pd.offsets.MonthEnd(0)) for mm in range(1, 13)]
            yv = yearly.get(pd.Timestamp(year=year, month=12, day=31))
            cells = [f"{v * 100:+.1f}" if v is not None and np.isfinite(v) else "" for v in vals] + [f"{yv * 100:+.1f}" if yv is not None and np.isfinite(yv) else ""]
            rows.append([str(year)] + cells)
            tones.append([None] + [("up" if v > 0 else "down") if v is not None and np.isfinite(v) else None for v in vals] + [("up" if yv > 0 else "down") if yv is not None and np.isfinite(yv) else None])
        self.monthly.fill(rows, tones)
        self.monthly.fit_height(15)
        self.source.set_sources([s for s in (ws.history.source, ws.benchmark.source if ws.benchmark else None, ws.risk_free_source) if s])
