"""Price chart: candles or line, moving averages, Bollinger Bands, volume, RSI, MACD."""

from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QHBoxLayout, QVBoxLayout, QWidget

from finlit_quant.analysis import Analysis
from finlit_quant.analytics import indicators as ind
from finlit_quant.ui import theme
from finlit_quant.ui.charts import Chart, compact_formatter, draw_candles, index_date_formatter, price_formatter
from finlit_quant.ui.widgets import chip, label

RANGES = [("1M", 31), ("3M", 92), ("6M", 183), ("YTD", None), ("1Y", 365), ("2Y", 730), ("5Y", 1826), ("10Y", 3653)]
# Past this many bars, candles turn into a smear of colour; a line reads better.
MAX_CANDLES = 520


class ChartTab(QWidget):
    def __init__(self, default_range: str = "1Y") -> None:
        super().__init__()
        self.analysis: Analysis | None = None
        self.range_key = default_range.upper() if default_range.upper() in dict(RANGES) else "1Y"
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        bar = QHBoxLayout()
        self.range_group = QButtonGroup(self)
        self.range_group.setExclusive(True)
        for key, _ in RANGES:
            b = chip(key)
            b.setChecked(key == self.range_key)
            b.clicked.connect(lambda _=False, k=key: self._set_range(k))
            self.range_group.addButton(b)
            bar.addWidget(b)
        bar.addSpacing(16)
        self.kind = QComboBox()
        self.kind.addItems(["Candles", "Line"])
        self.kind.currentIndexChanged.connect(self.redraw)
        bar.addWidget(self.kind)
        bar.addSpacing(12)
        self.toggles: dict[str, QCheckBox] = {}
        for key, on in (("SMA 20", True), ("SMA 50", True), ("SMA 200", True), ("Bollinger", False), ("Volume", True), ("RSI", True), ("MACD", False)):
            cb = QCheckBox(key)
            cb.setChecked(on)
            cb.toggled.connect(self.redraw)
            self.toggles[key] = cb
            bar.addWidget(cb)
        bar.addStretch(1)
        root.addLayout(bar)

        self.readout = label("Hover over the chart for that day's prices.", "Muted")
        root.addWidget(self.readout)
        self.chart = Chart(height=560, toolbar=True)
        root.addWidget(self.chart, 1)
        self.chart.canvas.mpl_connect("motion_notify_event", self._hover)
        self._axes: list = []
        self._vlines: list = []
        self._window: pd.DataFrame | None = None

    def _set_range(self, key: str) -> None:
        self.range_key = key
        self.redraw()

    def render(self, analysis: Analysis) -> None:
        self.analysis = analysis
        self.redraw()

    def _slice(self, bars: pd.DataFrame) -> pd.DataFrame:
        last = bars.index[-1]
        days = dict(RANGES)[self.range_key]
        start = pd.Timestamp(year=last.year, month=1, day=1) if days is None else last - pd.Timedelta(days=days)
        return bars[bars.index >= start]

    def redraw(self) -> None:
        a = self.analysis
        if not a or not a.history:
            self.chart.message("Load a ticker to see its chart.")
            return
        h = a.history
        full = h.bars.copy()
        close = full["close"]
        full["sma20"], full["sma50"], full["sma200"] = ind.sma(close, 20), ind.sma(close, 50), ind.sma(close, 200)
        bb = ind.bollinger(close)
        full["bb_up"], full["bb_lo"] = bb["upper"], bb["lower"]
        full["rsi"] = ind.rsi(close)
        m = ind.macd(close)
        full["macd"], full["macd_sig"], full["macd_hist"] = m["macd"], m["signal"], m["hist"]
        w = self._slice(full)
        if len(w) < 2:
            self.chart.message("Not enough history in this range. Pick a longer one.")
            return
        self._window = w

        panels = ["price"] + [k for k in ("Volume", "RSI", "MACD") if self.toggles[k].isChecked()]
        ratios = {"price": 4, "Volume": 1, "RSI": 1.2, "MACD": 1.2}
        fig = self.chart.clear()
        gs = fig.add_gridspec(len(panels), 1, height_ratios=[ratios[p] for p in panels], hspace=0.05)
        axes = []
        for i in range(len(panels)):
            axes.append(fig.add_subplot(gs[i], sharex=axes[0] if axes else None))
        x = range(len(w))
        ax = axes[0]
        candles = self.kind.currentText() == "Candles" and len(w) <= MAX_CANDLES
        if candles:
            draw_candles(ax, w)
        else:
            up = w["close"].iloc[-1] >= w["close"].iloc[0]
            color = theme.ACCENT if up else theme.RED
            ax.plot(x, w["close"], color=color, linewidth=1.6, label="Close")
            ax.fill_between(x, w["close"], w["close"].min(), color=color, alpha=0.08)
            ax.set_xlim(-1, len(w))
        for key, col, color in (("SMA 20", "sma20", theme.SKY), ("SMA 50", "sma50", theme.AMBER), ("SMA 200", "sma200", theme.PURPLE)):
            if self.toggles[key].isChecked() and w[col].notna().any():
                ax.plot(x, w[col], color=color, linewidth=1.1, label=key)
        if self.toggles["Bollinger"].isChecked():
            ax.plot(x, w["bb_up"], color=theme.MUTED, linewidth=0.8, linestyle="--", label="Bollinger")
            ax.plot(x, w["bb_lo"], color=theme.MUTED, linewidth=0.8, linestyle="--")
            ax.fill_between(x, w["bb_lo"], w["bb_up"], color=theme.SKY, alpha=0.05)
        ax.axhline(h.price, color=theme.MUTED, linewidth=0.7, linestyle=":")
        ax.yaxis.set_major_formatter(price_formatter(h.currency))
        ax.yaxis.tick_right()
        title = f"{h.symbol}  {h.name}"
        if not candles and self.kind.currentText() == "Candles":
            title += f"   line shown: {len(w)} bars is too many for candles"
        ax.set_title(title)
        ax.legend(loc="upper left", ncols=5)

        for axis, name in zip(axes[1:], panels[1:]):
            axis.yaxis.tick_right()
            if name == "Volume":
                colors = [theme.ACCENT if c >= o else theme.RED for o, c in zip(w["open"], w["close"])]
                axis.bar(x, w["volume"], color=colors, width=0.8, alpha=0.7)
                axis.yaxis.set_major_formatter(compact_formatter())
                axis.set_ylabel("Volume")
            elif name == "RSI":
                axis.plot(x, w["rsi"], color=theme.SKY, linewidth=1.1)
                axis.axhline(70, color=theme.RED, linewidth=0.7, linestyle="--")
                axis.axhline(30, color=theme.ACCENT, linewidth=0.7, linestyle="--")
                axis.set_ylim(0, 100)
                axis.set_yticks([30, 50, 70])
                axis.set_ylabel("RSI 14")
            elif name == "MACD":
                hist = w["macd_hist"]
                axis.bar(x, hist, color=[theme.ACCENT if v >= 0 else theme.RED for v in hist], width=0.8, alpha=0.6)
                axis.plot(x, w["macd"], color=theme.SKY, linewidth=1.0, label="MACD")
                axis.plot(x, w["macd_sig"], color=theme.AMBER, linewidth=1.0, label="Signal")
                axis.set_ylabel("MACD")
        for axis in axes[:-1]:
            axis.tick_params(labelbottom=False)
        axes[-1].xaxis.set_major_formatter(index_date_formatter(w.index))
        self._axes = axes
        self._vlines = [axis.axvline(0, color=theme.MUTED, linewidth=0.6, visible=False) for axis in axes]
        self.chart.draw()

    def _hover(self, event) -> None:
        w = self._window
        if w is None or event.inaxes not in self._axes or event.xdata is None:
            return
        i = int(round(event.xdata))
        if not 0 <= i < len(w):
            return
        row = w.iloc[i]
        prev = w["close"].iloc[i - 1] if i > 0 else row["open"]
        change = row["close"] / prev - 1 if prev else 0
        rsi = f"   RSI {row['rsi']:.0f}" if pd.notna(row.get("rsi")) else ""
        self.readout.setText(
            f"{w.index[i].strftime('%a %d %b %Y')}   O {row['open']:,.2f}   H {row['high']:,.2f}   L {row['low']:,.2f}   "
            f"C {row['close']:,.2f}   {change:+.2%}   Vol {row['volume']:,.0f}{rsi}"
        )
        for line in self._vlines:
            line.set_xdata([i, i])
            line.set_visible(True)
        self.chart.canvas.draw_idle()
