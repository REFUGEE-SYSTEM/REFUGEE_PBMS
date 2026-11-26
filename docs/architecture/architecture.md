# Architecture Specification — Refugee Management Standalone Project

## 1. System Topology

The standalone `refugee_management` project provides an isolated, containerized or hybrid-capable execution architecture that mirrors the capabilities of OpenG2P PBMS without relying on external developer harnesses.

```
+-----------------------------------------------------------------------------------------+
| REFUGEE MANAGEMENT STANDALONE RUNTIME (refugee-management)                              |
|                                                                                         |
|  +-----------------------------+           +-------------------------------------+      |
|  | Odoo 17 Application Server  | --------> | PostgreSQL 16 (Container)           |      |
|  | - Port :8169                |           | - Port :5543                        |      |
|  | - Database: refugee_mgmt_db |           | - Database: refugee_management_db   |      |
|  | - Extensions: g2p_registry  |           | - Volume: refugee_mgmt_postgres_data|      |
|  +-----------------------------+           +-------------------------------------+      |
|                |                                              |                         |
|                v                                              |                         |
|  +-----------------------------+                              |                         |
|  | PBMS Staff Portal API       | -----------------------------+                         |
|  | - Port :8150 (FastAPI)      |                                                        |
|  +-----------------------------+                                                        |
|                |                                                                        |
|                v                                                                        |
|  +-----------------------------+           +-------------------------------------+      |
|  | Celery Background Workers   | --------> | Redis 7 (Container)                 |      |
|  | - Queue: bg_task_queue      |           | - Port :6389                        |      |
|  | - Beat: periodic sync       |           | - Volume: refugee_mgmt_redis_data   |      |
|  +-----------------------------+           +-------------------------------------+      |
|                                                                                         |
|  +-----------------------------+           +-------------------------------------+      |
|  | SPAR Mapper API (Optional)  |           | G2P Bridge Payment API (Optional)   |      |
|  | - Port :8104                |           | - Port :8102                        |      |
|  +-----------------------------+           +-------------------------------------+      |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### A. Refugee Registry Extension (`g2p_registry_addon`)
The core domain model extending OpenG2P PBMS to support refugee registry operations:
- **`g2p.register.refugee_individual`**: Captures individual demographic, identity document, biometric reference, legal status/RSD, Washington Group disability domains, and vulnerability attributes.
- **`g2p.register.refugee_group`**: Captures household/case units, settlement and dwelling coordinates, livelihood indicators, and computed dependency ratios.
- **`g2p.refugee.group.member`**: Relational membership linking individuals to households with relationship codes and presence statuses.

### B. PBMS Core Subsystem (`g2p_pbms`)
- Program Definitions and enrollment cycles.
- Entitlement calculations and targeting rules.
- Disbursement cycles, payment transaction tracking, and reconciliation.

### C. Background Task Subsystem
- FastAPIs executing dynamic registry searches and batch generation.
- Celery workers handling asynchronous enrollment and disbursement pipelines without blocking the Odoo web worker threads.

---

## 3. Decoupling & Isolation Principles

1. **No Shared Docker Network**: Uses a dedicated bridge network (`refugee_mgmt_net`).
2. **No Shared Volumes**: Uses dedicated persistent volumes (`refugee_mgmt_postgres_data`, etc.).
3. **No Database Cross-Talk**: Operates exclusively against `refugee_management_db`.
4. **No Shared Filestore**: Uses a project-local filestore directory.
5. **No Relative Path Traversal**: Zero references to sibling folders or `openg2p-developer`.
