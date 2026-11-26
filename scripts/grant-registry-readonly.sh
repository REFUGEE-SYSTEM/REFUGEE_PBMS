#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./scripts/grant-registry-readonly.sh [registry_compose_project]

Creates or updates the read-only PostgreSQL role (PBMS_SR_DB_USER from .env,
default pbms_reader) in the running Refugee-Registry Postgres container and
grants SELECT on all tables in schema public of PBMS_SR_DB_NAME.
EOF
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Run ./scripts/init-env.sh first." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

REG_PROJECT="${1:-refugee-registry}"
PG_CID="$(docker ps --filter "label=com.docker.compose.project=${REG_PROJECT}" --filter "label=com.docker.compose.service=postgres" -q | head -n1)"

if [[ -z "$PG_CID" ]]; then
  echo "ERROR: Could not find running postgres container for compose project '${REG_PROJECT}'." >&2
  exit 1
fi

SR_USER="${PBMS_SR_DB_USER:-pbms_reader}"
SR_DB="${PBMS_SR_DB_NAME:-refugee_registry_db}"
SR_PASS="${PBMS_SR_DB_PASSWORD}"

docker exec -i -e SR_USER="$SR_USER" -e SR_DB="$SR_DB" -e SR_PASS="$SR_PASS" "$PG_CID" sh -eu <<'EOS'
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$SR_DB" -v sr_user="$SR_USER" -v sr_pass="$SR_PASS" -v sr_db="$SR_DB" <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'sr_user') THEN
    EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE', :'sr_user', :'sr_pass');
  ELSE
    EXECUTE format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'sr_user', :'sr_pass');
  END IF;
END
$$;
GRANT CONNECT ON DATABASE :"sr_db" TO :"sr_user";
GRANT USAGE ON SCHEMA public TO :"sr_user";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO :"sr_user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO :"sr_user";
SQL
EOS

echo "[grant-registry-readonly] Granted read-only SELECT access to '${SR_USER}' on '${SR_DB}'."
