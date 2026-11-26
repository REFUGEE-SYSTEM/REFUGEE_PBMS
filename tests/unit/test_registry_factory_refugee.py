import unittest
from openg2p_bg_task_registry_adapters.factory import RegistryFactory
from openg2p_bg_task_registry_adapters.computations import RegistryRefugee


class TestRegistryFactoryRefugee(unittest.TestCase):
    def test_factory_resolves_refugee_to_registry_refugee(self):
        adapter = RegistryFactory.get_registry_class("refugee")
        self.assertIsInstance(adapter, RegistryRefugee)


if __name__ == "__main__":
    unittest.main()
