# Refugee PBMS Customizations & Patch Management

This directory documents and organizes all custom-developed modules, configuration overrides, UI/currency customizations, and source-code patches in the standalone **Refugee PBMS** project (`/Users/apple/refugee_management`), based on publication branch `refugee-pbms-standalone` (commit `d4b679d5`, parent `ed54ddd7`).

> [!NOTE]
> This is a **documentation and patch-management directory**. All active application code remains in its runtime locations (`extensions/g2p_registry_addon/`, `source/pbms/`, and `source/odoo17/`).

## Directory Structure

- [CUSTOMIZATION_INVENTORY.md](file:///Users/apple/refugee_management/customizations/CUSTOMIZATION_INVENTORY.md) — Master inventory table of all verified custom modules, PBMS modifications, views, security rules, currency/JS assets, tests, and documentation.
- [refugee_registry/README.md](file:///Users/apple/refugee_management/customizations/refugee_registry/README.md) — Inventory of `extensions/g2p_registry_addon/` (models, views, security, menus, target registry restrictions, and dependencies).
- [pbms_modifications/README.md](file:///Users/apple/refugee_management/customizations/pbms_modifications/README.md) — Documentation of the DEF-03 Celery worker fix in `source/pbms/` and its regression tests.
- [odoo_modifications/README.md](file:///Users/apple/refugee_management/customizations/odoo_modifications/README.md) — Inspection results for `source/odoo17/` core files.
- [currency_customizations/README.md](file:///Users/apple/refugee_management/customizations/currency_customizations/README.md) — UGX currency metadata, programme currency field, programme view, and `BenefitUnitWidget` JS patch.
- [patches/README.md](file:///Users/apple/refugee_management/customizations/patches/README.md) — Patch-management guide (review, safe apply, verification, and rollback) and generated patch files.

## Baseline & Dependency Summary

| Component | Path | Baseline / Version |
|---|---|---|
| **Odoo Core** | `source/odoo17/` | Odoo `17.0` (`436b018af565`) |
| **OpenG2P PBMS** | `source/pbms/` | PBMS `3.1.0` (`4c0173a1d5e2` + DEF-03 patch) |
| **OpenG2P Odoo Commons** | `source/openg2p-odoo-commons/` | `b5a68cd082f9` (`boto3` relaxed) |
| **Refugee Registry Addon** | `extensions/g2p_registry_addon/` | `3.1.1` (depends on `base_setup`, `web`, `g2p_pbms`) |
| **Python Runtime** | `requirements.txt` | Python `3.11.9`, `pydantic==2.13.5`, `openg2p-bg-task-models==3.1.0`, `openg2p-g2p-bridge-models==2.1.0` |

## Compatibility & Maintenance Risks

1. **Duplicate `g2p_registry_addon` Directories:**
   Both `extensions/g2p_registry_addon/` (active, customized) and `source/pbms/odoo/extensions/g2p_registry_addon/` (inactive upstream/migrated copy) exist in the repository. If both paths are present in `addons_path`, any misordering will shadow the customizations in `extensions/g2p_registry_addon/`.
2. **Addons Path Precedence:**
   In `infrastructure/configs/odoo.conf.example`, `./extensions` is listed **before** `./source/pbms/odoo/extensions`:
   `addons_path = ./source/odoo17/addons,./source/pbms/odoo/community-addons,./source/pbms/odoo,./extensions,./source/pbms/odoo/extensions,./source/openg2p-odoo-commons`
   This precedence must be preserved in all deployments, or `source/pbms/odoo/extensions/g2p_registry_addon/` should be excluded when deploying to an external environment.
3. **Refugee-Only Programme Target Registry Selection:**
   `extensions/g2p_registry_addon/models/program_definition.py` overrides `g2p.program.definition.target_registry` to restrict choices strictly to `refugee_individual` and `refugee_group`. Any integration expecting `farmer` or `households` in the UI dropdown will be blocked from creating new programmes with those types.
4. **Existing Farmer and Household Programme Compatibility:**
   The underlying models (`g2p.register.farmer`, `g2p.register.households`), database tables, and existing programme rows remain intact and readable. However, creating new programmes targeting `farmer` or `households` is rejected, and `Farmer Registry`, `Register Household`, and `Registry Models` menus are hidden/removed in `extensions/g2p_registry_addon/views/menu.xml`.
5. **DEF-03 Celery Retry Behaviour:**
   `construct_disbursement_sql_query()` now raises `ValueError` when no `APPROVED_FINAL_ENROLMENT` list exists. Because `beneficiary_list_worker()` catches all `Exception` subclasses uniformly, Celery Beat will still retry this permanent prerequisite error up to `_config.worker_max_attempts` before marking the list `failed`.
6. **UGX Payment Integration Limitations:**
   UGX currency metadata (`base.UGX`), `g2p.program.definition.currency_id`, and the `BenefitUnitWidget` JS option are configured and CRUD-tested in Odoo, but **end-to-end async Celery entitlement calculation, G2P Bridge disbursement envelope/batch generation, and payment settlement reconciliation in UGX have not been executed or verified**.
