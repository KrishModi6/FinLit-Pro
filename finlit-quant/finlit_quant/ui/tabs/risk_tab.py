"""Risk: volatility, drawdowns, tail risk, and beta/alpha against a benchmark."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_quant import validation
from finlit_quant.ai.brief import num, pct
from finlit_quant.analysis import Analysis
from finlit_quant.ui import theme
from finlit_quant.ui.charts import Chart, date_axis, percent_formatter
from finlit_quant.ui.widgets import Banner, Field, Table, label, panel, scroll_page

WINDOWS = [("1 year", 1), ("3 years", 3), ("5 years", 5), ("10 years", 10)]

ROWS = [
    ("cagr", "CAGR", "pct"),
    ("total_return", "Total return", "pct"),
    ("volatility", "Volatility (annualised)", "pct"),
    ("sharpe", "Sharpe ratio", "num"),
    ("sortino", "Sortino ratio", "num"),
    ("max_drawdown", "Max drawdown", "neg"),
    ("longest_drawdown_days", "Longest time under water (days)", "int"),
    ("calmar", "Calmar ratio (CAGR / max DD)", "num"),
    ("var95_1d", "1-day VaR 95% (historical)", "neg"),
    ("cvar95_1d", "1-day CVaR 95% (expected shortfall)", "neg"),
    ("var99_1d", "1-day VaR 99% (historical)", "neg"),
    ("parametric_var95_1d", "1-day VaR 95% (normal)", "neg"),
    ("skew", "Skew of daily returns", "num"),
    ("excess_kurtosis", "Excess kurtosis (fat tails > 0)", "num"),
    ("best_day", "Best day", "pct"),
    ("worst_day", "Worst day", "pct"),
    ("positive_days", "Share of up days", "pct"),
    ("beta", "Beta", "num"),
    ("alpha", "Alpha (Jensen, annualised)", "pct"),
    ("correlation", "Correlation", "num"),
    ("r_squared", "R squared", "num"),
    ("tracking_error", "Tracking error", "pct"),
    ("information_ratio", "Information ratio", "num"),
    ("up_capture", "Up-market capture", "num"),
    ("down_capture", "Down-market capture", "num"),
]
BENCH_KEYS = {"cagr": "bench_cagr", "total_return": "bench_total_return", "volatility": "bench_volatility", "sharpe": "bench_sharpe", "max_drawdown": "bench_max_drawdown", "var95_1d": "bench_var95_1d", "worst_day": "bench_worst_day"}


class RiskTab(QWidget):
    settings_changed = Signal(float, str)  # years, benchmark

    def __init__(self, benchmark: str = "SPY") -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)

        bar = QHBoxLayout()
        self.window = QComboBox()
        for name, years in WINDOWS:
            self.window.addItem(name, years)
        self.window.setCurrentIndex(1)
        self.bench = Field("Benchmark", benchmark, tip="Any ticker: SPY for the S&P 500, QQQ for the Nasdaq 100, XLK for tech.", width=120)
        apply_btn = QPushButton("Recalculate")
        apply_btn.setObjectName("Primary")
        apply_btn.clicked.connect(self._apply)
        bar.addWidget(label("Window", "Muted"))
        bar.addWidget(self.window)
        bar.addSpacing(16)
        bar.addWidget(self.bench)
        bar.addWidget(apply_btn)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.banner = Banner()
        lay.addWidget(self.banner)
        self.rf_note = label("", "Muted", wrap=True)
        lay.addWidget(self.rf_note)

        row = QHBoxLayout()
        m_frame, m_lay = panel("Risk and performance")
        self.table = Table(["Metric", "Stock", "Benchmark"])
        m_lay.addWidget(self.table)
        g_frame, g_lay = panel("Growth of $1 and drawdowns")
        self.growth = Chart(height=520)
        g_lay.addWidget(self.growth)
        row.addWidget(m_frame, 2)
        row.addWidget(g_frame, 3)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        r_frame, r_lay = panel("Rolling 3-month volatility and 6-month beta")
        self.rolling = Chart(height=300)
        r_lay.addWidget(self.rolling)
        d_frame, d_lay = panel("Daily return distribution vs a normal curve", "Bars beyond the curve in the tails are the days a normal model says should almost never happen.")
        self.dist = Chart(height=300)
        d_lay.addWidget(self.dist)
        row2.addWidget(r_frame, 1)
        row2.addWidget(d_frame, 1)
        lay.addLayout(row2)
        lay.addStretch(1)

    def years(self) -> float:
        return float(self.window.currentData())

    def _apply(self) -> None:
        try:
            sym = validation.ticker(self.bench.text())
            self.bench.clear_error()
        except validation.ValidationError as exc:
            self.bench.set_error(str(exc))
            return
        self.settings_changed.emit(self.years(), sym)

    def show_error(self, message: str) -> None:
        self.banner.show_message(message, "warn")

    def render(self, a: Analysis) -> None:
        rk = a.risk
        if rk is None:
            self.growth.message("Load a ticker to see its risk profile.")
            return
        if rk.notes:
            self.banner.show_message(" ".join(rk.notes), "warn")
        else:
            self.banner.hide()
        self.rf_note.setText(
            f"Risk-free rate {a.risk_free:.2%} ({'live 13-week T-bill yield' if a.risk_free_live else 'from Settings; the live T-bill yield was unavailable'}). "
            f"Window: {rk.growth.index[0].date()} to {rk.growth.index[-1].date()}."
        )
        m = rk.metrics

        def fmt(v, kind):
            if v is None or not np.isfinite(v):
                return "n/a"
            return {"pct": pct(v), "neg": pct(-v), "num": num(v), "int": f"{v:,.0f}"}[kind]

        rows = []
        for key, name, kind in ROWS:
            if key not in m:
                continue
            bench = m.get(BENCH_KEYS[key]) if key in BENCH_KEYS else None
            rows.append([name, fmt(m[key], kind), fmt(bench, kind) if bench is not None else ""])
        self.table.fill(rows)
        self.table.fit_height(40)

        sym = a.history.symbol if a.history else ""
        fig = self.growth.clear()
        ax1, ax2 = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 2]})
        ax1.plot(rk.growth.index, rk.growth, color=theme.ACCENT, linewidth=1.4, label=sym)
        if rk.bench_growth is not None:
            ax1.plot(rk.bench_growth.index, rk.bench_growth, color=theme.MUTED, linewidth=1.2, label=rk.benchmark)
        ax1.axhline(1, color=theme.BORDER, linewidth=0.8)
        ax1.set_title("Growth of $1 (dividends reinvested)")
        ax1.legend(loc="upper left")
        ax2.fill_between(rk.drawdown.index, rk.drawdown, 0, color=theme.RED, alpha=0.35, linewidth=0)
        ax2.plot(rk.drawdown.index, rk.drawdown, color=theme.RED, linewidth=0.8)
        ax2.yaxis.set_major_formatter(percent_formatter())
        ax2.set_title("Drawdown from the running high")
        date_axis(ax2)
        self.growth.draw()

        fig = self.rolling.clear()
        ax = fig.add_subplot()
        ax.plot(rk.rolling_vol.index, rk.rolling_vol, color=theme.AMBER, linewidth=1.1, label="Volatility (left)")
        ax.yaxis.set_major_formatter(percent_formatter())
        date_axis(ax)
        if rk.rolling_beta is not None:
            ax_b = ax.twinx()
            ax_b.plot(rk.rolling_beta.index, rk.rolling_beta, color=theme.SKY, linewidth=1.1, label="Beta (right)")
            ax_b.axhline(1, color=theme.SKY, linewidth=0.6, linestyle=":")
            ax_b.grid(False)
            ax_b.spines["right"].set_visible(True)
            lines = ax.get_lines() + ax_b.get_lines()[:1]
            ax.legend(lines, [ln.get_label() for ln in lines], loc="upper left")
        else:
            ax.legend(loc="upper left")
        self.rolling.draw()

        fig = self.dist.clear()
        ax = fig.add_subplot()
        r = rk.returns.to_numpy()
        lo, hi = np.percentile(r, [0.2, 99.8])
        ax.hist(r, bins=90, range=(lo, hi), density=True, color=theme.SKY, alpha=0.75)
        mu, sd = r.mean(), r.std(ddof=1)
        xs = np.linspace(lo, hi, 300)
        ax.plot(xs, np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)), color=theme.AMBER, linewidth=1.4, label="Normal, same mean and vol")
        ax.axvline(-m["var95_1d"], color=theme.RED, linewidth=1, linestyle="--", label="VaR 95%")
        ax.xaxis.set_major_formatter(percent_formatter(1))
        ax.set_yticks([])
        ax.legend(loc="upper left")
        self.dist.draw()
