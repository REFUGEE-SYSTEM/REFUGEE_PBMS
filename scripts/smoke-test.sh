#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./scripts/smoke-test.sh

Runs end-to-end health, DB, Odoo, Staff API, Celery, and adapter unit checks
for the standalone Refugee-PBMS stack.
EOF
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

pass() { echo "[PASS] $*"; }
fail() { echo "[FAIL] $*" >&2; exit 1; }

# 1. All 6 containers running (not restarting)
for svc in postgres redis pbms-odoo pbms-staff-api pbms-celery-worker pbms-celery-beat; do
  cid="$(docker compose ps -q "$svc")"
  [[ -n "$cid" ]] || fail "Service $svc has no container"
  status="$(docker inspect -f '{{.State.Status}}' "$cid")"
  [[ "$status" == "running" ]] || fail "Service $svc status is '$status' (expected running)"
done
pass "All 6 compose services running"

# 1b. Celery worker responds to ping (allow brief startup mingle)
ping_ok=0
for _ in $(seq 1 5); do
  if docker compose exec -T pbms-celery-worker celery -A openg2p_bg_task_celery_workers.main.celery_app inspect ping -t 5 >/dev/null 2>&1; then
    ping_ok=1
    break
  fi
  sleep 2
done
[[ "$ping_ok" == "1" ]] || fail "Celery worker failed inspect ping"
pass "Celery worker responds to inspect ping"

# 2. Postgres databases exist
dbs="$(docker compose exec -T postgres psql -U "${PBMS_DB_USER:-pbmsuser}" -d postgres -tAc "\l")"
echo "$dbs" | grep -q "${PBMS_ODOO_DB:-pbmsdb}" || fail "Database ${PBMS_ODOO_DB:-pbmsdb} missing"
echo "$dbs" | grep -q "${PBMS_BGTASK_DB:-bgtaskdb}" || fail "Database ${PBMS_BGTASK_DB:-bgtaskdb} missing"
pass "Postgres databases pbmsdb and bgtaskdb exist"

# 3. Redis ping
[[ "$(docker compose exec -T redis redis-cli ping)" == "PONG" ]] || fail "Redis ping failed"
pass "Redis responds PONG"

# 4. Odoo addon installed & required config parameters present
mod_state="$(docker compose exec -T postgres psql -U "${PBMS_DB_USER:-pbmsuser}" -d "${PBMS_ODOO_DB:-pbmsdb}" -tAc \
  "SELECT state FROM ir_module_module WHERE name='g2p_registry_type_refugee'")"
[[ "$mod_state" == "installed" ]] || fail "g2p_registry_type_refugee state='$mod_state'"
staff_url="$(docker compose exec -T postgres psql -U "${PBMS_DB_USER:-pbmsuser}" -d "${PBMS_ODOO_DB:-pbmsdb}" -tAc \
  "SELECT value FROM ir_config_parameter WHERE key='g2p_pbms.staff_portal_api_url'")"
[[ "$staff_url" == "http://pbms-staff-api:8000" ]] || fail "g2p_pbms.staff_portal_api_url='$staff_url'"
sender_id="$(docker compose exec -T postgres psql -U "${PBMS_DB_USER:-pbmsuser}" -d "${PBMS_ODOO_DB:-pbmsdb}" -tAc \
  "SELECT value FROM ir_config_parameter WHERE key='g2p_pbms.keymanager_sign_application_id'")"
[[ -n "$sender_id" ]] || fail "g2p_pbms.keymanager_sign_application_id is empty"
pass "Odoo addon g2p_registry_type_refugee installed and config parameters set"

# 5. Odoo HTTP + admin login + target_registry selection
code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${PBMS_ODOO_PORT:-8369}/web/login")"
[[ "$code" == "200" ]] || fail "Odoo /web/login returned $code"
python3 - <<'PY'
import json, urllib.request
env = dict(line.strip().split("=", 1) for line in open(".env") if line.strip() and not line.startswith("#") and "=" in line)
def rpc(service, method, args):
    req = urllib.request.Request(
        f"http://localhost:{env.get('PBMS_ODOO_PORT', '8369')}/jsonrpc",
        data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": {"service": service, "method": method, "args": args}, "id": 1}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=10).read().decode())["result"]
uid = rpc("common", "authenticate", [env["PBMS_ODOO_DB"], "admin", env["PBMS_ODOO_ADMIN_PASSWORD"], {}])
assert isinstance(uid, int) and uid > 0, "Admin login failed"
fg = rpc("object", "execute_kw", [env["PBMS_ODOO_DB"], uid, env["PBMS_ODOO_ADMIN_PASSWORD"], "g2p.program.definition", "fields_get", ["target_registry"], {"attributes": ["selection"]}])
assert any(k == "refugees" for k, _ in fg["target_registry"]["selection"]), "refugees missing from g2p.program.definition.target_registry"
wfg = rpc("object", "execute_kw", [env["PBMS_ODOO_DB"], uid, env["PBMS_ODOO_ADMIN_PASSWORD"], "g2p.bgtask.summary.wizard", "fields_get", ["target_registry"], {"attributes": ["selection"]}])
assert any(k == "refugees" for k, _ in wfg["target_registry"]["selection"]), "refugees missing from g2p.bgtask.summary.wizard.target_registry"

# Test enrolment cycle create wizard -> action_confirm for a refugee program (cleanup afterwards)
prog_ids = rpc("object", "execute_kw", [env["PBMS_ODOO_DB"], uid, env["PBMS_ODOO_ADMIN_PASSWORD"], "g2p.program.definition", "search", [[("target_registry", "=", "refugees")]], {"limit": 1}])
if prog_ids:
    wiz_id = rpc("object", "execute_kw", [env["PBMS_ODOO_DB"], uid, env["PBMS_ODOO_ADMIN_PASSWORD"], "g2p.enrollment.cycle.create.wizard", "create", [{"program_id": prog_ids[0], "cycle_name": "SmokeTest Cycle"}]])
    action = rpc("object", "execute_kw", [env["PBMS_ODOO_DB"], uid, env["PBMS_ODOO_ADMIN_PASSWORD"], "g2p.enrollment.cycle.create.wizard", "action_confirm", [[wiz_id]]])
    assert action.get("res_model") == "g2p.bgtask.summary.wizard", f"Unexpected action: {action}"
    cycle_id = action.get("context", {}).get("default_enrollment_cycle_id")
    if cycle_id:
        rpc("object", "execute_kw", [env["PBMS_ODOO_DB"], uid, env["PBMS_ODOO_ADMIN_PASSWORD"], "g2p.enrollment.cycle", "unlink", [[cycle_id]]])
PY
pass "Odoo /web/login (200), admin login, target_registry='refugees' (program + summary wizard), and cycle creation verified"

# 6. Staff Portal API /ping & /docs
ping_res="$(curl -sf "http://localhost:${PBMS_STAFF_API_PORT:-8350}/ping")"
echo "$ping_res" | grep -q "pong" || fail "Staff API /ping returned: $ping_res"
docs_code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${PBMS_STAFF_API_PORT:-8350}/docs")"
[[ "$docs_code" == "200" ]] || fail "Staff API /docs returned $docs_code"
pass "Staff Portal API /ping and /docs (200) verified"

# 7. Refugee adapter unit tests
docker compose exec -T pbms-staff-api python3 - < tests/test_refugee_adapter.py >/dev/null
pass "Refugee adapter unit tests passed"

echo "[smoke-test] All checks passed!"
