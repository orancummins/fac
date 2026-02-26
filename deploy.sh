#!/bin/bash
# deploy.sh — Copy project files to a remote Mac and set up the environment.
#
# Usage:
#   ./deploy.sh                              # uses defaults
#   ./deploy.sh user@host                    # custom host, default dir
#   ./deploy.sh user@host /opt/app           # custom host and dir
#
# Asks for the SSH password once and reuses it for all connections.
# Does NOT stop/start the server — use run.sh on the remote for that.

set -euo pipefail

REMOTE="${1:-orancummins@192.168.68.117}"
REMOTE_DIR="${2:-~/dev-server/fac}"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"

# Ask for password once, reuse via sshpass
read -rsp "Password for ${REMOTE}: " SSHPASS
echo
export SSHPASS

# Check sshpass is installed
if ! command -v sshpass &>/dev/null; then
    echo "sshpass not found. Installing via Homebrew..."
    brew install sshpass 2>/dev/null || brew install esolitos/ipa/sshpass
fi

SSH="sshpass -e ssh -o StrictHostKeyChecking=no"
SCP="sshpass -e scp -o StrictHostKeyChecking=no"

echo "==> Deploying to ${REMOTE}:${REMOTE_DIR}"

# Back up existing remote files before overwriting
echo "==> Backing up existing files on remote..."
$SSH "$REMOTE" bash -l <<BACKUP
    set -euo pipefail
    BACKUP_DIR="${REMOTE_DIR}/BACKUP"
    mkdir -p "\$BACKUP_DIR"

    # Only back up if there are files to archive
    if [ -f "${REMOTE_DIR}/app.py" ]; then
        TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
        ARCHIVE="\${BACKUP_DIR}/\${TIMESTAMP}.tar.gz"
        cd ${REMOTE_DIR}
        tar czf "\$ARCHIVE" \
            --exclude='.venv' \
            --exclude='venv' \
            --exclude='__pycache__' \
            --exclude='instance' \
            --exclude='BACKUP' \
            --exclude='*.log' \
            --exclude='.DS_Store' \
            . 2>/dev/null || true
        echo "  Backed up to \$ARCHIVE"
    else
        echo "  No existing files to back up."
    fi
BACKUP

# Create remote directory
$SSH "$REMOTE" "mkdir -p ${REMOTE_DIR}/templates"

# Copy project files (no venv, no db, no pycache)
$SCP \
    "${LOCAL_DIR}/app.py" \
    "${LOCAL_DIR}/models.py" \
    "${LOCAL_DIR}/scraper.py" \
    "${LOCAL_DIR}/scheduler.py" \
    "${LOCAL_DIR}/requirements.txt" \
    "${LOCAL_DIR}/run.sh" \
    "${REMOTE}:${REMOTE_DIR}/"

$SCP \
    "${LOCAL_DIR}/templates/index.html" \
    "${LOCAL_DIR}/templates/login.html" \
    "${REMOTE}:${REMOTE_DIR}/templates/"

# Make run.sh executable on remote
$SSH "$REMOTE" "chmod +x ${REMOTE_DIR}/run.sh"

echo "==> Files copied. Setting up remote environment..."

# Set up venv, install deps, install Playwright's Chromium
$SSH "$REMOTE" bash -l <<SETUP
    set -euo pipefail
    cd ${REMOTE_DIR}

    if [ ! -d .venv ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi

    source .venv/bin/activate
    echo "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo "Installing Playwright Chromium..."
    playwright install chromium

    echo ""
    echo "=============================="
    echo "  Deploy complete!"
    echo "  To start the server:"
    echo "    cd ${REMOTE_DIR} && ./run.sh"
    echo "=============================="
SETUP
