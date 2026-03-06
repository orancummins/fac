#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "${REPO_DIR}"

docker compose build app

echo "Built Docker image for app service (docker compose build app)."
