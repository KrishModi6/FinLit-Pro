"""Reusable widgets: KPI strips, notices, validated fields, tables, source lines.

Every caption, table row, column heading and verdict these widgets show looks
itself up in the glossary, so hovering over it explains what it means. Views
add a note about the specific number by passing `tip`.
"""

from __future__ import annotations

import html

import numpy as np
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from finlit_pro import glossary
from finlit_pro.data.models import STATUS_LABEL, Source
from finlit_pro.ui import theme

TONES = {"up": theme.UP, "down": theme.DOWN, "warn": theme.WARN, "accent": theme.ACCENT, "muted": theme.MUTED, None: theme.TEXT, "neutral": theme.TEXT}


def label(text: str = "", name: str | None = None, wrap: bool = False, selectable: bool = True) -> QLabel:
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    w.setWordWrap(wrap)
    if selectable:
        w.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
    w.setOpenExternalLinks(True)
    return w


def tone(value, positive_is_good: bool = True) -> str:
    if value is None or not np.isfinite(value) or value == 0:
        return "neutral"
    return "up" if (value > 0) == positive_is_good else "down"


class Kpi(QWidget):
    """A small caption above a value, as in a quote header."""

    def __init__(self, caption: str, tip: str = "") -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 14, 0)
        lay.setSpacing(1)
        self.caption = label(caption, "Small")
        self.value = label("n/a", "Kpi")
        self.sub = label("", "Small")
        lay.addWidget(self.caption)
        lay.addWidget(self.value)
        lay.addWidget(self.sub)
        text = glossary.tip(caption, tip)
        if text:
            self.setToolTip(text)

    def set(self, value: str, sub: str = "", tone_name: str | None = None) -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {TONES.get(tone_name, theme.TEXT)};")
        self.sub.setText(sub)
        # A value that is itself a term (a verdict such as STRONG SELL) explains itself.
        term = glossary.lookup(value) if value and not any(ch.isdigit() for ch in value) else None
        self.value.setToolTip(glossary.tip_for(term) if term else "")


class KpiStrip(QFrame):
    def __init__(self, columns: int = 8) -> None:
        super().__init__()
        self.setObjectName("Panel")
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(10, 8, 10, 8)
        self.grid.setHorizontalSpacing(8)
        self.grid.setVerticalSpacing(8)
        self.columns = columns
        self.items: dict[str, Kpi] = {}

    def kpi(self, key: str, caption: str = "", tip: str = "") -> Kpi:
        if key not in self.items:
            k = Kpi(caption, tip)
            n = len(self.items)
            self.grid.addWidget(k, n // self.columns, n % self.columns)
            self.items[key] = k
        return self.items[key]


class Notice(QFrame):
    """A one-line status or error with a coloured edge. Hidden when empty."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Notice")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        self.text = label("", wrap=True)
        lay.addWidget(self.text)
        self.hide()

    def show_message(self, message: str, level: str = "info") -> None:
        self.setProperty("level", level)
        self.style().unpolish(self)
        self.style().polish(self)
        self.text.setText(message)
        self.setVisible(bool(message))

    def clear(self) -> None:
        self.text.setText("")
        self.hide()


def source_html(sources: list[Source]) -> str:
    """'Source: Yahoo Finance chart API (Live, as of 2026-10-20, retrieved 22:05)' with links."""
    parts = []
    for s in sources:
        name = html.escape(s.name)
        if s.url:
            name = f'<a href="{html.escape(s.url)}" style="color:{theme.ACCENT}; text-decoration:none;">{name}</a>'
        bits = [STATUS_LABEL.get(s.status, s.status)]
        if s.as_of:
            bits.append(f"as of {html.escape(s.as_of)}")
        bits.append(f"retrieved {s.retrieved_at:%Y-%m-%d %H:%M}")
        if s.detail:
            bits.append(html.escape(s.detail))
        parts.append(f"{name} ({', '.join(bits)})")
    return "Source: " + "; ".join(parts) if parts else ""


class SourceLine(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Small")
        self.setWordWrap(True)
        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)

    def set_sources(self, sources: list[Source]) -> None:
        self.setText(source_html([s for s in sources if s]))


class Table(QTableWidget):
    def __init__(self, headers: list[str] | None = None) -> None:
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(22)
        self.setShowGrid(False)
        self.setWordWrap(False)
        if headers:
            self.set_headers(headers)

    def set_headers(self, headers: list[str]) -> None:
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._header_tips()

    def _header_tips(self) -> None:
        for j in range(self.columnCount()):
            head = self.horizontalHeaderItem(j)
            if head is not None and not head.toolTip():
                head.setToolTip(glossary.tip(head.text()))

    @staticmethod
    def _cell_tip(text: str, column: int) -> str:
        """The first column names the row (a metric, a test, a component); other cells explain only exact terms."""
        if not text or (column > 0 and (len(text) > 40 or any(ch.isdigit() for ch in text))):
            return ""
        return glossary.tip(text)

    def fill(self, rows: list[list], tones: list[list[str | None]] | None = None, align_right_from: int = 1, stretch_col: int | None = None, tips: list[list[str]] | None = None) -> None:
        self.setRowCount(len(rows))
        self._header_tips()
        for j in range(self.columnCount()):
            head = self.horizontalHeaderItem(j)
            if head is not None:
                head.setTextAlignment((Qt.AlignRight if j >= align_right_from else Qt.AlignLeft) | Qt.AlignVCenter)
        for i, row in enumerate(rows):
            # A row named after a term (a metric, a test, a statement line) lends its definition to every
            # value in the row, so hovering a number explains it too.
            row_label = "" if not row or row[0] is None else str(row[0])
            row_term = glossary.lookup(row_label)
            for j, value in enumerate(row):
                text = "" if value is None else str(value)
                item = QTableWidgetItem(text)
                if j >= align_right_from:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if tones and tones[i][j]:
                    item.setForeground(QColor(TONES.get(tones[i][j], theme.TEXT)))
                explicit = tips[i][j] if tips and j < len(tips[i]) else ""
                if j == 0:
                    tip = glossary.tip(text, explicit) if explicit else self._cell_tip(text, 0)
                else:
                    tip = self._cell_tip(text, j) if not explicit else ""
                    if not tip and row_term is not None:
                        tip = glossary.tip_for(row_term, explicit)
                    tip = tip or explicit
                if tip:
                    item.setToolTip(tip)
                self.setItem(i, j, item)
        self.resizeColumnsToContents()
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        if stretch_col is None:
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        else:
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            header.setSectionResizeMode(stretch_col, QHeaderView.Stretch)

    def fit_height(self, max_rows: int = 30) -> None:
        rows = min(self.rowCount(), max_rows)
        h = self.horizontalHeader().height() + sum(self.rowHeight(i) for i in range(rows)) + 4
        self.setMinimumHeight(h)
        self.setMaximumHeight(h if self.rowCount() <= max_rows else 16777215)


class Field(QWidget):
    """A caption above a line edit, with an inline error under it."""

    def __init__(self, title: str, value: str = "", placeholder: str = "", tip: str = "", width: int | None = None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        self.title = label(title, "Small")
        self.edit = QLineEdit(value)
        self.edit.setPlaceholderText(placeholder)
        text = glossary.tip(title, tip)
        if text:
            self.edit.setToolTip(text)
            self.title.setToolTip(text)
        if width:
            self.edit.setFixedWidth(width)
        self.error = label("", wrap=True)
        self.error.setStyleSheet(f"color: {theme.DOWN}; font-size: 11px;")
        self.error.hide()
        self.edit.textEdited.connect(lambda _: self.clear_error())
        lay.addWidget(self.title)
        lay.addWidget(self.edit)
        lay.addWidget(self.error)
        lay.addStretch(1)  # keeps captions aligned in a grid when a neighbour shows an error

    def text(self) -> str:
        return self.edit.text()

    def set_text(self, value: str) -> None:
        self.edit.setText(value)

    def set_error(self, message: str) -> None:
        self.edit.setProperty("invalid", True)
        self.edit.style().unpolish(self.edit)
        self.edit.style().polish(self.edit)
        self.error.setText(message)
        self.error.show()

    def clear_error(self) -> None:
        if self.edit.property("invalid"):
            self.edit.setProperty("invalid", False)
            self.edit.style().unpolish(self.edit)
            self.edit.style().polish(self.edit)
        self.error.hide()


def section(text: str) -> QLabel:
    return label(text, "Section")


def panel(title: str | None = None, sub: str | None = None, fill: bool = False) -> tuple[QFrame, QVBoxLayout]:
    """A bordered group. `fill=True` lets the content take the full height."""
    frame = QFrame()
    frame.setObjectName("Panel")
    outer = QVBoxLayout(frame)
    outer.setContentsMargins(10, 8, 10, 10)
    lay = QVBoxLayout()
    lay.setSpacing(6)
    outer.addLayout(lay, 1 if fill else 0)
    if not fill:
        outer.addStretch(1)
    if title:
        lay.addWidget(section(title))
    if sub:
        lay.addWidget(label(sub, "Small", wrap=True))
    return frame, lay


def scroll_page() -> tuple[QScrollArea, QVBoxLayout]:
    area = QScrollArea()
    area.setWidgetResizable(True)
    inner = QWidget()
    inner.setObjectName("Page")
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(10, 10, 10, 14)
    lay.setSpacing(10)
    area.setWidget(inner)
    return area, lay


def hrow(*widgets, stretch_last: bool = True, spacing: int = 8) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(spacing)
    for w in widgets:
        if isinstance(w, int):
            row.addSpacing(w)
        else:
            row.addWidget(w)
    if stretch_last:
        row.addStretch(1)
    return row


def install_tooltips(root: QWidget) -> int:
    """Give every caption, checkbox, button, list choice and tab under `root` its glossary definition.

    Widgets that already carry a tooltip keep it. Returns how many tooltips were added.
    """
    added = 0

    def put(widget, text: str) -> None:
        nonlocal added
        if not widget.toolTip():
            tip = glossary.tip(text)
            if tip:
                widget.setToolTip(tip)
                added += 1

    for w in root.findChildren(QLabel):
        if w.textFormat() != Qt.RichText and w.objectName() not in ("Kpi",):
            put(w, w.text())
    for w in root.findChildren(QAbstractButton):
        put(w, w.text())
        if not w.toolTip() and w.text() in glossary.ACTIONS:
            w.setToolTip(glossary.ACTIONS[w.text()])
            added += 1
    for box in root.findChildren(QComboBox):
        for i in range(box.count()):
            if not box.itemData(i, Qt.ToolTipRole):
                tip = glossary.tip(box.itemText(i))
                if tip:
                    box.setItemData(i, tip, Qt.ToolTipRole)
                    added += 1
        if not box.toolTip() and box.count():
            box.currentIndexChanged.connect(lambda _i, b=box: b.setToolTip(b.itemData(b.currentIndex(), Qt.ToolTipRole) or ""))
            box.setToolTip(box.itemData(box.currentIndex(), Qt.ToolTipRole) or "")
    for tabs in root.findChildren(QTabWidget):
        for i in range(tabs.count()):
            if not tabs.tabToolTip(i):
                tip = glossary.tip(tabs.tabText(i))
                if tip:
                    tabs.setTabToolTip(i, tip)
                    added += 1
    return added


class TipBrowser(QTextBrowser):
    """A text browser that shows the hover title of the word under the mouse.

    Qt reads an HTML `title` attribute into the text's format but only shows it
    for anchors; the research note puts definitions on plain words too.
    """

    def viewportEvent(self, event) -> bool:  # noqa: N802 - Qt naming
        if event.type() == QEvent.ToolTip:
            text = self.cursorForPosition(event.pos()).charFormat().toolTip()
            if text:
                QToolTip.showText(event.globalPos(), f"<table width='380'><tr><td>{html.escape(text)}</td></tr></table>", self.viewport())
            else:
                QToolTip.hideText()
                event.ignore()
            return True
        return super().viewportEvent(event)
