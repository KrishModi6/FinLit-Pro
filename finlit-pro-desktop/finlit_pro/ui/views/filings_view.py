"""Filings: the company's EDGAR filing index and the text of its latest reports."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QComboBox, QListWidget, QListWidgetItem, QPushButton, QSplitter, QTextBrowser, QVBoxLayout, QWidget

from finlit_pro.data.filings import FilingText
from finlit_pro.ui.widgets import Notice, SourceLine, Table, hrow, label, panel
from finlit_pro.workspace import Workspace


class FilingsView(QWidget):
    read_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        self.notice = Notice()
        root.addWidget(self.notice)
        split = QSplitter(Qt.Vertical)

        idx_frame, idx = panel("Filing index", "Double-click a filing to open its primary document on sec.gov.", fill=True)
        self.filter = QComboBox()
        self.filter.addItems(["Periodic and material (10-K, 10-Q, 8-K, proxy, ownership)", "All filings, including Form 4"])
        self.filter.currentIndexChanged.connect(lambda _: self._fill())
        self.insiders = label("", "Small")
        idx.addLayout(hrow(self.filter, self.insiders))
        self.table = Table(["Filed", "Form", "Report date", "Description", "Accession"])
        self.table.cellDoubleClicked.connect(self._open)
        idx.addWidget(self.table, 1)
        split.addWidget(idx_frame)

        txt_frame, txt = panel("Report text", "Business, Risk Factors and MD&A extracted from the latest 10-K, and MD&A and Risk Factors from a newer 10-Q. These excerpts are what the research note reads.", fill=True)
        self.read_btn = QPushButton("Load latest 10-K and 10-Q text")
        self.read_btn.clicked.connect(self.read_requested.emit)
        self.text_status = label("", "Small", wrap=True)
        txt.addLayout(hrow(self.read_btn, self.text_status))
        inner = QSplitter(Qt.Horizontal)
        self.sections = QListWidget()
        self.sections.currentItemChanged.connect(self._show_section)
        self.body = QTextBrowser()
        self.body.setOpenExternalLinks(True)
        inner.addWidget(self.sections)
        inner.addWidget(self.body)
        inner.setStretchFactor(1, 4)
        txt.addWidget(inner, 1)
        self.text_source = SourceLine()
        txt.addWidget(self.text_source)
        split.addWidget(txt_frame)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 3)
        root.addWidget(split, 1)
        self.ws: Workspace | None = None
        self._rows = []
        self._texts: dict[str, tuple[FilingText, str]] = {}

    def render(self, ws: Workspace) -> None:
        self.ws = ws
        f = ws.fundamentals
        if f is None:
            self.notice.show_message(ws.fundamentals_error or "No SEC filings loaded for this security.", "warn")
            self.table.setRowCount(0)
            self.read_btn.setEnabled(False)
            return
        self.notice.clear()
        self.read_btn.setEnabled(not ws.is_demo)
        self._fill()
        self._fill_texts()

    def _fill(self) -> None:
        f = self.ws.fundamentals if self.ws else None
        if f is None:
            return
        self._rows = f.key_filings() if self.filter.currentIndex() == 0 else f.filings
        self.table.fill([[x.filed, x.form, x.report_date, x.description, x.accession] for x in self._rows], align_right_from=99, stretch_col=3)
        self.insiders.setText(f"{f.insider_filings(90)} Form 4 (insider transaction) filings in the last 90 days")

    def _open(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._rows):
            url = self._rows[row].url or self._rows[row].index_url
            if url:
                QDesktopServices.openUrl(QUrl(url))

    def set_busy(self, busy: bool) -> None:
        self.read_btn.setEnabled(not busy)
        if busy:
            self.text_status.setText("Downloading filing documents from SEC EDGAR.")

    def _fill_texts(self) -> None:
        ws = self.ws
        self.sections.clear()
        self._texts = {}
        if not ws or not ws.filing_texts:
            self.body.clear()
            problems = " ".join(ws.filing_problems) if ws else ""
            self.text_status.setText(problems or "Not loaded. The research note loads them automatically.")
            return
        for ft in ws.filing_texts:
            for name, body in ft.sections.items():
                key = f"{ft.filing.form} {ft.filing.report_date}: {name}"
                self._texts[key] = (ft, body)
                item = QListWidgetItem(key)
                item.setToolTip(f"Filed {ft.filing.filed}, {ft.full_chars[name]:,} characters" + (", truncated" if ft.truncated[name] else ""))
                self.sections.addItem(item)
        notes = [n for ft in ws.filing_texts for n in ft.notes] + ws.filing_problems
        self.text_status.setText(" ".join(notes) if notes else f"{self.sections.count()} sections loaded.")
        self.sections.setCurrentRow(0)

    def _show_section(self, item: QListWidgetItem | None, _prev=None) -> None:
        if item is None or item.text() not in self._texts:
            return
        ft, body = self._texts[item.text()]
        name = item.text().split(": ", 1)[1]
        cut = f" Showing {len(body):,} of {ft.full_chars[name]:,} characters." if ft.truncated[name] else ""
        self.body.setPlainText(body)
        self.text_source.set_sources([ft.source])
        self.text_source.setText(self.text_source.text() + cut)
