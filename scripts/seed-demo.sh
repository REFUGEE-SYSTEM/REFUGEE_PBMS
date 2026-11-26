#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./scripts/seed-demo.sh

Idempotently seeds the demo program ("Uganda Refugee Cash-Based Intervention",
program_mnemonic=UG_REF_CBI) in PBMS Odoo via JSON-RPC:
  - Benefit code UGX_CASH (CASH_DIGITAL, UGX)
  - Program targeting 'refugees'
  - Eligibility rule: legal_status = 'RECOGNISED_REFUGEE' and record_status = 'ACTIVE'
  - Entitlement rule: flat 100,000 UGX

Does NOT touch Refugee-Registry. Run ./scripts/grant-registry-readonly.sh once
before triggering an enrollment cycle in PBMS Odoo.
EOF
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Run ./scripts/init-env.sh first." >&2
  exit 1
fi

python3 - <<'PY'
import json
import urllib.request

env = {}
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v

url = f"http://localhost:{env.get('PBMS_ODOO_PORT', '8369')}/jsonrpc"
db = env.get("PBMS_ODOO_DB", "pbmsdb")
pw = env["PBMS_ODOO_ADMIN_PASSWORD"]


def rpc(service, method, args):
    req = urllib.request.Request(
        url,
        data=json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {"service": service, "method": method, "args": args},
                "id": 1,
            }
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode())
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload["result"]


uid = rpc("common", "authenticate", [db, "admin", pw, {}])
if not isinstance(uid, int) or uid <= 0:
    raise RuntimeError("Failed to authenticate as Odoo admin")


def ensure_record(model, domain, vals):
    ids = rpc("object", "execute_kw", [db, uid, pw, model, "search", [domain]])
    if ids:
        return ids[0], False
    rec_id = rpc("object", "execute_kw", [db, uid, pw, model, "create", [vals]])
    return rec_id, True


benefit_id, created_bc = ensure_record(
    "g2p.benefit.codes",
    [("benefit_mnemonic", "=", "UGX_CASH")],
    {
        "benefit_mnemonic": "UGX_CASH",
        "benefit_type": "CASH_DIGITAL",
        "measurement_unit": "UGX",
    },
)
print(f"[seed-demo] Benefit code UGX_CASH id={benefit_id} (created={created_bc})")

program_id, created_prog = ensure_record(
    "g2p.program.definition",
    [("program_mnemonic", "=", "UG_REF_CBI")],
    {
        "program_mnemonic": "UG_REF_CBI",
        "target_registry": "refugees",
        "program_status": "ACTIVE",
        "enrollment_frequency": "Monthly",
        "disbursement_frequency": "Monthly",
        "beneficiary_list": "latest_always",
    },
)
print(f"[seed-demo] Program UG_REF_CBI id={program_id} (created={created_prog})")

pbc_id, created_pbc = ensure_record(
    "g2p.program.benefit.codes",
    [("program_id", "=", program_id), ("benefit_code_id", "=", benefit_id)],
    {
        "program_id": program_id,
        "benefit_code_id": benefit_id,
        "max_quantity": 100000.0,
    },
)
print(f"[seed-demo] Program benefit code id={pbc_id} (created={created_pbc})")

elig_id, created_elig = ensure_record(
    "g2p.eligibility.rule.definition",
    [("mnemonic", "=", "UG_REF_RECOGNISED"), ("program_id", "=", program_id)],
    {
        "mnemonic": "UG_REF_RECOGNISED",
        "program_id": program_id,
        "target_registry": "refugees",
        "rule_number": 1,
        "set_operator": "NONE",
        "pbms_domain": "[('legal_status', '=', 'RECOGNISED_REFUGEE'), ('record_status', '=', 'ACTIVE')]",
    },
)
print(f"[seed-demo] Eligibility rule UG_REF_RECOGNISED id={elig_id} (created={created_elig})")

ent_id, created_ent = ensure_record(
    "g2p.entitlement.rule.definition",
    [("mnemonic", "=", "UG_REF_FLAT_100K"), ("program_id", "=", program_id)],
    {
        "mnemonic": "UG_REF_FLAT_100K",
        "program_id": program_id,
        "target_registry": "refugees",
        "benefit_code_id": benefit_id,
        "quantity": 100000.0,
        "multiplier": "none",
        "pbms_domain": "[('legal_status', '=', 'RECOGNISED_REFUGEE'), ('record_status', '=', 'ACTIVE')]",
    },
)
print(f"[seed-demo] Entitlement rule UG_REF_FLAT_100K id={ent_id} (created={created_ent})")
PY
