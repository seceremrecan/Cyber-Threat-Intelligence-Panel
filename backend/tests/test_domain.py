import os, sys
# backend/ klasörünü Python path’e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest, json
from app import app   # artık çalışacak

class TestDomainEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_valid_domain(self):
        resp = self.client.post("/api/domain", json={"domain":"example.com"})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        # Eğer Data_Breach döndüyse, en azından bu anahtarı kontrol edelim
        self.assertTrue(
            "IoC" in data or "Data_Breach" in data,
            f"Beklenen 'IoC' ya da 'Data_Breach' anahtarlarından en az biri olmalı, ama data: {data}"
        )

    def test_empty_domain(self):
        resp = self.client.post("/api/domain", json={"domain":""})
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertEqual(data.get("message"), "Domain is required")

if __name__ == "__main__":
    unittest.main()
