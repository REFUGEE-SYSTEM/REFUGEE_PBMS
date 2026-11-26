import logging
import uuid
from datetime import datetime, timezone

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class G2PRefugeeSparSync(models.Model):
    _inherit = "g2p.refugee"

    spar_sync_status = fields.Selection(
        selection=[
            ("not_synced", "Not Synced"),
            ("synced", "Synced"),
            ("error", "Sync Error"),
        ],
        string="SPAR Sync Status",
        default="not_synced",
        readonly=True,
    )
    spar_last_sync_at = fields.Datetime(string="SPAR Last Sync", readonly=True)

    def _build_spar_fa_payload(self):
        """Build minimal Strategy 2 (Bank) FA payload without exposing sensitive refugee PII."""
        self.ensure_one()
        return {
            "fa_type": "BANK",
            "account_number": self.account_number or "",
            "bank_name": self.financial_service_provider or "Example Bank",
            "bank_code": self.financial_service_provider or "EXAMPLE-BANK",
            "branch_name": "Main Branch",
            "branch_code": "001",
            "strategy_id": 2,
        }

    def action_sync_to_spar(self):
        """Queue asynchronous SPAR /mapper/link synchronization via Odoo queue_job."""
        for rec in self:
            if not rec.internal_record_id or not rec.account_number:
                continue
            rec.with_delay()._sync_spar_record()
        return True

    def _sync_spar_record(self, mode="link"):
        """Execute synchronous HTTP POST to SPAR Mapper Partner API (/mapper/link or /mapper/update)."""
        self.ensure_one()
        base_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("refugee_registry.spar_mapper_api_url", "http://127.0.0.1:8104")
            .rstrip("/")
        )
        endpoint = f"{base_url}/mapper/{mode}"
        now_iso = datetime.now(timezone.utc).isoformat()
        txn_id = str(uuid.uuid4())
        ref_id = str(uuid.uuid4())
        req_key = "link_request" if mode == "link" else "update_request"

        payload = {
            "request_header": {
                "sender_app_mnemonic": "OPENG2P_PBMS",
                "sender_app_url": "",
                "request_id": str(uuid.uuid4()),
                "request_timestamp": now_iso,
                "instance_id": "refugee_management",
            },
            "request_body": {
                "request_payload": {
                    "transaction_id": txn_id,
                    req_key: [
                        {
                            "reference_id": ref_id,
                            "timestamp": now_iso,
                            "id": self.internal_record_id,
                            "fa": self._build_spar_fa_payload(),
                            "name": self.name or "",
                            "additional_info": [{"strategy_id": 2}],
                            "locale": "en",
                        }
                    ],
                }
            },
        }

        masked = f"****{self.account_number[-4:]}" if self.account_number and len(self.account_number) >= 4 else "****"
        _logger.info("Syncing g2p.refugee %s (account %s) to SPAR %s", self.internal_record_id, masked, endpoint)

        resp = requests.post(endpoint, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        resp_key = "link_response" if mode == "link" else "update_response"
        items = (
            data.get("response_body", {})
            .get("response_payload", {})
            .get(resp_key, [])
        )
        if items and items[0].get("status") == "succ":
            self.sudo().write({"spar_sync_status": "synced", "spar_last_sync_at": fields.Datetime.now()})
            return True

        reason = items[0].get("status_reason_code") if items else "unknown"
        if mode == "link" and reason in ("rjct.reference_id.duplicate", "rjct.id.invalid", "rjct.other.error"):
            return self._sync_spar_record(mode="update")

        self.sudo().write({"spar_sync_status": "error"})
        _logger.warning("SPAR %s failed for %s: %s", mode, self.internal_record_id, reason)
        return False
