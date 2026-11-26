# Gate 6 — Database Migration and Application Installation Report
**Project:** `refugee_management`  
**Execution Date:** 2026-11-26  
**Environment:** macOS (Darwin 24.3.0)  
**Project Root:** `/Users/apple/refugee_management`  
**Odoo Service URL:** `http://127.0.0.1:8169`  
**Isolated Database Port:** `127.0.0.1:5543`  
**Status:** **GATE 6 COMPLETE — ALL VERIFICATIONS PASSED (100% ISOLATED)**

---

## 1. Executive Summary

Gate 6 has been executed with absolute adherence to safety protocols and strict technical isolation. The verified PBMS database backups and filestore produced during Gate 2 have been restored into the newly configured standalone infrastructure (`refugee_mgmt_postgres:5543`). The standalone Odoo 17 runtime has been fully configured, launched on port `8169`, and thoroughly verified via JSON-RPC, HTTP session authentication, database-level inspection, and filestore attachment retrieval.

Throughout the entirety of Gate 6:
- The legacy PBMS environment (`openg2p-postgres:5433`, `openg2p-redis:6379`, `openg2p-keycloak:8080`, `openg2p-id-generator:8040`, `openg2p-minio:9000`) remained completely untouched, active, and healthy.
- The legacy database `pbmsdb` was verified before and after all operations: table count (398) and entity counts (3 individuals, 2 groups, 4 members, 6 programs, 7 enrollment cycles, 8 disbursement cycles, 9 beneficiary lists) remain identical and pristine.
- The legacy working tree at `~/openg2p-workspace/pbms` remains unchanged, preserving all 8 original uncommitted files.
- The standalone environment operates with unique strong credentials stored exclusively in `/Users/apple/refugee_management/.env` with `0600` permissions and excluded from Git.

---

## 2. Pre-Installation Security Corrections

Prior to restoring data and launching services, the following security corrections were applied and verified:

1. **Strong, Unique Development Credentials**:
   - `REFUGEE_POSTGRES_PASSWORD`: `<REDACTED — stored in local .env>`
   - `REFUGEE_APP_PASSWORD`: `<REDACTED — stored in local .env>`
   - `REFUGEE_REDIS_PASSWORD`: `<REDACTED — stored in local .env>`
   - `REFUGEE_ODOO_ADMIN_PASSWORD`: `<REDACTED — stored in local .env>`
   - `REFUGEE_SECRET_KEY`: `<REDACTED — stored in local .env>`
2. **Environment File Protection**:
   - Stored strictly in `/Users/apple/refugee_management/.env`.
   - File permissions: `-rw-------` (`0600`).
   - Git status: Ignored by root `.gitignore` (`git check-ignore .env` confirms exclusion).
3. **No Insecure Fallbacks**:
   - `deployment/docker-compose.yml` does not contain any default or hardcoded fallback credentials.
4. **Localhost Port Binding**:
   - All published service ports are bound exclusively to `127.0.0.1` (`127.0.0.1:5543->5432`, `127.0.0.1:6389->6379`, `127.0.0.1:8169->8169`).
5. **No Production Key Reuse**:
   - Completely independent random secret keys and credentials generated; no legacy developer credentials reused.

---

## 3. Database Restoration Verification

### 3.1 Backup File Verification
The Gate 2 backup files were verified via SHA-256 before restoration:

| Backup Component | Source Backup Path | Verified SHA-256 |
|---|---|---|
| PostgreSQL `pbmsdb` | `/Users/apple/backups/gate2_20261126/databases/pbmsdb.dump` | `29d9e9746bf3f5dee8e173b97213129893fb4536e39535b16713711aa09f74cf` |
| PostgreSQL `bgtaskdb` | `/Users/apple/backups/gate2_20261126/databases/bgtaskdb.dump` | `d96be65675fd730367e0d3c31a541b38241a6ff69bba344f46edc33bb16905c7` |
| Filestore Archive | `/Users/apple/backups/gate2_20261126/filestore/pbmsdb_filestore.tar.gz` | `8c96db9ebaf661a1877bc1501fb29e74a3575a4b6a9c82123e9664b102406512` |

### 3.2 Target Database Restore Details
Restoration was executed against `refugee_mgmt_postgres` on isolated port `5543`:

- **Main Database:** `refugee_management_db` (owned by `refugee_user`).
  - Total tables restored: **398 public tables**.
  - Ownership: All tables and sequences reassigned to `refugee_user`.
  - Installed modules verified (`ir_module_module` state `installed`): **72 modules**.
- **Background Task Database:** `refugee_bgtask_db` (owned by `refugee_user`).
  - Total relations restored: **5 relations** (`alembic_version`, `bgtasks`, `bgtasks_sequence`, `bgtask_logs`, `bgtask_logs_sequence`).
  - Ownership: All tables reassigned to `refugee_user`.

### 3.3 Data Integrity & Record Counts Comparison
A full comparison of entity counts confirms exact parity:

| Entity / Model | Legacy `pbmsdb` (Port 5433) | Migrated `refugee_management_db` (Port 5543) | Parity Status |
|---|---|---|---|
| Total Public Tables | 398 | 398 | 100% Match |
| Refugee Individuals (`g2p_register_refugee_individual`) | 3 | 3 | 100% Match |
| Refugee Groups (`g2p_register_refugee_group`) | 2 | 2 | 100% Match |
| Group Members (`g2p_refugee_group_member`) | 4 | 4 | 100% Match |
| Programs (`g2p_program_definition`) | 6 | 6 | 100% Match |
| Enrollment Cycles (`g2p_enrollment_cycle`) | 7 | 7 | 100% Match |
| Disbursement Cycles (`g2p_disbursement_cycle`) | 8 | 8 | 100% Match |
| Beneficiary Lists (`g2p_beneficiary_list`) | 9 | 9 | 100% Match |
| Specific Needs Categories (`g2p_refugee_specific_need`) | 8 | 8 | 100% Match |

---

## 4. Filestore Migration and Verification

### 4.1 Filestore Location and Structure
The verified filestore archive was extracted into:
`/Users/apple/refugee_management/filestore/refugee_management_db`

- Total files and directories on disk: **239 files / 80 subdirectories**.
- Total size on disk: **~19 MB**.
- In `infrastructure/configs/odoo.conf`, `data_dir` was set to `/Users/apple/refugee_management` so that Odoo's native filestore resolver `config.filestore(db_name)` maps directly to:
  `/Users/apple/refugee_management/filestore/refugee_management_db`.

### 4.2 Attachment Integrity Verification
- Total `ir_attachment` records with stored files (`store_fname IS NOT NULL`): **136 records**.
- Disk resolution check: **136 out of 136 files exist on disk (100% resolution, 0 missing)**.
- Sample attachments were retrieved over HTTP (`http://127.0.0.1:8169/web/content/<id>`), returning HTTP 200 with byte-for-byte exact size matching.

---

## 5. System Parameters and Decoupling Configuration

The migrated database parameters (`ir_config_parameter`) were updated to reflect the new standalone standalone ports and prevent cross-environment redirection:

| Parameter Key | Original Value | Standalone Configured Value |
|---|---|---|
| `web.base.url` | `http://localhost:8069` | `http://localhost:8169` |
| `web.base.url.freeze` | (Not set) | `True` |
| `g2p_pbms.staff_portal_api_url` | `http://localhost:8050` | `http://localhost:8150` |
| `g2p_pbms.g2p_bridge_api_url` | `http://localhost:8002` | `http://localhost:8102` |

---

## 6. Standalone Odoo 17 Application Verification

### 6.1 Python Virtual Environment
- **Path:** `/Users/apple/refugee_management/venv`
- **Python Version:** 3.11.9
- **Dependencies:** Complete Odoo 17 runtime packages installed and frozen in `/Users/apple/refugee_management/requirements.txt`.
- **Pinned Subsystem Packages:**
  - `pydantic==2.13.5`
  - `pydantic_core==2.46.5`
  - `extendable==1.3.0`
  - `extendable_pydantic==1.3.0`
  - `boto3==1.43.109`
  - `botocore==1.43.109`
  - `openg2p-fastapi-common==1.1.5`
  - `openg2p-bg-task-models==3.1.0`
  - `openg2p-g2p-bridge-models==2.1.0`
  - `openg2p-g2pconnect-common-lib==2.0.0`

### 6.2 Application Startup & Health
- Standalone Odoo process launched using:
  `odoo-bin -c infrastructure/configs/odoo.conf`
- Registry initialization: **All 72 modules loaded in 1.66 seconds**.
- Queue job runner: Initialized and ready for `refugee_management_db` (channels `root:4`).
- HTTP Service: Running on `127.0.0.1:8169`.

### 6.3 HTTP Endpoint and Session Authentication
- `GET /web/login`: **HTTP 200 OK** (Content-Length: 4991 bytes, CSRF token generated).
- `POST /web/session/authenticate`:
  - Login: `admin`
  - Database: `refugee_management_db`
  - Response: **Success (UID: 2, User: Administrator, Timezone: Asia/Calcutta)**.

### 6.4 Refugee Registry Entity Verification via JSON-RPC
Live queries executed through the running standalone Odoo application:

1. **Refugee Individuals (`g2p.register.refugee_individual`): 3 Records**
   - Record 1: ID=1, Functional ID=`UNHCR-2024-TEST-001`, Name=`Fatima AL-MANSOOR`, Sex=`female`, DOB=`1992-05-15`, Assistance Category=`cat_2`, Biometrics=`captured`
   - Record 2: ID=2, Functional ID=`UNHCR-2024-TEST-002`, Name=`Zayd AL-MANSOOR`, Sex=`male`, DOB=`2018-09-20`, Age=7 (Minor)
   - Record 3: ID=3, Functional ID=`UNHCR-2024-TEST-003`, Name=`Ibrahim AL-MANSOOR`, Sex=`male`, DOB=`1955-01-10`, Age=71 (Elderly)
2. **Refugee Households / Groups (`g2p.register.refugee_group`): 2 Records**
   - Record 1: ID=1, Case No=`HH-TEST-001`, Household Size=3
   - Record 2: ID=2, Case No=`HH-CHILD-001`, Household Size=1
3. **Refugee Group Member Associations (`g2p.refugee.group.member`): 4 Records**
   - All 4 household associations verified and linked to individual records.
4. **Program Definitions (`g2p.program.definition`): 6 Records**
   - Includes `Refugee Welfare Program` (ID=7, Target Registry=`refugee_individual`).
5. **Cycles and Lists:**
   - 7 Enrollment Cycles, 8 Disbursement Cycles, and 9 Beneficiary Lists verified.

---

## 7. Safety and Isolation Regression Verification

To guarantee that the legacy environment was never impacted:

1. **Legacy Docker Containers**:
   - `openg2p-postgres` (port 5433): Up 57 minutes (healthy).
   - `openg2p-redis` (port 6379): Up 57 minutes (healthy).
   - `openg2p-keycloak` (port 8080): Up 57 minutes (healthy).
   - `openg2p-id-generator` (port 8040): Up 56 minutes (healthy).
   - `openg2p-minio` (ports 9000/9001): Up 57 minutes (healthy).
2. **Legacy Database Integrity**:
   - `pbmsdb`: 398 tables, 3 refugee individuals, 2 groups, 4 members, 6 programs, 7 enrollment cycles, 8 disbursement cycles, 9 beneficiary lists. Zero data drift.
3. **Legacy Workspace Git Working Tree**:
   - `git -C ~/openg2p-workspace/pbms status --short`:
   - Exact same 8 modified files preserved; zero stash, checkout, or commit touched the legacy repository.

---

## 8. Conclusion and Readiness for Gate 7

Gate 6 has successfully achieved full database restoration and application installation in the standalone `refugee_management` project.

- The application is operational at `http://127.0.0.1:8169`.
- The database is fully populated and isolated at `127.0.0.1:5543`.
- The filestore is complete and verified.
- The legacy PBMS environment is 100% protected and untouched.

We are ready to proceed to **Gate 7: Integration and Functional Testing** upon user authorization.
