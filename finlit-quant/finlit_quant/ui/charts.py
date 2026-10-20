"""Matplotlib embedded in Qt, plus the drawing helpers every tab shares."""

from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("QtAgg")

import matplotlib.dates as mdates  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget  # noqa: E402

from finlit_quant.ui import theme  # noqa: E402


class Chart(QWidget):
    """A figure, its canvas, and (optionally) the zoom/pan toolbar."""

    def __init__(self, height: int = 320, toolbar: bool = False) -> None:
        super().__init__()
        self.figure = Figure(figsize=(8, height / 100), dpi=100, layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(height)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        if toolbar:
            self.toolbar = NavigationToolbar2QT(self.canvas, self)
            self.toolbar.setStyleSheet(f"background: {theme.PANEL}; border: none;")
            lay.addWidget(self.toolbar)
        lay.addWidget(self.canvas)

    def clear(self) -> Figure:
        self.figure.clear()
        return self.figure

    def draw(self) -> None:
        self.canvas.draw_idle()

    def png_base64(self, dpi: int = 110) -> str:
        buf = io.BytesIO()
        self.figure.savefig(buf, format="png", dpi=dpi, facecolor=theme.PANEL)
        return base64.b64encode(buf.getvalue()).decode("ascii")

    def message(self, text: str) -> None:
        fig = self.clear()
        ax = fig.add_subplot()
        ax.axis("off")
        ax.text(0.5, 0.5, text, ha="center", va="center", color=theme.MUTED, fontsize=11, wrap=True, transform=ax.transAxes)
        self.draw()


def price_formatter(currency: str = "USD") -> FuncFormatter:
    symbol = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$"}.get(currency, "")
    # Yahoo quotes London listings in pence (GBp); show them as such rather
    # than mislabelling pence as pounds.
    suffix = "p" if currency == "GBp" else ""

    def fmt(v, _pos):
        if abs(v) >= 1000:
            return f"{symbol}{v:,.0f}{suffix}"
        if abs(v) >= 10:
            return f"{symbol}{v:,.0f}{suffix}" if v == int(v) else f"{symbol}{v:,.1f}{suffix}"
        return f"{symbol}{v:,.2f}{suffix}"

    return FuncFormatter(fmt)


def compact_formatter() -> FuncFormatter:
    def fmt(v, _pos):
        a = abs(v)
        for size, unit in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
            if a >= size:
                return f"{v / size:,.0f}{unit}" if a / size >= 10 else f"{v / size:,.1f}{unit}"
        return f"{v:,.0f}"

    return FuncFormatter(fmt)


def percent_formatter(dp: int = 0) -> FuncFormatter:
    return FuncFormatter(lambda v, _pos: f"{v * 100:.{dp}f}%")


def index_date_formatter(dates: pd.DatetimeIndex) -> FuncFormatter:
    """Label integer bar positions with dates, so weekends leave no gaps."""
    span_days = (dates[-1] - dates[0]).days if len(dates) > 1 else 0
    fmt = "%b %d" if span_days < 120 else ("%b %Y" if span_days < 1100 else "%Y")

    def f(x, _pos):
        i = int(round(x))
        if 0 <= i < len(dates):
            return dates[i].strftime(fmt)
        return ""

    return FuncFormatter(f)


def draw_candles(ax, bars: pd.DataFrame, width: float = 0.7) -> None:
    x = np.arange(len(bars))
    o, h, lo, c = (bars[k].to_numpy() for k in ("open", "high", "low", "close"))
    up = c >= o
    colors = np.where(up, theme.ACCENT, theme.RED)
    wicks = LineCollection([((xi, li), (xi, hi)) for xi, li, hi in zip(x, lo, h)], colors=colors, linewidths=0.8)
    ax.add_collection(wicks)
    body_bottom = np.minimum(o, c)
    body_height = np.maximum(np.abs(c - o), (h.max() - lo.min()) * 0.0015)
    ax.bar(x, body_height, width, bottom=body_bottom, color=colors, edgecolor=colors, linewidth=0.5)
    ax.set_xlim(-1, len(bars))
    pad = (h.max() - lo.min()) * 0.04
    ax.set_ylim(lo.min() - pad, h.max() + pad)


def date_axis(ax) -> None:
    """Few, compact date labels: "2024", "Apr", "Jul" instead of colliding ISO dates."""
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def style_legend(ax, loc: str = "upper left") -> None:
    leg = ax.legend(loc=loc, ncols=4, handlelength=1.4)
    if leg:
        for t in leg.get_texts():
            t.set_color(theme.TEXT)
