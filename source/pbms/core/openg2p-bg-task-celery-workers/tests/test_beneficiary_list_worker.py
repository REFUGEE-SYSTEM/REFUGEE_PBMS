import importlib.util
import json
import sys
import types
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch


def _load_beneficiary_list_worker_module():
    """Load beneficiary_list_worker.py with lightweight stubs for optional runtime deps."""
    worker_src = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "openg2p_bg_task_celery_workers"
        / "tasks"
        / "beneficiary_list_worker.py"
    )

    # Provide minimal package stubs so importing the module does not require
    # an active Celery broker, DB engine, or uninstalled companion packages.
    pkg_name = "openg2p_bg_task_celery_workers"
    tasks_pkg_name = f"{pkg_name}.tasks"

    for name in [pkg_name, tasks_pkg_name]:
        if name not in sys.modules:
            mod = types.ModuleType(name)
            mod.__path__ = [str(worker_src.parent.parent if name == pkg_name else worker_src.parent)]
            sys.modules[name] = mod

    if "openg2p_bg_task_registry_adapters" not in sys.modules:
        adapters_mod = types.ModuleType("openg2p_bg_task_registry_adapters")
        factory_mod = types.ModuleType("openg2p_bg_task_registry_adapters.factory")
        interface_mod = types.ModuleType("openg2p_bg_task_registry_adapters.interface")
        factory_mod.RegistryFactory = MagicMock()
        interface_mod.RegistryInterface = MagicMock()
        sys.modules["openg2p_bg_task_registry_adapters"] = adapters_mod
        sys.modules["openg2p_bg_task_registry_adapters.factory"] = factory_mod
        sys.modules["openg2p_bg_task_registry_adapters.interface"] = interface_mod

    if "openg2p_pbms_models" not in sys.modules:
        pbms_mod = types.ModuleType("openg2p_pbms_models")
        pbms_models_mod = types.ModuleType("openg2p_pbms_models.models")

        class _ListStageEnum(str, Enum):
            ENROLLMENT = "enrollment"
            DISBURSEMENT = "disbursement"

        class _ListWorkflowStatusEnum(str, Enum):
            APPROVED_FINAL_ENROLMENT = "approved_final_enrolment"

        class _StatusEnum(str, Enum):
            pending = "pending"
            complete = "complete"
            failed = "failed"
            not_applicable = "not_applicable"

        from sqlalchemy import column

        class _G2PBeneficiaryList:
            id = column("id")
            program_id = column("program_id")
            beneficiary_list_id = column("beneficiary_list_id")
            list_stage = column("list_stage")
            list_workflow_status = column("list_workflow_status")
            creation_date = column("creation_date")

        class _G2PEligibilityRuleDefinition:
            sql_query = column("sql_query")
            set_operator = column("set_operator")
            program_id = column("program_id")
            rule_number = column("rule_number")

        class _G2PPriorityRuleDefinition:
            sql_query = column("sql_query")
            disbursement_cycle_id = column("disbursement_cycle_id")

        class _G2PProgramDefinition:
            id = column("id")

        pbms_models_mod.G2PBeneficiaryList = _G2PBeneficiaryList
        pbms_models_mod.G2PEligibilityRuleDefinition = _G2PEligibilityRuleDefinition
        pbms_models_mod.G2PPriorityRuleDefinition = _G2PPriorityRuleDefinition
        pbms_models_mod.G2PProgramDefinition = _G2PProgramDefinition
        pbms_models_mod.ListStageEnum = _ListStageEnum
        pbms_models_mod.ListWorkflowStatusEnum = _ListWorkflowStatusEnum
        pbms_models_mod.StatusEnum = _StatusEnum

        sys.modules["openg2p_pbms_models"] = pbms_mod
        sys.modules["openg2p_pbms_models.models"] = pbms_models_mod

    app_mod = types.ModuleType(f"{pkg_name}.app")
    celery_app_mock = MagicMock()
    celery_app_mock.task = lambda *a, **kw: (lambda fn: fn)
    app_mod.celery_app = celery_app_mock
    app_mod.get_engine = lambda: {
        "db_engine_bg_task": MagicMock(),
        "db_engine_sr": MagicMock(),
        "db_engine_pbms": MagicMock(),
    }
    sys.modules[f"{pkg_name}.app"] = app_mod

    config_mod = types.ModuleType(f"{pkg_name}.config")
    cfg = MagicMock()
    cfg.logging_default_logger_name = "test_beneficiary_list_worker"
    cfg.worker_max_attempts = 3
    cfg.batch_size = 100
    config_mod.Settings = MagicMock()
    config_mod.Settings.get_config.return_value = cfg
    sys.modules[f"{pkg_name}.config"] = config_mod

    helpers_mod = types.ModuleType(f"{pkg_name}.helpers")
    helpers_mod.construct_eligibility_query = MagicMock(return_value="SELECT 1")
    helpers_mod.construct_priority_query = MagicMock(return_value="SELECT 2")
    sys.modules[f"{pkg_name}.helpers"] = helpers_mod

    spec = importlib.util.spec_from_file_location(
        f"{tasks_pkg_name}.beneficiary_list_worker", worker_src
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{tasks_pkg_name}.beneficiary_list_worker"] = module
    spec.loader.exec_module(module)
    return module


worker_mod = _load_beneficiary_list_worker_module()


class TestConstructDisbursementSqlQuery(unittest.TestCase):
    def setUp(self):
        self.pbms_session = MagicMock()
        self.bg_task_session = MagicMock()
        self.beneficiary_list = MagicMock(
            id=999,
            program_id=99,
            disbursement_cycle_id=199,
            beneficiary_list_id="syn-list-uuid-999",
            list_stage="disbursement",
            eligibility_number_of_attempts=0,
        )
        worker_mod.construct_priority_query.reset_mock()
        worker_mod.construct_enrollment_sql_query = MagicMock(return_value="SELECT_ENROLL")

    def test_a_missing_approved_final_enrollment_list_raises_value_error(self):
        """Test A: Missing approved final enrollment list raises ValueError cleanly."""
        (
            self.pbms_session.query.return_value.filter.return_value.order_by.return_value.first.return_value
        ) = None

        with self.assertRaises(ValueError) as ctx:
            worker_mod.construct_disbursement_sql_query(
                self.pbms_session, self.bg_task_session, self.beneficiary_list
            )

        msg = str(ctx.exception)
        self.assertIn("999", msg)
        self.assertIn("99", msg)
        self.assertIn("no approved final enrollment list exists", msg)
        self.bg_task_session.execute.assert_not_called()
        worker_mod.construct_priority_query.assert_not_called()

    def test_b_approved_final_enrollment_list_exists_processes_registrants(self):
        """Test B: Valid approved final enrollment list extracts registrant IDs."""
        (
            self.pbms_session.query.return_value.filter.return_value.order_by.return_value.first.return_value
        ) = ("approved-enroll-uuid-1",)

        registrants_json = json.dumps([{"registrant_id": "SYN-IND-001"}, {"registrant_id": "SYN-IND-002"}])
        self.bg_task_session.execute.return_value.scalars.return_value.all.return_value = [
            registrants_json
        ]
        self.pbms_session.execute.return_value.scalars.return_value.all.return_value = [
            "SELECT internal_record_id FROM g2p_register_refugee_individual"
        ]

        result = worker_mod.construct_disbursement_sql_query(
            self.pbms_session, self.bg_task_session, self.beneficiary_list
        )

        self.assertEqual(result, "SELECT 2")
        worker_mod.construct_priority_query.assert_called_once_with(
            ["SELECT internal_record_id FROM g2p_register_refugee_individual"],
            ["SYN-IND-001", "SYN-IND-002"],
        )

    def test_c_empty_registrant_details_no_none_iteration_error(self):
        """Test C: Approved final enrollment list with empty registrant details does not raise TypeError."""
        (
            self.pbms_session.query.return_value.filter.return_value.order_by.return_value.first.return_value
        ) = ("approved-enroll-uuid-2",)
        self.bg_task_session.execute.return_value.scalars.return_value.all.return_value = []
        self.pbms_session.execute.return_value.scalars.return_value.all.return_value = [
            "SELECT internal_record_id FROM g2p_register_refugee_individual"
        ]

        result = worker_mod.construct_disbursement_sql_query(
            self.pbms_session, self.bg_task_session, self.beneficiary_list
        )

        self.assertEqual(result, "SELECT 2")
        worker_mod.construct_priority_query.assert_called_once_with(
            ["SELECT internal_record_id FROM g2p_register_refugee_individual"],
            [],
        )

    def test_d_worker_failure_handler_records_controlled_exception(self):
        """Test D: Task exception handler rolls back, records error, increments attempts, and re-raises."""
        pbms_session = MagicMock()
        bg_task_session = MagicMock()
        sr_session = MagicMock()

        bl_record = MagicMock(
            id=999,
            program_id=99,
            disbursement_cycle_id=199,
            list_stage="disbursement",
            eligibility_number_of_attempts=0,
            eligibility_process_status="processing",
            eligibility_latest_error_code=None,
        )
        prog_record = MagicMock(id=99, program_mnemonic="SYN_PROG", target_registry="refugee_individual")

        pbms_session.query.return_value.filter.return_value.first.side_effect = [
            bl_record,
            prog_record,
        ]
        pbms_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with patch.object(
            worker_mod,
            "sessionmaker",
            side_effect=[
                MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=bg_task_session), __exit__=MagicMock(return_value=False))),
                MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=sr_session), __exit__=MagicMock(return_value=False))),
                MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=pbms_session), __exit__=MagicMock(return_value=False))),
            ],
        ):
            with self.assertRaises(ValueError):
                worker_mod.beneficiary_list_worker(999)

        pbms_session.rollback.assert_called_once()
        bg_task_session.rollback.assert_called_once()
        self.assertEqual(bl_record.eligibility_number_of_attempts, 1)
        self.assertIn("no approved final enrollment list exists", bl_record.eligibility_latest_error_code)
        self.assertEqual(bl_record.eligibility_process_status, "pending")
        pbms_session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
