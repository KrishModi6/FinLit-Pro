"""Palette, Qt stylesheet, and matching chart styles.

A neutral graphite theme in the manner of trading and terminal software:
dense, low-contrast chrome, colour reserved for data (up, down, accent).
"""

from __future__ import annotations

import sys

import matplotlib

BG = "#0f1115"
PANEL = "#151920"
RAISED = "#1b2028"
BORDER = "#2a313b"
GRID = "#1f252e"
TEXT = "#d7dce2"
MUTED = "#8b949e"
ACCENT = "#3b82f6"
ACCENT_DIM = "#1e3a5f"
UP = "#26a269"
DOWN = "#e5534b"
WARN = "#d29922"
SERIES = [ACCENT, "#f0883e", "#a371f7", "#3fb950", "#db61a2", "#79c0ff", "#e3b341", "#8b949e"]

FONT_FAMILY = "Segoe UI" if sys.platform.startswith("win") else ("SF Pro Text" if sys.platform == "darwin" else "Inter, DejaVu Sans")
MONO_FAMILY = "Consolas" if sys.platform.startswith("win") else "Menlo, DejaVu Sans Mono"

STYLESHEET = f"""
* {{ color: {TEXT}; font-size: 12px; }}
QMainWindow, QDialog {{ background: {BG}; }}
QWidget#Page {{ background: {BG}; }}
QToolTip {{ background: {RAISED}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px; }}
QMenuBar {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; }}
QMenuBar::item {{ padding: 4px 10px; background: transparent; }}
QMenuBar::item:selected, QMenu::item:selected {{ background: {ACCENT_DIM}; }}
QMenu {{ background: {RAISED}; border: 1px solid {BORDER}; padding: 2px; }}
QMenu::item {{ padding: 4px 18px; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 3px 6px; }}
QToolBar {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; spacing: 6px; padding: 4px 6px; }}
QToolBar QLabel {{ color: {MUTED}; }}
QToolBar::separator {{ background: {BORDER}; width: 1px; margin: 3px 6px; }}
QStatusBar {{ background: {PANEL}; color: {MUTED}; border-top: 1px solid {BORDER}; }}
QStatusBar QLabel {{ color: {MUTED}; padding: 0 8px; }}
QDockWidget {{ color: {MUTED}; titlebar-close-icon: none; }}
QDockWidget::title {{ background: {PANEL}; padding: 5px 8px; border-bottom: 1px solid {BORDER}; text-transform: uppercase; }}
QFrame#Panel {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 3px; }}
QLabel#Section {{ color: {MUTED}; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
QLabel#Title {{ font-size: 15px; font-weight: 600; }}
QLabel#Muted {{ color: {MUTED}; }}
QLabel#Small {{ color: {MUTED}; font-size: 11px; }}
QLabel#Quote {{ font-size: 15px; font-weight: 600; font-family: {MONO_FAMILY}; }}
QLabel#Kpi {{ font-size: 16px; font-weight: 600; font-family: {MONO_FAMILY}; }}
QLabel#Verdict {{ font-size: 16px; font-weight: 700; }}
QFrame#Notice {{ background: {RAISED}; border: 1px solid {BORDER}; border-left: 3px solid {ACCENT}; }}
QFrame#Notice[level="error"] {{ border-left-color: {DOWN}; }}
QFrame#Notice[level="warn"] {{ border-left-color: {WARN}; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QPlainTextEdit, QTextBrowser {{
    background: {RAISED}; border: 1px solid {BORDER}; border-radius: 2px; padding: 3px 6px; selection-background-color: {ACCENT_DIM};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{ border-color: {ACCENT}; }}
QLineEdit[invalid="true"] {{ border-color: {DOWN}; }}
QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled {{ color: {MUTED}; background: {PANEL}; }}
QComboBox QAbstractItemView {{ background: {RAISED}; border: 1px solid {BORDER}; selection-background-color: {ACCENT_DIM}; }}
QPushButton {{ background: {RAISED}; border: 1px solid {BORDER}; border-radius: 2px; padding: 4px 12px; }}
QPushButton:hover {{ border-color: {MUTED}; }}
QPushButton:pressed {{ background: {BORDER}; }}
QPushButton:disabled {{ color: {MUTED}; }}
QPushButton#Primary {{ background: {ACCENT}; border-color: {ACCENT}; color: white; }}
QPushButton#Primary:hover {{ background: #4f8ff7; }}
QPushButton#Primary:disabled {{ background: {ACCENT_DIM}; border-color: {ACCENT_DIM}; color: {MUTED}; }}
QCheckBox::indicator, QRadioButton::indicator {{ width: 12px; height: 12px; }}
QTabWidget::pane {{ border: none; border-top: 1px solid {BORDER}; }}
QTabBar::tab {{ background: {PANEL}; color: {MUTED}; padding: 6px 14px; border: 1px solid {BORDER}; border-bottom: none; margin-right: -1px; }}
QTabBar::tab:selected {{ background: {BG}; color: {TEXT}; border-top: 2px solid {ACCENT}; }}
QTabBar::tab:hover {{ color: {TEXT}; }}
QTableWidget, QTableView, QListWidget {{ background: {PANEL}; alternate-background-color: {RAISED}; gridline-color: {GRID}; border: 1px solid {BORDER}; selection-background-color: {ACCENT_DIM}; }}
QHeaderView {{ background: {RAISED}; border: none; }}
QHeaderView::section {{ background: {RAISED}; color: {MUTED}; border: none; border-right: 1px solid {BORDER}; border-bottom: 1px solid {BORDER}; padding: 3px 6px; font-weight: 600; }}
QTableCornerButton::section {{ background: {RAISED}; border: none; }}
QScrollArea {{ border: none; background: {BG}; }}
QScrollBar:vertical {{ background: {BG}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER}; min-height: 24px; }}
QScrollBar:horizontal {{ background: {BG}; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; min-width: 24px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QSplitter::handle {{ background: {BORDER}; }}
QMainWindow::separator {{ background: {BORDER}; width: 1px; height: 1px; }}
QProgressBar {{ background: {RAISED}; border: 1px solid {BORDER}; height: 10px; text-align: center; color: {MUTED}; font-size: 10px; }}
QProgressBar::chunk {{ background: {ACCENT}; }}
"""


def apply_matplotlib_style() -> None:
    matplotlib.rcParams.update(
        {
            "figure.facecolor": PANEL,
            "axes.facecolor": PANEL,
            "savefig.facecolor": PANEL,
            "axes.edgecolor": BORDER,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": TEXT,
            "axes.titlesize": 10,
            "axes.titleweight": "semibold",
            "axes.titlelocation": "left",
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "text.color": TEXT,
            "legend.frameon": False,
            "legend.fontsize": 8.5,
            "legend.labelcolor": TEXT,
            "font.size": 9,
            "axes.prop_cycle": matplotlib.cycler(color=SERIES),
        }
    )


def apply_pyqtgraph_style() -> None:
    import pyqtgraph as pg

    # exitCleanup races Qt's own teardown under PySide6 and raises at exit.
    pg.setConfigOptions(antialias=True, background=PANEL, foreground=MUTED, exitCleanup=False)
