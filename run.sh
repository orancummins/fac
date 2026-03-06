#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_DIR}"

case "${1:-up}" in
  up)
    docker compose up -d
    echo "Services are running."
    echo "App: http://localhost:9094"
    ;;
  stop)
    docker compose down
    echo "Services stopped."
    ;;
  restart)
    docker compose down
    docker compose up -d
    echo "Services restarted."
    echo "App: http://localhost:9094"
    ;;
  logs)
    docker compose logs -f
    ;;
  *)
    echo "Usage: $0 [up|stop|restart|logs]" >&2
    exit 1
    ;;
esac
