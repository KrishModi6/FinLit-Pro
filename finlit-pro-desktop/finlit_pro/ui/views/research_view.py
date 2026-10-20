"""Research: a cited note on the filings and financial data."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QTextBrowser, QVBoxLayout, QWidget

from finlit_pro import framing
from finlit_pro.research.note import Note
from finlit_pro.research.render import to_html
from finlit_pro.research.sources import SourceRegistry
from finlit_pro.ui import theme
from finlit_pro.ui.widgets import Notice, hrow, label


class ResearchView(QWidget):
    run_requested = Signal()
    cancel_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        self.engine = label("", "Small")
        self.run_btn = QPushButton("Generate note")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self.run_requested.emit)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        self.brief_btn = QPushButton("Show brief")
        self.brief_btn.setCheckable(True)
        self.brief_btn.toggled.connect(self._toggle)
        copy = QPushButton("Copy")
        copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.view.toPlainText()))
        self.status = label("", "Small")
        root.addLayout(hrow(self.run_btn, self.cancel_btn, self.brief_btn, copy, 12, self.engine, self.status))
        for text in (framing.ANALYSIS_NOTE, framing.PERSONAL_USE):
            n = Notice()
            n.show_message(text)
            root.addWidget(n)
        self.notice = Notice()
        root.addWidget(self.notice)
        self.view = QTextBrowser()
        self.view.setOpenExternalLinks(True)
        self.view.setPlaceholderText(
            "Generate a research note from the loaded prices, SEC financial statements, the latest 10-K and 10-Q text, "
            "the prediction model and its evaluation, and the Monte Carlo results. Every fact is tied to a numbered source."
        )
        root.addWidget(self.view, 1)
        self._html = ""
        self._brief = ""

    def set_engine(self, text: str) -> None:
        self.engine.setText(f"Engine: {text}")

    def _toggle(self, on: bool) -> None:
        self.brief_btn.setText("Show note" if on else "Show brief")
        if on:
            self.view.setPlainText(self._brief or "Generate a note first.")
        else:
            self.view.setHtml(self._html)

    def begin(self) -> None:
        self.notice.clear()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status.setText("Preparing brief and loading filings")

    def progress(self, chars: int) -> None:
        self.status.setText(f"Receiving analysis ({chars:,} characters)")

    def finish(self) -> None:
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def show_note(self, note: Note, registry: SourceRegistry, brief: str, symbol: str) -> None:
        self.finish()
        self._brief = brief
        self._html = to_html(note, registry, symbol, {"text": theme.TEXT, "muted": theme.MUTED, "border": theme.BORDER, "link": theme.ACCENT})
        self.brief_btn.setChecked(False)
        self.view.setHtml(self._html)
        self.status.setText(f"{len(note.facts)} facts, {len(note.interpretation)} interpretations, {len(registry.entries)} sources in the brief")

    def fail(self, message: str) -> None:
        self.finish()
        self.status.setText("")
        self.notice.show_message(message, "error")

    def reset(self) -> None:
        self._html = self._brief = ""
        self.view.clear()
        self.status.setText("")
        self.notice.clear()

    def html(self) -> str:
        return self._html
