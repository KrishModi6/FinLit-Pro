"""Reusable widgets: KPI strips, notices, validated fields, tables, source lines."""

from __future__ import annotations

import html

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

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
        if tip:
            self.setToolTip(tip)

    def set(self, value: str, sub: str = "", tone_name: str | None = None) -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {TONES.get(tone_name, theme.TEXT)};")
        self.sub.setText(sub)


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

    def fill(self, rows: list[list], tones: list[list[str | None]] | None = None, align_right_from: int = 1, stretch_col: int | None = None, tips: list[list[str]] | None = None) -> None:
        self.setRowCount(len(rows))
        for j in range(self.columnCount()):
            head = self.horizontalHeaderItem(j)
            if head is not None:
                head.setTextAlignment((Qt.AlignRight if j >= align_right_from else Qt.AlignLeft) | Qt.AlignVCenter)
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                if j >= align_right_from:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if tones and tones[i][j]:
                    item.setForeground(QColor(TONES.get(tones[i][j], theme.TEXT)))
                if tips and tips[i][j]:
                    item.setToolTip(tips[i][j])
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
        if tip:
            self.edit.setToolTip(tip)
            self.title.setToolTip(tip)
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
