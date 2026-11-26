from datetime import date

from psycopg2 import IntegrityError

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestRefugeeRegistry(TransactionCase):
    """Automated tests for Refugee Individual, Group, RBAC, Programme Config, and Menus."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Individual = cls.env["g2p.register.refugee_individual"]
        cls.Group = cls.env["g2p.register.refugee_group"]
        cls.Member = cls.env["g2p.refugee.group.member"]
        cls.Program = cls.env["g2p.program.definition"]

    def _create_individual(self, suffix="001", **kwargs):
        vals = {
            "internal_record_id": f"SYN-INT-{suffix}",
            "functional_record_id": f"SYN-FUNC-{suffix}",
            "surname": "DOE",
            "given_names": "Jane",
            "sex": "female",
            "date_of_birth": date(1995, 5, 15),
            "country_of_origin": "SSD",
            "nationality": "SSD",
        }
        vals.update(kwargs)
        return self.Individual.create(vals)

    # ------------------------------------------------------------------
    # A. Refugee Individual
    # ------------------------------------------------------------------
    def test_01_refugee_individual_registration_and_creation(self):
        self.assertIn("g2p.register.refugee_individual", self.env)
        rec = self._create_individual("IND01")
        self.assertEqual(rec.surname, "DOE")
        self.assertEqual(rec.record_status, "active")

    def test_02_refugee_individual_required_fields_validation(self):
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            with self.env.cr.savepoint():
                self.Individual.create({"given_names": "MissingRequired"})

    def test_03_refugee_individual_duplicate_ids_rejected(self):
        self._create_individual("DUP01")
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            with self.env.cr.savepoint():
                self._create_individual("DUP02", internal_record_id="SYN-INT-DUP01")
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            with self.env.cr.savepoint():
                self._create_individual("DUP03", functional_record_id="SYN-FUNC-DUP01")

    # ------------------------------------------------------------------
    # B. Refugee Group & Members
    # ------------------------------------------------------------------
    def test_04_refugee_group_creation_and_member_lifecycle(self):
        head = self._create_individual("GRP-HEAD")
        dep = self._create_individual("GRP-DEP", given_names="John", sex="male")
        grp = self.Group.create(
            {
                "internal_record_id": "SYN-GRP-INT-01",
                "functional_record_id": "SYN-GRP-FUNC-01",
                "head_of_household_id": head.id,
            }
        )
        m1 = self.Member.create(
            {
                "group_id": grp.id,
                "individual_id": head.id,
                "relationship_to_head": "self",
                "physical_presence_status": "present",
            }
        )
        m2 = self.Member.create(
            {
                "group_id": grp.id,
                "individual_id": dep.id,
                "relationship_to_head": "child",
                "physical_presence_status": "present",
            }
        )
        self.assertEqual(len(grp.member_ids), 2)
        m2.unlink()
        self.assertEqual(len(grp.member_ids), 1)
        self.assertEqual(grp.member_ids[0].id, m1.id)

    def test_05_refugee_group_duplicate_member_constraint(self):
        ind = self._create_individual("GRP-DUPM")
        grp = self.Group.create(
            {
                "internal_record_id": "SYN-GRP-INT-02",
                "functional_record_id": "SYN-GRP-FUNC-02",
            }
        )
        self.Member.create({"group_id": grp.id, "individual_id": ind.id})
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            with self.env.cr.savepoint():
                self.Member.create({"group_id": grp.id, "individual_id": ind.id})

    # ------------------------------------------------------------------
    # C. Access Control (RBAC)
    # ------------------------------------------------------------------
    def _make_user(self, login, group_xml_ids):
        user = self.env["res.users"].create(
            {
                "name": login,
                "login": login,
                "email": f"{login}@example.test",
            }
        )
        for gid in group_xml_ids:
            self.env.ref(gid).write({"users": [(4, user.id)]})
        self.env.invalidate_all()
        self.env.registry.clear_cache()
        return user

    def test_06_access_control_matrix(self):
        rec = self._create_individual("RBAC01")

        # Ordinary internal user without PBMS registry groups -> denied
        ordinary = self._make_user("syn_ordinary", ["base.group_user"])
        with self.assertRaises(AccessError):
            self.Individual.with_user(ordinary).search([("id", "=", rec.id)])

        # Viewer -> read allowed, create/write denied
        viewer = self._make_user(
            "syn_viewer", ["base.group_user", "g2p_pbms.group_beneficiary_list_viewer"]
        )
        self.assertEqual(
            self.Individual.with_user(viewer).browse(rec.id).surname, "DOE"
        )
        with self.assertRaises(AccessError):
            self.Individual.with_user(viewer).create(
                {
                    "surname": "FAIL",
                    "given_names": "Viewer",
                    "sex": "female",
                    "date_of_birth": date(1990, 1, 1),
                    "country_of_origin": "SSD",
                    "nationality": "SSD",
                }
            )

        # Editor -> full CRUD allowed
        editor = self._make_user(
            "syn_editor", ["base.group_user", "g2p_pbms.group_beneficiary_list_editor"]
        )
        created = self.Individual.with_user(editor).create(
            {
                "internal_record_id": "SYN-INT-ED01",
                "functional_record_id": "SYN-FUNC-ED01",
                "surname": "EDITOR",
                "given_names": "User",
                "sex": "male",
                "date_of_birth": date(1992, 2, 2),
                "country_of_origin": "SSD",
                "nationality": "SSD",
            }
        )
        created.with_user(editor).write({"given_names": "Updated"})
        self.assertEqual(created.given_names, "Updated")

        # Programme Administrator -> read allowed (inherits viewer)
        prog_admin = self._make_user(
            "syn_prog_admin", ["base.group_user", "g2p_pbms.group_program_administration"]
        )
        self.assertTrue(
            self.Individual.with_user(prog_admin).search([("id", "=", rec.id)])
        )

    # ------------------------------------------------------------------
    # D. Programme Configuration & Menu Visibility
    # ------------------------------------------------------------------
    def test_07_programme_target_registry_refugee_only(self):
        selection_keys = [
            k for k, _ in self.Program._fields["target_registry"].selection
        ]
        self.assertEqual(selection_keys, ["refugee"])

        from odoo.addons.g2p_registry_type_addon.models import G2PTargetModelMapping
        self.assertEqual(G2PTargetModelMapping.get_target_model_name("refugee"), "g2p.refugee")

        super_admin = self._make_user(
            "syn_super_admin",
            [
                "base.group_user",
                "base.group_system",
                "g2p_pbms.group_program_super_administration",
            ],
        )
        ProgramAsAdmin = self.Program.with_user(super_admin)

        p_refugee = ProgramAsAdmin.create(
            {
                "program_mnemonic": "SYN_REF_PROG",
                "target_registry": "refugee",
                "program_status": "ACTIVE",
            }
        )
        self.assertEqual(p_refugee.target_registry, "refugee")
        self.assertTrue(p_refugee.currency_id)

        # Blocked legacy options
        for blocked in ("farmer", "households", "refugee_individual", "refugee_group"):
            with self.assertRaises(Exception):
                ProgramAsAdmin.create(
                    {
                        "program_mnemonic": f"SYN_{blocked.upper()}_BLOCKED",
                        "target_registry": blocked,
                        "program_status": "ACTIVE",
                    }
                )

    def test_08_registry_menus_hidden(self):
        parent_menu = self.env.ref("g2p_pbms.menu_g2p_registry", raise_if_not_found=False)
        self.assertTrue(parent_menu)
        self.assertFalse(parent_menu.active)
        for xml_id in (
            "g2p_registry_addon.menu_g2p_refugee_individual_registry",
            "g2p_registry_addon.menu_g2p_refugee_group_registry",
            "g2p_registry_addon.menu_g2p_refugee_specific_need",
        ):
            menu = self.env.ref(xml_id, raise_if_not_found=False)
            self.assertTrue(menu, f"Expected menu {xml_id}")
            self.assertFalse(menu.active)
