# PBMS Base Registry — Refugee-Only Navigation Report

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Branch:** `fix/def03-missing-approved-enrollment`  
**Date:** 2026-11-26  
**Standalone Odoo:** `http://127.0.0.1:8169`  
**Standalone Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Status:** **PASS — FARMER & HOUSEHOLD TEMPLATES REMOVED FROM NAVIGATION; REFUGEE REGISTRY PRESERVED**

---

## 1. Executive Summary

Removed `menu_g2p_farmer_registry` (ID `265`) and `menu_g2p_register_household` (ID `266`) from the active addon navigation file [`extensions/g2p_registry_addon/views/menu.xml`](file:///Users/apple/refugee_management/extensions/g2p_registry_addon/views/menu.xml) and upgraded only `g2p_registry_addon` on `refugee_management_db`. The PBMS Base Registry menu (`g2p_pbms.menu_g2p_registry`, ID `264`) now exposes only the three Refugee Registry menus (`267`, `268`, `269`), while underlying `g2p.register.farmer` and `g2p.register.households` models, tables, access rules, DEF-03, and the legacy OpenG2P environment remain completely untouched.

---

## 2. Files Modified

- **Modified:** `extensions/g2p_registry_addon/views/menu.xml`  
  SHA-256: `5651028dafe7ef9218d15ebf2088ffe4345bea3a93effa7f9dc1ed13536629a6`
- **Added (Report):** `docs/pbms_base_registry_refugee_only_report.md`

---

## 3. Backup Location & Checksums

Verified existing standalone backup under `/Users/apple/refugee_management/database/backups/2026-11-26_pre_menu_fix/` via `shasum -a 256 -c sha256sums.txt` (all `OK`):

| Artifact | Size | SHA-256 |
|---|---|---|
| `refugee_management_db.dump` | `4.8M` | `99d578ca0153477a0911bd10e4f2a766b52ac30fb058fe7ab915fe5f337032c0` |
| `refugee_bgtask_db.dump` | `48K` | `cf35968efe217d6b8a63dd2905272a197296c725526de6945d08c1b9bcbbeec0` |
| `filestore.tar.gz` | `8.5M` | `7884cb3d38456574becd762b5727d0fd7b1c3b3375db7a998cdc91fad5b2ceec` |

---

## 4. Exact XML Changes (`extensions/g2p_registry_addon/views/menu.xml`)

Removed `<menuitem id="menu_g2p_farmer_registry" .../>` and `<menuitem id="menu_g2p_register_household" .../>` and re-sequenced the 3 Refugee Registry menus (`sequence="1"`, `"2"`, `"3"`), while preserving `g2p_pbms.menu_g2p_registry` (`active=True`, 4 PBMS groups):

```xml
<odoo>
    <!-- Make Registry Models parent menu active and visible to authorized PBMS roles -->
    <record id="g2p_pbms.menu_g2p_registry" model="ir.ui.menu">
        <field name="active" eval="True"/>
        <field name="groups_id" eval="[(6, 0, [
            ref('g2p_pbms.group_program_super_administration'),
            ref('g2p_pbms.group_program_administration'),
            ref('g2p_pbms.group_beneficiary_list_editor'),
            ref('g2p_pbms.group_beneficiary_list_viewer'),
        ])]"/>
    </record>

    <!-- Expose Refugee Registry menus to authorized PBMS roles -->
    <menuitem id="menu_g2p_refugee_individual_registry"
              name="Refugee Individual Registry"
              parent="g2p_pbms.menu_g2p_registry"
              action="action_g2p_refugee_individual_registry"
              groups="g2p_pbms.group_program_super_administration,g2p_pbms.group_program_administration,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_beneficiary_list_viewer"
              sequence="1"/>
    <menuitem id="menu_g2p_refugee_group_registry"
              name="Refugee Group / Household Registry"
              parent="g2p_pbms.menu_g2p_registry"
              action="action_g2p_refugee_group_registry"
              groups="g2p_pbms.group_program_super_administration,g2p_pbms.group_program_administration,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_beneficiary_list_viewer"
              sequence="2"/>
    <menuitem id="menu_g2p_refugee_specific_need"
              name="Refugee Specific Needs"
              parent="g2p_pbms.menu_g2p_registry"
              action="action_g2p_refugee_specific_need"
              groups="g2p_pbms.group_program_super_administration,g2p_pbms.group_program_administration,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_beneficiary_list_viewer"
              sequence="3"/>
</odoo>
```

---

## 5. Module Upgrade & Preservation Result

- **XML Validation:** `xml.etree.ElementTree.parse` -> **PASS**
- **Upgrade Command:** `odoo-bin -c infrastructure/configs/odoo.conf -d refugee_management_db -u g2p_registry_addon --stop-after-init` -> **PASS** (`Registry loaded in 6.514s`, exit `0`).
- **Database `ir_ui_menu` (IDs `264..269`):** Only `(264, 'Registry Models', True)`, `(267, 'Refugee Individual Registry', True)`, `(268, 'Refugee Group / Household Registry', True)`, and `(269, 'Refugee Specific Needs', True)` remain; IDs `265` and `266` were removed.
- **Model Preservation:** `g2p.register.farmer` and `g2p.register.households` remain registered in `ir_model`; no tables, records, or `ir.model.access.csv` rules were altered.

---

## 6. Role-by-Role Menu Visibility & Model Permission Validation

All synthetic test users (`UIDs 21, 22, 23`) were deleted (`unlink=True`) after verification.

| Role | Refugee Individual (`267`) | Refugee Group (`268`) | Specific Needs (`269`) | Farmer Registry (`265`) | Register Household (`266`) | Model Permissions (`R/W/C/D`) | Status |
|---|---|---|---|---|---|---|---|
| **Admin (`UID=2`)** | Visible | Visible | Visible | Absent | Absent | Full `True/True/True/True` | **PASS** |
| **PBMS Editor (`UID=21`)** | Visible | Visible | Visible | Absent | Absent | `True/True/True/True` on all 3 models | **PASS** |
| **PBMS Viewer (`UID=22`)** | Visible | Visible | Visible | Absent | Absent | `True/False/False/False` on all 3 models | **PASS** |
| **Ordinary User (`UID=23`)** | Hidden | Hidden | Hidden | Absent | Absent | `AccessError` on direct `search_read` | **PASS** |

---

## 7. Git Status, Logs & Safety Confirmation

- **Git Branch:** `fix/def03-missing-approved-enrollment` (nothing staged or committed).
- **DEF-03 Preservation:** `beneficiary_list_worker.py` SHA-256 unchanged (`5c791bb98993b2d673ab92d203e5472acdbe94189f61836c5704764db1c827de`).
- **Odoo Logs (`logs/odoo.log`):** Standalone daemon restarted cleanly on `127.0.0.1:8169`; only warnings/errors during testing were the expected `AccessError`s for Ordinary User `UID=23`.
- **Legacy Environment:** Port `5433`, `pbmsdb`, port `8069`, core PBMS source, and inactive duplicate `source/pbms/odoo/extensions/g2p_registry_addon` were not touched.
