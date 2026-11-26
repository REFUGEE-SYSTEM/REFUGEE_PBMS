# PBMS Registry Models Navigation Hidden Report

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Branch:** `fix/def03-missing-approved-enrollment`  
**Date:** 2026-11-26  
**Standalone Odoo:** `http://127.0.0.1:8169`  
**Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Status:** **PASS — REGISTRY MODELS & CHILD MENUS HIDDEN; MODELS, DATA & PBMS MENUS PRESERVED**

---

## 1. Executive Summary

Hid the entire **Registry Models** navigation section (`264`, `267`, `268`, `269`) from the PBMS UI in [`extensions/g2p_registry_addon/views/menu.xml`](file:///Users/apple/refugee_management/extensions/g2p_registry_addon/views/menu.xml) and upgraded only `g2p_registry_addon` on `refugee_management_db`. All four menus are now hidden (`active=False`) for Admin, PBMS Editor, PBMS Viewer, and Ordinary Users, while Refugee Registry models, database records, security rules, `target_registry` dropdown restrictions, core PBMS menus, DEF-03, and the legacy OpenG2P environment remain completely intact.

---

## 2. Files Modified & Backups

- **Modified:** `extensions/g2p_registry_addon/views/menu.xml`  
  SHA-256: `34ce63b10b10e4ebdea9772ca5856b5717cfa08a31f07284a9903a7136e6059f`
- **Added (Report):** `docs/pbms_registry_models_navigation_hidden_report.md`
- **Existing Backup Verified (`database/backups/2026-11-26_pre_menu_fix/`):** All 3 checksums verified `OK`.
- **Fresh Pre-Upgrade Backup (`database/backups/2026-11-26_pre_hide_registry_menus/`):**
  - `refugee_management_db.dump`: `5a2de202764f395496517c65d1ee136651f6a5dbdcf16bb5f59ae93bd8b7546b`
  - `refugee_bgtask_db.dump`: `544c49dd5f4b1865cf4a9ff2fc9f8d0525a7c06ea17ab55f1203df02c3a9b8b2`
  - `filestore.tar.gz`: `cadac03b9ed0de05c355961d80a2793db08ad3de357b15c2ec12969e9f0b0fc3`

---

## 3. Exact XML Changes (`extensions/g2p_registry_addon/views/menu.xml`)

Set `active="False"` and `groups="base.group_no_one"` on `g2p_pbms.menu_g2p_registry`, and `active="False"` on all three Refugee Registry child menus (`menu_g2p_refugee_individual_registry`, `menu_g2p_refugee_group_registry`, `menu_g2p_refugee_specific_need`):

```xml
<odoo>
    <!-- Hide Registry Models parent menu and all Refugee Registry child menus from PBMS navigation -->
    <record id="g2p_pbms.menu_g2p_registry" model="ir.ui.menu">
        <field name="active" eval="False"/>
        <field name="groups_id" eval="[(6, 0, [ref('base.group_no_one')])]"/>
    </record>

    <menuitem id="menu_g2p_refugee_individual_registry"
              name="Refugee Individual Registry"
              parent="g2p_pbms.menu_g2p_registry"
              action="action_g2p_refugee_individual_registry"
              groups="g2p_pbms.group_program_super_administration,g2p_pbms.group_program_administration,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_beneficiary_list_viewer"
              active="False"
              sequence="1"/>
    <menuitem id="menu_g2p_refugee_group_registry"
              name="Refugee Group / Household Registry"
              parent="g2p_pbms.menu_g2p_registry"
              action="action_g2p_refugee_group_registry"
              groups="g2p_pbms.group_program_super_administration,g2p_pbms.group_program_administration,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_beneficiary_list_viewer"
              active="False"
              sequence="2"/>
    <menuitem id="menu_g2p_refugee_specific_need"
              name="Refugee Specific Needs"
              parent="g2p_pbms.menu_g2p_registry"
              action="action_g2p_refugee_specific_need"
              groups="g2p_pbms.group_program_super_administration,g2p_pbms.group_program_administration,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_beneficiary_list_viewer"
              active="False"
              sequence="3"/>
</odoo>
```

---

## 4. Module Upgrade & Validation Results

- **XML Validation & Module Upgrade:** `odoo-bin -c infrastructure/configs/odoo.conf -d refugee_management_db -u g2p_registry_addon --stop-after-init` -> **PASS** (`Registry loaded in 7.506s`, exit `0`), followed by standalone Odoo daemon reload on `8169`.
- **Database `ir_ui_menu` State:** `(264, 'Registry Models', False)`, `(267, 'Refugee Individual Registry', False)`, `(268, 'Refugee Group / Household Registry', False)`, `(269, 'Refugee Specific Needs', False)`.
- **Preserved Refugee Registry Records:** `g2p_register_refugee_individual` = `4`, `g2p_register_refugee_group` = `3`, `g2p_refugee_specific_need` = `6`.
- **Preserved `target_registry` Dropdown:** `[['refugee_individual', 'Refugee Individual'], ['refugee_group', 'Refugee Group']]`.

| Role | `264` | `267` | `268` | `269` | Authorized PBMS Menus (`252..257`) | Status |
|---|---|---|---|---|---|---|
| **Admin (`UID=2`)** | Hidden | Hidden | Hidden | Hidden | `PBMS`, `Approvals`, `Programs`, `Enrolment Cycles`, `Disbursement Cycles`, `Master Data`: **Visible** | **PASS** |
| **PBMS Editor (`UID=24`, + `program_viewer`)** | Hidden | Hidden | Hidden | Hidden | `PBMS`, `Programs`: **Visible** | **PASS** |
| **PBMS Viewer (`UID=25`, + `program_viewer`)** | Hidden | Hidden | Hidden | Hidden | `PBMS`, `Programs`: **Visible** | **PASS** |
| **Ordinary User (`UID=26`)** | Hidden | Hidden | Hidden | Hidden | All PBMS menus: **Hidden** | **PASS** |

*(Synthetic test users `[24, 25, 26]` were cleaned up via `unlink=True`.)*

---

## 5. Logs, Git Status & Safety Confirmation

- **Odoo Logs (`logs/odoo.log`):** Clean restart and zero errors during all menu/authentication checks.
- **DEF-03 Preservation:** `beneficiary_list_worker.py` SHA-256 unchanged (`5c791bb98993b2d673ab92d203e5472acdbe94189f61836c5704764db1c827de`).
- **Git State:** Branch `fix/def03-missing-approved-enrollment`, nothing staged or committed.
- **Legacy Environment:** Ports `5433`, `8069`, `6379`, `pbmsdb`, inactive duplicate addon, and legacy repos remain untouched.
