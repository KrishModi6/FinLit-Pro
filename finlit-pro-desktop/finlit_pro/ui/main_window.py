"""Main window: toolbar, docked watchlist and data sources, the analysis views, and the jobs behind them."""

from __future__ import annotations

import dataclasses

import pandas as pd
from PySide6.QtCore import QByteArray, QDate, QStringListModel, Qt, QThreadPool, QTimer, QUrl
from PySide6.QtGui import QAction, QColor, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDateEdit,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from finlit_pro import APP_NAME, __version__, framing, glossary, pipeline, research, validation
from finlit_pro.analytics import montecarlo
from finlit_pro.config import Settings, save_settings
from finlit_pro.data import demo, filings, prices, sec, yahoo, yf_provider
from finlit_pro.data.models import STATUS_LABEL, DataError
from finlit_pro.model import registry
from finlit_pro.model.evaluation import walk_forward
from finlit_pro.ui import report, theme
from finlit_pro.ui.glossary_dialog import GlossaryDialog
from finlit_pro.ui.settings_dialog import SettingsDialog
from finlit_pro.ui.views.chart_view import ChartView
from finlit_pro.ui.views.filings_view import FilingsView
from finlit_pro.ui.views.fundamentals_view import FundamentalsView
from finlit_pro.ui.views.montecarlo_view import MonteCarloView
from finlit_pro.ui.views.options_view import OptionsView
from finlit_pro.ui.views.prediction_view import PredictionView
from finlit_pro.ui.views.research_view import ResearchView
from finlit_pro.ui.views.returns_view import ReturnsView
from finlit_pro.ui.views.valuation_view import recompute
from finlit_pro.ui.widgets import Notice, Table, install_tooltips, label
from finlit_pro.ui.workers import Job, Runner
from finlit_pro.workspace import Workspace

RANGES = ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "10Y", "Max", "Custom"]
RANGE_DAYS = {"1M": 31, "3M": 92, "6M": 183, "1Y": 365, "3Y": 1096, "5Y": 1826, "10Y": 3653}


# ---------------------------------------------------------------- worker functions


def _fetch_prices(symbol: str, benchmark: str, fallback_rf: float, force: bool) -> Workspace:
    ws = Workspace(symbol)
    pipeline.load_prices(ws, benchmark, fallback_rf, force)
    return ws


def _quote(symbol: str):
    if demo.is_demo(symbol):
        h = demo.history(symbol)
        return symbol, h.price, h.day_change
    return (symbol, *yahoo.quote(symbol))


def _run_model(symbol, bars, key, horizon, sims):
    return symbol, key, registry.get(key).predict(bars, horizon, sims)


def _evaluate(symbol, bars, key, horizon, step, cost_bps, progress=None, cancelled=None):
    return symbol, walk_forward(registry.get(key), bars, horizon, simulations=500, step=step or None, cost_bps=cost_bps, progress=progress, cancelled=cancelled)


def _simulate(symbol, hist, cfg):
    mc = montecarlo.simulate(hist.closes, cfg, start_price=hist.price)
    return symbol, mc, montecarlo.calibration(hist.closes, cfg.horizon_days, cfg.lookback_days)


def _research(ws: Workspace, settings: Settings, progress=None, cancelled=None):
    texts, problems = ws.filing_texts, ws.filing_problems
    if ws.fundamentals and not ws.is_demo and not texts:
        texts, problems = filings.latest_reports(ws.fundamentals, settings.sec_contact_email, settings.filing_section_chars)
    snapshot = dataclasses.replace(ws, filing_texts=texts, filing_problems=problems)
    note, reg, brief = research.run(snapshot, settings, progress, cancelled)
    return ws.symbol, note, reg, brief, texts, problems


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.runner = Runner()
        # Watchlist quotes get their own single thread, so a long watchlist never queues ahead of the
        # symbol being loaded. (First Version: they shared the pool and could delay the load.)
        self.quote_pool = QThreadPool(self)
        self.quote_pool.setMaxThreadCount(1)
        self.quote_runner = Runner(self.quote_pool)
        self._pending_bench: str | None = None
        self.ids = {k: 0 for k in ("load", "model", "eval", "mc", "chain", "research", "filings", "search", "bench")}
        self.ws: Workspace | None = None
        self.jobs: dict[str, Job] = {}
        self.option_chain = None
        self.setWindowTitle(APP_NAME)
        self.resize(1500, 940)

        self._build_toolbar()
        self.views = QTabWidget()
        self.views.setDocumentMode(True)
        self.chart = ChartView()
        self.returns = ReturnsView(settings.benchmark)
        self.prediction = PredictionView()
        self.mc_view = MonteCarloView()
        self.options = OptionsView()
        self.fundamentals = FundamentalsView()
        self.filings = FilingsView()
        self.research = ResearchView()
        for view, name, about in (
            (self.chart, "Chart", "Price history with moving averages, Bollinger Bands, volume, RSI and MACD. Drag to pan, scroll to zoom."),
            (self.returns, "Returns and Risk", "Return, volatility, drawdown and risk statistics over the selected range, against a benchmark."),
            (self.prediction, "Prediction Model", "The FinLit AI Predictor's forecast, its inputs and signals, and how it has performed out of sample on this stock."),
            (self.mc_view, "Monte Carlo", "Thousands of simulated price paths under adjustable assumptions, with the spread of outcomes."),
            (self.options, "Options", "The option chain, and for any contract its probabilities, Greeks and whether it is worth its price."),
            (self.fundamentals, "Fundamentals", "Ten years of financial statements from SEC filings, key ratios, quality scores and a DCF valuation."),
            (self.filings, "Filings", "The company's SEC filings, and the text of its latest annual and quarterly reports."),
            (self.research, "Research Note", "A cited research note that separates facts from interpretation and ends in a recommendation."),
        ):
            self.views.addTab(view, name)
            self.views.setTabToolTip(self.views.count() - 1, about)
        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.notice = Notice()
        lay.addWidget(self.notice)
        lay.addWidget(self.views, 1)
        self.setCentralWidget(central)
        self._build_docks()
        self._build_menu()
        self._build_status()

        self.prediction.run_requested.connect(self.run_model)
        self.prediction.evaluate_requested.connect(self.run_evaluation)
        self.prediction.cancel_requested.connect(lambda: self._cancel("eval"))
        self.mc_view.run_requested.connect(self.run_mc)
        self.options.chain_requested.connect(self.load_chain)
        self.fundamentals.email_saved.connect(self._email_saved)
        self.fundamentals.valuation.inputs_changed.connect(self._dcf_changed)
        self.returns.benchmark_changed.connect(self._benchmark_changed)
        self.filings.read_requested.connect(self.read_filings)
        self.research.run_requested.connect(self.run_research)
        self.research.cancel_requested.connect(lambda: self._cancel("research"))
        self._update_engine_label()
        self.fundamentals.need_email(not settings.sec_contact_email)
        install_tooltips(self)
        if settings.window_state:
            try:
                self.restoreState(QByteArray.fromHex(settings.window_state.encode()))
            except (ValueError, TypeError):
                pass

    # ------------------------------------------------------------------ layout
    def _build_toolbar(self) -> None:
        bar = QToolBar("Main")
        bar.setObjectName("MainToolbar")
        bar.setMovable(False)
        self.addToolBar(bar)
        self.symbol = QLineEdit()
        self.symbol.setPlaceholderText("Symbol or company name")
        self.symbol.setFixedWidth(220)
        self.symbol.returnPressed.connect(lambda: self.load(self.symbol.text()))
        self.completer_model = QStringListModel()
        completer = QCompleter(self.completer_model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.activated.connect(lambda text: QTimer.singleShot(0, lambda: self.load(text.split("  ")[0])))
        self.symbol.setCompleter(completer)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(350)
        self.search_timer.timeout.connect(self._search)
        self.symbol.textEdited.connect(lambda _: self.search_timer.start())
        bar.addWidget(self.symbol)
        load = QPushButton("Load")
        load.setObjectName("Primary")
        load.clicked.connect(lambda: self.load(self.symbol.text()))
        bar.addWidget(load)
        bar.addSeparator()
        bar.addWidget(QLabel("Range"))
        self.range_box = QComboBox()
        self.range_box.addItems(RANGES)
        self.range_box.setCurrentText(self.settings.default_range if self.settings.default_range in RANGES else "1Y")
        self.range_box.currentTextChanged.connect(self._range_changed)
        bar.addWidget(self.range_box)
        self.date_from = QDateEdit(QDate.currentDate().addYears(-1))
        self.date_to = QDateEdit(QDate.currentDate())
        for d in (self.date_from, self.date_to):
            d.setCalendarPopup(True)
            d.setDisplayFormat("yyyy-MM-dd")
            d.setEnabled(False)
            d.dateChanged.connect(lambda _: self._apply_range() if self.range_box.currentText() == "Custom" else None)
        bar.addWidget(QLabel("From"))
        bar.addWidget(self.date_from)
        bar.addWidget(QLabel("To"))
        bar.addWidget(self.date_to)
        bar.addSeparator()
        refresh = QPushButton("Refresh")
        refresh.setToolTip("Reload from the providers, bypassing the cache (F5)")
        refresh.clicked.connect(lambda: self.load(self.ws.symbol if self.ws else self.symbol.text(), force=True))
        bar.addWidget(refresh)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bar.addWidget(spacer)
        self.quote = label("", "Quote")
        bar.addWidget(self.quote)

    def _build_docks(self) -> None:
        dock = QDockWidget("Watchlist", self)
        dock.setObjectName("WatchlistDock")
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(4, 4, 4, 4)
        self.watch = Table(["Symbol", "Last", "Chg %"])
        self.watch.cellClicked.connect(lambda r, _c: self.load(self.watch.item(r, 0).text()))
        lay.addWidget(self.watch)
        row = QHBoxLayout()
        add, rem = QPushButton("Add"), QPushButton("Remove")
        add.clicked.connect(self._watch_add)
        rem.clicked.connect(self._watch_remove)
        row.addWidget(add)
        row.addWidget(rem)
        lay.addLayout(row)
        dock.setWidget(w)
        dock.setMinimumWidth(210)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.watch_dock = dock

        sdock = QDockWidget("Data sources", self)
        sdock.setObjectName("SourcesDock")
        sw = QWidget()
        slay = QHBoxLayout(sw)
        slay.setContentsMargins(4, 4, 4, 4)
        self.sources = Table(["Dataset", "Provider", "Status", "As of", "Retrieved", "Detail"])
        self.sources.setToolTip("Double-click a row to open the source.")
        self.sources.cellDoubleClicked.connect(self._open_source)
        slay.addWidget(self.sources, 3)
        self.attempts = QPlainTextEdit()
        self.attempts.setReadOnly(True)
        self.attempts.setPlaceholderText("Provider fallbacks and failures appear here.")
        slay.addWidget(self.attempts, 1)
        sdock.setWidget(sw)
        self.addDockWidget(Qt.BottomDockWidgetArea, sdock)
        self.resizeDocks([sdock], [160], Qt.Vertical)
        self.sources_dock = sdock
        self._source_urls: list[str] = []
        self._refresh_watchlist()

    def _build_menu(self) -> None:
        m = self.menuBar()
        file_menu = m.addMenu("&File")
        for text, key, slot in (
            ("Import prices from CSV...", None, self.import_csv),
            ("Export report (HTML)...", "Ctrl+E", self.export_report),
            ("Export price history (CSV)...", None, self.export_csv),
            (None, None, None),
            ("Settings...", "Ctrl+,", self.open_settings),
            (None, None, None),
            ("Exit", "Ctrl+Q", self.close),
        ):
            if text is None:
                file_menu.addSeparator()
                continue
            act = QAction(text, self)
            if key:
                act.setShortcut(QKeySequence(key))
            act.triggered.connect(slot)
            file_menu.addAction(act)
        view = m.addMenu("&View")
        view.addAction(self.watch_dock.toggleViewAction())
        view.addAction(self.sources_dock.toggleViewAction())
        focus = QAction("Find symbol", self)
        focus.setShortcut(QKeySequence("Ctrl+L"))
        focus.triggered.connect(lambda: (self.symbol.setFocus(), self.symbol.selectAll()))
        view.addAction(focus)
        refresh = QAction("Refresh data", self)
        refresh.setShortcut(QKeySequence("F5"))
        refresh.triggered.connect(lambda: self.load(self.ws.symbol, force=True) if self.ws else None)
        view.addAction(refresh)
        analysis = m.addMenu("&Analysis")
        for text, slot in (
            ("Run prediction model", lambda: self.run_model(*self.prediction.selection())),
            ("Run model evaluation", lambda: self.run_evaluation(self.prediction.selection()[0], self.prediction.selection()[1], 0)),
            ("Run Monte Carlo", lambda: (cfg := self.mc_view.config()) and self.run_mc(cfg)),
            ("Generate research note", self.run_research),
        ):
            act = QAction(text, self)
            act.triggered.connect(slot)
            analysis.addAction(act)
        help_menu = m.addMenu("&Help")
        for text, key, slot in (("Glossary", "F1", self.show_glossary), ("Data sources and limitations", None, self.show_data_help), ("About", None, self.about)):
            act = QAction(text, self)
            if key:
                act.setShortcut(QKeySequence(key))
            act.triggered.connect(slot)
            help_menu.addAction(act)

    def _build_status(self) -> None:
        self.status_prices = label("", "Small")
        self.status_sec = label("", "Small")
        personal = label("Personal use", "Small")
        personal.setToolTip(framing.PERSONAL_USE)
        for w in (self.status_prices, self.status_sec, personal):
            self.statusBar().addPermanentWidget(w)
        self.statusBar().showMessage("Ready")

    # ---------------------------------------------------------------- helpers
    def _next(self, kind: str) -> int:
        self.ids[kind] += 1
        return self.ids[kind]

    def _current(self, kind: str, rid: int, symbol: str | None = None) -> bool:
        return rid == self.ids[kind] and self.ws is not None and (symbol is None or symbol == self.ws.symbol)

    def _cancel(self, kind: str) -> None:
        job = self.jobs.get(kind)
        if job:
            job.cancel()

    def _range(self) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
        choice = self.range_box.currentText()
        last = self.ws.history.bars.index[-1] if self.ws and self.ws.history else pd.Timestamp.today().normalize()
        if choice == "Custom":
            return pd.Timestamp(self.date_from.date().toPython()), pd.Timestamp(self.date_to.date().toPython())
        if choice == "Max":
            return None, None
        if choice == "YTD":
            return pd.Timestamp(year=last.year, month=1, day=1), None
        return last - pd.Timedelta(days=RANGE_DAYS[choice]), None

    def _range_changed(self, choice: str) -> None:
        custom = choice == "Custom"
        self.date_from.setEnabled(custom)
        self.date_to.setEnabled(custom)
        if not custom and self.ws and self.ws.history:
            start, _ = self._range()
            self.date_from.blockSignals(True)
            self.date_from.setDate(QDate(start.year, start.month, start.day) if start is not None else QDate(self.ws.history.bars.index[0].year, 1, 1))
            self.date_from.blockSignals(False)
        self.settings.default_range = choice if choice != "Custom" else self.settings.default_range
        self._apply_range()

    def _apply_range(self) -> None:
        ws = self.ws
        if not ws or not ws.history:
            return
        start, end = self._range()
        if start is not None and end is not None and start >= end:
            self.notice.show_message("The start date must be before the end date.", "error")
            return
        self.notice.clear()
        self.chart.render(ws, start, end)
        self._compute_risk()

    def _compute_risk(self) -> None:
        ws = self.ws
        start, end = self._range()
        try:
            ws.risk = pipeline.risk.report(ws.history.closes, ws.benchmark.closes if ws.benchmark else None, ws.risk_free, None, ws.benchmark.symbol if ws.benchmark else None, start=start if start is not None else ws.history.bars.index[0], end=end)
            self.returns.render(ws)
        except ValueError as exc:
            self.returns.show_error(str(exc))

    def _refresh_sources(self) -> None:
        ws = self.ws
        if not ws:
            return
        rows, urls = [], []
        entries = []
        if ws.history:
            entries.append(("Prices", ws.history.source))
        if ws.benchmark:
            entries.append((f"Benchmark {ws.benchmark.symbol}", ws.benchmark.source))
        if ws.risk_free_source:
            entries.append(("Risk-free rate", ws.risk_free_source))
        if ws.fundamentals:
            entries += [("Fundamentals", s) for s in ws.fundamentals.sources]
        entries += [(f"{ft.filing.form} text", ft.source) for ft in ws.filing_texts]
        if self.option_chain is not None and self.option_chain.symbol == ws.symbol:
            entries.append(("Options", self.option_chain.source))
        for name, s in entries:
            rows.append([name, s.name, STATUS_LABEL.get(s.status, s.status), s.as_of or "", f"{s.retrieved_at:%Y-%m-%d %H:%M}", s.detail])
            urls.append(s.url)
        self._source_urls = urls
        self.sources.fill(rows, [[None, None, "warn" if r[2] in ("Offline copy", "Imported file", "Simulated") else None, None, None, None] for r in rows], align_right_from=99, stretch_col=5)
        log = list(ws.history.attempts) if ws.history else []
        if ws.fundamentals_error:
            log.append(f"SEC EDGAR: {ws.fundamentals_error}")
        log += ws.filing_problems
        self.attempts.setPlainText("\n".join(log))
        if ws.history:
            s = ws.history.source
            self.status_prices.setText(f"Prices: {s.name}, {STATUS_LABEL.get(s.status, s.status).lower()}, {s.retrieved_at:%H:%M}")
            self.status_prices.setToolTip(glossary.tip(STATUS_LABEL.get(s.status, ""), f"Retrieved {s.retrieved_at:%Y-%m-%d %H:%M}; data as of {s.as_of or 'n/a'}."))
        self.status_sec.setText(f"SEC: {STATUS_LABEL.get(ws.fundamentals.status, '').lower()}" if ws.fundamentals else "SEC: not loaded")
        self.status_sec.setToolTip(glossary.tip(STATUS_LABEL.get(ws.fundamentals.status, "")) if ws.fundamentals else (ws.fundamentals_error or ""))

    def _open_source(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._source_urls) and self._source_urls[row]:
            QDesktopServices.openUrl(QUrl(self._source_urls[row]))

    # -------------------------------------------------------------- watchlist
    def _refresh_watchlist(self) -> None:
        syms = self.settings.watchlist
        self.watch.fill([[s, "", ""] for s in syms])
        self.quote_runner.cancel_all()
        for s in syms:
            self.quote_runner.start(Job(0, _quote, s), self._watch_quote, lambda *_: None)

    def _watch_quote(self, _rid: int, result) -> None:
        sym, price, change = result
        for i in range(self.watch.rowCount()):
            if self.watch.item(i, 0) and self.watch.item(i, 0).text() == sym:
                self.watch.item(i, 1).setText(f"{price:,.2f}")
                item = self.watch.item(i, 2)
                if change is not None:
                    item.setText(f"{change:+.2%}")
                    item.setForeground(QColor(theme.UP if change >= 0 else theme.DOWN))

    def _watch_add(self) -> None:
        if not self.ws or not self.ws.history:  # only symbols that actually loaded
            self.notice.show_message("Load a symbol successfully before adding it to the watchlist.", "info")
            return
        if self.ws.symbol in self.settings.watchlist:
            return
        if len(self.settings.watchlist) >= 50:
            self.notice.show_message("The watchlist holds up to 50 symbols.", "warn")
            return
        self.settings.watchlist.append(self.ws.symbol)
        save_settings(self.settings)
        self._refresh_watchlist()

    def _watch_remove(self) -> None:
        row = self.watch.currentRow()
        if row < 0:
            self.notice.show_message("Select a symbol in the watchlist, then Remove.", "info")
            return
        sym = self.watch.item(row, 0).text()
        self.settings.watchlist = [s for s in self.settings.watchlist if s != sym]
        save_settings(self.settings)
        self._refresh_watchlist()

    # ------------------------------------------------------------------ search
    def _search(self) -> None:
        text = self.symbol.text().strip()
        if len(text) < 2:
            return
        rid = self._next("search")
        self.runner.start(Job(rid, yahoo.search, text), self._search_done, lambda *_: None)

    def _search_done(self, rid: int, results) -> None:
        if rid != self.ids["search"]:
            return
        self.completer_model.setStringList([f"{r['symbol']}  {r['name']}  {r['exchange']} {r['type']}".strip() for r in results])
        self.symbol.completer().complete()

    # -------------------------------------------------------------------- load
    def load(self, text: str, force: bool = False) -> None:
        try:
            sym = validation.ticker(text)
        except validation.ValidationError as exc:
            self.notice.show_message(str(exc), "error")
            return
        self.notice.clear()
        rid = self._next("load")
        # Stop and disown everything still running for the previous symbol. (First Version: a research note
        # or evaluation started for the old symbol kept running, left its buttons disabled, and showed its
        # progress under the new one.)
        for kind in ("research", "eval"):
            self._cancel(kind)
        for kind in ("model", "eval", "mc", "chain", "research", "filings", "bench"):
            self._next(kind)
        self.research.finish()
        self._previous = self.ws if self.ws and self.ws.history else None
        self.ws = Workspace(sym)
        self.option_chain = None
        self.research.reset()
        self.prediction.clear()
        self.mc_view.clear()
        self.symbol.setText(sym)
        self.quote.setText(f"{sym}  loading")
        self.statusBar().showMessage(f"Loading {sym}")
        bench = "DEMO-MKT" if demo.is_demo(sym) else self.settings.benchmark
        self.returns.bench.set_text(bench)
        self.runner.start(Job(rid, _fetch_prices, sym, bench, self.settings.risk_free_rate_pct / 100, force), self._prices_done, self._prices_failed)
        if demo.is_demo(sym) or self.settings.sec_contact_email:
            self.fundamentals.need_email(False)
            self.fundamentals.show_loading()
            self.runner.start(Job(rid, sec.fundamentals, sym, self.settings.sec_contact_email, force), self._fund_done, self._fund_failed)
        else:
            self.ws.fundamentals_error = "Set the SEC contact email (Fundamentals view or Settings > Data) to load filings."
            self.fundamentals.need_email(True)

    def _prices_failed(self, rid: int, message: str) -> None:
        if rid != self.ids["load"]:
            return
        failed = self.ws.symbol if self.ws else ""
        prev = getattr(self, "_previous", None)
        if prev is not None:
            # Keep showing the symbol that did load, rather than its charts under the failed symbol's name.
            # (First Version: the old charts stayed up while the window and the Add button used the new name.)
            self._next("load")  # SEC and news results for the failed symbol are ignored
            self.ws = prev
            self.symbol.setText(prev.symbol)
            self.prediction.render(prev)
            if prev.evaluation:
                self.prediction.render_evaluation(prev.evaluation)
            self.mc_view.render(prev)
            self.fundamentals.render(prev)
            self.filings.render(prev)
            self._show_quote(prev.history)
            self.notice.show_message(f"{message}  Still showing {prev.symbol}.", "error")
        else:
            self.quote.setText("")
            self.setWindowTitle(APP_NAME)
            self.status_prices.setText("")
            self.status_sec.setText("")
            self.fundamentals.render(self.ws)
            self.notice.show_message(message + "  For an offline trial, load DEMO.", "error")
        self.statusBar().showMessage(f"Could not load {failed}")

    def _prices_done(self, rid: int, loaded: Workspace) -> None:
        if not self._current("load", rid, loaded.symbol):
            return
        ws = self.ws
        ws.history, ws.benchmark, ws.risk_free, ws.risk_free_source = loaded.history, loaded.benchmark, loaded.risk_free, loaded.risk_free_source
        h = ws.history
        if h.symbol and h.symbol != ws.symbol:
            # Yahoo knows the symbol under another spelling (BRK.B is BRK-B there); use it from here on.
            ws.symbol = h.symbol
            self.symbol.setText(h.symbol)
        self._check_fund_applies()
        if not ws.is_demo:
            self.runner.start(Job(rid, yahoo.news, ws.symbol, 10, h.name), self._news_done, lambda *_: None)
        self._show_quote(h)
        self._range_changed(self.range_box.currentText())
        self.options.render(ws)
        if ws.fundamentals and self._check_fund_applies():
            self._compute_fundamentals()
        elif ws.fundamentals is None and ws.fundamentals_error:
            # SEC answered (with an error) before the prices did; draw that now. (First Version: the tab kept
            # the previous company's statements and a "Loading" notice forever.)
            self.fundamentals.render(ws)
            self.filings.render(ws)
        if self._pending_bench:
            bench, self._pending_bench = self._pending_bench, None
            self._benchmark_changed(bench)
        self.run_model(*self.prediction.selection())
        self.run_mc(self.mc_view.config() or montecarlo.MCConfig())
        self._refresh_sources()
        self.settings.last_symbol = ws.symbol
        save_settings(self.settings)
        self.statusBar().showMessage(f"{ws.symbol}: {len(h.bars):,} daily bars from {h.bars.index[0].date()} to {h.bars.index[-1].date()}")
        if h.attempts:
            self.notice.show_message(f"Prices came from {h.source.name} after: " + " ".join(h.attempts), "warn")

    def _show_quote(self, h) -> None:
        ch = h.day_change
        color = theme.UP if (ch or 0) >= 0 else theme.DOWN
        cur = f" {h.currency}" if h.currency else ""
        self.quote.setText(
            f"<span style='color:{theme.MUTED}'>{h.symbol}</span>  {h.price:,.2f}{cur}  <span style='color:{color}'>{(h.price - h.previous_close):+,.2f}  {ch:+.2%}</span>"
            if ch is not None
            else f"{h.symbol} {h.price:,.2f}{cur}"
        )
        self.setWindowTitle(f"{APP_NAME} - {h.symbol} {h.name}")

    def _check_fund_applies(self) -> bool:
        """Drop SEC statements for funds, indices and the like, whichever of prices or SEC arrived first."""
        ws = self.ws
        reason = sec.not_a_company(ws.history.instrument_type, ws.history.name) if ws and ws.history else None
        if not reason:
            return True
        ws.fundamentals, ws.fundamentals_error = None, reason
        ws.ratios, ws.piotroski, ws.altman, ws.dcf_inputs, ws.dcf, ws.implied_growth = {}, None, None, None, None, None
        self.fundamentals.render(ws)
        self.filings.render(ws)
        return False

    def _fund_done(self, rid: int, fund) -> None:
        if not self._current("load", rid):
            return
        self.ws.fundamentals = fund
        self.ws.fundamentals_error = None
        if self.ws.history:
            if self._check_fund_applies():
                self._compute_fundamentals()
            self._refresh_sources()
        else:
            self.filings.render(self.ws)

    def _fund_failed(self, rid: int, message: str) -> None:
        if not self._current("load", rid):
            return
        self.ws.fundamentals_error = message
        self.fundamentals.render(self.ws) if self.ws.history else None
        self.filings.render(self.ws)
        self._refresh_sources()

    def _compute_fundamentals(self) -> None:
        pipeline.compute_fundamentals(self.ws)
        self.fundamentals.render(self.ws)
        self.filings.render(self.ws)
        self._refresh_sources()

    def _dcf_changed(self, inp) -> None:
        if self.ws and self.ws.history:
            recompute(self.ws, inp)
            self.fundamentals.valuation.render(self.ws)

    def _email_saved(self, email: str) -> None:
        self.settings.sec_contact_email = email
        save_settings(self.settings)
        if self.ws:
            self.load(self.ws.symbol)

    def _news_done(self, rid: int, items) -> None:
        if self._current("load", rid):
            self.ws.news = items

    def _benchmark_changed(self, sym: str) -> None:
        if not self.ws or not self.ws.history:
            self._pending_bench = sym  # applied when the prices arrive
            return
        rid = self._next("bench")
        target = self.ws.symbol

        def done(r, hist):
            if r == self.ids["bench"] and self.ws and self.ws.symbol == target and self.ws.history is not None:
                self.ws.benchmark = hist
                self._compute_risk()
                self._refresh_sources()

        self.runner.start(Job(rid, prices.load_history, sym), done, lambda _r, msg: self.returns.show_error(f"Benchmark {sym}: {msg}"))

    # --------------------------------------------------------------- analysis
    def run_model(self, key: str, horizon: int, sims: int) -> None:
        if not self.ws or not self.ws.history:
            return
        rid = self._next("model")
        self.prediction.set_busy(True)
        self.runner.start(Job(rid, _run_model, self.ws.symbol, self.ws.history.bars, key, horizon, sims), self._model_done, self._model_failed)

    def _model_done(self, rid: int, result) -> None:
        self.prediction.set_busy(False)
        symbol, key, fc = result
        if not self._current("model", rid, symbol):
            return
        self.ws.forecast = fc
        self.prediction.render(self.ws)
        # Evaluate the model that produced this forecast, at its horizon, unless that is already done.
        # (First Version rebuilt the key from the version number, which only worked for FinLit models.)
        ev = self.ws.evaluation
        if ev is None or ev.horizon != fc.horizon_days or ev.model_key != key:
            self.run_evaluation(key, fc.horizon_days, 0)

    def _model_failed(self, rid: int, message: str) -> None:
        self.prediction.set_busy(False)
        if rid == self.ids["model"]:
            self.prediction.show_error(message)

    def run_evaluation(self, key: str, horizon: int, step: int) -> None:
        if not self.ws or not self.ws.history:
            return
        self._cancel("eval")
        rid = self._next("eval")
        self.prediction.set_eval_busy(True)
        job = Job(rid, _evaluate, self.ws.symbol, self.ws.history.bars, key, horizon, step, self.settings.transaction_cost_bps)
        self.jobs["eval"] = job
        self.runner.start(job, self._eval_done, self._eval_failed, lambda r, d, t: self.prediction.set_progress(d, t) if r == self.ids["eval"] else None)

    def _eval_done(self, rid: int, result) -> None:
        symbol, ev = result
        if not self._current("eval", rid, symbol):
            return
        self.prediction.set_eval_busy(False)
        self.ws.evaluation = ev
        self.prediction.render_evaluation(ev)

    def _eval_failed(self, rid: int, message: str) -> None:
        if rid != self.ids["eval"]:
            return
        self.prediction.set_eval_busy(False)
        self.prediction.show_eval_error(message)

    def run_mc(self, cfg) -> None:
        if not self.ws or not self.ws.history:
            return
        rid = self._next("mc")
        self.mc_view.set_busy(True)
        self.runner.start(Job(rid, _simulate, self.ws.symbol, self.ws.history, cfg), self._mc_done, self._mc_failed)

    def _mc_done(self, rid: int, result) -> None:
        self.mc_view.set_busy(False)
        symbol, mc, cal = result
        if not self._current("mc", rid, symbol):
            return
        self.ws.mc, self.ws.calibration = mc, cal
        self.mc_view.render(self.ws)

    def _mc_failed(self, rid: int, message: str) -> None:
        self.mc_view.set_busy(False)
        if rid == self.ids["mc"]:
            self.mc_view.show_error(message)

    def load_chain(self, expiry: str) -> None:
        if not self.ws or not self.ws.history:
            return
        if self.ws.is_demo:
            self.options.show_chain_error("DEMO has no listed options. Enter a contract manually.")
            return
        rid = self._next("chain")
        self.options.show_chain_error("Loading option chain from Yahoo Finance.")
        self.runner.start(Job(rid, yf_provider.option_chain, self.ws.symbol, expiry or None, self.ws.history.price), self._chain_done, lambda r, m: self.options.show_chain_error(m) if r == self.ids["chain"] else None)

    def _chain_done(self, rid: int, chain) -> None:
        if not self._current("chain", rid, chain.symbol):
            return
        self.option_chain = chain
        self.options.set_chain(chain)
        self._refresh_sources()

    def read_filings(self) -> None:
        ws = self.ws
        if not ws or not ws.fundamentals:
            return
        rid = self._next("filings")
        self.filings.set_busy(True)
        symbol = ws.symbol

        def done(r, result):
            self.filings.set_busy(False)
            if r == self.ids["filings"] and self.ws and self.ws.symbol == symbol:
                self.ws.filing_texts, self.ws.filing_problems = result
                self.filings.render(self.ws)
                self._refresh_sources()

        def failed(r, msg):
            self.filings.set_busy(False)
            self.filings.text_status.setText(msg)

        self.runner.start(Job(rid, filings.latest_reports, ws.fundamentals, self.settings.sec_contact_email, self.settings.filing_section_chars), done, failed)

    def _update_engine_label(self) -> None:
        try:
            engine = research.engine_for(self.settings)
            if engine:
                self.research.set_engine(engine.label)
            else:
                chosen = self.settings.ai_provider == "rules"
                self.research.set_engine("FinLit Pro rules engine" + (" (selected in Settings)" if chosen else " (no API key stored)"))
        except research.AnalysisError as exc:
            self.research.set_engine(str(exc))

    def run_research(self) -> None:
        if not self.ws or not self.ws.history:
            self.research.fail("Load a symbol first.")
            return
        self._cancel("research")
        rid = self._next("research")
        self.research.begin()
        job = Job(rid, _research, self.ws, self.settings)
        self.jobs["research"] = job
        self.runner.start(job, self._research_done, self._research_failed, lambda r, d, _t: self.research.progress(d) if r == self.ids["research"] else None)

    def _research_done(self, rid: int, result) -> None:
        symbol, note, reg, brief, texts, problems = result
        if not self._current("research", rid, symbol):
            return
        self.ws.filing_texts, self.ws.filing_problems = texts, problems
        self.research.show_note(note, reg, brief, symbol)
        self.filings.render(self.ws)
        self._refresh_sources()

    def _research_failed(self, rid: int, message: str) -> None:
        if rid == self.ids["research"]:
            self.research.fail(message)

    # --------------------------------------------------------------- file ops
    def import_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import daily prices", "", "CSV files (*.csv)")
        if not path:
            return
        default = self.ws.symbol if self.ws else ""
        sym, ok = QInputDialog.getText(self, "Symbol", "Symbol for these prices:", text=default)
        if not ok:
            return
        try:
            hist = prices.import_csv(path, sym)
        except (DataError, validation.ValidationError, OSError) as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        except (ValueError, TypeError) as exc:  # a file the parser could not make sense of
            QMessageBox.warning(self, "Import failed", f"That file could not be read as daily prices ({exc.__class__.__name__}). Save it as a CSV with Date and Close columns and import it again.")
            return
        self.statusBar().showMessage(f"Imported {len(hist.bars):,} rows for {hist.symbol}. They are used when online providers fail.")

    def export_report(self, path: str | None = None) -> str | None:
        ws = self.ws
        if not ws or not ws.history:
            self.notice.show_message("Load a symbol before exporting.", "info")
            return None
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Export report", f"{ws.symbol}_report.html", "HTML (*.html)")
        if not path:
            return None
        # Charts are chosen from what has been computed for this symbol, not from what a widget happens
        # to show. (First Version: a payoff chart left over from the previous symbol could be exported.)
        charts = {}
        for caption, widget, present in (
            ("Price", self.chart.view, ws.history is not None),
            ("Returns and drawdown", self.returns.growth, ws.risk is not None),
            ("Prediction model", self.prediction.fan, ws.forecast is not None),
            ("Monte Carlo", self.mc_view.fan, ws.mc is not None),
            ("Options payoff", self.options.payoff, not self.options.res_frame.isHidden()),
        ):
            if present:
                charts[caption] = report.widget_png(widget)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(report.build_html(ws, charts, self.research.html()))
        except OSError as exc:
            self.notice.show_message(f"Could not write the report ({exc.strerror}).", "error")
            return None
        self.statusBar().showMessage(f"Report saved to {path}")
        return path

    def export_csv(self) -> None:
        if not self.ws or not self.ws.history:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export prices", f"{self.ws.symbol}_prices.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(report.price_csv(self.ws))
        except OSError as exc:
            self.notice.show_message(f"Could not write the CSV ({exc.strerror}). Choose another folder or close the file if it is open elsewhere.", "error")
            return
        self.statusBar().showMessage(f"Prices saved to {path}")

    def open_settings(self) -> None:
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec() and dlg.result_settings:
            old = self.settings
            self.settings = dlg.result_settings
            save_settings(self.settings)
            self._update_engine_label()
            if self.ws and (old.sec_contact_email != self.settings.sec_contact_email or old.benchmark != self.settings.benchmark):
                self.load(self.ws.symbol)
            elif self.ws and self.ws.history and self.ws.risk_free_source is None and old.risk_free_rate_pct != self.settings.risk_free_rate_pct:
                # The live T-bill rate was unavailable, so the fallback in Settings is in use: apply the new one now.
                self.ws.risk_free = self.settings.risk_free_rate_pct / 100
                self._compute_risk()
                self.options.render(self.ws)

    def show_glossary(self, term: str = "") -> None:
        GlossaryDialog(self, term if isinstance(term, str) else "").exec()

    def show_data_help(self) -> None:
        QMessageBox.information(
            self,
            "Data sources and limitations",
            "Prices: Yahoo Finance public chart and options endpoints, which are unofficial, undocumented, intended for personal use, "
            "and may change or rate limit without notice. The app throttles to 2 requests per second, caches results, falls back to "
            "yfinance and then to the last cached copy, and accepts CSV imports.\n\n"
            "Fundamentals and filings: SEC EDGAR (data.sec.gov and sec.gov), official and free. The SEC requires a contact email in "
            "each request and allows up to 10 requests per second; the app uses at most 5.\n\n"
            "Every view lists its sources with status, as-of date and retrieval time. See docs/DATA_SOURCES.md for details.",
        )

    def about(self) -> None:
        QMessageBox.about(self, f"About {APP_NAME}", f"<b>{APP_NAME}</b> {__version__}<br>Personal stock research workstation.<br><br>{framing.PERSONAL_USE}")

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        for job in self.jobs.values():
            job.cancel()
        self.quote_runner.cancel_all()
        self.runner.cancel_all()
        self.quote_runner.wait(3000)
        self.runner.wait(3000)  # long jobs check for cancellation between steps
        self.settings.window_state = bytes(self.saveState().toHex()).decode()
        save_settings(self.settings)
        super().closeEvent(event)
