import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest, asyncio
from src.api.ipgeolocation import get_ip_location

class TestIPGeo(unittest.TestCase):
    def test_valid_ip(self):
        result = asyncio.run(get_ip_location("8.8.8.8"))
        self.assertIn("country", result)
        self.assertEqual(result.get("query"), "8.8.8.8")

    def test_invalid_ip(self):
        result = asyncio.run(get_ip_location("999.999.999.999"))
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
