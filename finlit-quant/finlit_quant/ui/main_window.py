"""The main window: search, watchlist, header, tabs, and the jobs that feed them."""

from __future__ import annotations

import time

from PySide6.QtCore import QStringListModel, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
    QCompleter,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from finlit_quant import APP_NAME, __version__, validation
from finlit_quant.ai import AIError, make_provider, offline
from finlit_quant.ai import brief as brief_mod
from finlit_quant.analysis import Analysis
from finlit_quant.analytics import montecarlo, portfolio, predictor, risk, valuation
from finlit_quant.config import Settings, save_settings
from finlit_quant.data import demo, sec, yahoo
from finlit_quant.data.models import DataError
from finlit_quant.ui import report, theme
from finlit_quant.ui.settings_dialog import SettingsDialog
from finlit_quant.ui.tabs.ai_tab import AITab
from finlit_quant.ui.tabs.chart_tab import ChartTab
from finlit_quant.ui.tabs.compare_tab import CompareTab
from finlit_quant.ui.tabs.fundamentals_tab import FundamentalsTab
from finlit_quant.ui.tabs.predictor_tab import PredictorTab
from finlit_quant.ui.tabs.risk_tab import RiskTab
from finlit_quant.ui.tabs.valuation_tab import ValuationTab, recompute
from finlit_quant.ui.widgets import Banner, label
from finlit_quant.ui.workers import Job, Runner, StreamJob

OFFLINE_HINT = " To try the app without a connection, type DEMO for a simulated stock."


def _fetch_prices(symbol: str, bench_symbol: str | None, force: bool):
    """Runs on a worker thread: the stock, its benchmark, and the T-bill yield."""
    hist = yahoo.history(symbol, force=force)
    bench = None
    if bench_symbol and bench_symbol != hist.symbol:
        try:
            bench = yahoo.history(bench_symbol)
        except DataError:
            bench = None
    rf = None if demo.is_demo(symbol) else yahoo.risk_free_rate()
    return hist, bench, rf


def _simulate(symbol: str, hist, cfg: montecarlo.MCConfig):
    mc = montecarlo.simulate(hist.closes, cfg, start_price=hist.price)
    pred = predictor.run(hist.bars, mc.stats["median"], cfg.horizon_days)
    cal = montecarlo.calibration(hist.closes, cfg.horizon_days, cfg.lookback_days)
    return symbol, mc, pred, cal


def _compare(symbols: list[str], years: float, rf: float):
    closes, skipped = {}, []
    for sym in symbols:
        try:
            closes[sym] = yahoo.history(sym).closes
        except DataError as exc:
            skipped.append(f"{sym} ({exc})")
    if len(closes) < 2:
        raise DataError("Fewer than two of those tickers could be loaded, so there is nothing to compare. " + " ".join(skipped))
    cmp = portfolio.compare(closes, years, rf)
    return cmp, portfolio.frontier(cmp.returns, rf), skipped


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.runner = Runner()
        self.req = self.mc_req = self.ai_req = self.cmp_req = self.search_req = 0
        self.analysis: Analysis | None = None
        self.ai_messages: list[dict] = []
        self.ai_job: StreamJob | None = None
        self.ai_provider = None

        self.setWindowTitle(APP_NAME)
        self.resize(1440, 920)
        self._build_menu()

        central = QWidget()
        central.setObjectName("Page")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_header())
        self.banner = Banner()
        wrap = QWidget()
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(18, 8, 18, 0)
        wl.addWidget(self.banner)
        root.addWidget(wrap)

        self.tabs = QTabWidget()
        self.chart_tab = ChartTab(settings.default_range)
        self.predictor_tab = PredictorTab()
        self.fund_tab = FundamentalsTab()
        self.val_tab = ValuationTab()
        self.risk_tab = RiskTab(settings.benchmark)
        self.compare_tab = CompareTab()
        self.ai_tab = AITab()
        for tab, name in (
            (self.chart_tab, "Chart"),
            (self.predictor_tab, "Monte Carlo Predictor"),
            (self.fund_tab, "Fundamentals (SEC)"),
            (self.val_tab, "Valuation"),
            (self.risk_tab, "Risk"),
            (self.compare_tab, "Compare"),
            (self.ai_tab, "AI Analyst"),
        ):
            self.tabs.addTab(tab, name)
        root.addWidget(self.tabs, 1)
        self.setCentralWidget(central)
        self._build_watchlist()
        self.statusBar().showMessage("Ready. Type a ticker or a company name.")

        self.predictor_tab.run_requested.connect(self.run_mc)
        self.fund_tab.email_saved.connect(self._email_saved)
        self.val_tab.inputs_changed.connect(self._dcf_changed)
        self.risk_tab.settings_changed.connect(self._risk_changed)
        self.compare_tab.run_requested.connect(self.run_compare)
        self.ai_tab.generate_requested.connect(self.generate_memo)
        self.ai_tab.ask_requested.connect(self.ask_followup)
        self.ai_tab.stop_requested.connect(self.stop_ai)
        self._update_provider_label()
        self.fund_tab.need_email(not settings.sec_contact_email)

    # ------------------------------------------------------------------ layout
    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        for text, shortcut, slot in (
            ("Export research report (HTML)...", "Ctrl+E", self.export_report),
            ("Export price history (CSV)...", None, self.export_csv),
            ("Settings...", "Ctrl+,", self.open_settings),
            ("Quit", "Ctrl+Q", self.close),
        ):
            act = QAction(text, self)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(slot)
            file_menu.addAction(act)
        view = self.menuBar().addMenu("&View")
        for text, shortcut, slot in (("Find ticker", "Ctrl+L", lambda: self.search.setFocus()), ("Refresh data", "F5", lambda: self.load(self.search.text() or (self.analysis.symbol if self.analysis else ""), force=True))):
            act = QAction(text, self)
            act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(slot)
            view.addAction(act)
        help_menu = self.menuBar().addMenu("&Help")
        about = QAction("About FinLit Quant", self)
        about.triggered.connect(self.about)
        help_menu.addAction(about)

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("Toolbar")
        bar.setAttribute(Qt.WA_StyledBackground, True)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 10, 18, 10)
        brand = QLabel(f"<span style='color:{theme.ACCENT}; font-weight:800; font-size:18px;'>FinLit</span> <span style='font-weight:800; font-size:18px;'>Quant</span>")
        lay.addWidget(brand)
        lay.addSpacing(18)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Ticker or company name, e.g. AAPL, Microsoft, BRK-B, DEMO")
        self.search.setMinimumWidth(380)
        self.search.returnPressed.connect(lambda: self.load(self.search.text()))
        self.completer_model = QStringListModel()
        completer = QCompleter(self.completer_model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.activated.connect(self._completion_chosen)
        self.search.setCompleter(completer)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(350)
        self.search_timer.timeout.connect(self._run_search)
        self.search.textEdited.connect(lambda _: self.search_timer.start())
        lay.addWidget(self.search)
        go = QPushButton("Analyze")
        go.setObjectName("Primary")
        go.clicked.connect(lambda: self.load(self.search.text()))
        lay.addWidget(go)
        refresh = QPushButton("Refresh")
        refresh.setToolTip("Fetch fresh data, skipping the cache (F5)")
        refresh.clicked.connect(lambda: self.load(self.analysis.symbol if self.analysis else self.search.text(), force=True))
        lay.addWidget(refresh)
        lay.addStretch(1)
        export = QPushButton("Export report")
        export.clicked.connect(self.export_report)
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)
        lay.addWidget(export)
        lay.addWidget(settings_btn)
        return bar

    def _build_header(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(18, 12, 18, 4)
        left = QVBoxLayout()
        self.h_name = label("No ticker loaded", "H1")
        self.h_badges = QHBoxLayout()
        self.h_badges.setSpacing(6)
        left.addWidget(self.h_name)
        left.addLayout(self.h_badges)
        lay.addLayout(left, 1)
        right = QVBoxLayout()
        self.h_price = label("", "Price")
        self.h_price.setAlignment(Qt.AlignRight)
        self.h_change = label("", "Muted")
        self.h_change.setAlignment(Qt.AlignRight)
        right.addWidget(self.h_price)
        right.addWidget(self.h_change)
        lay.addLayout(right)
        return w

    def _set_badges(self, items: list[tuple[str, str]]) -> None:
        while self.h_badges.count():
            item = self.h_badges.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for text, kind in items:
            self.h_badges.addWidget(label(text, "BadgeWarn" if kind == "warn" else "Badge"))
        self.h_badges.addStretch(1)

    def _build_watchlist(self) -> None:
        dock = QDockWidget("Watchlist", self)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 6, 10, 10)
        self.watch = QListWidget()
        self.watch.itemClicked.connect(lambda item: self.load(item.data(Qt.UserRole)))
        lay.addWidget(self.watch, 1)
        row = QHBoxLayout()
        add = QPushButton("Add current")
        add.clicked.connect(self._watch_add)
        rem = QPushButton("Remove")
        rem.clicked.connect(self._watch_remove)
        row.addWidget(add)
        row.addWidget(rem)
        lay.addLayout(row)
        dock.setWidget(w)
        dock.setMinimumWidth(220)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self._refresh_watchlist()

    # --------------------------------------------------------------- watchlist
    def _refresh_watchlist(self) -> None:
        self.watch.clear()
        for sym in self.settings.watchlist:
            item = QListWidgetItem(sym)
            item.setData(Qt.UserRole, sym)
            self.watch.addItem(item)
            self.runner.start(Job(0, lambda s=sym: (s, *yahoo.quote(s))), self._watch_quote, lambda *_: None)

    def _watch_quote(self, _rid: int, result) -> None:
        sym, price, change = result
        for i in range(self.watch.count()):
            item = self.watch.item(i)
            if item.data(Qt.UserRole) == sym:
                ch = f"{change:+.2%}" if change is not None else ""
                item.setText(f"{sym:<9} {price:>10,.2f}  {ch}")
                if change is not None:
                    item.setForeground(QColor(theme.ACCENT if change >= 0 else theme.RED))

    def _watch_add(self) -> None:
        if self.analysis and self.analysis.symbol not in self.settings.watchlist:
            if len(self.settings.watchlist) >= 40:
                self.banner.show_message("The watchlist holds 40 tickers. Remove one before adding another.", "warn")
                return
            self.settings.watchlist.append(self.analysis.symbol)
            save_settings(self.settings)
            self._refresh_watchlist()
        elif not self.analysis:
            self.banner.show_message("Load a ticker first, then add it to the watchlist.", "info")

    def _watch_remove(self) -> None:
        item = self.watch.currentItem()
        if not item:
            self.banner.show_message("Click a ticker in the watchlist first, then press Remove.", "info")
            return
        self.settings.watchlist = [s for s in self.settings.watchlist if s != item.data(Qt.UserRole)]
        save_settings(self.settings)
        self._refresh_watchlist()

    # ------------------------------------------------------------------ search
    def _run_search(self) -> None:
        text = self.search.text().strip()
        if len(text) < 2:
            return
        self.search_req += 1
        self.runner.start(Job(self.search_req, yahoo.search, text), self._search_done, lambda *_: None)

    def _search_done(self, rid: int, results: list[dict]) -> None:
        if rid != self.search_req:
            return
        self.completer_model.setStringList([f"{r['symbol']}  |  {r['name']}  ({r['exchange']} {r['type']})".strip() for r in results])
        self.search.completer().complete()

    def _completion_chosen(self, text: str) -> None:
        sym = text.split("|")[0].strip()
        QTimer.singleShot(0, lambda: (self.search.setText(sym), self.load(sym)))

    # -------------------------------------------------------------------- load
    def load(self, text: str, force: bool = False) -> None:
        try:
            sym = validation.ticker(text)
        except validation.ValidationError as exc:
            self.banner.show_message(str(exc), "error")
            return
        self.banner.hide()
        self.req += 1
        rid = self.req
        self.analysis = Analysis(sym)
        self.ai_messages = []
        self.ai_tab.reset()
        self.search.setText(sym)
        self.h_name.setText(f"{sym}   loading...")
        self.h_price.setText("")
        self.h_change.setText("")
        self.statusBar().showMessage(f"Loading {sym} from Yahoo Finance...")
        bench = "DEMO-MKT" if demo.is_demo(sym) else self.settings.benchmark
        if not demo.is_demo(sym):
            self.risk_tab.bench.set_text(self.settings.benchmark)
        else:
            self.risk_tab.bench.set_text("DEMO-MKT")
        self.runner.start(Job(rid, _fetch_prices, sym, bench, force), self._prices_done, self._prices_failed)

        if demo.is_demo(sym) or self.settings.sec_contact_email:
            self.fund_tab.need_email(False)
            self.fund_tab.show_loading()
            self.runner.start(Job(rid, sec.fundamentals, sym, self.settings.sec_contact_email, force), self._fund_done, self._fund_failed)
        else:
            self.analysis.fundamentals_error = "Add your email in the box above (or in Settings) to load SEC filings for this company."
            self.fund_tab.need_email(True)
            self.fund_tab.render(self.analysis)
        self.runner.start(Job(rid, yahoo.news, sym), self._news_done, lambda *_: None)

    def _prices_failed(self, rid: int, message: str) -> None:
        if rid != self.req:
            return
        self.h_name.setText("No ticker loaded")
        hint = OFFLINE_HINT if "reach" in message or "connection" in message else ""
        self.banner.show_message(message + hint, "error")
        self.statusBar().showMessage("Load failed.")

    def _prices_done(self, rid: int, result) -> None:
        if rid != self.req or self.analysis is None:
            return
        hist, bench, rf = result
        a = self.analysis
        a.history, a.benchmark = hist, bench
        a.risk_free = rf if rf is not None else self.settings.risk_free_rate_pct / 100
        a.risk_free_live = rf is not None
        self._render_header()
        self._compute_risk()
        self.chart_tab.render(a)
        self.risk_tab.render(a)
        if a.fundamentals:
            self._compute_fundamentals()
        cfg = self.predictor_tab.config() or montecarlo.MCConfig()
        self.run_mc(cfg)
        self._refresh_brief()
        self.settings.last_symbol = a.symbol
        save_settings(self.settings)
        age = time.time() - hist.fetched_at.timestamp()
        where = {"live": "live from Yahoo Finance", "cache": f"from cache ({age / 60:.0f} min old)", "stale": f"OFFLINE: cached copy from {hist.fetched_at:%Y-%m-%d %H:%M}", "demo": "simulated demo data"}[hist.source]
        self.statusBar().showMessage(f"{a.symbol}: {len(hist.bars):,} daily bars, {where}.")

    def _render_header(self) -> None:
        a = self.analysis
        h = a.history
        self.h_name.setText(f"{h.symbol}   {h.name}")
        self.h_price.setText(f"{h.price:,.2f} {h.currency}")
        if h.day_change is not None:
            color = theme.ACCENT if h.day_change >= 0 else theme.RED
            self.h_change.setText(f"<span style='color:{color}; font-weight:700;'>{h.price - h.previous_close:+,.2f} ({h.day_change:+.2%})</span> today")
        badges = []
        if h.source == "demo":
            badges.append(("SIMULATED DEMO DATA, NOT A REAL COMPANY", "warn"))
        elif h.source == "stale":
            badges.append((f"OFFLINE: cached prices from {h.fetched_at:%b %d %H:%M}", "warn"))
        else:
            badges.append(("Yahoo Finance " + ("live" if h.source == "live" else "cached"), "ok"))
        for extra in (h.exchange, h.instrument_type):
            if extra:
                badges.append((extra, "ok"))
        badges.append((f"As of {h.bars.index[-1]:%b %d, %Y}", "ok"))
        self._set_badges(badges)

    def _compute_risk(self, years: float | None = None) -> None:
        a = self.analysis
        if not a or not a.history:
            return
        try:
            a.risk = risk.report(
                a.history.closes,
                a.benchmark.closes if a.benchmark else None,
                a.risk_free,
                years or self.risk_tab.years(),
                a.benchmark.symbol if a.benchmark else self.risk_tab.bench.text().strip().upper() or None,
            )
        except ValueError as exc:
            a.risk = None
            self.risk_tab.show_error(str(exc))

    def _risk_changed(self, years: float, bench_symbol: str) -> None:
        a = self.analysis
        if not a or not a.history:
            self.risk_tab.show_error("Load a ticker first.")
            return
        if a.benchmark and a.benchmark.symbol == bench_symbol:
            self._compute_risk(years)
            self.risk_tab.render(a)
            self._refresh_brief()
            return
        rid = self.req

        def done(job_rid, bench):
            if job_rid != self.req:
                return
            a.benchmark = bench
            self._compute_risk(years)
            self.risk_tab.render(a)
            self._refresh_brief()

        self.runner.start(Job(rid, yahoo.history, bench_symbol), done, lambda _r, msg: self.risk_tab.show_error(f"Benchmark {bench_symbol}: {msg}"))

    # ---------------------------------------------------------- fundamentals
    def _fund_done(self, rid: int, fund) -> None:
        if rid != self.req or self.analysis is None:
            return
        self.analysis.fundamentals = fund
        self.analysis.fundamentals_error = None
        if self.analysis.history:
            self._compute_fundamentals()

    def _fund_failed(self, rid: int, message: str) -> None:
        if rid != self.req or self.analysis is None:
            return
        self.analysis.fundamentals_error = message
        self.fund_tab.render(self.analysis)
        self.val_tab.render(self.analysis)
        self._refresh_brief()

    def _compute_fundamentals(self) -> None:
        a = self.analysis
        f, h = a.fundamentals, a.history
        sec.apply_splits(f, h.splits)
        a.ratios = valuation.ratios(f, h.price, h.trailing_dividends())
        a.piotroski = valuation.piotroski(f.annual)
        a.altman = valuation.altman_z(f, a.ratios.get("market_cap", float("nan")))
        recompute(a, valuation.default_inputs(f, a.ratios))
        self.fund_tab.render(a)
        self.val_tab.render(a)
        self._refresh_brief()

    def _dcf_changed(self, inp) -> None:
        a = self.analysis
        if not a or not a.history:
            return
        recompute(a, inp)
        self.val_tab.render(a)
        self._refresh_brief()

    def _email_saved(self, email: str) -> None:
        self.settings.sec_contact_email = email
        save_settings(self.settings)
        self.statusBar().showMessage("SEC contact email saved.")
        if self.analysis:
            self.load(self.analysis.symbol)

    def _news_done(self, rid: int, items) -> None:
        if rid != self.req or self.analysis is None:
            return
        self.analysis.news = items
        self.ai_tab.set_news(items)
        self._refresh_brief()

    # ------------------------------------------------------------ simulation
    def run_mc(self, cfg: montecarlo.MCConfig) -> None:
        a = self.analysis
        if not a or not a.history:
            self.predictor_tab.show_error("Load a ticker first, then run the simulation.")
            return
        self.mc_req += 1
        self.predictor_tab.set_busy(True)
        self.runner.start(Job(self.mc_req, _simulate, a.symbol, a.history, cfg), self._mc_done, self._mc_failed)

    def _mc_done(self, rid: int, result) -> None:
        if rid != self.mc_req:
            return
        self.predictor_tab.set_busy(False)
        symbol, mc, pred, cal = result
        a = self.analysis
        if not a or a.symbol != symbol:
            return
        a.mc, a.predictor, a.calibration = mc, pred, cal
        self.predictor_tab.render(a)
        self._refresh_brief()

    def _mc_failed(self, rid: int, message: str) -> None:
        if rid != self.mc_req:
            return
        self.predictor_tab.set_busy(False)
        self.predictor_tab.show_error(message)

    # ---------------------------------------------------------------- compare
    def run_compare(self, symbols: list[str], years: float) -> None:
        self.cmp_req += 1
        self.compare_tab.set_busy(True)
        rf = self.analysis.risk_free if self.analysis else self.settings.risk_free_rate_pct / 100
        self.runner.start(Job(self.cmp_req, _compare, symbols, years, rf), self._compare_done, self._compare_failed)

    def _compare_done(self, rid: int, result) -> None:
        if rid != self.cmp_req:
            return
        self.compare_tab.set_busy(False)
        self.compare_tab.render(*result)

    def _compare_failed(self, rid: int, message: str) -> None:
        if rid != self.cmp_req:
            return
        self.compare_tab.set_busy(False)
        self.compare_tab.show_error(message)

    # --------------------------------------------------------------------- AI
    def _update_provider_label(self) -> None:
        choice = self.settings.resolved_provider()
        text = {
            "claude": f"Claude ({self.settings.anthropic_model}, effort {self.settings.anthropic_effort})",
            "openai": f"OpenAI ({self.settings.openai_model})",
            "offline": "Offline rule-based analyst (add a key in Settings for AI)",
        }[choice]
        self.ai_tab.set_provider(text)

    def _refresh_brief(self) -> None:
        if self.analysis and self.analysis.history:
            self.ai_tab.set_brief(brief_mod.build(self.analysis))

    def _ai_ready(self) -> bool:
        if not self.analysis or not self.analysis.history:
            self.ai_tab.fail("Load a ticker first. The analyst needs data to read.")
            return False
        return True

    def generate_memo(self) -> None:
        if not self._ai_ready():
            return
        a = self.analysis
        try:
            provider = make_provider(self.settings)
        except AIError as exc:
            self.ai_tab.fail(str(exc))
            return
        brief = brief_mod.build(a)
        self.ai_tab.set_brief(brief)
        if provider is None:
            self.ai_tab.begin()
            self.ai_tab.append(offline.memo(a))
            self.ai_tab.finish("Offline rule-based analyst")
            self.ai_messages = []
            return
        self.ai_messages = [brief_mod.first_message(brief)]
        self._stream(provider, brief_mod.SYSTEM_PROMPT)

    def ask_followup(self, question: str) -> None:
        if not self._ai_ready():
            return
        try:
            provider = make_provider(self.settings)
        except AIError as exc:
            self.ai_tab.fail(str(exc))
            return
        if provider is None:
            self.ai_tab.fail("Follow-up questions need an AI model. Add an Anthropic or OpenAI key in Settings; the offline analyst only writes the memo.")
            return
        if not self.ai_messages:
            brief = brief_mod.build(self.analysis)
            self.ai_messages = [{"role": "user", "content": f"{brief}\n\n{brief_mod.FOLLOW_UP_NOTE}\n\nQuestion: {question}"}]
        else:
            self.ai_messages.append({"role": "user", "content": f"{brief_mod.FOLLOW_UP_NOTE}\n\nQuestion: {question}"})
        self._stream(provider, brief_mod.SYSTEM_PROMPT, heading=question)

    def _stream(self, provider, system: str, heading: str | None = None) -> None:
        self.ai_req += 1
        rid = self.ai_req
        messages = list(self.ai_messages)
        self.ai_provider = provider
        self.ai_tab.begin(heading)
        self.ai_job = StreamJob(rid, lambda: provider.stream(system, messages))
        self.runner.start(self.ai_job, self._ai_done, self._ai_failed, self._ai_chunk)

    def _ai_chunk(self, rid: int, text: str) -> None:
        if rid == self.ai_req:
            self.ai_tab.append(text)

    def _ai_done(self, rid: int, full: str) -> None:
        if rid != self.ai_req:
            return
        self.ai_messages.append({"role": "assistant", "content": full})
        served = getattr(self.ai_provider, "served_model", None)
        self.ai_tab.finish(f"{self.ai_provider.label}, answered by {served}" if served else None)

    def _ai_failed(self, rid: int, message: str) -> None:
        if rid != self.ai_req:
            return
        if self.ai_messages and self.ai_messages[-1]["role"] == "user":
            self.ai_messages.pop()
        self.ai_tab.fail(message)

    def stop_ai(self) -> None:
        if self.ai_job:
            self.ai_job.cancelled.set()
        self.ai_req += 1
        if self.ai_messages and self.ai_messages[-1]["role"] == "user":
            self.ai_messages.pop()
        self.ai_tab.finish()
        self.ai_tab.append("\n\n*Stopped.*")

    # ------------------------------------------------------------- settings
    def open_settings(self) -> None:
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec() and dlg.result_settings:
            old = self.settings
            self.settings = dlg.result_settings
            save_settings(self.settings)
            self._update_provider_label()
            self.statusBar().showMessage("Settings saved.")
            if self.analysis and (old.sec_contact_email != self.settings.sec_contact_email or old.benchmark != self.settings.benchmark):
                self.load(self.analysis.symbol)

    # --------------------------------------------------------------- export
    def _charts(self) -> dict[str, str]:
        out = {}
        for caption, chart in (
            ("Price chart", self.chart_tab.chart),
            ("Monte Carlo spread", self.predictor_tab.fan),
            ("Monte Carlo terminal distribution", self.predictor_tab.hist),
            ("Ten years of results (SEC filings)", self.fund_tab.chart),
            ("Monte Carlo DCF", self.val_tab.mc_chart),
            ("Growth and drawdowns", self.risk_tab.growth),
            ("Daily return distribution", self.risk_tab.dist),
        ):
            if chart.figure.axes and any(ax.has_data() for ax in chart.figure.axes):
                out[caption] = chart.png_base64()
        return out

    def export_report(self, path: str | None = None) -> str | None:
        a = self.analysis
        if not a or not a.history:
            self.banner.show_message("Load a ticker first, then export its report.", "info")
            return None
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Export research report", f"{a.symbol}_research_report.html", "HTML (*.html)")
        if not path:
            return None
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(report.build_html(a, self._charts(), self.ai_tab.markdown()))
        except OSError as exc:
            self.banner.show_message(f"Could not save the report there ({exc.strerror}). Pick another folder.", "error")
            return None
        self.statusBar().showMessage(f"Report saved to {path}")
        return path

    def export_csv(self) -> None:
        a = self.analysis
        if not a or not a.history:
            self.banner.show_message("Load a ticker first, then export its prices.", "info")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export price history", f"{a.symbol}_prices.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(report.price_csv(a))
        except OSError as exc:
            self.banner.show_message(f"Could not save the file there ({exc.strerror}). Pick another folder.", "error")
            return
        self.statusBar().showMessage(f"Prices saved to {path}")

    def about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} {__version__}</h3>"
            "<p>A desktop stock research workstation from the makers of FinLit Pro.</p>"
            "<p><b>Data:</b> prices from Yahoo Finance; fundamentals and filings from SEC EDGAR.<br>"
            "<b>AI:</b> Claude or OpenAI with your own key, or the offline rule-based analyst.</p>"
            "<p>The Monte Carlo predictor describes risk; it is not a forecast. Nothing here is personal financial advice.</p>",
        )

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if self.ai_job:
            self.ai_job.cancelled.set()
        save_settings(self.settings)
        super().closeEvent(event)
