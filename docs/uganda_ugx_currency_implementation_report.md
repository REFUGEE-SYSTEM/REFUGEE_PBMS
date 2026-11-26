# Uganda Shilling (UGX) Currency Implementation Report

**Project:** `refugee_management` (`/Users/apple/refugee_management`)  
**Branch:** `fix/def03-missing-approved-enrollment`  
**Date:** 2026-11-26  
**Standalone Odoo:** `http://127.0.0.1:8169`  
**Standalone Database:** `refugee_management_db` (`127.0.0.1:5543`)  
**Status:** **PASS (UGX ACTIVE & PROGRAM/ENTITLEMENT/UNIT ARCHITECTURE CONFIGURED)** / **PARTIAL (ASYNC CELERY PAYMENT & RECONCILIATION NOT EXECUTED LOCALLY)**

---

## 1. Original Currency Configuration & Master Verification

- **Original `res_currency` (`id=43`):** `name='UGX'`, `full_name='Ugandan shilling'`, `symbol='USh'`, `rounding=1.000000`, `decimal_places=0`, **`active=False`**.
- **Uganda (`res_country` `id=230`, `code='UG'`):** Already linked to `currency_id = 43` (`UGX`).
- **Updated `res.currency` (`id=43`):** Activated via Odoo ORM (`active=True`, `full_name='Ugandan Shilling'`, `symbol='USh'`, `rounding=1.0`, `decimal_places=0`).
- **Active Currencies After Change:** `UGX` (`id=43`, `USh`, `0` decimals) and `USD` (`id=1`, `$`, `2` decimals). Zero duplicate `UGX` records exist.
- **Exchange Rates (`res.currency.rate`):** `admin` holds full `R/W/C/D` (`[True, True, True, True]`) on `res.currency.rate`; no fabricated rates were inserted.

---

## 2. Models & Fields Where Currency / Units Are Used

| Area | Model / Component | Field / Mechanism | Notes |
|---|---|---|---|
| **Master Data** | `res.currency`, `res.currency.rate`, `res.country` | `active`, `symbol`, `rounding`, `decimal_places` | Standard Odoo 17 multi-currency & rate tables. |
| **Programme Configuration** | `g2p.program.definition` | `currency_id` (`Many2one('res.currency')`) | Added in `extensions/g2p_registry_addon` + exposed on `view_g2p_programs_config_form`. |
| **Benefit Codes & Entitlements** | `g2p.benefit.codes`, `g2p.program.benefit.codes`, `g2p.entitlement.rule.definition` | `measurement_unit` (`Char`), `decimal_places` (`Integer`) | `BenefitUnitWidget` JS patched to include `UGX` in `currencyOptions`. |
| **Disbursement & Summaries** | `g2p.disbursement.envelope.summary`, `g2p.disbursement.batch.summary`, `bgtask_summary_wizard.py` | `measurement_unit` (`Char`) | Propagates `measurement_unit='UGX'` and formats integer/0-decimal values as `<amount> UGX`. |
| **Refugee Registry** | `g2p.register.refugee_individual`, `g2p.register.refugee_group` | `entitlement_amount` (`Float`), `monthly_household_income` (`Float`) | Existing float fields preserved without destructive schema changes. |

---

## 3. Files Modified / Added

All changes were scoped strictly to the active addon `extensions/g2p_registry_addon/` (zero core PBMS or inactive duplicate addon modifications):

1. **Added:** `extensions/g2p_registry_addon/data/currency_data.xml` (data record for `base.UGX`)
2. **Modified:** `extensions/g2p_registry_addon/models/program_definition.py` (added `currency_id` on `g2p.program.definition`)
3. **Added:** `extensions/g2p_registry_addon/views/program/program_view.xml` (added `currency_id` after `target_registry` in `g2p_pbms.view_g2p_programs_config_form`)
4. **Added:** `extensions/g2p_registry_addon/static/src/js/benefit_unit_widget_ugx.js` (patched `BenefitUnitWidget.prototype.setup` to prepend `{ value: "UGX", label: "UGX" }`)
5. **Modified:** `extensions/g2p_registry_addon/__manifest__.py` (registered data XML, view XML, and JS asset)
6. **Added (Report):** `docs/uganda_ugx_currency_implementation_report.md`

---

## 4. Database Changes & Module Upgrade

- **Module Upgraded:** `odoo-bin -c infrastructure/configs/odoo.conf -d refugee_management_db -u g2p_registry_addon --stop-after-init` -> **PASS** (`Registry loaded in 7.947s`, exit `0`), followed by standalone Odoo daemon reload on `8169`.
- **Database Changes:** Added `currency_id` column (`integer`, FK to `res_currency`) on `g2p_program_definition`; activated `res_currency` `id=43` (`UGX`). All 6 existing programs (`1, 2, 3, 4, 7, 8`) preserved.

---

## 5. Validation Results (Uganda Refugee Cash Assistance Pilot)

All synthetic pilot records were cleaned up (`unlink=True`) after verification.

| Test / Area | Status | Evidence / Notes |
|---|---|---|
| `res.currency` UGX active & 0 decimals | **PASS** | `{'id': 43, 'name': 'UGX', 'full_name': 'Ugandan Shilling', 'symbol': 'USh', 'decimal_places': 0, 'rounding': 1.0, 'active': True}` |
| `currency_id` on Program Configuration Form | **PASS** | `get_views` on `g2p_pbms.view_g2p_programs_config_form` confirms `name="currency_id"` present. |
| `BenefitUnitWidget` UGX dropdown patch | **PASS (Code/Asset)** | Registered in `web.assets_backend`; interactive browser click-through **NOT TESTED**. |
| Pilot Programme (`Uganda Refugee Cash Assistance Pilot`) | **PASS** | Created `ID=13` (`target_registry='refugee_individual'`, `currency_id=[43, 'UGX']`), saved & reopened cleanly. |
| Benefit Code & Entitlement Rule (`100,000 UGX`) | **PASS** | Created `SYN_UGX_CASH_PILOT` (`decimal_places=0`, `measurement_unit='UGX'`), `program_benefit_codes` (`max_quantity=100000.0`), and `entitlement_rule_definition` (`quantity=100000.0`, `measurement_unit='UGX'`). |
| Cycles & Disbursement List Creation | **PASS** | Created Pilot `EC=9`, `DC=10`, `BL=11` on synthetic programme. |
| Async Entitlement, Payment Batch & Reconciliation | **NOT TESTED** | Standalone Celery workers, Celery Beat, and mock G2P Bridge (`8102`) are not running locally; no real payments initiated. |
| Existing Programmes Preservation (`1, 2, 3, 4, 7, 8`) | **PASS** | All 6 existing programs remain intact and readable. |

---

## 6. Backup Paths & SHA-256 Checksums

Stored in `/Users/apple/refugee_management/database/backups/2026-11-26_pre_ugx_currency/`:
- `refugee_management_db.dump`: `4b0c7d1c9935f869b0d264c1c8a1024d9f0a8e73fedb7d0ea4ac7108d0478b82`
- `refugee_bgtask_db.dump`: `81f238eef8d5d6dc5239de0b2f9a6cf261a36fc023d8a6bcc56f6e3724c5962e`
- `filestore.tar.gz`: `5b010f07c8b972d1787ce10ec19b6bf3998d0306983723f8d0e10f737b7af8e4`

Prior backup (`2026-11-26_pre_hide_registry_menus/`) also verified `OK`.

---

## 7. Git Status & Preservation Confirmation

- **Git Branch:** `fix/def03-missing-approved-enrollment` (nothing staged or committed).
- **DEF-03 Preservation:** `beneficiary_list_worker.py` SHA-256 unchanged (`5c791bb98993b2d673ab92d203e5472acdbe94189f61836c5704764db1c827de`).
- **Legacy Environment:** Ports `5433`, `8069`, `6379`, `pbmsdb`, and legacy repos untouched.

---

## 8. Remaining Limitations

1. **Async Payment & Reconciliation:** End-to-end Celery worker entitlement calculation, G2P Bridge envelope/batch generation, and settlement reconciliation remain **NOT TESTED** until Celery workers and mock G2P Bridge services are started.
2. **Browser UI Click-Through:** `BenefitUnitWidget` UGX option rendering in Chrome was **NOT TESTED** interactively.
