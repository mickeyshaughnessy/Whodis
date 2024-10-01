import requests, random, json, time

API_URL = "http://localhost:8050"
API_KEY = "test_api_key"

def test_resolve_basic():
    data = {
        "api_key": API_KEY,
        "body": {"name": "John Doe", "email": "john@example.com"},
        "resolution": 500
    }
    response = requests.post(f"{API_URL}/resolve", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result and "features" in result["result"]
    print("Basic resolve test passed")

def test_inject_and_resolve():
    inject_data = {
        "api_key": API_KEY,
        "body": {"name": "Jane Smith", "email": "jane@example.com"},
        "privacy": 100
    }
    inject_response = requests.post(f"{API_URL}/inject", json=inject_data)
    assert inject_response.status_code == 200

    resolve_data = {
        "api_key": API_KEY,
        "body": {"name": "Jane Smith", "email": "jane@example.com"},
        "resolution": 1000
    }
    resolve_response = requests.post(f"{API_URL}/resolve", json=resolve_data)
    assert resolve_response.status_code == 200
    result = resolve_response.json()
    assert "result" in result and "features" in result["result"]
    print("Inject and resolve test passed")

def test_privacy_levels():
    data = {
        "api_key": API_KEY,
        "body": {"name": "Bob Johnson", "email": "bob@example.com"}
    }
    low_privacy = requests.post(f"{API_URL}/resolve", json={**data, "privacy": -1000}).json()
    high_privacy = requests.post(f"{API_URL}/resolve", json={**data, "privacy": 1000}).json()
    assert low_privacy["result"]["features"] != high_privacy["result"]["features"]
    print("Privacy levels test passed")

def test_error_handling():
    data = {"api_key": "invalid_key", "body": {}}
    response = requests.post(f"{API_URL}/resolve", json=data)
    assert response.status_code != 200
    print("Error handling test passed")

def test_resolution_performance():
    data = {
        "api_key": API_KEY,
        "body": {"name": "Alice Brown", "email": "alice@example.com"}
    }
    start_time = time.time()
    low_res = requests.post(f"{API_URL}/resolve", json={**data, "resolution": 0}).json()
    low_res_time = time.time() - start_time

    start_time = time.time()
    high_res = requests.post(f"{API_URL}/resolve", json={**data, "resolution": 1000}).json()
    high_res_time = time.time() - start_time

    assert low_res_time < high_res_time
    assert low_res["steps"] <= high_res["steps"]
    print("Resolution performance test passed")

def test_entity_matching():
    entities = [
        {"name": "John Smith", "email": "john@example.com"},
        {"name": "John Smith", "email": "johnsmith@example.com"},
        {"name": "J. Smith", "email": "john@example.com"}
    ]
    results = []
    for entity in entities:
        data = {"api_key": API_KEY, "body": entity, "resolution": 1000}
        response = requests.post(f"{API_URL}/resolve", json=data).json()
        results.append(response["result"])
    
    assert len(set(json.dumps(r) for r in results)) <= 2  # At least 2 should match
    print("Entity matching test passed")

if __name__ == "__main__":
    test_resolve_basic()
    test_inject_and_resolve()
    test_privacy_levels()
    test_error_handling()
    test_resolution_performance()
    test_entity_matching()
    print("All integration tests completed successfully")