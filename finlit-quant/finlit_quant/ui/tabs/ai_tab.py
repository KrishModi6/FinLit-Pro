"""AI Analyst: a hedge-fund-style research memo, then follow-up questions."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from finlit_quant.data.models import NewsItem
from finlit_quant.ui.widgets import Banner, label, panel


class AITab(QWidget):
    generate_requested = Signal()
    ask_requested = Signal(str)
    stop_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        self.provider = label("", "Badge")
        self.generate_btn = QPushButton("Write research memo")
        self.generate_btn.setObjectName("Primary")
        self.generate_btn.clicked.connect(self.generate_requested.emit)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        self.stop_btn.setEnabled(False)
        self.brief_btn = QPushButton("Show data brief")
        self.brief_btn.setCheckable(True)
        self.brief_btn.toggled.connect(self._toggle_brief)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.output.toPlainText()))
        top.addWidget(label("Analyst:", "Muted"))
        top.addWidget(self.provider)
        top.addStretch(1)
        top.addWidget(self.brief_btn)
        top.addWidget(copy_btn)
        top.addWidget(self.stop_btn)
        top.addWidget(self.generate_btn)
        root.addLayout(top)

        self.banner = Banner()
        root.addWidget(self.banner)

        split = QSplitter(Qt.Horizontal)
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        self.output = QTextBrowser()
        self.output.setOpenExternalLinks(True)
        # Breathing room between memo sections; Qt applies this to the
        # blocks its Markdown importer creates.
        self.output.document().setDefaultStyleSheet("h2 { margin-top: 14px; margin-bottom: 4px; } li { margin-bottom: 3px; } p { margin-bottom: 6px; }")
        self.output.setStyleSheet("font-size: 14px; padding: 10px;")
        self.output.setPlaceholderText(
            "Press Write research memo. The analyst reads every number this app has computed for the ticker "
            "(prices, SEC fundamentals, risk, Monte Carlo, calibration, DCF, filings and headlines) and writes a memo "
            "in the style of a hedge fund research note.\n\nWith no API key set, a transparent rule-based analyst writes it instead."
        )
        left_lay.addWidget(self.output, 1)
        ask = QHBoxLayout()
        self.question = QLineEdit()
        self.question.setPlaceholderText("Ask a follow-up, e.g. What would make the bear case wrong?")
        self.question.returnPressed.connect(self._ask)
        self.ask_btn = QPushButton("Ask")
        self.ask_btn.clicked.connect(self._ask)
        ask.addWidget(self.question, 1)
        ask.addWidget(self.ask_btn)
        left_lay.addLayout(ask)
        self.ask_hint = label("", "Muted", wrap=True)
        left_lay.addWidget(self.ask_hint)
        split.addWidget(left)

        news_frame, news_lay = panel("Recent headlines", "From Yahoo Finance. Double-click to open. The analyst sees titles only.", fill=True)
        self.news = QListWidget()
        self.news.setWordWrap(True)
        self.news.itemDoubleClicked.connect(self._open_news)
        news_lay.addWidget(self.news)
        split.addWidget(news_frame)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 1)
        root.addWidget(split, 1)

        self._markdown = ""
        self._brief = ""
        self._streaming = False

    def _toggle_brief(self, on: bool) -> None:
        self.brief_btn.setText("Show memo" if on else "Show data brief")
        if on:
            self.output.setPlainText(self._brief or "Load a ticker first.")
        else:
            self.output.setMarkdown(self._markdown)

    def _ask(self) -> None:
        text = self.question.text().strip()
        if not text:
            self.ask_hint.setText("Type a question first, for example: How sensitive is the valuation to the discount rate?")
            return
        if len(text) > 2000:
            self.ask_hint.setText("That question is over 2,000 characters. Shorten it and ask again.")
            return
        self.ask_hint.setText("")
        self.question.clear()
        self.ask_requested.emit(text)

    def _open_news(self, item: QListWidgetItem) -> None:
        url = item.data(Qt.UserRole)
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def set_provider(self, text: str) -> None:
        self.provider.setText(text)

    def set_brief(self, brief: str) -> None:
        self._brief = brief

    def set_news(self, items: list[NewsItem]) -> None:
        self.news.clear()
        for n in items:
            when = n.published.strftime("%b %d") if n.published else ""
            item = QListWidgetItem(f"{n.title}\n{n.publisher}  {when}")
            item.setData(Qt.UserRole, n.url)
            item.setToolTip(n.url)
            self.news.addItem(item)
        if not items:
            self.news.addItem(QListWidgetItem("No headlines loaded."))

    def begin(self, heading: str | None = None) -> None:
        self._streaming = True
        self.banner.hide()
        self.brief_btn.setChecked(False)
        if heading:
            self._markdown += f"\n\n---\n\n**You:** {heading}\n\n"
        else:
            self._markdown = ""
        self.output.setMarkdown(self._markdown + "*Thinking...*")
        self.generate_btn.setEnabled(False)
        self.ask_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def append(self, text: str) -> None:
        self._markdown += text
        self.output.setMarkdown(self._markdown)
        bar = self.output.verticalScrollBar()
        bar.setValue(bar.maximum())

    def finish(self, served: str | None = None) -> None:
        self._streaming = False
        self.generate_btn.setEnabled(True)
        self.ask_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if served:
            self.provider.setText(served)

    def fail(self, message: str) -> None:
        self.finish()
        self.banner.show_message(message, "error")
        self.output.setMarkdown(self._markdown)

    def reset(self) -> None:
        self._markdown = ""
        self.output.clear()

    def markdown(self) -> str:
        return self._markdown
