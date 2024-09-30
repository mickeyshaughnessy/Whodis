import requests, json, unittest

API_URL = "http://localhost:8050"
API_KEY = "test_api_key"

class WhodisIntegrationTests(unittest.TestCase):
    def test_ping(self):
        response = requests.get(f"{API_URL}/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "ok"})

    def test_resolve_existing_entity(self):
        payload = {
            "api_key": API_KEY,
            "body": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        response = requests.post(f"{API_URL}/resolve", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "john@example.com")
        self.assertIn("confidence", data)
        self.assertIn("privacy", data)

    def test_resolve_non_existing_entity(self):
        payload = {
            "api_key": API_KEY,
            "body": {
                "name": "Nonexistent User",
                "email": "nonexistent@example.com"
            }
        }
        response = requests.post(f"{API_URL}/resolve", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)

    def test_inject_privacy(self):
        # First, resolve an existing entity
        resolve_payload = {
            "api_key": API_KEY,
            "body": {
                "name": "Jane Smith",
                "email": "jane@example.com"
            }
        }
        resolve_response = requests.post(f"{API_URL}/resolve", json=resolve_payload)
        self.assertEqual(resolve_response.status_code, 200)
        resolved_data = resolve_response.json()

        # Now, inject privacy
        inject_payload = {
            "api_key": API_KEY,
            "body": resolved_data,
            "privacy": 500
        }
        inject_response = requests.post(f"{API_URL}/inject", json=inject_payload)
        self.assertEqual(inject_response.status_code, 200)
        inject_data = inject_response.json()
        self.assertIn("message", inject_data)

        # Verify that the privacy was injected
        resolve_response = requests.post(f"{API_URL}/resolve", json=resolve_payload)
        self.assertEqual(resolve_response.status_code, 200)
        updated_data = resolve_response.json()
        self.assertEqual(updated_data["privacy"], 500)

    def test_invalid_api_key(self):
        payload = {
            "api_key": "invalid_key",
            "body": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        response = requests.post(f"{API_URL}/resolve", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()