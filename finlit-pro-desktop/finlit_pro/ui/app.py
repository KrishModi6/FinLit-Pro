"""Application setup and launch."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from finlit_pro import APP_NAME, __version__
from finlit_pro.config import load_settings
from finlit_pro.ui import theme

ICON = Path(__file__).resolve().parent.parent / "assets" / "icon.png"


def make_app(argv: list[str] | None = None) -> QApplication:
    if sys.platform.startswith("win"):
        # Give the process its own taskbar identity instead of python.exe's.
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FinLitPro.Desktop")
        except (AttributeError, OSError):
            pass
    app = QApplication.instance() or QApplication(argv or sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("FinLit Pro")
    app.setStyle("Fusion")
    font = QFont(theme.FONT_FAMILY.split(",")[0])
    font.setPointSizeF(9.0)
    app.setFont(font)
    app.setStyleSheet(theme.STYLESHEET)
    if ICON.exists():
        app.setWindowIcon(QIcon(str(ICON)))
    theme.apply_matplotlib_style()
    theme.apply_pyqtgraph_style()
    return app


def run(argv: list[str]) -> int:
    app = make_app(argv)
    from finlit_pro.ui.main_window import MainWindow

    settings = load_settings()
    window = MainWindow(settings)
    window.show()
    first = next((a for a in argv[1:] if not a.startswith("-")), None) or settings.last_symbol or "AAPL"
    window.load(first)
    return app.exec()
