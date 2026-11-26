# Migration Inventory & Dependency Analysis — Refugee Management

**Project:** `refugee_management`  
**Date:** 2026-11-26  
**Status:** Baseline Established (Gate 3)  

---

## 1. Source Repositories to Migrate (Gate 4)

| Repository | Source Location | Git Branch | Commit SHA | Target Path in `refugee_management` |
|---|---|---|---|---|
| **Odoo 17 Core** | `~/openg2p-workspace/odoo17` | `17.0` | `436b018af565` | `source/odoo17/` |
| **PBMS Monorepo** | `~/openg2p-workspace/pbms` | `feature/refugee-registry-templates` | `4c0173a1d5e2` | `source/pbms/` |
| **OpenG2P Commons** | `~/openg2p-workspace/openg2p-odoo-commons` | `develop` | `b5a68cd082f9` | `source/openg2p-odoo-commons/` |
| **Refugee Registry Addon** | `~/openg2p-workspace/pbms/odoo/extensions/g2p_registry_addon` | *(Uncommitted working tree)* | `4c0173a1d5e2` + 8 files | `extensions/g2p_registry_addon/` |

---

## 2. Uncommitted Working Tree Customizations to Preserve

All eight modified files from `~/openg2p-workspace/pbms` are backed up in `/Users/apple/backups/gate2_20261126/repositories/pbms_modified_files/`:
1. `odoo/extensions/g2p_registry_addon/models/refugee_individual.py`
2. `odoo/extensions/g2p_registry_addon/models/refugee_group.py`
3. `odoo/extensions/g2p_registry_addon/views/registry/refugee_individual_view.xml`
4. `odoo/extensions/g2p_registry_addon/views/registry/refugee_group_view.xml`
5. `odoo/extensions/g2p_registry_addon/views/menu.xml`
6. `odoo/extensions/g2p_registry_addon/security/ir.model.access.csv`
7. `odoo/g2p_pbms/models/beneficiary_list/beneficiary_list.py`
8. `odoo/g2p_pbms/models/beneficiary_list/bgtask_summary_wizard.py`

Plus the dependency fix in `openg2p-odoo-commons`:
- `g2p_documents/__manifest__.py` (relaxed boto3 pin)

---

## 3. Coupling Points Resolution Plan

| # | Coupling Point in Legacy Environment | Legacy Location | Standalone Location in `refugee_management` |
|---|---|---|---|
| **1** | **Addons Path** | `generated/odoo/pbms-odoo.conf` traverses `../openg2p-workspace/` | `infrastructure/configs/odoo.conf` using relative project paths |
| **2** | **Startup Script Sourcing** | `scripts/run-pbms.sh` references `openg2p-developer` | `scripts/start.sh` self-contained within project |
| **3** | **API URL DB Injection** | `scripts/run-pbms.sh` writes `:8050` and `:8002` to `ir_config_parameter` | Initialized to `:8150` and `:8102` during database setup |
| **4** | **Celery PYTHONPATH** | Points to `openg2p-developer/scripts` | Contained inside `source/pbms` |
| **5** | **Signing Key Paths** | Points to `openg2p-workspace/g2p-bridge/test/keys/test-partner.p12` | Independent keys inside `infrastructure/configs/keys/` |

---

## 4. Unresolved Migration Decisions

1. **Source Dependency Strategy (Submodules vs Direct Vendor Copy)**:
   - *Recommendation*: Pin via frozen vendor copies or pinned Git submodules with all local patches applied directly to guarantee 100% independence from any parent workspace.
2. **Category H (3 Attributes)**:
   - Data dictionary Category H (Telephone & Digital Connectivity) attributes (`H01` Phone Number, `H02` Phone Ownership, `H03` SIM Registration) are pending formal inclusion in `refugee_individual.py` / `refugee_group.py` during Gate 4.
