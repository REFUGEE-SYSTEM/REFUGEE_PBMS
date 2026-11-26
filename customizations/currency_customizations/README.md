# UGX Currency Customizations

## Overview

Uganda Shilling (`UGX`) support is implemented entirely inside `extensions/g2p_registry_addon/` without modifying `source/pbms/` or `source/odoo17/`.

## Implementation Paths

| Component | File Path | Details |
|---|---|---|
| **UGX Currency Metadata** | `extensions/g2p_registry_addon/data/currency_data.xml` | Defines `base.UGX` (`model="res.currency"`) with `full_name='Ugandan Shilling'`, `symbol='USh'`, `rounding=1.0`, `active=True`. Note: `base.UGX` carries `noupdate="1"` in `ir_model_data`, so activating an existing inactive `UGX` row in an already-initialized DB also requires ORM/UI activation (`id=43`, `decimal_places=0`). |
| **Programme Currency Field** | `extensions/g2p_registry_addon/models/program_definition.py` | Adds `currency_id = fields.Many2one("res.currency", string="Programme Currency", domain=[("active", "=", True)], default=lambda self: self.env.ref("base.UGX", raise_if_not_found=False))` to `g2p.program.definition`. |
| **Programme Form View** | `extensions/g2p_registry_addon/views/program/program_view.xml` | Inherits `g2p_pbms.view_g2p_programs_config_form` (`id="view_g2p_programs_config_form_currency"`) to insert `currency_id` immediately after `target_registry`. |
| **Benefit Unit JS Patch** | `extensions/g2p_registry_addon/static/src/js/benefit_unit_widget_ugx.js` | Patches `BenefitUnitWidget.prototype.setup` (from `@g2p_pbms/js/benefit_unit_widget`) to prepend `{ value: "UGX", label: "UGX" }` to `this.currencyOptions` if not already present. |
| **Module Asset Registration** | `extensions/g2p_registry_addon/__manifest__.py` | Registers `data/currency_data.xml` and `views/program/program_view.xml` in `data`, and `/g2p_registry_addon/static/src/js/benefit_unit_widget_ugx.js` in `web.assets_backend`. |

## Verification Scope & Limitations

- **Verified (Metadata & Odoo CRUD):** `res.currency` `UGX` (`id=43`, `USh`, `decimal_places=0`, `active=True`), `currency_id` presence in `g2p_pbms.view_g2p_programs_config_form` (`get_views`), and creation/reading of synthetic UGX programme, benefit code, entitlement rule, and cycles in Odoo (`docs/uganda_ugx_currency_implementation_report.md`).
- **Not Verified (UI & End-to-End Payments):**
  - Interactive browser click-through of `BenefitUnitWidget` showing `UGX` in Chrome was **not tested**.
  - End-to-end async Celery entitlement calculation, G2P Bridge disbursement envelope/batch generation, and payment settlement reconciliation in `UGX` were **not tested** and are **not claimed**.
