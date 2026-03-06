#!/bin/bash
# run.sh — Start the Find A Card server.
#
# Stops any existing instance on port 5432, asks for the app password,
# then starts the server in the background via nohup.
#
# Usage:
#   ./run.sh          # interactive — prompts for password
#   ./run.sh stop     # just stop the server

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=5432
LOG_FILE="${SCRIPT_DIR}/app.log"

stop_server() {
    local PID
    PID=$(lsof -ti:"$PORT" 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo "Stopping server on port ${PORT} (PID $PID)..."
        kill $PID 2>/dev/null || true
        sleep 1
        for p in $PID; do
            if kill -0 "$p" 2>/dev/null; then
                kill -9 "$p" 2>/dev/null || true
            fi
        done
        echo "Stopped."
    else
        echo "No server running on port ${PORT}."
    fi
}

# Handle "stop" subcommand
if [ "${1:-}" = "stop" ]; then
    stop_server
    exit 0
fi

# Stop existing server before starting a new one
stop_server

# Ask for app password
read -rsp "App password (visitors will enter this to access the site): " APP_PASSWORD
echo
export APP_PASSWORD

if [ -z "$APP_PASSWORD" ]; then
    echo "Warning: No password set — the app will run without authentication."
fi

# Activate venv (create if missing)
cd "$SCRIPT_DIR"
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
else
    source .venv/bin/activate
fi

# Start in background (use explicit venv python to avoid PATH issues under nohup)
echo "Starting server on port ${PORT}..."
nohup "${SCRIPT_DIR}/.venv/bin/python" app.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
sleep 1

if kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Server started (PID ${SERVER_PID})."
    echo "Logs: ${LOG_FILE}"
    echo "Local: http://localhost:${PORT}"
else
    echo "ERROR: Server failed to start. Check ${LOG_FILE}"
    exit 1
fi
