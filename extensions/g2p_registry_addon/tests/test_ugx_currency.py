from pathlib import Path

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUgxCurrencyCustomization(TransactionCase):
    """Automated tests for UGX currency metadata, programme currency field, view, and JS asset."""

    def test_01_ugx_currency_metadata_and_precision(self):
        ugx = self.env.ref("base.UGX")
        self.assertEqual(ugx.name, "UGX")
        self.assertEqual(ugx.symbol, "USh")
        self.assertEqual(ugx.decimal_places, 0)
        self.assertEqual(ugx.rounding, 1.0)
        self.assertTrue(ugx.active)

    def test_02_programme_currency_field_and_default(self):
        Program = self.env["g2p.program.definition"]
        self.assertIn("currency_id", Program._fields)
        super_admin = self.env["res.users"].create(
            {
                "name": "syn_ugx_super_admin",
                "login": "syn_ugx_super_admin",
                "email": "syn_ugx_super_admin@example.test",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("base.group_system").id,
                            self.env.ref("g2p_pbms.group_program_super_administration").id,
                        ],
                    )
                ],
            }
        )
        prog = Program.with_user(super_admin).create(
            {
                "program_mnemonic": "SYN_UGX_TEST_PROG",
                "target_registry": "refugee",
                "program_status": "ACTIVE",
            }
        )
        self.assertEqual(prog.currency_id.name, "UGX")

    def test_03_programme_form_view_exposes_currency_id(self):
        Program = self.env["g2p.program.definition"]
        view_info = Program.get_view(
            view_id=self.env.ref("g2p_pbms.view_g2p_programs_config_form").id,
            view_type="form",
        )
        self.assertIn('name="currency_id"', view_info["arch"])

    def test_04_benefit_unit_ugx_js_asset_registered(self):
        manifest_path = Path(__file__).resolve().parents[1] / "__manifest__.py"
        manifest_text = manifest_path.read_text(encoding="utf-8")
        self.assertIn(
            "/g2p_registry_addon/static/src/js/benefit_unit_widget_ugx.js",
            manifest_text,
        )

        js_path = (
            Path(__file__).resolve().parents[1]
            / "static"
            / "src"
            / "js"
            / "benefit_unit_widget_ugx.js"
        )
        js_text = js_path.read_text(encoding="utf-8")
        self.assertIn("BenefitUnitWidget", js_text)
        self.assertIn('"UGX"', js_text)
