"""Price chart: candles or line, overlays, volume, RSI and MACD on linked axes."""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QCheckBox, QComboBox, QVBoxLayout, QWidget

from finlit_pro.analytics import indicators as ind
from finlit_pro.ui import theme
from finlit_pro.ui.pgcharts import CandlestickItem, Crosshair, epoch, legend, style_plot
from finlit_pro.ui.widgets import SourceLine, hrow, label
from finlit_pro.workspace import Workspace

MAX_CANDLES = 700  # beyond this, candles blur into a band and a line reads better


class ChartView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ws: Workspace | None = None
        self.start = self.end = None
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(4)

        self.kind = QComboBox()
        self.kind.addItems(["Candles", "Line"])
        self.log = QCheckBox("Log scale")
        self.toggles: dict[str, QCheckBox] = {}
        widgets = [label("Type", "Small"), self.kind, self.log, 12]
        for key, on in (("SMA 20", False), ("SMA 50", True), ("SMA 200", True), ("Bollinger 20,2", False), ("Volume", True), ("RSI 14", True), ("MACD 12,26,9", False)):
            cb = QCheckBox(key)
            cb.setChecked(on)
            cb.toggled.connect(self.redraw)
            self.toggles[key] = cb
            widgets.append(cb)
        self.kind.currentIndexChanged.connect(self.redraw)
        self.log.toggled.connect(self.redraw)
        root.addLayout(hrow(*widgets))
        self.readout = label("", "Small")
        root.addWidget(self.readout)
        self.view = pg.GraphicsLayoutWidget()
        root.addWidget(self.view, 1)
        self.source = SourceLine()
        root.addWidget(self.source)
        self._frame: pd.DataFrame | None = None
        self._x: np.ndarray | None = None
        self._crosshair = None

    def render(self, ws: Workspace, start=None, end=None) -> None:
        self.ws, self.start, self.end = ws, start, end
        self.redraw()

    def redraw(self) -> None:
        self.view.clear()
        ws = self.ws
        if not ws or not ws.history:
            return
        h = ws.history
        full = h.bars.copy()
        c = full["close"]
        full["sma20"], full["sma50"], full["sma200"] = ind.sma(c, 20), ind.sma(c, 50), ind.sma(c, 200)
        bb = ind.bollinger(c)
        full["bb_up"], full["bb_lo"] = bb["upper"], bb["lower"]
        full["rsi"] = ind.rsi(c)
        m = ind.macd(c)
        full["macd"], full["macd_sig"], full["macd_hist"] = m["macd"], m["signal"], m["hist"]
        w = full
        if self.start is not None:
            w = w[w.index >= self.start]
        if self.end is not None:
            w = w[w.index <= self.end]
        if len(w) < 2:
            self.readout.setText("No bars in the selected date range.")
            return
        self._frame = w
        x = epoch(w.index)
        self._x = x
        log = self.log.isChecked()

        def y(series):
            v = series.to_numpy(dtype=float)
            return np.log10(v) if log else v

        price = self.view.addPlot(row=0, col=0, axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
        style_plot(price, show_x=False, y_mode="log10" if log else "plain")
        lg = legend(price)
        candles = self.kind.currentText() == "Candles" and len(w) <= MAX_CANDLES
        if candles:
            price.addItem(CandlestickItem(x, y(w["open"]), y(w["high"]), y(w["low"]), y(w["close"]), width=86400.0))
        else:
            price.plot(x, y(w["close"]), pen=pg.mkPen(theme.ACCENT, width=1.4), name="Close")
        for key, col, color in (("SMA 20", "sma20", "#79c0ff"), ("SMA 50", "sma50", "#f0883e"), ("SMA 200", "sma200", "#a371f7")):
            if self.toggles[key].isChecked():
                price.plot(x, y(w[col]), pen=pg.mkPen(color, width=1.1), name=key, connect="finite")
        if self.toggles["Bollinger 20,2"].isChecked():
            up = price.plot(x, y(w["bb_up"]), pen=pg.mkPen(theme.MUTED, width=0.8), name="Bollinger", connect="finite")
            lo = price.plot(x, y(w["bb_lo"]), pen=pg.mkPen(theme.MUTED, width=0.8), connect="finite")
            price.addItem(pg.FillBetweenItem(up, lo, brush=pg.mkBrush(121, 192, 255, 18)), ignoreBounds=True)
        price.addItem(pg.InfiniteLine(pos=np.log10(h.price) if log else h.price, angle=0, pen=pg.mkPen(theme.MUTED, width=0.6, style=pg.QtCore.Qt.DotLine)))
        if candles:
            lg.addItem(pg.PlotDataItem(pen=pg.mkPen(theme.UP)), "OHLC")
        plots = [price]
        row = 1
        heights = [5]
        for key in ("Volume", "RSI 14", "MACD 12,26,9"):
            if not self.toggles[key].isChecked():
                continue
            p = self.view.addPlot(row=row, col=0, axisItems={"bottom": pg.DateAxisItem(utcOffset=0)})
            style_plot(p, show_x=False, y_mode="compact" if key == "Volume" else "plain")
            p.setXLink(price)
            if key == "Volume":
                ups = (w["close"] >= w["open"]).to_numpy()
                vols = w["volume"].to_numpy(dtype=float)
                p.addItem(pg.BarGraphItem(x=x[ups], height=vols[ups], width=86400 * 0.7, brush=theme.UP + "99", pen=None))
                p.addItem(pg.BarGraphItem(x=x[~ups], height=vols[~ups], width=86400 * 0.7, brush=theme.DOWN + "99", pen=None))
                p.setLabel("right", "Volume")
            elif key == "RSI 14":
                p.plot(x, w["rsi"].to_numpy(dtype=float), pen=pg.mkPen("#79c0ff", width=1.1), connect="finite")
                for level, color in ((70, theme.DOWN), (30, theme.UP)):
                    p.addItem(pg.InfiniteLine(pos=level, angle=0, pen=pg.mkPen(color, width=0.7, style=pg.QtCore.Qt.DashLine)))
                p.setYRange(0, 100)
                p.setLabel("right", "RSI")
            else:
                hist = w["macd_hist"].to_numpy(dtype=float)
                pos = hist >= 0
                p.addItem(pg.BarGraphItem(x=x[pos], height=hist[pos], width=86400 * 0.7, brush=theme.UP + "88", pen=None))
                p.addItem(pg.BarGraphItem(x=x[~pos], height=hist[~pos], width=86400 * 0.7, brush=theme.DOWN + "88", pen=None))
                p.plot(x, w["macd"].to_numpy(dtype=float), pen=pg.mkPen("#79c0ff", width=1))
                p.plot(x, w["macd_sig"].to_numpy(dtype=float), pen=pg.mkPen("#f0883e", width=1))
                p.setLabel("right", "MACD")
            plots.append(p)
            heights.append(1.4)
            row += 1
        plots[-1].getAxis("bottom").setStyle(showValues=True)
        for i, hgt in enumerate(heights):
            self.view.ci.layout.setRowStretchFactor(i, int(hgt * 10))
        price.setXRange(x[0], x[-1], padding=0.01)
        self._crosshair = Crosshair(plots, self._hover)
        self.source.set_sources([h.source])
        note = "" if candles or self.kind.currentText() == "Line" else f"   Line shown: {len(w):,} bars exceed the candle limit of {MAX_CANDLES}."
        self.readout.setText(f"{h.symbol}  {h.name}   {w.index[0].date()} to {w.index[-1].date()}   {len(w):,} sessions{note}")

    def _hover(self, xv: float) -> None:
        w, x = self._frame, self._x
        if w is None or x is None:
            return
        i = int(np.clip(np.searchsorted(x, xv), 0, len(x) - 1))
        row = w.iloc[i]
        prev = w["close"].iloc[i - 1] if i > 0 else row["open"]
        when = datetime.fromtimestamp(x[i], tz=timezone.utc).strftime("%a %d %b %Y")
        rsi = f"   RSI {row['rsi']:.1f}" if pd.notna(row.get("rsi")) else ""
        self.readout.setText(
            f"{when}   O {row['open']:,.2f}   H {row['high']:,.2f}   L {row['low']:,.2f}   C {row['close']:,.2f}   "
            f"{row['close'] / prev - 1:+.2%}   Vol {row['volume']:,.0f}{rsi}"
        )
