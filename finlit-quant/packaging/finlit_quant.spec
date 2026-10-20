# PyInstaller spec: `pyinstaller packaging/finlit_quant.spec` from the project root.
# Produces dist/FinLitQuant (a folder) and, on macOS, dist/FinLitQuant.app.
# PyInstaller converts the PNG icon to .ico / .icns itself when Pillow is installed.

import sys
from pathlib import Path

root = Path(SPECPATH).parent
icon = str(root / "finlit_quant" / "assets" / "icon.png")

a = Analysis(
    [str(root / "packaging" / "launch.py")],
    pathex=[str(root)],
    datas=[(str(root / "finlit_quant" / "assets"), "finlit_quant/assets")],
    hiddenimports=["matplotlib.backends.backend_qtagg"],
    # Qt modules the app never uses; leaving them out saves ~150 MB.
    excludes=["PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.Qt3DCore", "PySide6.QtQuick", "PySide6.QtQml", "PySide6.QtPdf", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="FinLitQuant", console=False, icon=icon)
coll = COLLECT(exe, a.binaries, a.datas, name="FinLitQuant")
if sys.platform == "darwin":
    app = BUNDLE(coll, name="FinLitQuant.app", icon=icon, bundle_identifier="org.finlitpro.quant")
