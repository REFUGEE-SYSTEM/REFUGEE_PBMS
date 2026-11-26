# Vendored & Image Versions

- **PBMS Odoo Base Image**: `openg2p/openg2p-pbms-core@sha256:6b4d4a40b11644ec9cb5133bfcd622aca45aa6ecd71880b9f92db149450a86f8` (Odoo `17.0-20250807`)
- **Vendored PBMS Workspace (`vendor/pbms/`)**: copied from `openg2p-workspace/pbms` commit `aa1ce60`:
  - `openg2p-bg-task-models`
  - `openg2p-pbms-models`
  - `openg2p-bg-task-registry-adapters` (extended with `RegisterRefugee`)
  - `openg2p-pbms-staff-portal-api`
  - `openg2p-bg-task-celery-beat-producers`
  - `openg2p-bg-task-celery-workers`
- **Vendored G2P Bridge Models (`vendor/pbms/openg2p-g2p-bridge-models`)**: copied from `openg2p-workspace/g2p-bridge/core/models` (required by `openg2p_bg_task_celery_workers` imports).
- **OpenG2P Odoo Commons Reference**: `openg2p-odoo-commons` commit `b5a68cd` (baked into `openg2p/openg2p-pbms-core`).
- **OpenG2P FastAPI Common**: `openg2p-fastapi-common==1.1.6`, `openg2p-fastapi-auth==1.1.6`, `openg2p-fastapi-auth-models==1.1.6` (PyPI).
