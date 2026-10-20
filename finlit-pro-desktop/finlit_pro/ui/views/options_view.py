"""Options: chain lookup and a single-leg calculator with probabilities and a worth-it verdict."""

from __future__ import annotations

import math
from datetime import date

import numpy as np
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from finlit_pro import framing, validation
from finlit_pro.analytics import montecarlo, options
from finlit_pro.data.models import OptionChain, OptionQuote
from finlit_pro.fmt import dollars, num, pct
from finlit_pro.ui import theme
from finlit_pro.ui.charts import Chart, price_formatter
from finlit_pro.ui.widgets import Field, Notice, SourceLine, Table, hrow, label, panel, scroll_page
from finlit_pro.workspace import Workspace

VERDICT_TONE = {"Worth it": theme.UP, "Not worth it": theme.DOWN, "Marginal": theme.WARN}


def historical_vol(closes, days: int) -> float:
    r = np.diff(np.log(closes.to_numpy(dtype=float)[-(days + 1):]))
    return float(r.std(ddof=1) * math.sqrt(252)) if len(r) > 5 else float("nan")


class OptionsView(QWidget):
    chain_requested = Signal(str)  # expiry, "" for nearest

    def __init__(self) -> None:
        super().__init__()
        self.ws: Workspace | None = None
        self.chain: OptionChain | None = None
        self._quotes: list[OptionQuote] = []
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        area, lay = scroll_page()
        outer.addWidget(area)
        note = Notice()
        note.show_message(framing.OPTIONS_NOTE)
        lay.addWidget(note)

        top = QHBoxLayout()
        ch_frame, ch = panel("Option chain")
        self.expiry_box = QComboBox()
        self.expiry_box.setMinimumWidth(120)
        self.side_box = QComboBox()
        self.side_box.addItems(["Calls", "Puts"])
        self.side_box.currentIndexChanged.connect(lambda _: self._fill_chain())
        load = QPushButton("Load chain")
        load.clicked.connect(lambda: self.chain_requested.emit(self.expiry_box.currentText() if self.expiry_box.count() else ""))
        self.expiry_box.activated.connect(lambda _: self.chain_requested.emit(self.expiry_box.currentText()))
        ch.addLayout(hrow(label("Expiry", "Small"), self.expiry_box, self.side_box, load))
        self.chain_notice = Notice()
        ch.addWidget(self.chain_notice)
        self.table = Table(["Strike", "Bid", "Ask", "Mid", "Last", "IV (Yahoo)", "Volume", "Open int."])
        self.table.setMinimumHeight(380)
        self.table.cellClicked.connect(self._pick)
        ch.addWidget(self.table)
        self.chain_source = SourceLine()
        ch.addWidget(self.chain_source)
        top.addWidget(ch_frame, 5)

        calc_frame, calc = panel("Contract and assumptions", "Select a row in the chain or enter a contract. Premium is per share; one contract is 100 shares.")
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        self.kind = QComboBox()
        self.kind.addItems(["Call", "Put"])
        self.position = QComboBox()
        self.position.addItems(["Buy (long)", "Sell (short)"])
        self.strike = Field("Strike")
        self.premium = Field("Premium per share", tip="Use the mid of bid and ask when there is no recent trade.")
        self.expiry = QDateEdit(QDate.currentDate().addDays(30))
        self.expiry.setCalendarPopup(True)
        self.expiry.setDisplayFormat("yyyy-MM-dd")
        self.contracts = Field("Contracts", "1")
        self.vol_source = QComboBox()
        self.vol_source.addItems(["Historical, 1 year", "Historical, 3 months", "Implied (market)", "Custom"])
        self.vol = Field("Volatility (% per year)")
        self.ret_source = QComboBox()
        self.ret_source.addItems(["Risk-free rate (no view)", "Custom"])
        self.ret = Field("Expected return (% per year)")
        self.rate = Field("Risk-free rate (%)")
        self.div = Field("Dividend yield (%)")
        self.sim = QCheckBox("Also simulate fat tails (Student-t Monte Carlo)")
        self.sim.setChecked(True)
        self.vol_source.currentIndexChanged.connect(lambda _: self._vol_default())
        self.ret_source.currentIndexChanged.connect(lambda _: self._ret_default())

        def boxed(title, w):
            box = QWidget()
            v = QVBoxLayout(box)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(2)
            v.addWidget(label(title, "Small"))
            v.addWidget(w)
            v.addStretch(1)
            return box

        cells = [boxed("Type", self.kind), boxed("Position", self.position), self.strike, self.premium, boxed("Expiry", self.expiry), self.contracts,
                 boxed("Volatility source", self.vol_source), self.vol, boxed("Expected return", self.ret_source), self.ret, self.rate, self.div]
        for i, w in enumerate(cells):
            grid.addWidget(w, i // 2, i % 2)
        calc.addLayout(grid)
        calc.addWidget(self.sim)
        self.analyze_btn = QPushButton("Analyze contract")
        self.analyze_btn.setObjectName("Primary")
        self.analyze_btn.clicked.connect(self.analyze)
        calc.addLayout(hrow(self.analyze_btn))
        self.calc_notice = Notice()
        calc.addWidget(self.calc_notice)
        top.addWidget(calc_frame, 4)
        lay.addLayout(top)

        res_frame, res = panel("Result")
        self.verdict = label("", "Verdict")
        self.reason = label("", wrap=True)
        res.addWidget(self.verdict)
        res.addWidget(self.reason)
        res_row = QHBoxLayout()
        self.scenarios = Table(["Scenario", "Volatility", "Drift", "P(profit)", "P(ITM)", "EV / share", "EV / position", "Fair value"])
        self.scenarios.setToolTip("EV: expected profit or loss at expiry after the premium. Fair value: the premium at which EV would be zero under that scenario.")
        res_row.addWidget(self.scenarios, 3, Qt.AlignTop)
        side = QVBoxLayout()
        self.terms = Table(["Measure", "Value"])
        side.addWidget(self.terms)
        res_row.addLayout(side, 2)
        res.addLayout(res_row)
        self.greeks = Table(["Greek (position)", "Delta", "Gamma", "Theta / day", "Vega / 1 vol pt", "Rho / 1 pt"])
        res.addWidget(self.greeks)
        self.notes = label("", "Small", wrap=True)
        res.addWidget(self.notes)
        self.payoff = Chart(height=300)
        res.addWidget(self.payoff)
        lay.addWidget(res_frame)
        self.res_frame = res_frame
        res_frame.hide()  # shown once a contract has been analyzed
        lay.addStretch(1)

    # ------------------------------------------------------------------ data
    def render(self, ws: Workspace) -> None:
        first = self.ws is None or self.ws.symbol != ws.symbol
        self.ws = ws
        if first:
            self.chain = None
            self.table.setRowCount(0)
            self.expiry_box.clear()
            self.chain_notice.clear()
            self.chain_source.setText("")
            self.verdict.setText("")
            self.reason.setText("")
            self.res_frame.hide()
        if ws.history is None:
            return
        self.rate.set_text(f"{ws.risk_free * 100:.2f}")
        dy = ws.history.trailing_dividends() / ws.history.price if ws.history.price else 0.0
        self.div.set_text(f"{dy * 100:.2f}")
        if first or not self.strike.text():
            self.strike.set_text(f"{round(ws.history.price / 5) * 5:.2f}" if ws.history.price > 20 else f"{ws.history.price:.2f}")
        self._vol_default()
        self._ret_default()

    def _vol_default(self) -> None:
        ws = self.ws
        src = self.vol_source.currentIndex()
        if not ws or not ws.history:
            return
        if src == 0:
            v = historical_vol(ws.history.closes, 252)
        elif src == 1:
            v = historical_vol(ws.history.closes, 63)
        elif src == 2:
            v = self._implied_from_inputs()
        else:
            self.vol.edit.setEnabled(True)
            return
        self.vol.edit.setEnabled(False)
        self.vol.set_text(f"{v * 100:.1f}" if v and np.isfinite(v) else "")

    def _ret_default(self) -> None:
        if self.ret_source.currentIndex() == 0:
            self.ret.edit.setEnabled(False)
            self.ret.set_text(self.rate.text() or "4.0")
        else:
            self.ret.edit.setEnabled(True)

    def _implied_from_inputs(self) -> float | None:
        ws = self.ws
        try:
            k = float(self.strike.text())
            prem = float(self.premium.text())
            t = options.years_to(self.expiry.date().toPython())
        except (ValueError, validation.ValidationError):
            return None
        return options.implied_vol(self.kind.currentText().lower(), prem, ws.history.price, k, t, ws.risk_free, self._div_yield())

    def _div_yield(self) -> float:
        try:
            return float(self.div.text()) / 100
        except ValueError:
            return 0.0

    def set_chain(self, chain: OptionChain) -> None:
        self.chain = chain
        self.chain_notice.clear()
        current = self.expiry_box.currentText()
        self.expiry_box.blockSignals(True)
        self.expiry_box.clear()
        self.expiry_box.addItems(chain.expiries)
        self.expiry_box.setCurrentText(chain.expiry if chain.expiry in chain.expiries else current)
        self.expiry_box.blockSignals(False)
        self.chain_source.set_sources([chain.source])
        self._fill_chain()

    def show_chain_error(self, message: str) -> None:
        self.chain_notice.show_message(message, "warn")

    def _fill_chain(self) -> None:
        if not self.chain:
            return
        quotes = self.chain.calls if self.side_box.currentIndex() == 0 else self.chain.puts
        self._quotes = quotes
        spot = self.ws.history.price if self.ws and self.ws.history else None
        rows, tones = [], []
        for q in quotes:
            rows.append([num(q.strike), num(q.bid), num(q.ask), num(q.mid), num(q.last), pct(q.implied_vol, 1) if q.implied_vol else "n/a", f"{q.volume:,}" if q.volume is not None else "", f"{q.open_interest:,}" if q.open_interest is not None else ""])
            itm = spot is not None and ((q.strike < spot) if q.kind == "call" else (q.strike > spot))
            tones.append(["accent" if itm else None] + [None] * 7)
        self.table.fill(rows, tones, align_right_from=0)
        if spot is not None and quotes:
            atm = int(np.argmin([abs(q.strike - spot) for q in quotes]))
            self.table.scrollToItem(self.table.item(atm, 0))
            self.table.selectRow(atm)

    def _pick(self, row: int, _col: int) -> None:
        if not 0 <= row < len(self._quotes):
            return
        q = self._quotes[row]
        self.kind.setCurrentIndex(0 if q.kind == "call" else 1)
        self.strike.set_text(f"{q.strike:.2f}")
        if q.mid:
            self.premium.set_text(f"{q.mid:.2f}")
        y, m, d = (int(x) for x in q.expiry.split("-"))
        self.expiry.setDate(QDate(y, m, d))
        self._vol_default()

    # ------------------------------------------------------------- analysis
    def read_contract(self):
        ok, vals = True, {}
        for key, field, fn in (
            ("strike", self.strike, lambda t: validation.number(t, "Strike", allow_zero=False)),
            ("premium", self.premium, lambda t: validation.number(t, "Premium", allow_zero=False)),
            ("contracts", self.contracts, lambda t: validation.positive_int(t, "Contracts", 1, 10_000)),
            ("vol", self.vol, lambda t: validation.number(t, "Volatility", 1, 300, allow_zero=False) / 100),
            ("ret", self.ret, lambda t: validation.number(t, "Expected return", -90, 300, allow_negative=True) / 100),
            ("rate", self.rate, lambda t: validation.number(t, "Risk-free rate", 0, 25) / 100),
            ("div", self.div, lambda t: validation.number(t, "Dividend yield", 0, 25) / 100),
        ):
            try:
                vals[key] = fn(field.text())
                field.clear_error()
            except validation.ValidationError as exc:
                field.set_error(str(exc))
                ok = False
        expiry = self.expiry.date().toPython()
        if expiry <= date.today():
            self.calc_notice.show_message("The expiry date must be after today.", "error")
            return None
        if not ok:
            self.calc_notice.show_message("Correct the highlighted fields.", "error")
            return None
        kind = self.kind.currentText().lower()
        side = "long" if self.position.currentIndex() == 0 else "short"
        return options.Contract(kind, side, vals["strike"], vals["premium"], expiry), vals

    def analyze(self) -> None:
        ws = self.ws
        if not ws or not ws.history:
            self.calc_notice.show_message("Load a ticker first.", "error")
            return
        if self.vol_source.currentIndex() == 2:
            self._vol_default()
        parsed = self.read_contract()
        if parsed is None:
            return
        contract, v = parsed
        spot = ws.history.price
        t = options.years_to(contract.expiry)
        terminal = None
        if self.sim.isChecked():
            days = max(1, int(np.busday_count(date.today(), contract.expiry)))
            try:
                cfg = montecarlo.MCConfig(horizon_days=days, n_paths=min(40_000, max(2_000, 20_000_000 // days)), model="student_t", drift_mode="custom", custom_return=v["ret"], vol_override=v["vol"], seed=7)
                terminal = montecarlo.simulate(ws.history.closes, cfg, start_price=spot).terminal
            except validation.ValidationError:
                terminal = None
        try:
            res = options.analyze(contract, spot, t, v["rate"], v["div"], v["vol"], v["ret"], None, terminal, "Fat-tailed Monte Carlo")
        except validation.ValidationError as exc:
            self.calc_notice.show_message(str(exc), "error")
            return
        self.calc_notice.clear()
        self.show_result(res, v["contracts"], ws.history.currency)

    def show_result(self, res: options.OptionAnalysis, contracts: int, currency: str) -> None:
        c = res.contract
        mult = options.CONTRACT * contracts
        self.res_frame.show()
        self.verdict.setText(f"{res.verdict} at {num(c.premium)}  |  {'Buy' if c.side == 'long' else 'Sell'} {contracts} {c.kind} {num(c.strike)} {c.expiry:%Y-%m-%d}")
        self.verdict.setStyleSheet(f"color: {VERDICT_TONE.get(res.verdict, theme.TEXT)};")
        self.reason.setText(res.verdict_reason)
        rows, tones = [], []
        for s in res.scenarios:
            rows.append([s.label, pct(s.vol, 1) if np.isfinite(s.vol) else "simulated", pct(math.exp(s.mu) - 1, 1) if np.isfinite(s.mu) else "your return", pct(s.prob_profit, 1), pct(s.prob_itm, 1), num(s.expected_pnl, 2, True), dollars(s.expected_pnl * mult, True), num(s.fair_premium)])
            tones.append([None, None, None, None, None, "up" if s.expected_pnl > 0 else "down", "up" if s.expected_pnl > 0 else "down", None])
        self.scenarios.fill(rows, tones)
        self.scenarios.fit_height()
        unlimited = "Unlimited"
        terms = [
            ["Underlying", num(res.spot)],
            ["Breakeven at expiry", num(res.breakeven)],
            ["Days to expiry", f"{res.t_years * 365:.0f}"],
            ["Implied volatility (from premium)", pct(res.implied_vol, 1) if res.implied_vol else "n/a"],
            ["Model price at your volatility", num(res.greeks.get("model price"))],
            ["Max profit (position)", dollars(res.max_profit * mult) if res.max_profit is not None else unlimited],
            ["Max loss (position)", dollars(res.max_loss * mult) if res.max_loss is not None else unlimited],
            ["Premium (position)", dollars(c.premium * mult)],
        ]
        self.terms.fill(terms)
        self.terms.fit_height()
        g = res.greeks
        self.greeks.fill([[f"{contracts} contract(s)", num(g["delta"] * mult, 1), num(g["gamma"] * mult, 3), num(g["theta"] * mult, 2), num(g["vega"] * mult, 2), num(g["rho"] * mult, 2)]])
        self.greeks.fit_height()
        self.notes.setText(" ".join(res.notes))

        fig = self.payoff.clear()
        ax = fig.add_subplot()
        model = next(s for s in res.scenarios if s.label == "Your assumptions")
        sd = model.vol * math.sqrt(res.t_years)
        # Show about +-3.5 standard deviations of the terminal price, widened to keep
        # the strike and breakeven in view. (First Version: a fixed +-40% of spot, which
        # squeezed a one-week contract's whole distribution into a sliver.)
        width = min(max(3.5 * sd, 0.04), 1.2)
        lo = min(res.spot * math.exp(-width), c.strike, res.breakeven) * 0.98
        hi = max(res.spot * math.exp(width), c.strike, res.breakeven) * 1.02
        xs = np.linspace(lo, hi, 400)
        pnl = options.position_pnl(c, xs) * mult
        ax.plot(xs, pnl, color=theme.TEXT, linewidth=1.3, label="P&L at expiry")
        ax.fill_between(xs, pnl, 0, where=pnl >= 0, color=theme.UP, alpha=0.18, linewidth=0)
        ax.fill_between(xs, pnl, 0, where=pnl < 0, color=theme.DOWN, alpha=0.18, linewidth=0)
        ax.axhline(0, color=theme.BORDER, linewidth=0.8)
        for value, name, color in ((res.spot, "Spot", theme.ACCENT), (c.strike, "Strike", theme.MUTED), (res.breakeven, "Breakeven", theme.WARN)):
            ax.axvline(value, color=color, linewidth=0.9, linestyle="--", label=name)
        m = math.log(res.spot) + (model.mu - 0.5 * model.vol**2) * res.t_years
        density = np.exp(-((np.log(xs) - m) ** 2) / (2 * sd * sd)) / (xs * sd * math.sqrt(2 * math.pi))
        ax2 = ax.twinx()
        ax2.fill_between(xs, density, color=theme.ACCENT, alpha=0.12, linewidth=0)
        ax2.set_yticks([])
        ax2.grid(False)
        ax.xaxis.set_major_formatter(price_formatter(currency))
        ax.set_title("P&L at expiry for the position, with the price distribution under your assumptions (shaded)")
        ax.legend(loc="upper left", ncols=4)
        self.payoff.draw()
