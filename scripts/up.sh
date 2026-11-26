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

ODOO_DB="${PBMS_ODOO_DB:-pbmsdb}"
DB_USER="${PBMS_DB_USER:-pbmsuser}"

echo "[up] Starting Postgres and Redis ..."
docker compose up -d --wait postgres redis

HAS_ODOO="$(docker compose exec -T postgres psql -U "$DB_USER" -d "$ODOO_DB" -tAc \
  "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='ir_module_module'" || true)"

if [[ "$HAS_ODOO" != "1" ]]; then
  echo "[up] Initializing Odoo database '${ODOO_DB}' with base,queue_job,g2p_pbms,g2p_registry_type_refugee ..."
  docker compose run --rm --no-deps -T pbms-odoo \
    odoo -d "$ODOO_DB" -i base,queue_job,g2p_pbms,g2p_registry_type_refugee --stop-after-init --without-demo=all

  echo "[up] Setting Odoo admin password ..."
  ADMIN_HASH="$(docker compose run --rm --no-deps --entrypoint python3 -T -e NEW_PW="$PBMS_ODOO_ADMIN_PASSWORD" pbms-odoo \
    -c 'import os; from passlib.context import CryptContext; print(CryptContext(["pbkdf2_sha512"]).hash(os.environ["NEW_PW"]))')"
  docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$ODOO_DB" -v pw_hash="$ADMIN_HASH" <<'SQL'
UPDATE res_users SET password = :'pw_hash' WHERE login = 'admin';
SQL
else
  HAS_REFUGEE_MOD="$(docker compose exec -T postgres psql -U "$DB_USER" -d "$ODOO_DB" -tAc \
    "SELECT state FROM ir_module_module WHERE name='g2p_registry_type_refugee'" || true)"
  if [[ "$HAS_REFUGEE_MOD" != "installed" ]]; then
    echo "[up] Installing g2p_registry_type_refugee in '${ODOO_DB}' ..."
    docker compose stop pbms-odoo >/dev/null 2>&1 || true
    docker compose run --rm --no-deps -T pbms-odoo \
      odoo -d "$ODOO_DB" -i g2p_registry_type_refugee --stop-after-init --without-demo=all
  fi
fi

echo "[up] Configuring PBMS ir_config_parameter URLs ..."
STAFF_URL="http://localhost:${PBMS_STAFF_API_PORT:-8350}"
BRIDGE_URL="http://localhost:8999/unused"
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$ODOO_DB" \
  -v staff_url="$STAFF_URL" -v bridge_url="$BRIDGE_URL" <<'SQL'
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES
  ('g2p_pbms.staff_portal_api_url', :'staff_url', 1, NOW(), 1, NOW()),
  ('g2p_pbms.g2p_bridge_api_url', :'bridge_url', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
SQL

echo "[up] Building and starting all Refugee-PBMS services ..."
docker compose up -d --build --wait

echo "[up] Refugee-PBMS is ready!"
echo "  PBMS Odoo:     http://localhost:${PBMS_ODOO_PORT:-8369}/web/login"
echo "  Staff API:     http://localhost:${PBMS_STAFF_API_PORT:-8350}/docs"
