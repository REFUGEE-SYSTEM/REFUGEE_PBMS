import unittest
from datetime import datetime
from unittest.mock import MagicMock

from openg2p_bg_task_registry_adapters.computations import RegisterRefugee
from openg2p_bg_task_registry_adapters.factory import RegistryFactory
from openg2p_bg_task_registry_adapters.models import (
    BeneficiaryListSummaryRefugee,
    G2PRegisterRefugee,
    G2PRegistryType,
)


class TestRefugeeAdapter(unittest.TestCase):
    def test_registry_type_and_factory(self):
        self.assertEqual(G2PRegistryType.REFUGEES.value, "refugees")
        adapter = RegistryFactory.get_registry_class("refugees")
        self.assertIsInstance(adapter, RegisterRefugee)

    def test_model_tablename(self):
        self.assertEqual(G2PRegisterRefugee.__tablename__, "g2p_register_refugees")
        self.assertEqual(
            BeneficiaryListSummaryRefugee.__tablename__,
            "beneficiary_list_summary_refugee",
        )

    def test_search_sql_targets_refugees_table(self):
        adapter = RegisterRefugee()
        query, params = adapter.construct_beneficiary_search_sql_query(
            ["id-1", "id-2"], "refugees", "", "internal_record_id asc", 10, 1
        )
        self.assertIn("FROM g2p_register_refugees", str(query))
        self.assertEqual(params["registrant_id_0"], "id-1")
        self.assertEqual(params["registrant_id_1"], "id-2")

    def test_entitled_sql_targets_refugees_table(self):
        adapter = RegisterRefugee()
        clause = adapter.construct_get_is_registrant_entitled_sql_query(
            "id-1",
            "refugees",
            "SELECT internal_record_id FROM g2p_register_refugees WHERE legal_status = 'RECOGNISED_REFUGEE'",
        )
        sql_str = str(clause)
        self.assertIn("g2p_register_refugees.internal_record_id = :registrant_id", sql_str)

    def test_compute_stats_dict(self):
        adapter = RegisterRefugee()
        stats = adapter.compute_stats_dict({"UGX": [100000.0, 100000.0, 200000.0]})
        self.assertEqual(stats["total"]["UGX"], 400000.0)
        self.assertEqual(stats["average"]["UGX"], 133333.33)
        self.assertEqual(stats["q2"]["UGX"], 100000.0)

    def test_compute_eligibility_statistics_adds_summary(self):
        adapter = RegisterRefugee()
        base_summary = MagicMock(
            program_id=1,
            program_mnemonic="UG_REF_CBI",
            target_registry="refugees",
            beneficiary_list_id="bl-1",
            number_of_registrants=2,
            date_created=datetime(2026, 1, 1),
        )
        bg_session = MagicMock()
        sr_session = MagicMock()
        adapter.compute_eligibility_statistics([], base_summary, sr_session, bg_session)
        bg_session.add.assert_called_once()
        added = bg_session.add.call_args[0][0]
        self.assertIsInstance(added, BeneficiaryListSummaryRefugee)
        self.assertEqual(added.target_registry, "refugees")


if __name__ == "__main__":
    unittest.main()
