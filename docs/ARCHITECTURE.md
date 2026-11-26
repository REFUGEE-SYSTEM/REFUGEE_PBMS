# Architecture

## Overview

`Refugee-PBMS` is a standalone Docker Compose stack (`COMPOSE_PROJECT_NAME=refugee-pbms`) with its own bridge network (`refugee_pbms_net`) and volumes (`refugee_pbms_postgres_data`, `refugee_pbms_redis_data`, `refugee_pbms_odoo_data`).

```
  PBMS Odoo (:8369) ──► pbmsdb (Postgres :5635)
        │
        ▼
  Staff Portal API (:8350) ──► bgtaskdb (Postgres :5635)
        │                          ▲
        ▼                          │
  Redis (:6581) ◄── Celery Beat & Worker
                                   │
                                   ▼ (read-only SELECT via host.docker.internal:5535)
                          refugee_registry_db.g2p_register_refugees
```

## Refugee Registry Integration

- **Odoo Addon (`odoo-addons/g2p_registry_type_refugee`)**:
  - Registers `refugees` in `G2PRegistryType` and `G2PTargetModelMapping` (`g2p.register.refugees`).
  - Defines `_auto = False` metadata model `g2p.register.refugees` so Odoo domain builders generate valid SQL against `g2p_register_refugees`.
  - Extends `target_registry` selection on `g2p.program.definition`, `g2p.eligibility.rule.definition`, `g2p.entitlement.rule.definition`, and `g2p.priority.rule.definition`.
- **Registry Adapter (`vendor/pbms/openg2p-bg-task-registry-adapters`)**:
  - Adds `G2PRegisterRefugee`, `BeneficiaryListSummaryRefugee`, `RegisterRefugee`, and `RegistryFactory` dispatch for `target_registry = "refugees"`.

## Required Odoo Config Parameters (`ir_config_parameter`)

Configured idempotently by `scripts/up.sh`:
- `g2p_pbms.staff_portal_api_url` = `http://pbms-staff-api:8000` (internal Docker URL used by `pbms-odoo` for `/summary`, `/search_beneficiaries`, etc.)
- `g2p_pbms.g2p_bridge_api_url` = `http://localhost:8999/unused` (placeholder; G2P Bridge is disabled)
- `g2p_pbms.keymanager_sign_application_id` = `pbms` (required non-empty string for `G2PRequestHeader.sender_app_mnemonic` Pydantic validation)
