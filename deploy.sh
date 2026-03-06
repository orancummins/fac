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

# Ensure remote directory structure exists
echo "==> Ensuring remote directories exist..."
$SSH "$REMOTE" "mkdir -p ${REMOTE_DIR}/templates ${REMOTE_DIR}/static"

# Back up existing remote files before overwriting
echo "==> Backing up existing files on remote..."
$SSH "$REMOTE" bash -l <<BACKUP
    # Don't use set -e here — dir may not exist yet on first deploy
    BACKUP_DIR="${REMOTE_DIR}/BACKUP"
    mkdir -p "\$BACKUP_DIR" 2>/dev/null || true

    # Only back up if there are files to archive
    if [ -d "${REMOTE_DIR}" ] && [ -f "${REMOTE_DIR}/app.py" ]; then
        TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
        ARCHIVE="\${BACKUP_DIR}/\${TIMESTAMP}.tar.gz"
        cd ${REMOTE_DIR}
        tar czf "\$ARCHIVE" \
            --exclude='.venv' \
            --exclude='venv' \
            --exclude='BACKUP' \
            --exclude='*.log' \
            --exclude='.DS_Store' \
            . 2>/dev/null || true
        echo "  Backed up to \$ARCHIVE"
    else
        echo "  No existing files to back up."
    fi
BACKUP

# Copy project files (only those that exist locally)
echo "==> Copying files..."
LOCAL_FILES=()
for f in app.py models.py scraper.py scheduler.py requirements.txt run.sh deploy.sh; do
    [[ -f "${LOCAL_DIR}/${f}" ]] && LOCAL_FILES+=("${LOCAL_DIR}/${f}")
done
if (( ${#LOCAL_FILES[@]} )); then
    $SCP "${LOCAL_FILES[@]}" "${REMOTE}:${REMOTE_DIR}/"
fi

# Templates
TMPL_FILES=()
for f in index.html login.html; do
    [[ -f "${LOCAL_DIR}/templates/${f}" ]] && TMPL_FILES+=("${LOCAL_DIR}/templates/${f}")
done
if (( ${#TMPL_FILES[@]} )); then
    $SCP "${TMPL_FILES[@]}" "${REMOTE}:${REMOTE_DIR}/templates/"
fi

# Static assets
STATIC_FILES=()
for f in "${LOCAL_DIR}"/static/*; do
    [[ -f "$f" ]] && STATIC_FILES+=("$f")
done
if (( ${#STATIC_FILES[@]} )); then
    $SCP "${STATIC_FILES[@]}" "${REMOTE}:${REMOTE_DIR}/static/"
fi

# Make run.sh executable on remote
$SSH "$REMOTE" "chmod +x ${REMOTE_DIR}/run.sh"

echo "==> Files copied. Setting up remote environment..."

# Set up venv, install deps
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

    echo ""
    echo "=============================="
    echo "  Deploy complete!"
    echo "  To start the server:"
    echo "    cd ${REMOTE_DIR} && ./run.sh"
    echo "=============================="
SETUP
