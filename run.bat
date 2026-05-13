@echo off
REM run.bat - Start the Find A Card server on Windows.
REM Stops any existing instance on port 5432, sets up dependencies,
REM then starts the server.

setlocal enabledelayedexpansion
set PORT=5432
set SCRIPT_DIR=%~dp0
set LOG_FILE=%SCRIPT_DIR%app.log

REM --- Stop existing server on the port ---
echo Checking for existing server on port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr "LISTENING" ^| findstr ":%PORT% "') do (
    echo Stopping server PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

REM --- Prompt for app password ---
set "APP_PASSWORD="
set /p "APP_PASSWORD=App password (visitors will enter this to access the site): "
if not defined APP_PASSWORD echo Warning: No password set - the app will run without authentication.

REM --- Set up virtual environment and dependencies ---
cd /d "%SCRIPT_DIR%"
if not exist .venv (
    echo Creating virtual environment...
    py -m venv .venv
)
call .venv\Scripts\activate.bat
echo Installing dependencies...
py -m pip install -q --upgrade pip
py -m pip install -q -r requirements.txt

REM --- Start the server ---
echo Starting server on port %PORT%...
if exist "%LOG_FILE%" del /q "%LOG_FILE%"
start "FindACard" /MIN cmd /c ""%SCRIPT_DIR%.venv\Scripts\python.exe" app.py > "%LOG_FILE%" 2>&1"

REM Wait and verify
set STARTED=
for /l %%i in (1,1,10) do (
    powershell -NoProfile -Command "try { $response = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%PORT% -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        set STARTED=1
        goto :server_started
    )
    ping -n 2 127.0.0.1 >nul 2>&1
)

:server_failed
echo ERROR: Server failed to start.
if exist "%LOG_FILE%" (
    echo Log output:
    type "%LOG_FILE%"
)
exit /b 1

:server_started
echo Server started successfully.
echo Local: http://localhost:%PORT%
echo Logs: %LOG_FILE%
