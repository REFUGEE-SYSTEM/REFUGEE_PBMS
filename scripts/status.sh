#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./scripts/status.sh

Displays container status and key HTTP endpoints for Refugee-PBMS.
EOF
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

docker compose ps
echo ""
echo "Endpoints:"
echo "  PBMS Odoo:     http://localhost:${PBMS_ODOO_PORT:-8369}/web/login"
echo "  Staff API:     http://localhost:${PBMS_STAFF_API_PORT:-8350}/docs"
echo "  Postgres:      localhost:${PBMS_POSTGRES_PORT:-5635}"
echo "  Redis:         localhost:${PBMS_REDIS_PORT:-6581}"
