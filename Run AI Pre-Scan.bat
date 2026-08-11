@echo off
REM Double-click to run AI Pre-Scan. Windows.
REM
REM Sets itself up on first run and starts straight away afterwards. Falls back to demo mode
REM automatically when no API keys are present, so this works on a machine that has just cloned
REM the repository and configured nothing.

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "KEY_STORE=%USERPROFILE%\.config\ironhack\.env.local"
set "PORT=8000"

echo AI Pre-Scan
echo %CD%
echo.

REM ---- Python -----------------------------------------------------------
set "PY="
for %%C in (python py) do (
  if not defined PY (
    %%C -c "import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)" >nul 2>&1
    if !errorlevel! equ 0 set "PY=%%C"
  )
)
if not defined PY (
  echo Python 3.12 or newer is required and was not found.
  echo Install it from https://www.python.org/downloads/ then run this file again.
  echo.
  pause
  exit /b 1
)

REM ---- Environment ------------------------------------------------------
if not exist ".venv" (
  echo First run - setting up. This takes a couple of minutes and only happens once.
  %PY% -m venv .venv
  if !errorlevel! neq 0 (
    echo Could not create the environment.
    pause
    exit /b 1
  )
)

echo Checking dependencies...
".venv\Scripts\pip.exe" install -q -e . 2>"%TEMP%\ai-prescan-install.log"
if !errorlevel! neq 0 (
  echo Install failed. Details:
  type "%TEMP%\ai-prescan-install.log"
  pause
  exit /b 1
)

REM Only needed for live scans, and only downloaded once.
if exist "%KEY_STORE%" (
  ".venv\Scripts\python.exe" -c "import playwright" >nul 2>&1
  if !errorlevel! neq 0 ".venv\Scripts\python.exe" -m playwright install chromium >nul 2>&1
)

REM ---- Live or demo -----------------------------------------------------
set "MODE_ARG=--demo"
set "MODE_TEXT=demo mode (sample data - no API keys found)"
if exist "%KEY_STORE%" (
  findstr /b /c:"OPENAI_API_KEY=" "%KEY_STORE%" >nul 2>&1 && findstr /b /c:"PINECONE_API_KEY=" "%KEY_STORE%" >nul 2>&1 && (
    set "MODE_ARG="
    set "MODE_TEXT=live research (API keys found)"
  )
)

echo.
echo Starting in !MODE_TEXT!
echo Opening http://127.0.0.1:%PORT%
echo Close this window, or press Control-C, to stop.
echo.

start "" /b cmd /c "timeout /t 3 >nul & start http://127.0.0.1:%PORT%"

".venv\Scripts\ai-prescan-web.exe" !MODE_ARG! --port %PORT%
set "STATUS=!errorlevel!"

if !STATUS! neq 0 (
  echo.
  echo AI Pre-Scan stopped unexpectedly ^(exit !STATUS!^).
  echo If the port is already in use, close the other window and try again.
  pause
)
endlocal
