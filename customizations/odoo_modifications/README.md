# Odoo Core Modifications (`source/odoo17/`)

## Inspection Result

No verified Odoo core source modifications were identified in the inspected publication commit (`d4b679d5`).

## Verification Notes

- `source/odoo17/` was added in commit `d4b679d5` as part of the Gate 4 standalone source migration (Odoo `17.0`, baseline `436b018af565`).
- All Odoo-layer customizations (models, views, menus, security access rules, UGX currency data, and OWL JavaScript patches) are isolated in `extensions/g2p_registry_addon/` without modifying `source/odoo17/`.
