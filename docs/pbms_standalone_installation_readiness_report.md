# PBMS Standalone Installation Readiness Report

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Inspection Date:** 2026-11-26  
**Standalone Odoo URL:** `http://127.0.0.1:8169`  
**Standalone PostgreSQL:** `127.0.0.1:5543` (`refugee_management_db`, `refugee_bgtask_db`)  
**Standalone Redis:** `127.0.0.1:6389`  
**Overall Readiness Status:** **PASS (CORE ODOO PBMS ALREADY INSTALLED & OPERATIONAL)** / **PARTIAL (OPTIONAL BACKGROUND CELERY & EXTERNAL INTEGRATIONS NOT YET STARTED)**

---

## 1. Environment Connectivity (Phase 1)

| Check | Expected | Actual Evidence | Status |
|---|---|---|---|
| **Odoo 17 HTTP (`8169`)** | Responds on `127.0.0.1:8169` | `GET http://127.0.0.1:8169/web/login` returned `HTTP 200`. | **PASS** |
| **Odoo Process Config** | Uses `/Users/apple/refugee_management/infrastructure/configs/odoo.conf` | `PID 7668` running `source/odoo17/odoo-bin -c .../infrastructure/configs/odoo.conf`. | **PASS** |
| **PostgreSQL Connection (`5543`)** | Connected to `127.0.0.1:5543` | `PID 7668` sockets established exclusively to `127.0.0.1:5543`; `psycopg2` confirmed `current_database() = refugee_management_db`, `398` public tables. | **PASS** |
| **Redis Connectivity (`6389`)** | Standalone Redis accessible | `redis-py` `PING` on `127.0.0.1:6389` returned `True` (Redis `7.4.12`). | **PASS** |
| **Legacy Isolation** | Zero connections to `5433`, `6379`, `8069`, `pbmsdb` | Verified no legacy sockets or DB connections. | **PASS** |

---

## 2. PBMS Addon Inventory (Phase 2)

All 6 configured `addons_path` directories (`source/odoo17/addons`, `source/pbms/odoo/community-addons`, `source/pbms/odoo`, `extensions`, `source/pbms/odoo/extensions`, `source/openg2p-odoo-commons`) plus `source/odoo17/odoo/addons` were scanned (`653` unique addons discovered).

| Technical Name | Display Name | Manifest Path | Dependencies | Deps Available | DB State (`refugee_management_db`) | Installable |
|---|---|---|---|---|---|---|
| `g2p_app_filter` | G2P App Filter | `source/openg2p-odoo-commons/g2p_app_filter/__manifest__.py` | `['base']` | Yes | `installed` (`17.0.0.0.0`) | Yes |
| `g2p_documents` | G2P Documents Store | `source/openg2p-odoo-commons/g2p_documents/__manifest__.py` | `['storage_backend_s3', 'storage_file', 'web']` | Yes | `installed` (`17.0.0.0.0`) | Yes |
| `g2p_registry_type_addon` | PBMS Registry Type Addon | `source/pbms/odoo/extensions/g2p_registry_type_addon/__manifest__.py` | `['base_setup', 'web']` | Yes | `installed` (`17.0.3.1.1`) | Yes |
| `g2p_pbms` | PBMS | `source/pbms/odoo/g2p_pbms/__manifest__.py` | `['base_setup', 'web', 'g2p_documents', 'g2p_registry_type_addon']` | Yes | `installed` (`17.0.3.1.0`) | Yes |
| `g2p_pbms_program_access` | PBMS Program Access | `source/pbms/odoo/g2p_pbms_program_access/__manifest__.py` | `['g2p_pbms']` | Yes | `installed` (`17.0.3.1.0`) | Yes |
| `g2p_registry_addon` | PBMS Registry Addon | `extensions/g2p_registry_addon/__manifest__.py` *(active precedence)* & `source/pbms/odoo/extensions/g2p_registry_addon/__manifest__.py` | `['base_setup', 'web', 'g2p_pbms']` | Yes | `installed` (`17.0.3.1.1`) | Yes |
| `pbms_theme_extension` | PBMS Theme | `source/pbms/odoo/extensions/pbms_theme_extension/__manifest__.py` | `['base', 'web', 'auth_signup', 'website']` | Yes | `installed` (`17.0.3.1.1`) | Yes |
| `queue_job` | Job Queue | `source/pbms/odoo/community-addons/queue_job/__manifest__.py` | `['mail', 'base_sparse_field', 'web']` | Yes | `installed` (`17.0.1.1.1`) | Yes |
| `spp_registry_data_source` | OpenSPP Data Source | `source/pbms/odoo/community-addons/spp_registry_data_source/__manifest__.py` | `['base']` | Yes | `installed` (`17.0.1.0.0`) | Yes |
| `storage_backend` | Storage Bakend | `source/pbms/odoo/community-addons/storage_backend/__manifest__.py` | `['base', 'component', 'server_environment']` | Yes | `installed` (`17.0.1.0.0`) | Yes |
| `storage_backend_s3` | Storage Backend S3 | `source/pbms/odoo/community-addons/storage_backend_s3/__manifest__.py` | `['storage_backend']` | Yes | `installed` (`17.0.1.0.0`) | Yes |
| `storage_file` | Storage File | `source/pbms/odoo/community-addons/storage_file/__manifest__.py` | `['storage_backend']` | Yes | `installed` (`17.0.1.0.0`) | Yes |
| `g2p_security` | G2P Security | `source/openg2p-odoo-commons/g2p_security/__manifest__.py` | `['auth_signup', 'password_security']` | Yes | `uninstalled` | Yes |
| `g2p_auth_oidc` | OpenID Connect Authentication | `source/openg2p-odoo-commons/g2p_auth_oidc/__manifest__.py` | `['auth_oauth']` | Yes | `uninstalled` | Yes |
| `g2p_auth_oidc_keycloak` | Bootstrap OIDC Auth - Keycloak | `source/openg2p-odoo-commons/g2p_auth_oidc_keycloak/__manifest__.py` | `['g2p_auth_oidc']` | Yes | `uninstalled` | Yes |
| `g2p_disable_password_login` | Disable Password Login | `source/openg2p-odoo-commons/g2p_disable_password_login/__manifest__.py` | `['g2p_auth_oidc']` | Yes | `uninstalled` | Yes |
| `g2p_documents_bootstrap_s3` | Bootstrap G2P Documents - S3 | `source/openg2p-odoo-commons/g2p_documents_bootstrap_s3/__manifest__.py` | `['g2p_documents']` | Yes | `uninstalled` | Yes |
| `spp_area` | OpenSPP Area Management | `source/pbms/odoo/community-addons/spp_area/__manifest__.py` | `['base', 'g2p_registry_base', 'g2p_registry_individual', 'g2p_registry_group', 'queue_job']` | **No** | `uninstalled` | Yes (blocked) |
| `spp_programs` | OpenSPP Programs | `source/pbms/odoo/community-addons/spp_programs/__manifest__.py` | `['base', 'web', 'g2p_registry_base', 'g2p_programs', 'spp_area', 'product', 'stock']` | **No** | `uninstalled` | Yes (blocked) |
| `spp_entitlement_cash` | OpenSPP Cash Entitlement | `source/pbms/odoo/community-addons/spp_entitlement_cash/__manifest__.py` | `['base', 'g2p_registry_base', 'g2p_programs', 'spp_programs']` | **No** | `uninstalled` | Yes (blocked) |
| `spp_entitlement_in_kind` | OpenSPP In-Kind Entitlement | `source/pbms/odoo/community-addons/spp_entitlement_in_kind/__manifest__.py` | `['base', 'g2p_registry_base', 'g2p_programs', 'spp_programs', 'product', 'stock', 'spp_service_points']` | **No** | `uninstalled` | Yes (blocked) |
| `spp_service_points` | OpenSPP Service Points Management | `source/pbms/odoo/community-addons/spp_service_points/__manifest__.py` | `['g2p_registry_base', 'phone_validation', 'spp_area']` | **No** | `uninstalled` | Yes (blocked) |

---

## 3. Installed Modules & Database State (Phase 3)

- **Total `ir_module_module` rows:** `676`
- **Installed modules:** `72` (including all 12 core PBMS/Registry/Commons/Queue/Storage modules listed above).
- **PBMS tables (`g2p_*`):** `45` tables present in `refugee_management_db` (including `g2p_register_refugee_individual`, `g2p_register_refugee_group`, `g2p_refugee_group_member`, `g2p_program_definition`, `g2p_enrollment_cycle`, `g2p_disbursement_cycle`, `g2p_beneficiary_list`, `g2p_benefit_codes`, `g2p_program_benefit_codes`).
- **Status:** **PASS** — Core PBMS is already installed in `refugee_management_db` from the Gate 6 restore. No missing dependencies exist for any installed module.

---

## 4. Missing Dependencies

- **For core PBMS (`g2p_pbms`, `g2p_pbms_program_access`, `g2p_registry_addon`, `g2p_registry_type_addon`, `pbms_theme_extension`):** **None** — 100% of dependencies are present and installed.
- **For optional OpenG2P Commons modules (`g2p_security`, `g2p_auth_oidc`, `g2p_auth_oidc_keycloak`, `g2p_disable_password_login`, `g2p_documents_bootstrap_s3`):** **None** — all dependencies (`auth_signup`, `password_security`, `auth_oauth`, `g2p_documents`) are available in the configured `addons_path`.
- **For legacy OpenSPP modules (`spp_area`, `spp_programs`, `spp_entitlement_cash`, `spp_entitlement_in_kind`, `spp_service_points`):** Missing `g2p_registry_base`, `g2p_registry_individual`, `g2p_registry_group`, and `g2p_programs`. These are **OpenG2P v1/v2 legacy modules**, not used by PBMS 3.1.0, and **must NOT be installed**.

---

## 5. External Service Dependency Matrix (Phase 4)

| Dependency | Classification | Available Locally (Standalone) | Notes |
|---|---|---|---|
| **PostgreSQL (`127.0.0.1:5543`)** | Required for Odoo startup | **PASS** (Listening) | Hosts `refugee_management_db` and `refugee_bgtask_db`. |
| **Redis (`127.0.0.1:6389`)** | Required only for specific integrations (Celery) | **PASS** (Listening) | Required when running PBMS Celery workers / beat producers. |
| **Celery Workers (`openg2p-bg-task-celery-workers`)** | Required only for specific integrations | **NOT TESTED** (Not running) | Needed for async eligibility, entitlement, and disbursement background processing. |
| **Celery Beat (`openg2p-bg-task-celery-beat-producers`)** | Required only for specific integrations | **NOT TESTED** (Not running) | Polls `pending` tasks in `refugee_management_db` and enqueues Celery tasks. |
| **PBMS Staff / Bene Portal APIs (`8150`)** | Optional / Integration | **NOT TESTED** (Not listening) | `source/pbms/apis/openg2p-pbms-staff-portal-api` & `openg2p-pbms-bene-portal-api`. |
| **G2P Bridge (`8102`)** | Required only for specific integrations (Disbursement) | **NOT TESTED** (Not listening) | Required only for external disbursement envelope/batch submission. |
| **Keycloak (`8180`)** | Optional | **NOT TESTED** (Not listening) | Needed only if `g2p_auth_oidc_keycloak` is enabled. |
| **ID Generator (`8140`)** | Optional | **NOT TESTED** (Not listening) | Not installed or referenced by Odoo PBMS. |
| **MinIO (`9100/9101`)** | Optional | **NOT TESTED** (Not listening) | Local filestore handles attachments; S3 only needed if `g2p_documents_bootstrap_s3` is enabled. |

---

## 6. Recommended Installation Order (Phase 5)

*Note: For `refugee_management_db`, steps 1–4 are already `installed`. This sequence applies to a fresh standalone DB initialization or targeted module refresh.*

| Order | Layer | Technical Name | Dependencies | Purpose | Expected Impact & Risks |
|---|---|---|---|---|---|
| **1** | Base Odoo | `base`, `web`, `base_setup`, `mail`, `auth_signup`, `website`, `phone_validation` | Core Odoo 17 | Core UI, auth, mail, website, phone validation | Low risk; foundational schema. |
| **2** | Commons / Infra | `component`, `server_environment`, `base_sparse_field`, `queue_job`, `storage_backend`, `storage_backend_s3`, `storage_file`, `spp_registry_data_source` | Layer 1 | Job queue runner, storage backends, config env | Low risk; creates `queue_job` and storage tables. |
| **3** | OpenG2P Commons | `g2p_app_filter`, `g2p_documents` | Layer 2 | App launcher filter and G2P document store | Low risk; document store integration. |
| **4** | PBMS Models & Core | `g2p_registry_type_addon` -> `g2p_pbms` -> `g2p_pbms_program_access` -> `g2p_registry_addon` -> `pbms_theme_extension` | Layers 1–3 | Registry types, PBMS programs/cycles/lists, program RBAC, Refugee Registry (`g2p.register.refugee_*`), PBMS theme | **Medium risk on fresh DB:** creates 45 `g2p_*` tables. **Duplicate path note:** `g2p_registry_addon` exists in both `extensions/` and `source/pbms/odoo/extensions/`; `extensions/` takes precedence. |
| **5** | Background Tasks (OS) | `openg2p-bg-task-models`, `openg2p-pbms-models`, `openg2p-bg-task-celery-workers`, `openg2p-bg-task-celery-beat-producers` | PostgreSQL `5543`, Redis `6389` | Async eligibility, entitlement, summary, and disbursement workers | Requires separate Python venv / service startup; must point `DB_*` and `CELERY_*` to `5543` and `6389`. |
| **6** | Optional Integrations | `g2p_security`, `g2p_auth_oidc`, `g2p_auth_oidc_keycloak`, `g2p_disable_password_login`, `g2p_documents_bootstrap_s3` | Keycloak (`8180`), MinIO (`9100`) | OIDC SSO, password policy, S3 document bootstrap | **High risk if misconfigured:** `g2p_disable_password_login` blocks local admin password login unless Keycloak is active. |

---

## 7. Backup and Recovery Strategy (Phase 6)

- **Backup Strategy:** Use `pg_dump -Fc` against standalone PostgreSQL (`127.0.0.1:5543`) for `refugee_management_db` and `refugee_bgtask_db`, plus `tar -czf` of the standalone filestore before any module install/upgrade. Store snapshots under `/Users/apple/refugee_management/database/backups/<TIMESTAMP>/` with SHA-256 checksums.
- **Standalone Filestore Location:** `/Users/apple/refugee_management/filestore/refugee_management_db` (`data_dir = /Users/apple/refugee_management` in `odoo.conf`).
- **Schema Impact:** Installing/upgrading PBMS modules on `refugee_management_db` is expected to be a no-op or minor view/data refresh for already-installed modules, whereas installing optional `g2p_security` / `g2p_auth_oidc*` adds auth/password-history columns.
- **Recovery Procedure:** If an install/upgrade fails:
  1. Stop standalone Odoo (`8169`).
  2. Drop and recreate `refugee_management_db` on port `5543` (`createdb -O refugee_user refugee_management_db`) and restore via `pg_restore --no-owner`.
  3. Restore `/Users/apple/refugee_management/filestore/refugee_management_db` from the pre-change `.tar.gz`.
  4. Never target legacy port `5433` or `pbmsdb`.

---

## 8. Proposed Installation / Verification Commands (NOT EXECUTED)

*Per task restrictions, none of the following commands were executed:*

```bash
# 1. Pre-change standalone backup (port 5543 ONLY)
mkdir -p /Users/apple/refugee_management/database/backups/pre_pbms_refresh
docker exec refugee_mgmt_postgres pg_dump -U postgres -Fc refugee_management_db > /Users/apple/refugee_management/database/backups/pre_pbms_refresh/refugee_management_db.dump

# 2. Refresh/verify PBMS modules on a fresh or existing standalone DB (port 5543 / 8169)
PYTHONPATH=/Users/apple/refugee_management/source/odoo17 \
  /Users/apple/refugee_management/venv/bin/python \
  /Users/apple/refugee_management/source/odoo17/odoo-bin \
  -c /Users/apple/refugee_management/infrastructure/configs/odoo.conf \
  -d refugee_management_db \
  -i g2p_app_filter,g2p_documents,g2p_registry_type_addon,g2p_pbms,g2p_pbms_program_access,g2p_registry_addon,pbms_theme_extension \
  --stop-after-init
```

---

## 9. Risks and Blockers

1. **Duplicate `g2p_registry_addon` Path (Medium):** Exists in both `extensions/g2p_registry_addon` and `source/pbms/odoo/extensions/g2p_registry_addon`. `extensions/` currently shadows `source/pbms/odoo/extensions/` due to `addons_path` ordering; edits to one will not reflect in the other.
2. **Legacy `spp_*` Addons Have Unmet Dependencies (Low):** `spp_area`, `spp_programs`, `spp_entitlement_cash`, `spp_entitlement_in_kind`, and `spp_service_points` cannot be installed (`g2p_registry_base`, `g2p_programs` absent) and must not be selected for installation.
3. **Celery Workers / Beat Not Running (Medium):** Async eligibility, entitlement, and disbursement list workers (`openg2p-bg-task-celery-workers`) are not yet running against `5543`/`6389`.
4. **OIDC Lockout Risk (High if enabled prematurely):** Do not install `g2p_disable_password_login` until standalone Keycloak (`8180`) is configured and tested.

---

## 10. Final Readiness Status

- **Odoo PBMS & Refugee Registry Core:** **PASS** — Already installed (`72` modules, `45` `g2p_*` tables) and serving on `http://127.0.0.1:8169` against `refugee_management_db` (`127.0.0.1:5543`).
- **Full PBMS Async & External Integrations:** **PARTIAL** — Redis (`6389`) is ready, but standalone Celery workers/beat, PBMS APIs (`8150`), and G2P Bridge (`8102`) are not yet started.
