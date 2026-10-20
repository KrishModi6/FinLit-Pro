"""QApplication setup and launch."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from finlit_quant import APP_NAME, __version__
from finlit_quant.config import load_settings
from finlit_quant.ui import theme

ICON = Path(__file__).resolve().parent.parent / "assets" / "icon.png"


def make_app(argv: list[str] | None = None) -> QApplication:
    app = QApplication.instance() or QApplication(argv or sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("FinLit Pro")
    app.setStyle("Fusion")
    app.setStyleSheet(theme.STYLESHEET)
    if ICON.exists():
        app.setWindowIcon(QIcon(str(ICON)))
    theme.apply_matplotlib_style()
    return app


def run(argv: list[str]) -> int:
    app = make_app(argv)
    from finlit_quant.ui.main_window import MainWindow

    settings = load_settings()
    window = MainWindow(settings)
    window.show()
    first = next((a for a in argv[1:] if not a.startswith("-")), None) or settings.last_symbol or "AAPL"
    window.load(first)
    return app.exec()
