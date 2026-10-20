"""Compare several tickers: relative performance, correlation, and an efficient frontier."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_quant import validation
from finlit_quant.analytics.portfolio import Comparison, Frontier
from finlit_quant.ui import theme
from finlit_quant.ui.charts import Chart, date_axis, percent_formatter
from finlit_quant.ui.widgets import Banner, Field, Table, label, panel, scroll_page

WINDOWS = [("1 year", 1), ("3 years", 3), ("5 years", 5), ("10 years", 10)]


class CompareTab(QWidget):
    run_requested = Signal(list, float)

    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        bar = QHBoxLayout()
        self.tickers = Field("Tickers (2 to 8, separated by commas)", "AAPL, MSFT, NVDA, SPY", width=360)
        self.window = QComboBox()
        for name, years in WINDOWS:
            self.window.addItem(name, years)
        self.window.setCurrentIndex(1)
        self.run_btn = QPushButton("Compare")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._submit)
        self.tickers.edit.returnPressed.connect(self._submit)
        bar.addWidget(self.tickers)
        bar.addWidget(label("Window", "Muted"))
        bar.addWidget(self.window)
        bar.addWidget(self.run_btn)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.banner = Banner()
        lay.addWidget(self.banner)

        g_frame, g_lay = panel("Relative performance (rebased to 100)")
        self.growth = Chart(height=340, toolbar=True)
        g_lay.addWidget(self.growth)
        lay.addWidget(g_frame)

        row = QHBoxLayout()
        s_frame, s_lay = panel("Statistics")
        self.stats = Table(["Ticker", "Total return", "CAGR", "Volatility", "Sharpe", "Max DD"])
        s_lay.addWidget(self.stats)
        c_frame, c_lay = panel("Correlation of daily returns", "Low correlation is what makes diversification work.")
        self.corr = Chart(height=300)
        c_lay.addWidget(self.corr)
        row.addWidget(s_frame, 1)
        row.addWidget(c_frame, 1)
        lay.addLayout(row)

        f_frame, f_lay = panel(
            "Efficient frontier (5,000 random long-only portfolios)",
            "Built on past returns, so the max-Sharpe mix is the best mix for the past. The minimum-volatility mix depends only on volatility and correlation and is the more stable of the two.",
        )
        row2 = QHBoxLayout()
        self.frontier = Chart(height=340)
        self.weights = Table(["Ticker", "Max Sharpe", "Min volatility"])
        row2.addWidget(self.frontier, 3)
        row2.addWidget(self.weights, 2)
        f_lay.addLayout(row2)
        lay.addWidget(f_frame)
        lay.addStretch(1)

    def _submit(self) -> None:
        try:
            syms = validation.ticker_list(self.tickers.text())
            self.tickers.clear_error()
        except validation.ValidationError as exc:
            self.tickers.set_error(str(exc))
            return
        self.banner.hide()
        self.run_requested.emit(syms, float(self.window.currentData()))

    def set_busy(self, busy: bool) -> None:
        self.run_btn.setEnabled(not busy)
        self.run_btn.setText("Loading..." if busy else "Compare")

    def show_error(self, message: str) -> None:
        self.banner.show_message(message, "error")

    def render(self, cmp: Comparison, fr: Frontier, skipped: list[str]) -> None:
        if skipped:
            self.banner.show_message("Left out because they could not be loaded: " + "; ".join(skipped), "warn")
        else:
            self.banner.hide()
        fig = self.growth.clear()
        ax = fig.add_subplot()
        for i, sym in enumerate(cmp.growth.columns):
            ax.plot(cmp.growth.index, cmp.growth[sym], linewidth=1.4, label=sym, color=theme.SERIES[i % len(theme.SERIES)])
        ax.axhline(100, color=theme.BORDER, linewidth=0.8)
        date_axis(ax)
        ax.legend(loc="upper left", ncols=8)
        self.growth.draw()

        rows, tones = [], []
        for sym, r in cmp.stats.iterrows():
            rows.append([sym, f"{r['Total return']:+.1%}", f"{r['CAGR']:+.1%}", f"{r['Volatility']:.1%}", f"{r['Sharpe']:.2f}", f"-{r['Max drawdown']:.1%}"])
            tones.append([None, "good" if r["Total return"] > 0 else "bad", None, None, None, "bad"])
        self.stats.fill(rows, tones)
        self.stats.fit_height()

        fig = self.corr.clear()
        ax = fig.add_subplot()
        c = cmp.correlation.to_numpy()
        im = ax.imshow(c, cmap="RdYlGn_r", vmin=-1, vmax=1)
        labels = list(cmp.correlation.columns)
        ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
        ax.set_yticks(range(len(labels)), labels)
        ax.grid(False)
        for i in range(len(labels)):
            for j in range(len(labels)):
                # Dark text on the pale middle of the colour map, light on its dark ends.
                shade = (c[i, j] + 1) / 2
                ax.text(j, i, f"{c[i, j]:.2f}", ha="center", va="center", fontsize=9, color="#0b1220" if 0.25 < shade < 0.75 else "white")
        fig.colorbar(im, ax=ax, shrink=0.8)
        self.corr.draw()

        fig = self.frontier.clear()
        ax = fig.add_subplot()
        sc = ax.scatter(fr.vols, fr.returns, c=fr.sharpes, cmap="viridis", s=6, alpha=0.7)
        ax.scatter(fr.vols[fr.max_sharpe], fr.returns[fr.max_sharpe], marker="*", s=220, color=theme.AMBER, label="Max Sharpe", zorder=3)
        ax.scatter(fr.vols[fr.min_vol], fr.returns[fr.min_vol], marker="D", s=80, color=theme.SKY, label="Min volatility", zorder=3)
        vols = cmp.returns.std().to_numpy() * np.sqrt(252)
        rets = cmp.returns.mean().to_numpy() * 252
        for sym, v, r in zip(cmp.returns.columns, vols, rets):
            ax.scatter(v, r, color=theme.TEXT, s=18, zorder=3)
            ax.annotate(sym, (v, r), xytext=(4, 4), textcoords="offset points", fontsize=9)
        ax.xaxis.set_major_formatter(percent_formatter())
        ax.yaxis.set_major_formatter(percent_formatter())
        ax.set_xlabel("Volatility")
        ax.set_ylabel("Return (historical mean)")
        fig.colorbar(sc, ax=ax, label="Sharpe", shrink=0.8)
        ax.legend(loc="lower right")
        self.frontier.draw()

        self.weights.fill([[sym, f"{fr.weights[fr.max_sharpe][i]:.0%}", f"{fr.weights[fr.min_vol][i]:.0%}"] for i, sym in enumerate(fr.symbols)])
        self.weights.fit_height()
