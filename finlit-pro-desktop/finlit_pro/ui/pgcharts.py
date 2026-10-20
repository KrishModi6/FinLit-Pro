"""Interactive time-series charts on pyqtgraph: pan, zoom, linked axes, crosshair."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPicture

from finlit_pro.ui import theme


def epoch(index: pd.DatetimeIndex) -> np.ndarray:
    """Dates as UTC epoch seconds, the x unit of pg.DateAxisItem."""
    return (index.values.astype("datetime64[s]").astype("int64")).astype(float)


class CandlestickItem(pg.GraphicsObject):
    """OHLC candles drawn once into a QPicture."""

    def __init__(self, x: np.ndarray, o, h, lo, c, width: float) -> None:
        super().__init__()
        self.picture = QPicture()
        p = QPainter(self.picture)
        up_pen, down_pen = pg.mkPen(theme.UP, width=1), pg.mkPen(theme.DOWN, width=1)
        up_brush, down_brush = pg.mkBrush(theme.UP), pg.mkBrush(theme.DOWN)
        w = width * 0.35
        for xi, oi, hi, li, ci in zip(x, o, h, lo, c):
            up = ci >= oi
            p.setPen(up_pen if up else down_pen)
            p.drawLine(QPointF(xi, li), QPointF(xi, hi))
            p.setBrush(up_brush if up else down_brush)
            p.drawRect(QRectF(xi - w, min(oi, ci), 2 * w, max(abs(ci - oi), 1e-9)))
        p.end()
        self._bounds = QRectF(float(x.min()) - width, float(np.min(lo)), float(x.max() - x.min()) + 2 * width, float(np.max(h) - np.min(lo)))

    def paint(self, painter, *args):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return self._bounds


class Crosshair:
    """Vertical line across every linked plot and a readout callback."""

    def __init__(self, plots: list[pg.PlotItem], on_move) -> None:
        self.plots = plots
        self.lines = []
        for p in plots:
            line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(theme.MUTED, width=0.8, style=Qt.DashLine))
            p.addItem(line, ignoreBounds=True)
            self.lines.append(line)
        self.on_move = on_move
        self.proxy = pg.SignalProxy(plots[0].scene().sigMouseMoved, rateLimit=60, slot=self._moved)

    def _moved(self, event) -> None:
        pos = event[0]
        for p in self.plots:
            if p.sceneBoundingRect().contains(pos):
                x = p.vb.mapSceneToView(pos).x()
                for line in self.lines:
                    line.setPos(x)
                self.on_move(x)
                return


def compact(v: float) -> str:
    """1234567 -> 1.23M. Used for volume and other large counts."""
    a = abs(v)
    for div, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= div:
            return f"{v / div:.3g}{suffix}"
    return f"{v:.4g}"


class ValueAxis(pg.AxisItem):
    """Right-hand value axis.

    mode "plain": pyqtgraph's own labels, without its automatic SI prefix
    (which printed "x0.001" style multipliers).
    mode "compact": 12.5M instead of 1.25e+07.
    mode "log10": the data is log10 of a price or growth figure; ticks are
    placed at round values of the underlying number and labelled with it.

    First Version: the price chart in log scale labelled its axis with the
    log values themselves (1.6, 1.7, ...) and the volume axis read "1e+07".
    Current Version: this axis converts back, so labels are always in the
    units the user reads.
    """

    def __init__(self, mode: str = "plain", **kwargs) -> None:
        super().__init__("right", **kwargs)
        self.mode = mode
        self.enableAutoSIPrefix(False)

    def tickValues(self, minVal, maxVal, size):  # noqa: N802, N803 - pyqtgraph API
        if self.mode != "log10" or not (np.isfinite(minVal) and np.isfinite(maxVal)):
            return super().tickValues(minVal, maxVal, size)
        lo, hi = 10.0 ** minVal, 10.0 ** maxVal
        if hi / lo > 8:
            vals = [m * 10.0**e for e in range(int(np.floor(minVal)), int(np.ceil(maxVal)) + 1) for m in (1, 2, 5)]
            return [(1.0, [np.log10(v) for v in vals if lo <= v <= hi])]
        return [(spacing, [np.log10(v) for v in vals if v > 0]) for spacing, vals in super().tickValues(lo, hi, size)]

    def tickStrings(self, values, scale, spacing):  # noqa: N802 - pyqtgraph API
        if self.mode == "log10":
            return [_plain(10.0**v) for v in values]
        if self.mode == "compact":
            return [compact(v) for v in values]
        return super().tickStrings(values, scale, spacing)


def _plain(v: float) -> str:
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:.4g}"


def style_plot(p: pg.PlotItem, show_x: bool = True, y_mode: str = "plain") -> None:
    p.setAxisItems({"right": ValueAxis(y_mode)})
    p.showGrid(x=True, y=True, alpha=0.12)
    p.getAxis("left").setWidth(0)
    p.hideAxis("left")
    p.showAxis("right")
    for name in ("right", "bottom"):
        ax = p.getAxis(name)
        ax.setPen(pg.mkPen(theme.BORDER))
        ax.setTextPen(pg.mkPen(theme.MUTED))
    if not show_x:
        p.getAxis("bottom").setStyle(showValues=False)
    p.setMenuEnabled(False)


def legend(p: pg.PlotItem) -> pg.LegendItem:
    lg = p.addLegend(offset=(8, 6), labelTextColor=theme.TEXT, labelTextSize="8pt")
    lg.setBrush(pg.mkBrush(theme.PANEL + "cc"))
    return lg
