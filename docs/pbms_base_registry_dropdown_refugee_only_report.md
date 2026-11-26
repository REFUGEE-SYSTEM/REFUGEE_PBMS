# PBMS Program Base Registry Dropdown — Refugee-Only Report

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Branch:** `fix/def03-missing-approved-enrollment`  
**Date:** 2026-11-26  
**Standalone Odoo:** `http://127.0.0.1:8169`  
**Standalone Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Status:** **PASS — BASE REGISTRY DROPDOWN RESTRICTED TO REFUGEE REGISTRIES ONLY**

---

## 1. Investigation Findings

- **Model:** `g2p.program.definition` (`source/pbms/odoo/g2p_pbms/models/program/program_definition.py`)
- **Field:** `target_registry` (`fields.Selection`, `string="Target Registry"`, `required=True`)
- **Original Source of All 4 Options:** `G2PRegistryType.selection()` in `source/pbms/odoo/extensions/g2p_registry_type_addon/models/registry_type.py`:
  - `("farmer", "Farmer")`
  - `("households", "Households")`
  - `("refugee_individual", "Refugee Individual")`
  - `("refugee_group", "Refugee Group")`
- **Existing Programs in `refugee_management_db`:**
  - `1` (`seed distribution program`): `farmer`
  - `2` (`Cash Assistance Program`): `farmer`
  - `3` (`Pension Distribution Program`): `farmer`
  - `4` (`Student Welfare program`): `farmer`
  - `7` (`Refugee Welfare Program`): `refugee_individual`
  - `8` (`FLOOD_RELIEF_2026`): `farmer`

---

## 2. Files Modified / Added

- **Added:** `extensions/g2p_registry_addon/models/program_definition.py`  
  SHA-256: `dd0a86ed0674a3e884e2026abf31a33f0c404eccc89a194969b08b035d756a2f`
- **Modified:** `extensions/g2p_registry_addon/models/__init__.py`  
  SHA-256: `d96c6b84bcc29d074ca33eb6e6ec6b332e9c8de1a5f6bb1988efc73135e8cb6f`
- **Added (Report):** `docs/pbms_base_registry_dropdown_refugee_only_report.md`

Core PBMS source (`source/pbms/odoo/g2p_pbms/`), `g2p_registry_type_addon`, inactive duplicate addon (`source/pbms/odoo/extensions/g2p_registry_addon/`), underlying Farmer/Household models/tables/security rules, and DEF-03 were **not** modified.

---

## 3. Exact Implementation

In [`extensions/g2p_registry_addon/models/program_definition.py`](file:///Users/apple/refugee_management/extensions/g2p_registry_addon/models/program_definition.py):

```python
from odoo import fields, models


class G2PProgramDefinitionRefugeeOnly(models.Model):
    _inherit = "g2p.program.definition"

    target_registry = fields.Selection(
        selection=[
            ("refugee_individual", "Refugee Individual"),
            ("refugee_group", "Refugee Group"),
        ],
        string="Target Registry",
        required=True,
    )
```

---

## 4. Backup Checksums & Module Upgrade

- **Pre-change Standalone Backup (`database/backups/2026-11-26_pre_menu_fix/`):**
  - `refugee_management_db.dump`: `99d578ca0153477a0911bd10e4f2a766b52ac30fb058fe7ab915fe5f337032c0`
  - `refugee_bgtask_db.dump`: `cf35968efe217d6b8a63dd2905272a197296c725526de6945d08c1b9bcbbeec0`
  - `filestore.tar.gz`: `7884cb3d38456574becd762b5727d0fd7b1c3b3375db7a998cdc91fad5b2ceec`
- **Module Upgrade:** `odoo-bin -c infrastructure/configs/odoo.conf -d refugee_management_db -u g2p_registry_addon --stop-after-init` -> **PASS** (`Registry loaded in 7.041s`, exit `0`), followed by standalone Odoo daemon reload on `8169`.

---

## 5. Validation Results

| Check | Expected | Actual Result | Status |
|---|---|---|---|
| `fields_get(target_registry)` | Only `refugee_individual` & `refugee_group` | `[['refugee_individual', 'Refugee Individual'], ['refugee_group', 'Refugee Group']]` | **PASS** |
| Create with `farmer` | Rejected | Rejected (`ValueError: Wrong value for g2p.program.definition.target_registry: 'farmer'`) | **PASS** |
| Create with `households` | Rejected | Rejected (`ValueError: Wrong value for g2p.program.definition.target_registry: 'households'`) | **PASS** |
| Create & reopen (`refugee_individual`) | Created & readable | Created `ID=10` (`SYN_TEST_REFUGEE_INDIVIDUAL`), reopened cleanly, then cleaned up | **PASS** |
| Create & reopen (`refugee_group`) | Created & readable | Created `ID=11` (`SYN_TEST_REFUGEE_GROUP`), reopened cleanly, then cleaned up | **PASS** |
| Existing programs (`1, 2, 3, 4, 7, 8`) | Preserved & readable | All 6 existing programs intact and readable (`1..4, 8` retain `'farmer'`, `7` retains `'refugee_individual'`) | **PASS** |
| Interactive Chrome browser click-through | Optional UI check | Verified via Odoo RPC `fields_get` & `create`/`read`; live Chrome UI click-through not run | **NOT TESTED** |

---

## 6. Git Status, Logs & Safety Confirmation

- **Git Branch:** `fix/def03-missing-approved-enrollment` (nothing staged or committed).
- **DEF-03 Preservation:** `beneficiary_list_worker.py` SHA-256 unchanged (`5c791bb98993b2d673ab92d203e5472acdbe94189f61836c5704764db1c827de`).
- **Odoo Logs (`logs/odoo.log`):** Standalone daemon restarted cleanly on `8169`; only `ValueError` entries were the two intentional negative tests for `'farmer'` and `'households'`.
- **Legacy Environment:** Ports `5433`, `8069`, `6379`, `pbmsdb`, and legacy repositories remain untouched.
