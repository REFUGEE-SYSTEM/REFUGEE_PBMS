# Investigation Report — Hidden Refugee Registry Menus

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Date:** 2026-11-26  
**Standalone Odoo:** `http://127.0.0.1:8169`  
**Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Mode:** Strictly Read-Only Investigation (no XML, Python, DB, or Git modifications)

---

## 1. Executive Summary

The Refugee Registry menus (`Refugee Individual Registry`, `Refugee Group / Household Registry`, and `Refugee Specific Needs`) are hidden in the standalone PBMS UI because their parent menu, `Registry Models` (`id=264`, external ID `g2p_pbms.menu_g2p_registry`), is explicitly defined in `g2p_pbms/views/menu.xml` with `active="False"` and `groups="base.group_no_one"`. This is an **intentional upstream PBMS 3.1.0 configuration** that hides raw Odoo registry menus by default, and neither copy of `g2p_registry_addon` overrides `active="True"`.

---

## 2. Phase 1 — Read-Only Investigation Evidence

### 2.1 Active Addon Path & Duplicate Comparison
- **`odoo.conf` `addons_path` order:**
  `...,/Users/apple/refugee_management/source/pbms/odoo,/Users/apple/refugee_management/extensions,/Users/apple/refugee_management/source/pbms/odoo/extensions,...`
- **Active `g2p_registry_addon` path:** `/Users/apple/refugee_management/extensions/g2p_registry_addon` (appears before `source/pbms/odoo/extensions` in `addons_path`).
- **Comparison (`diff -ru`):** `extensions/g2p_registry_addon` and `source/pbms/odoo/extensions/g2p_registry_addon` are **100% identical** across all XML, Python, and CSV files (only `__pycache__` differs).

### 2.2 Parent & Child Menu XML Definitions

1. **Parent Menu (`source/pbms/odoo/g2p_pbms/views/menu.xml`, lines 26–27):**
   ```xml
   <!-- Registry Models (hidden; child menus from g2p_registry_addon attach here) -->
   <menuitem id="menu_g2p_registry" name="Registry Models" parent="menu_g2p_root" sequence="99" groups="base.group_no_one" active="False"/>
   ```
2. **Child Menus (`extensions/g2p_registry_addon/views/menu.xml`, lines 1–27):**
   - `menu_g2p_farmer_registry` ("Farmer Registry", `parent="g2p_pbms.menu_g2p_registry"`, `sequence="1"`, no `groups`)
   - `menu_g2p_register_household` ("Register Household", `parent="g2p_pbms.menu_g2p_registry"`, `sequence="2"`, no `groups`)
   - `menu_g2p_refugee_individual_registry` ("Refugee Individual Registry", `parent="g2p_pbms.menu_g2p_registry"`, `sequence="3"`, no `groups`)
   - `menu_g2p_refugee_group_registry` ("Refugee Group / Household Registry", `parent="g2p_pbms.menu_g2p_registry"`, `sequence="4"`, no `groups`)
   - `menu_g2p_refugee_specific_need` ("Refugee Specific Needs", `parent="g2p_pbms.menu_g2p_registry"`, `sequence="5"`, no `groups`)

### 2.3 Database State (`ir_ui_menu` + `ir_model_data` in `refugee_management_db`)

| ID | Name | External ID | Parent ID | `active` | `noupdate` | `groups_id` | Action |
|---|---|---|---|---|---|---|---|
| `252` | `PBMS` | `g2p_pbms.menu_g2p_root` | `NULL` | `True` | `False` | None | `NULL` |
| `264` | `Registry Models` | `g2p_pbms.menu_g2p_registry` | `252` | **`False`** | `False` | `7:Technical Features` (`base.group_no_one`) | `NULL` |
| `265` | `Farmer Registry` | `g2p_registry_addon.menu_g2p_farmer_registry` | `264` | `True` | `False` | None | `ir.actions.act_window,375` |
| `266` | `Register Household` | `g2p_registry_addon.menu_g2p_register_household` | `264` | `True` | `False` | None | `ir.actions.act_window,376` |
| `267` | `Refugee Individual Registry` | `g2p_registry_addon.menu_g2p_refugee_individual_registry` | `264` | `True` | `False` | None | `ir.actions.act_window,377` |
| `268` | `Refugee Group / Household Registry` | `g2p_registry_addon.menu_g2p_refugee_group_registry` | `264` | `True` | `False` | None | `ir.actions.act_window,378` |
| `269` | `Refugee Specific Needs` | `g2p_registry_addon.menu_g2p_refugee_specific_need` | `264` | `True` | `False` | None | `ir.actions.act_window,379` |

- `admin` (`UID=2`) **is** a member of group `7` (`Technical Features` / `res_groups_users_rel` `(2, 7)`), as well as `39` (`Program Super Administration`), `40` (`Program Administration`), `65` (`beneficiary_list_viewer`), and `66` (`beneficiary_list_editor`).

### 2.4 Model Access Rules (`extensions/g2p_registry_addon/security/ir.model.access.csv`)
- `g2p.register.refugee_individual`, `g2p.register.refugee_group`, `g2p.refugee.group.member`, and `g2p.refugee.specific_need` grant:
  - **Read-only (`1,0,0,0`):** `g2p_pbms.group_beneficiary_list_viewer` (`id=65`)
  - **Full CRUD (`1,1,1,1`):** `g2p_pbms.group_beneficiary_list_editor` (`id=66`)
- No other XML file disables or overrides `menu_g2p_registry`.

---

## 3. Phase 2 — Root Cause

**Classification:** **Intentional upstream technical/hidden menu restriction (`active="False"` + `groups="base.group_no_one"`), not overridden by `g2p_registry_addon`.**

Specifically:
1. `g2p_pbms/views/menu.xml:27` intentionally creates `menu_g2p_registry` with `active="False"` and `groups="base.group_no_one"` (explicitly commented: `<!-- Registry Models (hidden; child menus from g2p_registry_addon attach here) -->`).
2. Because Odoo's `ir.ui.menu.load_menus()` only loads menus where `active = True`, `menu_g2p_registry` (`id=264`) is excluded even for `admin` (`UID=2`, who has `Technical Features`).
3. Because child menus `265..269` have `parent_id = 264`, hiding the parent hides all 5 children from the UI menu tree.

---

## 4. Phase 3 — Proposed Solution & Security Implications

### Security Considerations
- Child menus in `extensions/g2p_registry_addon/views/menu.xml` currently have **no `groups` attribute**. While `ir.model.access.csv` blocks unauthorized model access, menu visibility should still be explicitly scoped so non-PBMS users (e.g., Portal/HR/Survey users) do not see registry menus, and unused legacy registries (`Farmer Registry`, `Register Household`) do not clutter the Refugee Management UI.
- Furthermore, `g2p_pbms.menu_g2p_registry` has `noupdate="False"`, meaning XML updates in an extension module can cleanly override it without modifying core `source/pbms/odoo/g2p_pbms/views/menu.xml`.

### Recommended Safest Fix (In Active `extensions/g2p_registry_addon/views/menu.xml`)
1. **Reactivate `g2p_pbms.menu_g2p_registry` and scope it to PBMS Administrators / Registry Editors & Viewers** (removing `base.group_no_one` so PBMS admins don't need Developer/Technical Features mode):
   - Rename or keep `Registry Models` -> `Refugee Registry` (or keep `Registry Models`), set `active=True`, and set `groups_id` to:
     - `g2p_pbms.group_program_super_administration`
     - `g2p_pbms.group_program_administration`
     - `g2p_pbms.group_beneficiary_list_editor`
     - `g2p_pbms.group_beneficiary_list_viewer`
2. **Scope child menus explicitly:**
   - Keep `menu_g2p_farmer_registry` and `menu_g2p_register_household` restricted to `groups="base.group_no_one"` (or `active="False"`) so they stay hidden from operational Refugee Management users.
   - Add explicit `groups="g2p_pbms.group_beneficiary_list_viewer,g2p_pbms.group_beneficiary_list_editor,g2p_pbms.group_program_administration,g2p_pbms.group_program_super_administration"` to:
     - `menu_g2p_refugee_individual_registry`
     - `menu_g2p_refugee_group_registry`
     - `menu_g2p_refugee_specific_need`
3. **Keep duplicate addon synchronized:** Either keep `source/pbms/odoo/extensions/g2p_registry_addon` in sync or remove the unused duplicate path after authorization so edits never diverge.

---

## 5. Phase 4 — Validation Plan (For Future Authorized Implementation)

After applying the XML update and upgrading `g2p_registry_addon` (`-u g2p_registry_addon`) on standalone `refugee_management_db`:

1. **Admin Visibility (`admin`, UID 2):**
   - Call `ir.ui.menu.load_menus(False)` and verify `PBMS -> Registry Models` (`264`), `Refugee Individual Registry` (`267`), `Refugee Group / Household Registry` (`268`), and `Refugee Specific Needs` (`269`) appear in the menu tree.
2. **PBMS Administrator / Editor Visibility:**
   - Test with a synthetic user holding `Program Administration` + `beneficiary_list_editor` (without `Technical Features`): verify all 3 Refugee Registry menus are visible and `Farmer Registry` / `Register Household` remain hidden.
3. **Read-Only Viewer Visibility:**
   - Test with a synthetic user holding `beneficiary_list_viewer` only: verify menus are visible, `read` works, and `create`/`write`/`unlink` are denied.
4. **Ordinary / Unauthorized User Restrictions:**
   - Test with a synthetic user without PBMS/Registry groups: verify none of `264`, `267`, `268`, `269` appear in `load_menus` and direct `search_read` on `g2p.register.refugee_individual` / `g2p.register.refugee_group` raises `AccessError`.
5. **Menu Action & Direct Model Access:**
   - Verify clicking actions `377` (`g2p.register.refugee_individual`), `378` (`g2p.register.refugee_group`), and `379` (`g2p.refugee.specific_need`) loads list/form views cleanly with zero server errors in `logs/odoo.log`.
