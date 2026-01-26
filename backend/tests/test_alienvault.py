import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest, asyncio
from src.api.alienvault import get_alienvault_data

class TestAlienVault(unittest.TestCase):
    def test_domain(self):
        result = asyncio.run(get_alienvault_data("example.com"))
        self.assertIn("type", result)
        self.assertIn("data", result)

    def test_invalid_ioc(self):
        result = asyncio.run(get_alienvault_data("!!!invalid!!!"))
        self.assertEqual(result["type"], "unknown")
        self.assertIsInstance(result["tags"], list)

if __name__ == "__main__":
    unittest.main()
