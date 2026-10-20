@echo off
rem FinLit Pro: start the app. Any arguments are passed on, for example: run.bat MSFT
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    echo FinLit Pro is not set up yet. Run setup.bat first.
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" -m finlit_pro %*
