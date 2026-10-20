@echo off
rem FinLit Pro: one-time setup on Windows.
rem Creates a private Python environment in .venv and installs the app into it.
setlocal
cd /d "%~dp0"

set "PY=py -3"
where py >nul 2>nul
if errorlevel 1 set "PY=python"
%PY% --version >nul 2>nul
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.12 from https://www.python.org/downloads/windows/
    echo and tick "Add python.exe to PATH" in the installer, then run setup.bat again.
    pause
    exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo FinLit Pro needs Python 3.11 or newer. Install Python 3.12, then run setup.bat again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the environment in .venv
    %PY% -m venv .venv
    if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install --no-deps -e .
if errorlevel 1 goto fail

echo.
echo Setup complete. Start FinLit Pro with run.bat.
pause
exit /b 0

:fail
echo.
echo Setup did not finish. Read the messages above, fix the cause (usually the internet
echo connection or an old Python), then run setup.bat again.
pause
exit /b 1
