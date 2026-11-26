#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
PID_DIR="${ROOT_DIR}/logs/pids"
mkdir -p "${LOG_DIR}" "${PID_DIR}"

SPAR_VENV="${ROOT_DIR}/source/spar/venv"
BRIDGE_VENV="${ROOT_DIR}/source/g2p-bridge/venv"

DB_USER="refugee_user"
DB_PASS="RfgMgmt_AppUser_92Lm!qZa"
DB_HOST="127.0.0.1"
DB_PORT="5543"

echo "Starting standalone SPAR & G2P Bridge services..."

# 1. SPAR Mapper Partner API (Port 8104)
(
  cd "${ROOT_DIR}/source/spar/core/mapper-partner-api"
  export SPAR_MAPPER_PARTNER_API_DB_USERNAME="${DB_USER}"
  export SPAR_MAPPER_PARTNER_API_DB_PASSWORD="${DB_PASS}"
  export SPAR_MAPPER_PARTNER_API_DB_HOSTNAME="${DB_HOST}"
  export SPAR_MAPPER_PARTNER_API_DB_PORT="${DB_PORT}"
  export SPAR_MAPPER_PARTNER_API_DB_DBNAME="refugee_spar_db"
  export SPAR_MAPPER_PARTNER_API_JWT_AUTH_ENABLED="false"
  nohup "${SPAR_VENV}/bin/uvicorn" main:app --host 127.0.0.1 --port 8104 --workers 1 \
    > "${LOG_DIR}/spar_mapper_api.log" 2>&1 &
  echo $! > "${PID_DIR}/spar_mapper_api.pid"
)

# 2. SPAR Bene Portal API (Port 8105)
(
  cd "${ROOT_DIR}/source/spar/core/bene-portal-api"
  export G2P_SPAR_BENE_PORTAL_API_DB_USERNAME="${DB_USER}"
  export G2P_SPAR_BENE_PORTAL_API_DB_PASSWORD="${DB_PASS}"
  export G2P_SPAR_BENE_PORTAL_API_DB_HOSTNAME="${DB_HOST}"
  export G2P_SPAR_BENE_PORTAL_API_DB_PORT="${DB_PORT}"
  export G2P_SPAR_BENE_PORTAL_API_DB_DBNAME="refugee_spar_db"
  nohup "${SPAR_VENV}/bin/uvicorn" main:app --host 127.0.0.1 --port 8105 --workers 1 \
    > "${LOG_DIR}/spar_bene_api.log" 2>&1 &
  echo $! > "${PID_DIR}/spar_bene_api.pid"
)

# 3. Example Bank Simulator API (Port 8103)
(
  cd "${ROOT_DIR}/source/g2p-bridge/example-bank/openg2p-example-bank-api"
  export EXAMPLE_BANK_DB_USERNAME="${DB_USER}"
  export EXAMPLE_BANK_DB_PASSWORD="${DB_PASS}"
  export EXAMPLE_BANK_DB_HOSTNAME="${DB_HOST}"
  export EXAMPLE_BANK_DB_PORT="${DB_PORT}"
  export EXAMPLE_BANK_DB_DBNAME="refugee_example_bank_db"
  export EXAMPLE_BANK_CELERY_BROKER_URL="redis://127.0.0.1:6389/2"
  export EXAMPLE_BANK_CELERY_BACKEND_URL="redis://127.0.0.1:6389/2"
  nohup "${BRIDGE_VENV}/bin/uvicorn" main:app --host 127.0.0.1 --port 8103 --workers 1 \
    > "${LOG_DIR}/example_bank_api.log" 2>&1 &
  echo $! > "${PID_DIR}/example_bank_api.pid"
)

# 4. G2P Bridge Partner API (Port 8102)
(
  cd "${ROOT_DIR}/source/g2p-bridge/core/partner-api"
  export G2P_BRIDGE_DB_USERNAME="${DB_USER}"
  export G2P_BRIDGE_DB_PASSWORD="${DB_PASS}"
  export G2P_BRIDGE_DB_HOSTNAME="${DB_HOST}"
  export G2P_BRIDGE_DB_PORT="${DB_PORT}"
  export G2P_BRIDGE_DB_DBNAME="refugee_bridge_db"
  export G2P_BRIDGE_SIGNATURE_VALIDATION_ENABLED="false"
  nohup "${BRIDGE_VENV}/bin/uvicorn" main:app --host 127.0.0.1 --port 8102 --workers 1 \
    > "${LOG_DIR}/g2p_bridge_partner_api.log" 2>&1 &
  echo $! > "${PID_DIR}/g2p_bridge_partner_api.pid"
)

# 5. G2P Bridge Celery Worker
(
  cd "${ROOT_DIR}/source/g2p-bridge/core/celery-workers"
  export G2P_BRIDGE_CELERY_WORKERS_DB_USERNAME="${DB_USER}"
  export G2P_BRIDGE_CELERY_WORKERS_DB_PASSWORD="${DB_PASS}"
  export G2P_BRIDGE_CELERY_WORKERS_DB_HOSTNAME="${DB_HOST}"
  export G2P_BRIDGE_CELERY_WORKERS_DB_PORT="${DB_PORT}"
  export G2P_BRIDGE_CELERY_WORKERS_DB_DBNAME="refugee_bridge_db"
  export G2P_BRIDGE_CELERY_WORKERS_CELERY_BROKER_URL="redis://127.0.0.1:6389/1"
  export G2P_BRIDGE_CELERY_WORKERS_CELERY_BACKEND_URL="redis://127.0.0.1:6389/1"
  export G2P_BRIDGE_MAPPER_CONNECTORS_SPAR_MAPPER_URL="http://127.0.0.1:8104/mapper/resolve"
  export G2P_BRIDGE_BANK_CONNECTORS_DB_USERNAME="${DB_USER}"
  export G2P_BRIDGE_BANK_CONNECTORS_DB_PASSWORD="${DB_PASS}"
  export G2P_BRIDGE_BANK_CONNECTORS_DB_HOSTNAME="${DB_HOST}"
  export G2P_BRIDGE_BANK_CONNECTORS_DB_PORT="${DB_PORT}"
  export G2P_BRIDGE_BANK_CONNECTORS_DB_DBNAME="refugee_bridge_db"
  export G2P_BRIDGE_BANK_CONNECTORS_FUNDS_AVAILABLE_CHECK_URL_EXAMPLE_BANK="http://127.0.0.1:8103/api/example-bank/check_funds"
  export G2P_BRIDGE_BANK_CONNECTORS_FUNDS_BLOCK_URL_EXAMPLE_BANK="http://127.0.0.1:8103/api/example-bank/block_funds"
  export G2P_BRIDGE_BANK_CONNECTORS_FUNDS_DISBURSEMENT_URL_EXAMPLE_BANK="http://127.0.0.1:8103/api/example-bank/initiate_payment"
  nohup "${BRIDGE_VENV}/bin/celery" -A main.celery_app worker -Q g2p_bridge_queue -l info -P solo --concurrency=1 \
    > "${LOG_DIR}/g2p_bridge_celery_worker.log" 2>&1 &
  echo $! > "${PID_DIR}/g2p_bridge_celery_worker.pid"
)

echo "Waiting for HTTP services..."
sleep 4
for port_name in "8104:SPAR-Mapper" "8105:SPAR-Bene" "8103:Example-Bank" "8102:G2P-Bridge"; do
  port="${port_name%%:*}"
  name="${port_name##*:}"
  if curl -sf "http://127.0.0.1:${port}/docs" >/dev/null 2>&1; then
    echo "  [OK] ${name} listening on http://127.0.0.1:${port}/docs"
  else
    echo "  [WARN] ${name} on port ${port} not responding yet (check logs/${name}.log)"
  fi
done
