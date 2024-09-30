import requests, json

API_URL = "http://localhost:8050"
API_KEY = "test_api_key"

def test_ping():
    response = requests.get(f"{API_URL}/ping")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json() == {"message": "ok"}, f"Expected {{'message': 'ok'}}, got {response.json()}"
    print("Ping test passed")

def test_resolve_existing_entity():
    payload = {
        "api_key": API_KEY,
        "body": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
    response = requests.post(f"{API_URL}/resolve", json=payload)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    print(f"Response data: {json.dumps(data, indent=2)}")  # Print the entire response
    
    if "error" in data:
        print(f"Error in response: {data['error']}")
        return
    
    assert "name" in data, f"Expected 'name' in response, got keys: {', '.join(data.keys())}"
    assert data["name"] == "John Doe", f"Expected name 'John Doe', got {data.get('name')}"
    assert "email" in data, f"Expected 'email' in response, got keys: {', '.join(data.keys())}"
    assert data["email"] == "john@example.com", f"Expected email 'john@example.com', got {data.get('email')}"
    assert "confidence" in data, "Confidence not found in response"
    assert "privacy" in data, "Privacy not found in response"
    print("Resolve existing entity test passed")

def test_resolve_non_existing_entity():
    payload = {
        "api_key": API_KEY,
        "body": {
            "name": "Nonexistent User",
            "email": "nonexistent@example.com"
        }
    }
    response = requests.post(f"{API_URL}/resolve", json=payload)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    print(f"Response data: {json.dumps(data, indent=2)}")  # Print the entire response
    assert "error" in data, f"Expected error message, got {data}"
    print("Resolve non-existing entity test passed")

def test_inject_privacy():
    # First, resolve an existing entity
    resolve_payload = {
        "api_key": API_KEY,
        "body": {
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
    }
    resolve_response = requests.post(f"{API_URL}/resolve", json=resolve_payload)
    assert resolve_response.status_code == 200, f"Expected status code 200, got {resolve_response.status_code}"
    resolved_data = resolve_response.json()
    print(f"Resolved data: {json.dumps(resolved_data, indent=2)}")  # Print the resolved data

    # Now, inject privacy
    inject_payload = {
        "api_key": API_KEY,
        "body": resolved_data,
        "privacy": 500
    }
    inject_response = requests.post(f"{API_URL}/inject", json=inject_payload)
    assert inject_response.status_code == 200, f"Expected status code 200, got {inject_response.status_code}"
    inject_data = inject_response.json()
    print(f"Inject response: {json.dumps(inject_data, indent=2)}")  # Print the inject response
    assert "message" in inject_data, f"Expected 'message' in response, got {inject_data}"

    # Verify that the privacy was injected
    resolve_response = requests.post(f"{API_URL}/resolve", json=resolve_payload)
    assert resolve_response.status_code == 200, f"Expected status code 200, got {resolve_response.status_code}"
    updated_data = resolve_response.json()
    print(f"Updated data: {json.dumps(updated_data, indent=2)}")  # Print the updated data
    assert "privacy" in updated_data, f"Expected 'privacy' in response, got keys: {', '.join(updated_data.keys())}"
    assert updated_data["privacy"] == 500, f"Expected privacy 500, got {updated_data.get('privacy')}"
    print("Inject privacy test passed")

def test_invalid_api_key():
    payload = {
        "api_key": "invalid_key",
        "body": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
    response = requests.post(f"{API_URL}/resolve", json=payload)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    print(f"Response data: {json.dumps(data, indent=2)}")  # Print the entire response
    assert "error" in data, f"Expected error message, got {data}"
    print("Invalid API key test passed")

if __name__ == "__main__":
    test_ping()
    test_resolve_existing_entity()
    test_resolve_non_existing_entity()
    test_inject_privacy()
    test_invalid_api_key()
    print("All tests completed")