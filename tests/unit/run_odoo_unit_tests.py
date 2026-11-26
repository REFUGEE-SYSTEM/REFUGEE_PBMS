#!/usr/bin/env python3
"""Runner for standalone Odoo unit tests."""
import os
import sys
import unittest

import odoo
from odoo.tools import config

config_path = os.path.abspath("infrastructure/configs/odoo.conf")
config.parse_config(["-c", config_path])

from odoo.addons.g2p_registry_addon.tests import (
    test_refugee_registry,
    test_ugx_currency,
    test_refugee_workflow,
)

loader = unittest.TestLoader()
suite = unittest.TestSuite([
    loader.loadTestsFromModule(m) for m in [
        test_refugee_registry,
        test_ugx_currency,
        test_refugee_workflow,
    ]
])
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
