# Refugee Registry Menu Visibility Implementation Report

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Branch:** `fix/def03-missing-approved-enrollment`  
**Date:** 2026-11-26  
**Standalone Odoo:** `http://127.0.0.1:8169`  
**Standalone Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Status:** **PASS — IMPLEMENTED, UPGRADED & VERIFIED**

---

## 1. Executive Summary

Implemented the approved Refugee Registry menu visibility fix in the active addon [`extensions/g2p_registry_addon/views/menu.xml`](file:///Users/apple/refugee_management/extensions/g2p_registry_addon/views/menu.xml). After backing up the standalone databases and filestore, `g2p_registry_addon` was upgraded on `refugee_management_db` and the standalone Odoo server (`8169`) was reloaded. User-by-user functional validation confirmed that `admin`, PBMS Editors, and PBMS Viewers can now see the 3 Refugee Registry menus with their existing RBAC permissions intact, while ordinary users and legacy Farmer/Household menus remain restricted.

---

## 2. Files Changed

- **Modified:** `extensions/g2p_registry_addon/views/menu.xml` (SHA-256 recorded below)
- **Added (Backup):** `database/backups/2026-11-26_pre_menu_fix/` (`refugee_management_db.dump`, `refugee_bgtask_db.dump`, `filestore.tar.gz`, `sha256sums.txt`)
- **Added (Report):** `docs/refugee_registry_menu_visibility_implementation_report.md`

Core PBMS source (`source/pbms/odoo/g2p_pbms/`), duplicate addon (`source/pbms/odoo/extensions/g2p_registry_addon/`), `ir.model.access.csv`, Python logic, schemas, and DEF-03 (`beneficiary_list_worker.py`) were **not** modified.

---

## 3. Before / After Menu Configuration

| Menu | Before | After |
|---|---|---|
| `g2p_pbms.menu_g2p_registry` (`id=264`, `Registry Models`) | `active=False`, `groups=base.group_no_one` | `active=True`, `groups_id` = `group_program_super_administration`, `group_program_administration`, `group_beneficiary_list_editor`, `group_beneficiary_list_viewer` |
| `menu_g2p_refugee_individual_registry` (`id=267`) | `active=True`, no `groups` (hidden by parent `264`) | `active=True`, explicit 4 PBMS groups above |
| `menu_g2p_refugee_group_registry` (`id=268`) | `active=True`, no `groups` (hidden by parent `264`) | `active=True`, explicit 4 PBMS groups above |
| `menu_g2p_refugee_specific_need` (`id=269`) | `active=True`, no `groups` (hidden by parent `264`) | `active=True`, explicit 4 PBMS groups above |
| `menu_g2p_farmer_registry` (`id=265`) | `active=True`, no `groups` (hidden by parent `264`) | `active=True`, `groups=base.group_no_one` (hidden in normal UI) |
| `menu_g2p_register_household` (`id=266`) | `active=True`, no `groups` (hidden by parent `264`) | `active=True`, `groups=base.group_no_one` (hidden in normal UI) |

---

## 4. Pre-Upgrade Backup Paths & SHA-256 Checksums

Stored under `/Users/apple/refugee_management/database/backups/2026-11-26_pre_menu_fix/`:

| Artifact | Size | SHA-256 |
|---|---|---|
| `refugee_management_db.dump` (`5543`) | `4.8M` | `99d578ca0153477a0911bd10e4f2a766b52ac30fb058fe7ab915fe5f337032c0` |
| `refugee_bgtask_db.dump` (`5543`) | `48K` | `cf35968efe217d6b8a63dd2905272a197296c725526de6945d08c1b9bcbbeec0` |
| `filestore.tar.gz` | `8.5M` | `7884cb3d38456574becd762b5727d0fd7b1c3b3375db7a998cdc91fad5b2ceec` |

---

## 5. Module Upgrade Result

- **XML Validation:** `xml.etree.ElementTree.parse(...)` -> **PASS**
- **Upgrade Command:** `odoo-bin -c infrastructure/configs/odoo.conf -d refugee_management_db -u g2p_registry_addon --stop-after-init`
- **Result:** **PASS** — Exit code `0`, `Registry loaded in 7.650s`, only `g2p_registry_addon` upgraded; standalone Odoo daemon restarted on `8169` to refresh in-memory menu cache.

---

## 6. User-by-User Visibility & Model Access Tests

All synthetic test users (`UIDs 18, 19, 20`) were cleaned up (`unlink=True`) immediately after testing.

| Test | User / Role | Menus Visible (`load_menus`) | Model Access (`refugee_individual`, `refugee_group`, `specific_need`) | Status |
|---|---|---|---|---|
| **A** | `admin` (`UID=2`) | `PBMS` (`252`), `Programs` (`254`), `Registry Models` (`264`), `267`, `268`, `269`: **True**; `265`, `266`: **False** | Full `R/W/C/D = True` | **PASS** |
| **B** | `syn_pbms_editor3` (`UID=18`, `beneficiary_list_editor`) | `252`, `264`, `267`, `268`, `269`: **True**; `265`, `266`: **False** | `R/W/C/D = [True, True, True, True]` on all 3 models | **PASS** |
| **C** | `syn_pbms_viewer3` (`UID=19`, `beneficiary_list_viewer`) | `252`, `264`, `267`, `268`, `269`: **True**; `265`, `266`: **False** | `R/W/C/D = [True, False, False, False]` on all 3 models (`search_count = 4`) | **PASS** |
| **D** | `syn_ordinary_user3` (`UID=20`, Internal User only) | All (`252`, `264`, `265`, `266`, `267`, `268`, `269`): **False** | Direct `search_read` denied with `odoo.exceptions.AccessError` | **PASS** |
| **E** | Legacy menus (`265`, `266`) | Hidden in normal UI across all tested users | N/A | **PASS** |

---

## 7. Log, DEF-03 Preservation & Git Verification

- **Odoo Logs (`logs/odoo.log`):** Standalone server restarted cleanly on `127.0.0.1:8169`, `queue_job` runner ready; only `ERROR` entries during validation were the expected `AccessError`s from Test D.
- **DEF-03 Preservation:** `beneficiary_list_worker.py` SHA-256 remains `5c791bb98993b2d673ab92d203e5472acdbe94189f61836c5704764db1c827de` (unchanged).
- **Git State:** Current branch `fix/def03-missing-approved-enrollment`; nothing staged or committed.

---

## 8. Remaining Limitations

- `source/pbms/odoo/extensions/g2p_registry_addon/views/menu.xml` (duplicate inactive copy) was intentionally left untouched per task scope.
- Interactive browser click-through was not run; menu visibility and actions were verified via Odoo's `ir.ui.menu.load_menus` and model RPC endpoints.
