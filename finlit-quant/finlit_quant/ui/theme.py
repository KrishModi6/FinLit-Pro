"""Colours, the Qt stylesheet, and the matching matplotlib style.

One palette drives both, so a chart never looks pasted onto the window. The
accent is FinLit Pro's emerald.
"""

from __future__ import annotations

import matplotlib

BG = "#0b1220"
PANEL = "#111a2e"
PANEL_2 = "#16213a"
BORDER = "#24314f"
TEXT = "#e6ebf5"
MUTED = "#8a97b1"
ACCENT = "#10b981"
ACCENT_SOFT = "#0f3d33"
SKY = "#38bdf8"
RED = "#f43f5e"
AMBER = "#f59e0b"
PURPLE = "#a78bfa"
GRID = "#1c2742"

SERIES = [ACCENT, SKY, AMBER, PURPLE, RED, "#f472b6", "#94a3b8", "#facc15"]

STYLESHEET = f"""
* {{ color: {TEXT}; font-size: 13px; }}
QMainWindow, QDialog, QWidget#Page {{ background: {BG}; }}
QWidget {{ background: transparent; }}
QToolTip {{ background: {PANEL_2}; color: {TEXT}; border: 1px solid {BORDER}; padding: 6px; }}
QFrame#Card, QFrame#Panel {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
QLabel#CardLabel {{ color: {MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
QLabel#CardValue {{ font-size: 20px; font-weight: 700; }}
QLabel#CardSub {{ color: {MUTED}; font-size: 11px; }}
QLabel#H1 {{ font-size: 22px; font-weight: 800; }}
QLabel#H2 {{ font-size: 15px; font-weight: 700; }}
QLabel#Muted {{ color: {MUTED}; }}
QLabel#Price {{ font-size: 26px; font-weight: 800; }}
QLabel#Badge {{ background: {PANEL_2}; border: 1px solid {BORDER}; border-radius: 9px; padding: 2px 9px; color: {MUTED}; font-size: 11px; }}
QLabel#BadgeWarn {{ background: #3a2a0a; border: 1px solid #6b4e10; border-radius: 9px; padding: 2px 9px; color: {AMBER}; font-size: 11px; }}
QFrame#Banner {{ border-radius: 8px; }}
QFrame#Banner[level="error"] {{ background: #3b1020; border: 1px solid #7a1d3a; }}
QFrame#Banner[level="warn"] {{ background: #3a2a0a; border: 1px solid #6b4e10; }}
QFrame#Banner[level="info"] {{ background: #0e2a3a; border: 1px solid #16506e; }}
QFrame#Banner[level="good"] {{ background: {ACCENT_SOFT}; border: 1px solid #16624f; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit, QTextBrowser {{
    background: {PANEL_2}; border: 1px solid {BORDER}; border-radius: 7px; padding: 6px 8px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{ border: 1px solid {ACCENT}; }}
QLineEdit[invalid="true"] {{ border: 1px solid {RED}; }}
QComboBox QAbstractItemView {{ background: {PANEL_2}; border: 1px solid {BORDER}; selection-background-color: {ACCENT_SOFT}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QPushButton {{ background: {PANEL_2}; border: 1px solid {BORDER}; border-radius: 7px; padding: 7px 14px; font-weight: 600; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton:pressed {{ background: {BORDER}; }}
QPushButton:disabled {{ color: {MUTED}; border-color: {GRID}; }}
QPushButton#Primary {{ background: {ACCENT}; color: #04110c; border: none; }}
QPushButton#Primary:hover {{ background: #34d399; }}
QPushButton#Primary:disabled {{ background: {ACCENT_SOFT}; color: {MUTED}; }}
QPushButton#Chip {{ padding: 4px 10px; border-radius: 12px; font-weight: 600; }}
QPushButton#Chip:checked {{ background: {ACCENT_SOFT}; border-color: {ACCENT}; color: {ACCENT}; }}
QCheckBox {{ spacing: 6px; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; color: {MUTED}; padding: 10px 16px; border-bottom: 2px solid transparent; font-weight: 600; }}
QTabBar::tab:selected {{ color: {TEXT}; border-bottom: 2px solid {ACCENT}; }}
QTabBar::tab:hover {{ color: {TEXT}; }}
QTableWidget, QTableView {{ background: {PANEL}; alternate-background-color: {PANEL_2}; gridline-color: {GRID}; border: 1px solid {BORDER}; border-radius: 8px; }}
QHeaderView::section {{ background: {PANEL_2}; color: {MUTED}; border: none; border-bottom: 1px solid {BORDER}; padding: 6px; font-weight: 600; }}
QTableWidget::item:selected {{ background: {ACCENT_SOFT}; }}
QListWidget {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 8px; }}
QListWidget::item {{ padding: 7px 6px; border-bottom: 1px solid {GRID}; }}
QListWidget::item:selected {{ background: {ACCENT_SOFT}; }}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{ background: {BG}; width: 10px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 30px; }}
QScrollBar:horizontal {{ background: {BG}; height: 10px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QWidget#Toolbar {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; }}
QMainWindow::separator {{ background: {BORDER}; width: 1px; height: 1px; }}
QStatusBar {{ background: {PANEL}; color: {MUTED}; border-top: 1px solid {BORDER}; }}
QDockWidget {{ color: {MUTED}; }}
QDockWidget::title {{ background: {PANEL}; padding: 8px; }}
QMenuBar {{ background: {PANEL}; }}
QMenuBar::item:selected, QMenu::item:selected {{ background: {ACCENT_SOFT}; }}
QMenu {{ background: {PANEL_2}; border: 1px solid {BORDER}; }}
QProgressBar {{ background: {PANEL_2}; border: 1px solid {BORDER}; border-radius: 4px; height: 6px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QSplitter::handle {{ background: {BORDER}; }}
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
            "axes.titleweight": "bold",
            "axes.titlesize": 11,
            "axes.titlelocation": "left",
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "text.color": TEXT,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "legend.labelcolor": TEXT,
            "font.size": 10,
            "axes.prop_cycle": matplotlib.cycler(color=SERIES),
        }
    )
