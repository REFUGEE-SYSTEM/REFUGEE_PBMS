# Refugee Registry Customizations (`extensions/g2p_registry_addon/`)

## Overview

The active Refugee Registry addon lives at `extensions/g2p_registry_addon/` (version `3.1.1`, license `LGPL-3`). It extends OpenG2P PBMS (`g2p_pbms`) with Refugee Individual, Refugee Group / Household, Refugee Group Member, and Refugee Specific Need models, views, access control, Refugee-only programme target registry restrictions, hidden registry navigation menus, and UGX currency support.

## Newly Developed / Customized Files vs. PBMS Migrated Copy

A second copy of `g2p_registry_addon` exists at `source/pbms/odoo/extensions/g2p_registry_addon/` (from Gate 4 source migration). Comparing `extensions/g2p_registry_addon/` against `source/pbms/odoo/extensions/g2p_registry_addon/` reveals the following exact differences:

| File Path | Status vs `source/pbms/odoo/extensions/g2p_registry_addon/` | Purpose |
|---|---|---|
| `extensions/g2p_registry_addon/__manifest__.py` | **Modified** | Registers `data/currency_data.xml`, `views/program/program_view.xml`, and `static/src/js/benefit_unit_widget_ugx.js`. |
| `extensions/g2p_registry_addon/models/__init__.py` | **Modified** | Imports `G2PProgramDefinitionRefugeeOnly` from `.program_definition`. |
| `extensions/g2p_registry_addon/models/program_definition.py` | **Added** | Restricts `target_registry` to `refugee_individual`/`refugee_group`; adds `currency_id`. |
| `extensions/g2p_registry_addon/data/currency_data.xml` | **Added** | `base.UGX` currency metadata record (`USh`, `rounding=1.0`, `active=True`). |
| `extensions/g2p_registry_addon/views/program/program_view.xml` | **Added** | Exposes `currency_id` on `g2p_pbms.view_g2p_programs_config_form`. |
| `extensions/g2p_registry_addon/static/src/js/benefit_unit_widget_ugx.js` | **Added** | Prepends `UGX` to `BenefitUnitWidget.currencyOptions`. |
| `extensions/g2p_registry_addon/views/menu.xml` | **Modified** | Deactivates `g2p_pbms.menu_g2p_registry`, removes Farmer/Household menus, sets Refugee child menus `active=False`. |

All other files in `extensions/g2p_registry_addon/` (`refugee_individual.py`, `refugee_group.py`, `farmer_registry.py`, `household.py`, `registry.py`, `security/ir.model.access.csv`, `views/registry/*.xml`, `views/eligibility/`, `views/entitlement/`, `views/priority/`, `views/bgtask/`, `beneficiaries_widget.js`, `g2p_beneficiaries_info_tpl.xml`, `registry_styles.scss`) are identical to `source/pbms/odoo/extensions/g2p_registry_addon/` and are custom Refugee/PBMS extension files relative to upstream OpenG2P PBMS `3.1.0`.

## Models Implemented

1. **Refugee Individual Model (`g2p.register.refugee_individual`)**
   - **File:** `extensions/g2p_registry_addon/models/refugee_individual.py`
   - **Inheritance:** `_inherit = "g2p.registry"`, `_rec_name = "functional_record_id"`
   - **Companion Model:** `g2p.refugee.specific_need` (configurable UNHCR ProGres v4 specific needs taxonomy with unique `code` SQL constraint).
2. **Refugee Group Model (`g2p.register.refugee_group`)**
   - **File:** `extensions/g2p_registry_addon/models/refugee_group.py`
   - **Inheritance:** `_inherit = "g2p.registry"`
   - **Features:** Links to Head of Household (`g2p.register.refugee_individual`), household members (`g2p.refugee.group.member`), settlement/urban classification, primary/alternate recipients, and unique SQL constraints on `internal_record_id` and `functional_record_id`.
3. **Refugee Group Member Model (`g2p.refugee.group.member`)**
   - **File:** `extensions/g2p_registry_addon/models/refugee_group.py` (lines 978–1041)
   - **Features:** Association model linking `group_id` (`g2p.register.refugee_group`, `ondelete="cascade"`) and `individual_id` (`g2p.register.refugee_individual`), mirroring `surname`, `given_names`, `sex`, `date_of_birth`, `age`, plus `relationship_to_head` (F02) and `physical_presence_status` (F07), with `group_individual_unique` SQL constraint.
4. **Programme Target Registry Customization (`g2p.program.definition`)**
   - **File:** `extensions/g2p_registry_addon/models/program_definition.py`
   - **Class:** `G2PProgramDefinitionRefugeeOnly` (`_inherit = "g2p.program.definition"`)
   - **Behavior:** Overrides `target_registry` selection to `[("refugee_individual", "Refugee Individual"), ("refugee_group", "Refugee Group")]` and adds `currency_id` (`Many2one("res.currency")`, default `base.UGX`).

## Views, Forms, and Menus

- **Refugee Individual & Specific Needs Views:** `extensions/g2p_registry_addon/views/registry/refugee_individual_view.xml` (`action_g2p_refugee_individual_registry`, `view_g2p_refugee_individual_registry_form`, `view_g2p_refugee_individual_registry_tree`, `view_g2p_refugee_specific_need_tree`, `action_g2p_refugee_specific_need`).
- **Refugee Group Views:** `extensions/g2p_registry_addon/views/registry/refugee_group_view.xml` (`action_g2p_refugee_group_registry`, `view_g2p_refugee_group_registry_form`, `view_g2p_refugee_group_registry_tree`).
- **Rule & Wizard Views:**
  - `extensions/g2p_registry_addon/views/eligibility/eligibility_rule_view.xml`
  - `extensions/g2p_registry_addon/views/entitlement/entitlement_rule_view.xml`
  - `extensions/g2p_registry_addon/views/priority/priority_rule_view.xml`
  - `extensions/g2p_registry_addon/views/bgtask/bgtask_view.xml`
- **Programme View:** `extensions/g2p_registry_addon/views/program/program_view.xml`
- **Menu Configuration:** `extensions/g2p_registry_addon/views/menu.xml` sets `g2p_pbms.menu_g2p_registry` `active=False` and `groups_id=base.group_no_one`, removes `menu_g2p_farmer_registry` and `menu_g2p_register_household`, and sets `menu_g2p_refugee_individual_registry`, `menu_g2p_refugee_group_registry`, and `menu_g2p_refugee_specific_need` to `active=False`.

## Security Groups, Access Control, and Record Rules

- **Access Control File:** `extensions/g2p_registry_addon/security/ir.model.access.csv`
- **Groups Referenced (defined in `g2p_pbms`):**
  - `g2p_pbms.group_beneficiary_list_viewer` — Read-only (`1,0,0,0`) on `g2p.register.farmer`, `g2p.register.households`, `g2p.register.refugee_individual`, `g2p.register.refugee_group`, `g2p.refugee.group.member`, and `g2p.refugee.specific_need`.
  - `g2p_pbms.group_beneficiary_list_editor` — Full CRUD (`1,1,1,1`) on the same six models.
- **Record Rules (`ir.rule`):** No `ir.rule` XML files exist inside `extensions/g2p_registry_addon/security/`.

## Manifest & Dependencies

- **Manifest:** `extensions/g2p_registry_addon/__manifest__.py`
- **Depends:** `["base_setup", "web", "g2p_pbms"]` (with `g2p_pbms` depending on `g2p_documents` and `g2p_registry_type_addon`).
- **Assets (`web.assets_backend`):**
  - `/g2p_registry_addon/static/src/css/registry_styles.scss`
  - `/g2p_registry_addon/static/src/js/beneficiaries_widget.js`
  - `/g2p_registry_addon/static/src/js/benefit_unit_widget_ugx.js`
  - `/g2p_registry_addon/static/src/xml/g2p_beneficiaries_info_tpl.xml`
