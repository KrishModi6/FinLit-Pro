# PyInstaller spec: `pyinstaller --noconfirm packaging/finlit_pro.spec` from the project root,
# or run build_windows.bat. Produces dist/FinLitPro/FinLitPro.exe on Windows (a folder build:
# it starts faster than a one-file build and antivirus tools flag it less often).
# PyInstaller converts the PNG icon to .ico / .icns itself when Pillow is installed.

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

root = Path(SPECPATH).parent
icon = str(root / "finlit_pro" / "assets" / "icon.png")

hidden = ["matplotlib.backends.backend_qtagg"]
# keyring picks its backend (Windows Credential Manager, macOS Keychain) at run time.
hidden += collect_submodules("keyring.backends")
# The analysis engines are imported only when a key is configured.
hidden += ["finlit_pro.research.claude", "finlit_pro.research.openai_provider"]

a = Analysis(
    [str(root / "packaging" / "launch.py")],
    pathex=[str(root)],
    datas=[(str(root / "finlit_pro" / "assets"), "finlit_pro/assets")],
    hiddenimports=hidden,
    # Qt modules the app never uses; leaving them out saves about 150 MB.
    excludes=["PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.Qt3DCore", "PySide6.QtQuick", "PySide6.QtQml", "PySide6.QtPdf", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="FinLitPro", console=False, icon=icon)
coll = COLLECT(exe, a.binaries, a.datas, name="FinLitPro")
if sys.platform == "darwin":
    app = BUNDLE(coll, name="FinLitPro.app", icon=icon, bundle_identifier="org.finlitpro.desktop")
