#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./scripts/up.sh

Starts the standalone Refugee-PBMS stack and runs idempotent initialization.
EOF
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "[up] .env not found; running ./scripts/init-env.sh ..."
  ./scripts/init-env.sh
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

echo "[up] Building and starting Refugee-PBMS services ..."
docker compose up -d --build --wait

echo "[up] Refugee-PBMS infrastructure is ready!"
echo "  Postgres:      localhost:${PBMS_POSTGRES_PORT:-5635}"
echo "  Redis:         localhost:${PBMS_REDIS_PORT:-6581}"
