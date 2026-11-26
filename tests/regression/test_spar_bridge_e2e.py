import json
import urllib.request
import uuid
from datetime import datetime, timezone

ODOO_URL = "http://127.0.0.1:8169"
SPAR_URL = "http://127.0.0.1:8104"
BRIDGE_URL = "http://127.0.0.1:8102"


def odoo_session():
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"db": "refugee_management_db", "login": "admin", "password": "admin"},
    }).encode()
    req = urllib.request.Request(
        f"{ODOO_URL}/web/session/authenticate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    resp = json.loads(opener.open(req).read().decode())
    assert resp.get("result", {}).get("uid"), f"Odoo auth failed: {resp}"
    return opener


def call_kw(opener, model, method, args=None, kwargs=None):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": model,
            "method": method,
            "args": args or [],
            "kwargs": kwargs or {},
        },
    }).encode()
    req = urllib.request.Request(
        f"{ODOO_URL}/web/dataset/call_kw/{model}/{method}",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    res = json.loads(opener.open(req).read().decode())
    if "error" in res:
        raise RuntimeError(f"Odoo RPC error on {model}.{method}: {res['error']}")
    return res.get("result")


def post_json(url, body):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def make_header():
    return {
        "sender_app_mnemonic": "OPENG2P_PBMS",
        "sender_app_url": "",
        "request_id": str(uuid.uuid4()),
        "request_timestamp": datetime.now(timezone.utc).isoformat(),
        "instance_id": "refugee_management",
    }


def run_e2e():
    opener = odoo_session()
    synthetic_uid = str(uuid.uuid4())
    acct_initial = f"UG99{uuid.uuid4().hex[:8].upper()}"
    acct_updated = f"UG88{uuid.uuid4().hex[:8].upper()}"
    refugee_id = None

    try:
        # 1. Create synthetic g2p.refugee record
        refugee_id = call_kw(opener, "g2p.refugee", "create", [{
            "surname": "TestRefugee",
            "given_names": "Integration",
            "date_of_birth": "1995-05-15",
            "sex": "female",
            "country_of_origin": "SSD",
            "nationality": "SSD",
            "internal_record_id": synthetic_uid,
            "functional_record_id": f"OPM-{uuid.uuid4().hex[:6].upper()}",
            "financial_service_provider": "EXAMPLE-BANK",
            "account_number": acct_initial,
        }])
        print(f"[PASS] 1. Created synthetic g2p.refugee ID={refugee_id}, internal_record_id={synthetic_uid}")

        # 2. Sync g2p.refugee -> SPAR (/mapper/link) via queue_job
        import time
        call_kw(opener, "g2p.refugee", "action_sync_to_spar", [[refugee_id]])
        rec_state = None
        for _ in range(15):
            time.sleep(1)
            rec_state = call_kw(opener, "g2p.refugee", "read", [[refugee_id], ["spar_sync_status"]])
            if rec_state[0]["spar_sync_status"] in ("synced", "error"):
                break
        assert rec_state[0]["spar_sync_status"] == "synced", f"Unexpected sync status: {rec_state}"
        print("[PASS] 2. Synced g2p.refugee to SPAR (/mapper/link via queue_job) -> spar_sync_status='synced'")

        # 3. Verify SPAR /mapper/resolve returns Strategy 5 FA
        resolve_res = post_json(f"{SPAR_URL}/mapper/resolve", {
            "request_header": make_header(),
            "request_body": {
                "request_payload": {
                    "transaction_id": str(uuid.uuid4()),
                    "resolve_request": [{
                        "reference_id": str(uuid.uuid4()),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "id": synthetic_uid,
                        "scope": "details",
                        "locale": "en",
                    }],
                }
            },
        })
        res_items = resolve_res["response_body"]["response_payload"]["resolve_response"]
        assert res_items and res_items[0]["status"] == "succ", f"SPAR resolve failed: {resolve_res}"
        print("[INFO] SPAR /mapper/resolve item:", json.dumps(res_items[0]))
        resolved_fa = res_items[0].get("fa")
        fa_str = json.dumps(resolved_fa) if isinstance(resolved_fa, dict) else str(resolved_fa)
        assert acct_initial in fa_str or "strategy_id" in fa_str, f"Unexpected FA: {resolved_fa}"
        print(f"[PASS] 3. SPAR /mapper/resolve returned FA: {fa_str}")

        # 4. Update account_number and verify /mapper/update via action_sync_to_spar (auto-fallback from link -> update)
        call_kw(opener, "g2p.refugee", "write", [[refugee_id], {"account_number": acct_updated, "spar_sync_status": "not_synced"}])
        call_kw(opener, "g2p.refugee", "action_sync_to_spar", [[refugee_id]])
        for _ in range(15):
            time.sleep(1)
            rec_state = call_kw(opener, "g2p.refugee", "read", [[refugee_id], ["spar_sync_status"]])
            if rec_state[0]["spar_sync_status"] in ("synced", "error"):
                break
        assert rec_state[0]["spar_sync_status"] == "synced", f"SPAR update sync failed: {rec_state}"
        print(f"[PASS] 4. Updated account in SPAR (/mapper/update) -> {acct_updated}")

        # 5. Create G2P Bridge Disbursement Envelope (UGX)
        envelope_id = str(uuid.uuid4())
        env_res = post_json(f"{BRIDGE_URL}/create_disbursement_envelopes", {
            "request_header": make_header(),
            "request_body": {
                "request_payload": [{
                    "disbursement_envelope_id": envelope_id,
                    "benefit_program_id": 14,
                    "benefit_program_mnemonic": "Emergency Cash Distribution",
                    "target_registry": "refugee",
                    "benefit_code_id": 1,
                    "benefit_code_mnemonic": "CASH_UGX",
                    "benefit_type": "CASH_DIGITAL",
                    "disbursement_frequency": "OnDemand",
                    "disbursement_cycle_id": 1,
                    "cycle_code_mnemonic": "CYCLE_01",
                    "number_of_beneficiaries": 1,
                    "number_of_disbursements": 1,
                    "total_disbursement_quantity": 50000.0,
                    "measurement_unit": "UGX",
                    "disbursement_schedule_date": datetime.now(timezone.utc).date().isoformat(),
                }]
            },
        })
        env_status = env_res.get("response_header", {}).get("response_status")
        assert env_status == "SUCCESS", f"Bridge create_disbursement_envelopes failed: {env_res}"
        envelope_id = env_res["response_body"]["response_payload"][0]["id"]
        print(f"[PASS] 5. Created G2P Bridge Disbursement Envelope ID={envelope_id} (50,000 UGX)")

        # 6. Create G2P Bridge Disbursement linked to synthetic refugee internal_record_id
        disb_id = str(uuid.uuid4())
        batch_ctrl_id = str(uuid.uuid4())
        disb_res = post_json(f"{BRIDGE_URL}/create_disbursements", {
            "request_header": make_header(),
            "request_body": {
                "request_payload": [{
                    "disbursement_id": disb_id,
                    "disbursement_envelope_id": envelope_id,
                    "beneficiary_id": synthetic_uid,
                    "beneficiary_name": "Integration TestRefugee",
                    "disbursement_quantity": 50000.0,
                    "disbursement_cycle_id": 1,
                    "disbursement_batch_control_id": batch_ctrl_id,
                    "narrative": "Refugee Emergency Cash Test",
                }]
            },
        })
        disb_status = disb_res.get("response_header", {}).get("response_status")
        assert disb_status == "SUCCESS", f"Bridge create_disbursements failed: {disb_res}"
        print(f"[PASS] 6. Created G2P Bridge Disbursement ID={disb_id}, batch={batch_ctrl_id}")

        # 7. Query Envelope & Batch Status from G2P Bridge Partner API
        env_check = post_json(f"{BRIDGE_URL}/get_disbursement_envelope_status", {
            "request_header": make_header(),
            "request_body": {"request_payload": envelope_id},
        })
        assert env_check.get("response_header", {}).get("response_status") == "SUCCESS", f"Envelope status failed: {env_check}"
        batch_check = post_json(f"{BRIDGE_URL}/get_disbursement_batch_control", {
            "request_header": make_header(),
            "request_body": {"request_payload": batch_ctrl_id},
        })
        assert batch_check.get("response_header", {}).get("response_status") == "SUCCESS", f"Batch status failed: {batch_check}"
        print("[PASS] 7. Verified G2P Bridge envelope and batch status endpoints")

        print("\nALL 7 E2E INTEGRATION CHECKS PASSED!")
    finally:
        if refugee_id:
            call_kw(opener, "g2p.refugee", "unlink", [[refugee_id]])
            print(f"[CLEANUP] Removed synthetic g2p.refugee ID={refugee_id}")


if __name__ == "__main__":
    run_e2e()
