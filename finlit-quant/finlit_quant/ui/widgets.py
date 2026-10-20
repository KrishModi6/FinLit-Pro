"""Small reusable widgets: stat cards, banners, tables, labelled fields."""

from __future__ import annotations

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
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from finlit_quant.ui import theme

TONES = {"good": theme.ACCENT, "bad": theme.RED, "warn": theme.AMBER, "info": theme.SKY, "neutral": theme.TEXT}


def label(text: str = "", name: str | None = None, wrap: bool = False) -> QLabel:
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    w.setWordWrap(wrap)
    w.setTextInteractionFlags(Qt.TextSelectableByMouse)
    return w


def tone_for(value: float | None, good_if_positive: bool = True) -> str:
    if value is None or not np.isfinite(value) or value == 0:
        return "neutral"
    return "good" if (value > 0) == good_if_positive else "bad"


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "n/a", sub: str = "", tone: str = "neutral", tip: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(2)
        self.title = label(title, "CardLabel")
        self.value = label(value, "CardValue")
        self.sub = label(sub, "CardSub", wrap=True)
        lay.addWidget(self.title)
        lay.addWidget(self.value)
        lay.addWidget(self.sub)
        if tip:
            self.setToolTip(tip)
        self.set(value, sub, tone)

    def set(self, value: str, sub: str | None = None, tone: str = "neutral") -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {TONES.get(tone, theme.TEXT)};")
        if sub is not None:
            self.sub.setText(sub)
            self.sub.setVisible(bool(sub))


class CardGrid(QWidget):
    def __init__(self, columns: int = 4) -> None:
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)
        self.columns = columns
        self.cards: dict[str, StatCard] = {}

    def card(self, key: str, title: str, tip: str = "") -> StatCard:
        if key not in self.cards:
            c = StatCard(title, tip=tip)
            n = len(self.cards)
            self.grid.addWidget(c, n // self.columns, n % self.columns)
            self.cards[key] = c
        return self.cards[key]


class Banner(QFrame):
    """An inline message: what happened and what to do about it."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Banner")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 9, 12, 9)
        self.text = label("", wrap=True)
        self.close_btn = QPushButton("Dismiss")
        self.close_btn.setObjectName("Chip")
        self.close_btn.clicked.connect(self.hide)
        lay.addWidget(self.text, 1)
        lay.addWidget(self.close_btn, 0, Qt.AlignTop)
        self.hide()

    def show_message(self, message: str, level: str = "error") -> None:
        self.setProperty("level", level)
        self.style().unpolish(self)
        self.style().polish(self)
        self.text.setText(message)
        self.show()


class Table(QTableWidget):
    def __init__(self, headers: list[str] | None = None) -> None:
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setShowGrid(False)
        self.setWordWrap(False)
        if headers:
            self.set_headers(headers)

    def set_headers(self, headers: list[str]) -> None:
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def fill(
        self,
        rows: list[list],
        tones: list[list[str | None]] | None = None,
        align_right_from: int = 1,
        stretch_col: int | None = None,
    ) -> None:
        """Fill the table. Numeric columns share the spare width unless
        `stretch_col` names the one text column that should take it all."""
        self.setRowCount(len(rows))
        for j in range(self.columnCount()):
            head = self.horizontalHeaderItem(j)
            if head is not None:
                # Headers line up with their values: numbers right, text left.
                head.setTextAlignment((Qt.AlignRight if j >= align_right_from else Qt.AlignLeft) | Qt.AlignVCenter)
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                if j >= align_right_from:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if tones and tones[i][j]:
                    item.setForeground(QColor(TONES.get(tones[i][j], theme.TEXT)))
                self.setItem(i, j, item)
        self.resizeColumnsToContents()
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        if stretch_col is None:
            # Share the width out evenly so numbers sit under their headers
            # instead of the last column swallowing all the slack.
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        else:
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            header.setSectionResizeMode(stretch_col, QHeaderView.Stretch)

    def fit_height(self, max_rows: int = 30) -> None:
        rows = min(self.rowCount(), max_rows)
        h = self.horizontalHeader().height() + sum(self.rowHeight(i) for i in range(rows)) + 6
        self.setMinimumHeight(h)
        self.setMaximumHeight(h if self.rowCount() <= max_rows else 16777215)


class Field(QWidget):
    """A label above a line edit, with an inline error line under it."""

    def __init__(self, title: str, value: str = "", placeholder: str = "", tip: str = "", width: int | None = None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        self.title = label(title, "Muted")
        self.edit = QLineEdit(value)
        self.edit.setPlaceholderText(placeholder)
        if tip:
            self.edit.setToolTip(tip)
            self.title.setToolTip(tip)
        if width:
            self.edit.setFixedWidth(width)
        self.error = label("", wrap=True)
        self.error.setStyleSheet(f"color: {theme.RED}; font-size: 11px;")
        self.error.hide()
        self.edit.textEdited.connect(lambda _: self.clear_error())
        lay.addWidget(self.title)
        lay.addWidget(self.edit)
        lay.addWidget(self.error)

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


def panel(title: str | None = None, sub: str | None = None, fill: bool = False) -> tuple[QFrame, QVBoxLayout]:
    """A titled card. `fill=True` lets the content grow to the panel's full height."""
    frame = QFrame()
    frame.setObjectName("Panel")
    outer = QVBoxLayout(frame)
    outer.setContentsMargins(14, 12, 14, 14)
    lay = QVBoxLayout()
    lay.setSpacing(8)
    outer.addLayout(lay, 1 if fill else 0)
    if not fill:
        # Content sits at the top: a panel stretched by a taller neighbour in the
        # same row leaves its spare space at the bottom, not between its lines.
        outer.addStretch(1)
    if title:
        lay.addWidget(label(title, "H2"))
    if sub:
        lay.addWidget(label(sub, "Muted", wrap=True))
    return frame, lay


def scroll_page() -> tuple[QScrollArea, QVBoxLayout]:
    """A vertically scrolling page with a padded column layout."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    inner = QWidget()
    inner.setObjectName("Page")
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(18, 16, 18, 24)
    lay.setSpacing(14)
    area.setWidget(inner)
    return area, lay


def chip(text: str, checkable: bool = True) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("Chip")
    b.setCheckable(checkable)
    b.setCursor(Qt.PointingHandCursor)
    return b
