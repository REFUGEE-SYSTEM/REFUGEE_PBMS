# Refugee Management Standalone Project (`refugee_management`)

An independent, standalone OpenG2P Programme Beneficiary Management System (PBMS) and Refugee Registry built on **Odoo 17.0** and **OpenG2P PBMS 3.1.0**, tailored for refugee assistance programmes in Uganda (UGX).

---

## 1. Project Purpose & Standalone Architecture

`refugee_management` provides a self-contained runtime and source tree decoupled from `openg2p-developer`, with dedicated containers, databases, filestore, Python virtual environment, and isolated localhost port bindings:

- **Application Server:** Odoo 17.0 (`127.0.0.1:8169`, Gevent `8172`)
- **Database:** PostgreSQL 16 (`127.0.0.1:5543`) hosting `refugee_management_db` and `refugee_bgtask_db`
- **Cache / Broker:** Redis 7 (`127.0.0.1:6389`)
- **Extensions:** `extensions/g2p_registry_addon` (Refugee Individual/Group/Specific Needs models, Refugee-only Program Base Registry dropdown, Uganda `UGX` currency configuration)
- **Background Workers:** `source/pbms/core/openg2p-bg-task-celery-workers` (including **DEF-03** fix and unit tests)

---

## 2. Repository Directory Structure

```text
refugee_management/
├── README.md                          # Project overview, setup, and operations guide
├── Makefile                           # Unified developer commands
├── .env.example                       # Sanitized environment variable template
├── .gitignore                         # Excludes .env, odoo.conf, venv, filestore, dumps, logs
├── requirements.txt                   # Pinned Python 3.11 dependencies
├── docs/                              # Architecture, setup, and Gate 4-8 / implementation reports
├── source/
│   ├── odoo17/                        # Odoo 17.0 core framework & addons
│   ├── pbms/                          # OpenG2P PBMS 3.1.0 (Odoo addons, APIs, Celery workers)
│   └── openg2p-odoo-commons/          # OpenG2P shared Odoo modules
├── extensions/
│   └── g2p_registry_addon/            # Custom Refugee Registry, UGX currency & PBMS extensions
├── infrastructure/
│   ├── configs/odoo.conf.example      # Sanitized Odoo configuration template
│   └── postgres/init/                 # PostgreSQL initialization SQL
├── deployment/
│   └── docker-compose.yml             # Standalone PostgreSQL, Redis, and optional services
├── scripts/                           # Operational script placeholders
├── database/backups/                  # Local backup directory (contents gitignored)
└── logs/                              # Runtime logs directory (contents gitignored)
```

---

## 3. Prerequisites

- Python `3.11.9`
- Docker & Docker Compose
- PostgreSQL client tools (`pg_dump`, `pg_restore`)
- Git

---

## 4. Environment, Database & Redis Configuration

1. **Create `.env` from template** (never commit `.env`):
   ```bash
   cp .env.example .env
   chmod 600 .env
   # Set strong unique values for POSTGRES_SUPERUSER_PASSWORD, POSTGRES_PASSWORD, ODOO_ADMIN_PASSWORD, etc.
   ```
2. **Create `infrastructure/configs/odoo.conf` from template** (never commit `odoo.conf`):
   ```bash
   cp infrastructure/configs/odoo.conf.example infrastructure/configs/odoo.conf
   # Update admin_passwd, db_password, and absolute paths for addons_path / data_dir
   ```
3. **Database & Redis ports (isolated from legacy defaults):**
   - PostgreSQL: `127.0.0.1:5543` (`refugee_management_db`, `refugee_bgtask_db`)
   - Redis: `127.0.0.1:6389`

### Configured Addon Paths (`odoo.conf`)
```text
source/odoo17/addons,
source/pbms/odoo/community-addons,
source/pbms/odoo,
extensions,
source/pbms/odoo/extensions,
source/openg2p-odoo-commons
```
*(Note: `extensions/g2p_registry_addon` takes precedence over `source/pbms/odoo/extensions/g2p_registry_addon`.)*

---

## 5. Installation & Startup Procedure

```bash
# 1. Start standalone PostgreSQL (5543) and Redis (6389)
docker compose -f deployment/docker-compose.yml up -d postgres redis

# 2. Create Python 3.11 virtual environment and install dependencies
python3.11 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Initialize or start standalone Odoo 17 on port 8169
PYTHONPATH=$PWD/source/odoo17 ./venv/bin/python source/odoo17/odoo-bin -c infrastructure/configs/odoo.conf
```

Access the application at `http://127.0.0.1:8169`.

---

## 6. Testing Procedure

- **DEF-03 Worker Unit Tests:**
  ```bash
  ./venv/bin/python -m unittest discover -s source/pbms/core/openg2p-bg-task-celery-workers/tests -v
  ```
- **Additional validation suites and Gate 4–8 reports** are documented under [`docs/`](docs/).

---

## 7. Refugee Registry Features & UGX Support

- **Refugee Individual & Group Registries:** `g2p.register.refugee_individual`, `g2p.register.refugee_group`, `g2p.refugee.group.member`, `g2p.refugee.specific_need` (96/100 Data Dictionary attributes implemented).
- **Refugee-Only Program Base Registry:** `g2p.program.definition.target_registry` restricted to `refugee_individual` and `refugee_group`; `Registry Models` navigation menus hidden by configuration.
- **Ugandan Shilling (UGX):** `UGX` (`USh`, 0 decimal places, rounding `1.0`) activated in `res.currency`, `currency_id` added to `g2p.program.definition`, and `BenefitUnitWidget` patched to support `UGX`.

---

## 8. Known Limitations & Integration Notes

- **Optional Microservices Disabled by Default:** Celery workers/beat, PBMS Staff Portal API (`8150`), G2P Bridge API (`8102`), Keycloak (`8180`), ID Generator (`8140`), and MinIO (`9100`) are not started in the base Odoo-only run; async disbursement envelope/batch/reconciliation workflows require starting those services.
- **Pending Data Dictionary Attributes:** `H01`–`H03` (Telephone & Digital Connectivity) and field-level temporal audit history (`Q04`) are designed in Gate 8 Phase 5 and pending implementation.
- **DEF-03 Retry Behavior:** `beneficiary_list_worker.py` raises `ValueError` for missing approved final enrollment lists; Celery Beat retries `Exception` subclasses up to `worker_max_attempts` unless classified as non-retryable.
