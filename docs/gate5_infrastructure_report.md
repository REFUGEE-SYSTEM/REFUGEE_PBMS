# Gate 5 — Independent Infrastructure Report
**Project:** `refugee_management` Standalone Migration  
**Date:** 2026-11-26  
**Status:** Gate 5 Complete — Infrastructure Provisioned & Verified Healthy — Awaiting Approval for Gate 6  

---

## 1. Infrastructure Architecture

The standalone infrastructure for `refugee_management` is provisioned under an isolated Docker Compose project name (`refugee-management`) using dedicated bridge networking, isolated persistent volumes, and non-conflicting port bindings.

```
+-----------------------------------------------------------------------------------------+
| STANDALONE DOCKER INFRASTRUCTURE (refugee-management)                                  |
| Network: refugee_mgmt_net (172.x.x.x bridge)                                           |
|                                                                                         |
|  +--------------------------------+          +-------------------------------------+    |
|  | PostgreSQL 16 (Container)      |          | Redis 7 (Container)                 |    |
|  | - Name: refugee_mgmt_postgres  |          | - Name: refugee_mgmt_redis          |    |
|  | - Port: 5543:5432              |          | - Port: 6389:6379                   |    |
|  | - Volume: refugee_mgmt_pg_data |          | - Volume: refugee_mgmt_redis_data   |    |
|  | - DBs: refugee_management_db   |          | - Health: PONG (healthy)            |    |
|  |        refugee_bgtask_db       |          +-------------------------------------+    |
|  | - User: refugee_user           |                                                     |
|  | - Health: pg_isready (healthy) |                                                     |
|  +--------------------------------+                                                     |
+-----------------------------------------------------------------------------------------+
                               |
                               v
+-----------------------------------------------------------------------------------------+
| STANDALONE RUNTIME CONFIGURATION (infrastructure/configs/odoo.conf)                     |
| - Target HTTP Port: 8169                                                                |
| - Target Gevent Port: 8172                                                              |
| - Target DB: refugee_management_db on localhost:5543 (refugee_user)                     |
| - Addons Path: 100% project-internal paths (odoo17, pbms community & core, extensions) |
| - Filestore: /Users/apple/refugee_management/filestore                                  |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Docker Compose Configuration (`deployment/docker-compose.yml`)

The compose definition is configured with strict network, volume, and container separation:

```yaml
name: refugee-management

networks:
  refugee_mgmt_net:
    driver: bridge
    name: refugee_mgmt_net

volumes:
  refugee_mgmt_postgres_data:
    name: refugee_mgmt_postgres_data
  refugee_mgmt_redis_data:
    name: refugee_mgmt_redis_data
  refugee_mgmt_minio_data:
    name: refugee_mgmt_minio_data

services:
  postgres:
    image: postgres:16
    container_name: refugee_mgmt_postgres
    restart: unless-stopped
    networks:
      - refugee_mgmt_net
    environment:
      POSTGRES_USER: ${POSTGRES_SUPERUSER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_SUPERUSER_PASSWORD:-postgres_dev_master}
    ports:
      - "${POSTGRES_PORT:-5543}:5432"
    volumes:
      - refugee_mgmt_postgres_data:/var/lib/postgresql/data
      - ../infrastructure/postgres/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_SUPERUSER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    container_name: refugee_mgmt_redis
    restart: unless-stopped
    networks:
      - refugee_mgmt_net
    ports:
      - "${REDIS_PORT:-6389}:6379"
    volumes:
      - refugee_mgmt_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
```

*(Additional optional integration profiles for ID Generator, Keycloak, and MinIO are defined in the compose file under their respective profile flags).*

---

## 3. Pinned Image Versions & Dependency Evidence

All images are pinned to explicit major/minor releases; no floating `latest` image tags are used for primary infrastructure:

| Service | Pinned Image Version | Local Cache Status | Runtime Evidence & Justification |
|---|---|---|---|
| **PostgreSQL** | `postgres:16` | Present locally | Verified binary `16.15-1.pgdg13+2`. Matches legacy PBMS Postgres version. |
| **Redis** | `redis:7-alpine` | Present locally | Verified binary `7.4.12`. Matches legacy PBMS Redis version. |
| **ID Generator (Profile)** | `openg2p/openg2p-id-generator:1.0.0` | Present locally | Exact version pinned in OpenG2P local developer stack. |
| **Keycloak (Profile)** | `quay.io/keycloak/keycloak:26.0` | Present locally | Verified exact Keycloak major version. |

---

## 4. Odoo Addons Path Verification (`infrastructure/configs/odoo.conf`)

The configuration file was written to:  
`/Users/apple/refugee_management/infrastructure/configs/odoo.conf`

### Configured `addons_path`
```ini
addons_path = /Users/apple/refugee_management/source/odoo17/addons,/Users/apple/refugee_management/source/pbms/odoo/community-addons,/Users/apple/refugee_management/source/pbms/odoo,/Users/apple/refugee_management/extensions,/Users/apple/refugee_management/source/pbms/odoo/extensions,/Users/apple/refugee_management/source/openg2p-odoo-commons
```

### Path Resolution Audit
Every directory was inspected and confirmed to exist with discoverable Odoo addons:
1. `source/odoo17/addons`: **581 addons** (`base`, `web`, `contacts`, `hr`, `mail`, `portal`, etc.)
2. `source/pbms/odoo/community-addons`: **30 addons** (`queue_job`, `component`, `storage_backend`, `server_environment`, etc.)
3. `source/pbms/odoo`: **2 addons** (`g2p_pbms`, `g2p_pbms_program_access`)
4. `extensions`: **1 addon** (`g2p_registry_addon` — priority placement ensures custom Refugee Registry models take precedence)
5. `source/pbms/odoo/extensions`: **3 addons** (`pbms_theme_extension`, `g2p_registry_type_addon`, `g2p_registry_addon`)
6. `source/openg2p-odoo-commons`: **7 addons** (`g2p_app_filter`, `g2p_documents`, `g2p_security`, `g2p_auth_oidc`, etc.)

**Result:** Zero references outside `/Users/apple/refugee_management`.

---

## 5. Port Conflict Checks

| Port | Bound Process | Service | Conflict Status |
|---|---|---|:---:|
| **`5543`** | `refugee_mgmt_postgres` (PID 801 com.docker) | Standalone PostgreSQL | **NO CONFLICT** (Legacy PBMS is on `5433`) |
| **`6389`** | `refugee_mgmt_redis` (PID 801 com.docker) | Standalone Redis | **NO CONFLICT** (Legacy PBMS is on `6379`) |
| **`8169`** | Free (Unbound) | Standalone Odoo HTTP | **NO CONFLICT** (Legacy PBMS is on `8069`) |
| **`8172`** | Free (Unbound) | Standalone Odoo Gevent | **NO CONFLICT** (Legacy PBMS is on `8072`) |
| **`8150`** | Free (Unbound) | PBMS Staff Portal API | **NO CONFLICT** (Legacy PBMS is on `8050`) |
| **`8140`** | Free (Unbound) | OpenG2P ID Generator | **NO CONFLICT** (Legacy PBMS is on `8040`) |
| **`8180`** | Free (Unbound) | Keycloak | **NO CONFLICT** (Legacy PBMS is on `8080`) |

---

## 6. Database Isolation Evidence

The standalone PostgreSQL container was started and verified:

```sql
-- Queried inside refugee_mgmt_postgres on port 5543:
SELECT datname, pg_get_userbyid(datdba) FROM pg_database;
-- Result:
-- refugee_management_db | refugee_user
-- refugee_bgtask_db     | refugee_user
-- postgres              | postgres

-- Tested authenticated connection:
psql -U refugee_user -d refugee_management_db -c "SELECT current_user, current_database();"
-- Result:
-- current_user: refugee_user
-- current_database: refugee_management_db
```

### Strict Isolation Proof:
- `refugee_management_db` is currently an empty database initialized exclusively with schema ownership privileges.
- Zero tables from `pbmsdb` were copied or restored.
- The legacy PostgreSQL server on host port `5433` remains completely separate.

---

## 7. Container, Network & Volume Names

| Resource Type | Resource Name | Purpose |
|---|---|---|
| **Network** | `refugee_mgmt_net` | Dedicated Docker bridge network for standalone services |
| **Volume** | `refugee_mgmt_postgres_data` | Persistent storage for standalone PostgreSQL instance |
| **Volume** | `refugee_mgmt_redis_data` | Persistent storage for standalone Redis instance |
| **Container** | `refugee_mgmt_postgres` | Isolated PostgreSQL 16 container (Port `5543:5432`) |
| **Container** | `refugee_mgmt_redis` | Isolated Redis 7 container (Port `6389:6379`) |

---

## 8. Security Configuration

1. **Credentials**: New development credentials generated for `.env` (`refugee_user` / `refugee_dev_pass`, `postgres_dev_master`). None of the legacy PBMS passwords (`pbmspass`, `postgres`) are reused.
2. **File Permissions**: `.env` set to mode `0600` (`-rw-------`).
3. **Exclusions**: Confirmed that `.env` is ignored by Git in `/Users/apple/refugee_management/.gitignore`.

---

## 9. Existing PBMS Safety Verification

Immediately following the launch of `refugee_mgmt_postgres` and `refugee_mgmt_redis`, the existing PBMS environment was inspected:

| Legacy Verification Item | Verified Status | Result |
|---|---|:---:|
| **Legacy PostgreSQL (`localhost:5433`)** | Container `openg2p-postgres` running healthy | **PASS** |
| **Legacy `pbmsdb` Database** | Contains 3 individuals, 2 groups, 4 members, 6 programs | **PASS** |
| **Legacy `bgtaskdb` Database** | 13 relations intact | **PASS** |
| **Legacy Redis (`localhost:6379`)** | Container `openg2p-redis` running healthy | **PASS** |
| **Legacy Keycloak (`localhost:8080`)** | Container `openg2p-keycloak` running healthy | **PASS** |
| **Legacy ID Generator (`localhost:8040`)** | Container `openg2p-id-generator` running healthy | **PASS** |
| **Legacy Volumes** | `openg2p-developer_postgres_data` untouched | **PASS** |

---

## 10. Outstanding Issues

1. **Category H Attributes (H01, H02, H03)**:
   - As documented in Gate 4, Category H fields (Primary Phone, Phone Ownership, SIM Registration Status) remain documented as outstanding schema declarations. In Gate 6, we will provide the clean schema extension.
2. **Q04 Audit Trail**:
   - Model audit tracking relies on Odoo's core ORM audit logging (`create_uid`, `write_date`, `create_date`). Additional model audit tracking will be confirmed during Gate 6/7.

---

## 11. Recommended Gate 6 Scope

With isolated infrastructure and database containers verified healthy:
1. Initialize the Odoo Python runtime environment for `refugee_management`.
2. Migrate and populate `refugee_management_db` from the verified Gate 2 backup (`pbmsdb.dump`), updating internal Odoo system parameters (`web.base.url`, `g2p_pbms.staff_portal_api_url`) to point to the standalone `:8169` and `:8150` ports.
3. Install/upgrade `g2p_registry_addon` and core PBMS modules.
4. Verify Odoo web interface login and initial refugee registry navigation at `http://localhost:8169`.

---
*End of Gate 5 Infrastructure Report. Awaiting user approval to proceed to Gate 6.*
