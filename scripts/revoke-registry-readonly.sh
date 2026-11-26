#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./scripts/revoke-registry-readonly.sh [registry_compose_project]

Revokes read-only privileges and drops PBMS_SR_DB_USER (default pbms_reader)
from the running Refugee-Registry Postgres container.
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

REG_PROJECT="${1:-refugee-registry}"
PG_CID="$(docker ps --filter "label=com.docker.compose.project=${REG_PROJECT}" --filter "label=com.docker.compose.service=postgres" -q | head -n1)"

if [[ -z "$PG_CID" ]]; then
  echo "ERROR: Could not find running postgres container for compose project '${REG_PROJECT}'." >&2
  exit 1
fi

SR_USER="${PBMS_SR_DB_USER:-pbms_reader}"
SR_DB="${PBMS_SR_DB_NAME:-refugee_registry_db}"

docker exec -i -e SR_USER="$SR_USER" -e SR_DB="$SR_DB" "$PG_CID" sh -eu <<'EOS'
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$SR_DB" -v sr_user="$SR_USER" -v sr_db="$SR_DB" <<'SQL'
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE SELECT ON TABLES FROM :"sr_user";
REVOKE SELECT ON ALL TABLES IN SCHEMA public FROM :"sr_user";
REVOKE USAGE ON SCHEMA public FROM :"sr_user";
REVOKE CONNECT ON DATABASE :"sr_db" FROM :"sr_user";
DROP ROLE IF EXISTS :"sr_user";
SQL
EOS

echo "[revoke-registry-readonly] Revoked and dropped '${SR_USER}' from '${SR_DB}'."
