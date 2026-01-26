import os, sys
# backend/ klasörünü Python path’e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest, asyncio
from src.api.models.handle_domain import async_check_http_security

class TestHttpSecurity(unittest.TestCase):
    def test_headers_exist(self):
        result = asyncio.run(async_check_http_security("example.com"))
        policies = {item["policy"]: item["status"] for item in result}
        self.assertIn("Content Security Policy", policies)
        self.assertIn("Strict Transport Security", policies)

    def test_invalid_host(self):
        result = asyncio.run(async_check_http_security("no-such-domain"))
        for item in result:
            self.assertEqual(item["status"], "No")

if __name__ == "__main__":
    unittest.main()
