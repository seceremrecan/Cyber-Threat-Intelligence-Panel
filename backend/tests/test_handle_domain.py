# backend/tests/test_handle_domain.py

import os
import sys
import unittest
import asyncio
from unittest.mock import patch

# tests/ klasörünün bir üstü (backend/) path'e eklensin:
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# handle_domain fonksiyonu models altından geliyor
from src.api.models.handle_domain import handle_domain

class TestHandleDomain(unittest.TestCase):
    # Tüm async bağımlılıkları mock'luyoruz
    @patch("src.api.models.handle_domain.async_get_dns", return_value={})
    @patch("src.api.models.handle_domain.async_check_http_security", return_value=[])
    @patch("src.api.models.handle_domain.async_get_robots_disallows", return_value={"status": "success", "data": []})
    @patch("src.api.models.handle_domain.async_get_whois", return_value={})
    @patch("src.api.models.handle_domain.get_alienvault_data", return_value={"type": "Domain", "data": {}, "tags": []})
    @patch("src.api.models.handle_domain.get_ip_location", return_value={"query": "globalpharmastore.com", "lat": "0", "lon": "0", "city": "", "country": ""})
    def test_valid_domain(self,
                          mock_iploc,
                          mock_av,
                          mock_whois,
                          mock_robots,
                          mock_sec,
                          mock_dns):
        """URL girdiğinde Type=Domain dönmeli"""
        result = asyncio.run(handle_domain("https://globalpharmastore.com/"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["Type"], "Domain")

    @patch("src.api.models.handle_domain.async_get_dns", return_value={})
    @patch("src.api.models.handle_domain.async_check_http_security", return_value=[])
    @patch("src.api.models.handle_domain.async_get_robots_disallows", return_value={"status": "success", "data": []})
    @patch("src.api.models.handle_domain.async_get_whois", return_value={})
    @patch("src.api.models.handle_domain.get_alienvault_data", return_value={"type": "IPv4", "data": {}, "tags": []})
    @patch("src.api.models.handle_domain.get_ip_location", return_value={"query": "152.32.128.64", "lat": "0", "lon": "0", "city": "", "country": ""})
    def test_valid_ip(self,
                      mock_iploc,
                      mock_av,
                      mock_whois,
                      mock_robots,
                      mock_sec,
                      mock_dns):
        """IP girdiğinde Type=IPv4 dönmeli"""
        result = asyncio.run(handle_domain("152.32.128.64"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["Type"], "IPv4")

    @patch("src.api.models.handle_domain.async_get_dns", return_value={})
    @patch("src.api.models.handle_domain.async_check_http_security", return_value=[])
    @patch("src.api.models.handle_domain.async_get_robots_disallows", return_value={"status": "success", "data": []})
    @patch("src.api.models.handle_domain.async_get_whois", return_value={})
    @patch("src.api.models.handle_domain.get_alienvault_data", return_value={"type": "Email", "data": {}, "tags": []})
    @patch("src.api.models.handle_domain.get_ip_location", return_value={"query": "german@gmail.com", "lat": "", "lon": "", "city": "", "country": ""})
    def test_valid_email(self,
                         mock_iploc,
                         mock_av,
                         mock_whois,
                         mock_robots,
                         mock_sec,
                         mock_dns):
        """E-posta girdiğinde Type=Email dönmeli"""
        result = asyncio.run(handle_domain("german@gmail.com"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["Type"], "Email")

if __name__ == "__main__":
    unittest.main()
