# Dependencies Catalog — Refugee Management Standalone Project

This document catalogs all dependencies required by the standalone `refugee_management` project.

---

## 1. System Prerequisites
- **Operating System**: Linux (Ubuntu 22.04+ recommended) or macOS (Apple Silicon / Intel).
- **Container Engine**: Docker 24.0+ and Docker Compose v2.20+.
- **Python**: Python 3.11.x (for native/hybrid execution; 3.11.9 verified).
- **PostgreSQL Client**: `psql` and `pg_dump` version 16.x.

---

## 2. Infrastructure Dependencies (Containerized)

| Component | Target Image | Standalone Port | Role & Classification |
|---|---|---:|---|
| **PostgreSQL** | `postgres:16` | **5543** | Primary database server (Mandatory) |
| **Redis** | `redis:7-alpine` | **6389** | Broker for Odoo queue_job and Celery (Mandatory) |
| **OpenG2P ID Generator** | `openg2p/openg2p-id-generator:1.0.0` | **8140** | Unique identifier service (Optional / Integration) |
| **Keycloak** | `quay.io/keycloak/keycloak:26.0` | **8180** | IAM and SSO Authentication (Optional / Integration) |
| **MinIO S3** | `quay.io/minio/minio:latest` | **9110 / 9111** | S3 object store (Optional; defaults to filesystem) |

---

## 3. Odoo Framework & Modules

### A. Odoo Framework Core
- **Repository**: `odoo17` (Branch `17.0`, Commit `436b018af565`)

### B. OpenG2P PBMS Core Modules
- **Repository**: `pbms` (Branch `feature/refugee-registry-templates`, Commit `4c0173a1d5e2` + Working Tree Patches)
  - `g2p_pbms`
  - `g2p_pbms_program_access`
  - `g2p_registry_addon` (Custom Refugee Registry module)
  - `g2p_registry_type_addon`
  - `pbms_theme_extension`

### C. OpenG2P Shared Commons
- **Repository**: `openg2p-odoo-commons` (Branch `develop`, Commit `b5a68cd082f9`)
  - `g2p_app_filter`
  - `g2p_documents`
  - `g2p_security`

### D. OCA Community Addons (39 Modules in PBMS)
- `queue_job`
- `component`
- `server_environment`
- `storage_backend`
- `storage_backend_s3`
- `storage_file`
- `spp_registry_data_source`

---

## 4. Python Package Dependencies
Key Python packages managed in virtualenv / container:
- `fastapi==0.112.2`
- `uvicorn==0.34.0`
- `celery>=5.3.0`
- `psycopg2>=2.9.5`
- `asyncpg>=0.29.0`
- `pydantic>=2.10.0`
- `boto3>=1.34.0` (modern pin preventing urllib3 regressions)
- `gevent==22.10.2`
