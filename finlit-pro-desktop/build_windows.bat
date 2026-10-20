@echo off
rem FinLit Pro: build a standalone dist\FinLitPro\FinLitPro.exe that runs without Python.
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m PyInstaller --noconfirm packaging\finlit_pro.spec
if errorlevel 1 goto fail
echo.
echo Built dist\FinLitPro\FinLitPro.exe. Copy the whole dist\FinLitPro folder to keep it together.
pause
exit /b 0

:fail
echo.
echo The build did not finish. Read the messages above.
pause
exit /b 1
