from datetime import date

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRefugeeEnrollmentWorkflow(TransactionCase):
    """Phase 4 & 8: Synthetic 10-individual, 2-group Refugee Programme & Approval Workflow."""

    def test_01_full_synthetic_refugee_programme_and_enrollment_approval(self):
        Individual = self.env["g2p.register.refugee_individual"]
        Group = self.env["g2p.register.refugee_group"]
        Member = self.env["g2p.refugee.group.member"]
        Program = self.env["g2p.program.definition"]
        BenefitCode = self.env["g2p.benefit.codes"]
        ProgBenefitCode = self.env["g2p.program.benefit.codes"]
        EnrollmentCycle = self.env["g2p.enrollment.cycle"]
        BeneficiaryList = self.env["g2p.beneficiary.list"]
        StageDef = self.env["g2p.workflow.stage.definition"]
        PendingStage = self.env["g2p.workflow.pending.stage"]

        super_admin = self.env["res.users"].create(
            {
                "name": "syn_wf_super_admin",
                "login": "syn_wf_super_admin",
                "email": "syn_wf_super_admin@example.test",
            }
        )
        for gid in (
            "base.group_user",
            "base.group_system",
            "g2p_pbms.group_program_super_administration",
            "g2p_pbms.group_enrolment_approver",
        ):
            self.env.ref(gid).write({"users": [(4, super_admin.id)]})
        self.env.invalidate_all()
        self.env.registry.clear_cache()

        # 1. Create 10 synthetic Refugee Individuals
        individuals = []
        for i in range(1, 11):
            ind = Individual.create(
                {
                    "internal_record_id": f"SYN-E2E-INT-{i:03d}",
                    "functional_record_id": f"SYN-E2E-FUNC-{i:03d}",
                    "surname": f"SYNREF{i:02d}",
                    "given_names": f"TestUser{i:02d}",
                    "sex": "female" if i % 2 == 0 else "male",
                    "date_of_birth": date(1990 + (i % 10), 1, 1),
                    "country_of_origin": "SSD",
                    "nationality": "SSD",
                }
            )
            individuals.append(ind)
        self.assertEqual(len(individuals), 10)

        # 2. Create 2 synthetic Refugee Groups (5 members each)
        groups = []
        for g_idx, chunk in enumerate((individuals[:5], individuals[5:]), start=1):
            grp = Group.create(
                {
                    "internal_record_id": f"SYN-E2E-GRP-INT-{g_idx:02d}",
                    "functional_record_id": f"SYN-E2E-GRP-FUNC-{g_idx:02d}",
                    "head_of_household_id": chunk[0].id,
                }
            )
            for m_idx, member_ind in enumerate(chunk):
                Member.create(
                    {
                        "group_id": grp.id,
                        "individual_id": member_ind.id,
                        "relationship_to_head": "self" if m_idx == 0 else "child",
                        "physical_presence_status": "present",
                    }
                )
            self.assertEqual(len(grp.member_ids), 5)
            groups.append(grp)
        self.assertEqual(len(groups), 2)

        # 3. Create Refugee Cash Assistance Programme with UGX currency
        ugx = self.env.ref("base.UGX")
        prog = Program.with_user(super_admin).create(
            {
                "program_mnemonic": "SYN_E2E_UGX_CASH",
                "description": "Synthetic E2E Refugee Cash Assistance (UGX)",
                "target_registry": "refugee",
                "program_status": "ACTIVE",
                "currency_id": ugx.id,
            }
        )
        self.assertEqual(prog.currency_id.name, "UGX")

        # 4. Configure UGX Benefit Code and Programme Benefit Unit (100,000 UGX)
        bc = BenefitCode.create(
            {
                "benefit_mnemonic": "SYN_E2E_UGX_BC",
                "benefit_type": "CASH_DIGITAL",
                "benefit_description": "Synthetic UGX Cash Benefit",
                "measurement_unit": "UGX",
                "decimal_places": 0,
            }
        )
        pbc = ProgBenefitCode.create(
            {
                "program_id": prog.id,
                "benefit_code_id": bc.id,
                "max_quantity": 100000.0,
            }
        )
        self.assertEqual(pbc.measurement_unit, "UGX")

        # 5. Prepare synthetic Enrollment Cycle, Workflow Stage, Beneficiary List & Approve
        StageDef.create(
            {
                "program_id": prog.id,
                "cycle_type": "ENROLMENT",
                "stage_number": 1,
                "stage_name": "Final Enrollment Approval",
                "group_id": self.env.ref("g2p_pbms.group_enrolment_approver").id,
            }
        )
        ec = EnrollmentCycle.create(
            {
                "program_id": prog.id,
                "cycle_mnemonic": "SYN_EC_01",
            }
        )
        bl = BeneficiaryList.create(
            {
                "mnemonic": "SYN_ENROLL_BL_01",
                "enrollment_cycle_id": ec.id,
                "list_stage": "enrollment",
                "eligibility_process_status": "complete",
                "number_of_registrants": 10,
                "workflow_approval_status": "PENDING",
            }
        )
        bl.with_user(super_admin).action_approve_stage(
            reason="Synthetic E2E enrollment approval"
        )
        self.assertEqual(bl.workflow_approval_status, "APPROVED")
        self.assertEqual(bl.list_workflow_status, "approved_final_enrolment")
