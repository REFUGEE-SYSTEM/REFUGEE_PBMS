# Migration Guide — Existing PBMS to `refugee_management`

## 1. Migration Strategy Overview

This migration is a safe, non-destructive extraction of the existing customized PBMS application from the `openg2p-developer` workspace into `~/refugee_management`.

The key constraint is **strict non-interference**: the existing PBMS remains live, operational, and untouched.

---

## 2. Decoupling the 5 Coupling Points

| # | Existing Coupling Point | Problem in Legacy Environment | Standalone Resolution in `refugee_management` |
|---|---|---|---|
| **1** | **Odoo `addons_path`** | Hardcoded relative paths (`../openg2p-workspace/...`) and absolute host paths | Self-contained paths relative to `~/refugee_management/source` and `~/refugee_management/extensions` |
| **2** | **Startup Script Sourcing** | `pbms-odoo.sh` and `run-pbms.sh` traverse up to `openg2p-developer` | Self-contained management scripts in `scripts/` using project-local `.env` |
| **3** | **Dynamic API URL Injection** | Shell scripts inject legacy ports `8050` and `8002` into Odoo DB on boot | Odoo system parameters configured to point to standalone ports `8150` and `8102` |
| **4** | **Background Task PYTHONPATH** | Celery worker scripts reference `openg2p-developer/scripts` | Dedicated Celery worker entrypoints housed within `~/refugee_management/source/pbms` |
| **5** | **Cryptographic Signing Keys** | Envs reference `/Users/apple/openg2p-workspace/g2p-bridge/test/keys` | Independent keys located inside `~/refugee_management/infrastructure/configs/keys` |

---

## 3. Data Migration Principles

1. **Never use the original database directly**: `pbmsdb` on port `5433` is read-only for migration.
2. **Restore from verified dump**: The new database `refugee_management_db` on port `5543` will be populated from `/Users/apple/backups/gate2_20261126/databases/pbmsdb.dump`.
3. **Filestore copy**: Filestore will be restored from `/Users/apple/backups/gate2_20261126/filestore/pbmsdb_filestore.tar.gz` into `~/refugee_management/filestore`.
4. **Update System Parameters**: Post-migration SQL script will update `web.base.url`, `g2p_pbms.staff_portal_api_url`, and other parameter records to match the `:81xx` port scheme.
