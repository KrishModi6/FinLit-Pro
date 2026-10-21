"""Help > Glossary: every term the app uses, searchable."""

from __future__ import annotations

import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QSplitter, QTextBrowser, QTreeWidget, QTreeWidgetItem, QVBoxLayout

from finlit_pro import glossary
from finlit_pro.ui.widgets import label


class GlossaryDialog(QDialog):
    def __init__(self, parent=None, term: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Glossary")
        self.resize(860, 560)
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search terms, for example Sharpe, bullish, delta, P/E")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        top.addWidget(self.search, 1)
        self.count = label("", "Small")
        top.addWidget(self.count)
        root.addLayout(top)
        root.addWidget(label("Hover over any label, value, column heading or verdict in FinLit Pro to see its definition. Every definition is listed here.", "Small", wrap=True))

        split = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.currentItemChanged.connect(self._show)
        split.addWidget(self.tree)
        self.body = QTextBrowser()
        self.body.setOpenExternalLinks(False)
        split.addWidget(self.body)
        split.setSizes([300, 560])
        root.addWidget(split, 1)

        self._items: list[tuple[QTreeWidgetItem, glossary.Term]] = []
        for category, terms in glossary.by_category().items():
            if not terms:
                continue
            parent_item = QTreeWidgetItem([category])
            parent_item.setFlags(parent_item.flags() & ~Qt.ItemIsSelectable)
            self.tree.addTopLevelItem(parent_item)
            for t in terms:
                child = QTreeWidgetItem([t.name])
                child.setData(0, Qt.UserRole, t)
                parent_item.addChild(child)
                self._items.append((child, t))
        self.tree.expandAll()
        self.search.setText(term)
        self._filter(term)
        if not term and self._items:
            self.tree.setCurrentItem(self._items[0][0])

    def _filter(self, text: str) -> None:
        q = text.strip().casefold()
        shown = 0
        first = None
        for item, t in self._items:
            hay = " ".join((t.name, *t.aliases, t.meaning, t.reading)).casefold()
            match = not q or q in hay
            item.setHidden(not match)
            if match:
                shown += 1
                # Prefer a term whose name or alias matches over one that only mentions the word.
                if first is None or (q and any(q in a.casefold() for a in (t.name, *t.aliases)) and not any(q in a.casefold() for a in (first[1].name, *first[1].aliases))):
                    first = (item, t)
        for i in range(self.tree.topLevelItemCount()):
            cat = self.tree.topLevelItem(i)
            cat.setHidden(all(cat.child(j).isHidden() for j in range(cat.childCount())))
        self.count.setText(f"{shown} of {len(self._items)} terms")
        if first is not None:
            self.tree.setCurrentItem(first[0])
        else:
            self.body.setHtml("<p>No term matches. Try a shorter word.</p>")

    def _show(self, item: QTreeWidgetItem | None, _prev=None) -> None:
        t = item.data(0, Qt.UserRole) if item else None
        if t is None:
            return
        e = html.escape
        parts = [f"<h3>{e(t.name)}</h3>", f"<p class='muted'>{e(t.category)}</p>", f"<p>{e(t.meaning)}</p>"]
        if t.reading:
            parts.append(f"<p><b>How to read it.</b> {e(t.reading)}</p>")
        if t.aliases:
            parts.append(f"<p class='muted'>Also shown as: {e(', '.join(t.aliases))}</p>")
        self.body.setHtml("".join(parts))
