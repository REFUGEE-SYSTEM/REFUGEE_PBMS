# Refugee Management Standalone Project (`refugee_management`)

An independent, standalone OpenG2P Social Registry and Programme Beneficiary Management System (PBMS) tailored for comprehensive Refugee Management.

---

## 1. Project Overview

The `refugee_management` project provides a fully self-contained runtime environment for managing:
- Individual Refugee Registration & Identification
- Household / Group Composition & Dependency Analysis
- All 100 Refugee Management Data Dictionary Attributes (Categories A–Q)
- Vulnerability Assessment, Targeting & Scoring
- Programme Enrolment & Lifecycle Management
- Entitlements, Assistance Delivery & Reconciliation

This project is decoupled from the legacy `openg2p-developer` runtime and operates with its own dedicated infrastructure, database, filestore, and network configurations.

---

## 2. Directory Structure

```text
refugee_management/
├── README.md                          # Project overview and quick start
├── Makefile                           # Unified developer commands
├── .env.example                       # Standalone configuration template
├── .gitignore                         # Git exclusion rules
│
├── docs/                              # Architecture and operation documentation
│   ├── architecture.md                # System topology and component interactions
│   ├── dependencies.md                # Component and package catalog
│   ├── installation.md                # Setup and deployment procedure
│   ├── migration.md                   # Source and data migration guide
│   ├── backup_restore.md              # Independent backup and recovery procedure
│   ├── testing.md                     # Validation suites and test results
│   └── migration_inventory.md         # Exact asset tracking and coupling analysis
│
├── source/                            # Self-contained application sources (Gate 4)
│   ├── odoo17/                        # Odoo 17 Core Framework
│   ├── openg2p-odoo-commons/          # Shared OpenG2P modules
│   └── pbms/                          # PBMS monorepo & community addons
│
├── extensions/                        # Custom domain extensions
│   └── g2p_registry_addon/            # Refugee Registry customization module
│
├── infrastructure/                    # Standalone container and service configs
│   ├── docker/                        # Docker Compose definitions (Gate 5)
│   ├── postgres/                      # PostgreSQL init scripts & schemas
│   ├── redis/                         # Redis cache/broker configurations
│   ├── keycloak/                      # Identity & realm configurations
│   ├── minio/                         # S3 storage configurations
│   └── configs/                       # Application runtime configurations
│
├── deployment/                        # Standalone deployment profiles
├── scripts/                           # Operational management scripts
├── database/
│   ├── backups/                       # Local backup snapshots
│   └── migration/                     # Schema and migration SQL scripts
├── tests/                             # Test suites across 7 verification gates
└── logs/                              # Service runtime logs
```

---

## 3. Dedicated Port Mapping

The standalone project uses a distinct port space to ensure full coexistence with any existing OpenG2P instances:

| Service | Legacy PBMS Port | Standalone Port | Endpoint |
|---|---|---|---|
| **Odoo HTTP** | 8069 | **8169** | `http://localhost:8169` |
| **Odoo Gevent** | 8072 | **8172** | `http://localhost:8172` |
| **PostgreSQL** | 5433 | **5543** | `localhost:5543` |
| **Redis** | 6379 | **6389** | `localhost:6389` |
| **PBMS Staff Portal API** | 8050 | **8150** | `http://localhost:8150/docs` |
| **OpenG2P ID Generator** | 8040 | **8140** | `http://localhost:8140/docs` |
| **Keycloak (Optional)** | 8080 | **8180** | `http://localhost:8180` |
| **MinIO S3 API (Optional)** | 9000 | **9110** | `http://localhost:9110` |
| **MinIO S3 Console** | 9001 | **9111** | `http://localhost:9111` |
| **G2P Bridge API** | 8002 | **8102** | `http://localhost:8102/docs` |
| **SPAR Mapper API** | 8004 | **8104** | `http://localhost:8104/docs` |

---

## 4. Current Migration Status

- [x] **Gate 1 — Existing Environment Investigation**: Completed.
- [x] **Gate 2 — Protection and Backup**: Completed. Verified backups stored in `/Users/apple/backups/gate2_20261126/`.
- [x] **Gate 3 — Project Structure & Independent Git**: In Progress (Structure initialized; source migration planned for Gate 4).
- [ ] **Gate 4 — Source Code Migration**: Pending.
- [ ] **Gate 5 — Independent Infrastructure**: Pending.
- [ ] **Gate 6 — Database & Application Installation**: Pending.
- [ ] **Gate 7 — Integration & Functional Testing**: Pending.
- [ ] **Gate 8 — Independence & Final Acceptance**: Pending.
