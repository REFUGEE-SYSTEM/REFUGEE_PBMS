# PBMS UI & Functional Verification Report (Standalone Odoo)

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Inspection Date:** 2026-11-26  
**Standalone URL:** `http://127.0.0.1:8169`  
**Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Verification Mode:** Strictly Read-Only (no installs, upgrades, record edits, or legacy access)

---

## 1. Executive Summary

Verified the installed PBMS modules, Odoo web menus, model registrations/views, `admin` user permissions, and standalone Odoo server logs on `http://127.0.0.1:8169`.

- **Installed Modules:** **PASS** — All 6 requested modules (`g2p_pbms`, `g2p_pbms_program_access`, `g2p_registry_addon`, `g2p_registry_type_addon`, `pbms_theme_extension`, `queue_job`) are `installed`.
- **Models & Views:** **PASS (with naming note)** — All 5 PBMS core models plus `g2p.register.refugee_individual` and `g2p.register.refugee_group` (note underscore rather than dot before `individual`/`group`) are registered, readable, and return valid `list` and `form` views.
- **Menus:** **PARTIAL** — Core `PBMS` menus (`Programs`, `Enrolment Cycles`, `Disbursement Cycles`, `Approvals`, `Master Data` -> `Benefit Codes`, etc.) are visible to `admin`, **but `Registry Models` (`id=264`, `g2p_pbms.menu_g2p_registry`) has `active=False` and `Technical Features` group restriction**, hiding `Refugee Individual Registry` (`267`), `Refugee Group / Household Registry` (`268`), and `Refugee Specific Needs` (`269`) from the UI menu bar.
- **User Permissions:** **PASS** — `admin` (UID `2`) has full R/W/C/D access on all verified PBMS and Refugee Registry models and holds PBMS Administration / Program Access groups.
- **Application Logs:** **PASS (with minor historical test errors)** — No missing addon, missing view, or server-reported JS asset errors. The only `ERROR` lines in `logs/odoo.log` correspond to earlier Gate 7/8 negative validation tests (duplicate `functional_record_id` constraint and probing non-existent dotted model names).

---

## 2. Module Verification

Queried read-only from `refugee_management_db.ir_module_module` (`127.0.0.1:5543`):

| Module | State | Version | Status |
|---|---|---|---|
| `g2p_pbms` | `installed` | `17.0.3.1.0` | **PASS** |
| `g2p_pbms_program_access` | `installed` | `17.0.3.1.0` | **PASS** |
| `g2p_registry_addon` | `installed` | `17.0.3.1.1` | **PASS** |
| `g2p_registry_type_addon` | `installed` | `17.0.3.1.1` | **PASS** |
| `pbms_theme_extension` | `installed` | `17.0.3.1.1` | **PASS** |
| `queue_job` | `installed` | `17.0.1.1.1` | **PASS** |

---

## 3. Menu Verification

Checked via authenticated JSON-RPC `ir.ui.menu.load_menus(False)` as `admin` (UID `2`) and cross-checked against `ir_ui_menu` in `refugee_management_db`:

| Requested Menu Area | Actual Menu / XMLID | Visible to `admin` | Status | Notes |
|---|---|---|---|---|
| **PBMS Application Menu** | `PBMS` (`id=252`, `g2p_pbms.menu_g2p_root`) | Yes | **PASS** | Root app menu with 5 visible children (`Approvals`, `Programs`, `Enrolment Cycles`, `Disbursement Cycles`, `Master Data`). |
| **Program Management** | `Programs` (`id=254`, `g2p_pbms.menu_g2p_programs`) | Yes | **PASS** | Action `ir.actions.act_window,357`. |
| **Enrollment Cycle Management** | `Enrolment Cycles` (`id=255`, `g2p_pbms.menu_g2p_enrollment_cycles`) | Yes | **PASS** | Action `ir.actions.act_window,359`. |
| **Disbursement Cycle Management** | `Disbursement Cycles` (`id=256`, `g2p_pbms.menu_g2p_disbursement_cycles`) | Yes | **PASS** | Action `ir.actions.act_window,360`. |
| **Benefit Codes** | `Master Data -> Benefit Codes` (`id=261`, `g2p_pbms.menu_g2p_benefit_codes`) | Yes | **PASS** | Action `ir.actions.act_window,350` (alongside `Warehouses`, `Agencies`, `Sponsor Banks`, `Administrative Areas`). |
| **Registry Management** | `Registry Models` (`id=264`, `g2p_pbms.menu_g2p_registry`) -> `Refugee Individual Registry` (`267`), `Refugee Group / Household Registry` (`268`), `Refugee Specific Needs` (`269`) | **No (Hidden)** | **PARTIAL** | Actions `377`, `378`, `379` exist, **but parent menu `264` has `active = False` and requires group `7:Technical Features`**, so all Registry submenus are hidden from `load_menus`. |
| **Beneficiary Lists** | Accessed inside Programs / Cycles | N/A (embedded) | **PASS** | No standalone top-level menu in `g2p_pbms`; accessed via Enrollment/Disbursement Cycle views. |
| **Program Access Controls** | `OpenG2P PBMS` / `OpenG2P PBMS Program Access` security groups | Via `Settings` | **PASS** | Managed through `Settings -> Users & Companies -> Groups` (`res.groups`). |

---

## 4. Model Verification

Verified via authenticated JSON-RPC (`search_count`, `get_views(['list', 'form'])`) against `http://127.0.0.1:8169`:

| Model Name | Record Count | `list` & `form` Views Loaded | Status | Notes |
|---|---|---|---|---|
| `g2p.program.definition` | `7` | Yes | **PASS** | Registered and accessible. |
| `g2p.enrollment.cycle` | `8` | Yes | **PASS** | Registered and accessible. |
| `g2p.disbursement.cycle` | `9` | Yes | **PASS** | Registered and accessible. |
| `g2p.beneficiary.list` | `10` | Yes | **PASS** | Registered and accessible. |
| `g2p.benefit.codes` | `5` | Yes | **PASS** | Registered and accessible. |
| `g2p.register.refugee_individual` | `4` | Yes | **PASS** | Registered with underscore (`refugee_individual`). |
| `g2p.register.refugee.individual` | — | No (`KeyError`) | **FAIL** *(Expected)* | Dotted name does not exist; actual technical name is `g2p.register.refugee_individual`. |
| `g2p.register.refugee_group` | `3` | Yes | **PASS** | Registered with underscore (`refugee_group`). |
| `g2p.register.refugee.group` | — | No (`KeyError`) | **FAIL** *(Expected)* | Dotted name does not exist; actual technical name is `g2p.register.refugee_group`. |

---

## 5. User Access Verification

- **Authenticated User:** `admin` (`UID=2`, `Administrator`)
- **Model Access (`check_access_rights`):** `read=True`, `write=True`, `create=True`, `unlink=True` on all 7 registered PBMS and Refugee Registry models above.
- **Assigned PBMS / Admin Groups:** `admin` holds `Administration / Settings`, `Job Queue / Job Queue Manager`, `OpenG2P PBMS / Program Super Administration`, `OpenG2P PBMS / Program Administration`, and all `OpenG2P PBMS` editor/viewer/approver roles.
- **Status:** **PASS**

---

## 6. Application Log Inspection (`/Users/apple/refugee_management/logs/odoo.log`)

- **Total lines inspected:** `2,633`
- **Missing addons / view loading failures / server JS errors:** **None** (`0` occurrences).
- **Warnings (`24` lines):** Non-fatal Odoo 17 ORM/API deprecation warnings (e.g., `not overriding create method in batch`, `inconsistent 'compute_sudo'` on `g2p.disbursement.cycle`, `inconsistent 'store'` on `g2p.enrollment.cycle`, and `searchable` field dependency warnings on `g2p.program.definition`).
- **Errors (`38` lines):** All `ERROR` lines are from negative/validation test requests (e.g., Gate 7 duplicate `functional_record_id` unique-constraint test and the dotted-name `KeyError` probes in Section 4 above). Scheduled cron `Jobs Garbage Collector` completed cleanly (`0.006s`).
- **Status:** **PASS**

---

## 7. Remaining Blockers & Follow-up Items

1. **Hidden Registry Menu (`id=264`, `g2p_pbms.menu_g2p_registry`):** Currently `active=False` and gated by `Technical Features`, preventing users from navigating to `Refugee Individual Registry`, `Refugee Group / Household Registry`, and `Refugee Specific Needs` from the `PBMS` menu bar without enabling/unhiding it.
2. **Model Naming Reference:** Documentation or scripts referencing `g2p.register.refugee.individual` / `g2p.register.refugee.group` should use the actual model names `g2p.register.refugee_individual` and `g2p.register.refugee_group`.
3. **Browser-Interactive UI Click-Through:** **NOT TESTED** in this read-only API/DB verification (views and menus were verified via Odoo's `load_menus` and `get_views` endpoints).
