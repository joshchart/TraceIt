from datetime import datetime
from fastapi.testclient import TestClient
from src.main import app  

client = TestClient(app)

def test_register_device():
    device_data = {"user_id": "user123", "device_name": "Test Device"}
    response = client.post("/api/v1/devices", json=device_data)
    assert response.status_code == 201
    assert response.json()["user_id"] == device_data["user_id"]
    assert response.json()["device_name"] == device_data["device_name"]

def test_update_device_location():
    # First, create a device
    device_data = {"user_id": "user123", "device_name": "Test Device"}
    register_response = client.post("/api/v1/devices", json=device_data)
    device_id = register_response.json()["device_id"]

    # Then, update its location
    location_data = {"latitude": 12.34, "longitude": 56.78, "timestamp": datetime.now().isoformat()}
    response = client.post(f"/api/v1/devices/{device_id}/locations", json=location_data)
    assert response.status_code == 200
    assert response.json()["latitude"] == location_data["latitude"]
    assert response.json()["longitude"] == location_data["longitude"]

def test_get_current_location():
    # First, create a device
    device_data = {"user_id": "user123", "device_name": "Test Device"}
    register_response = client.post("/api/v1/devices", json=device_data)
    device_id = register_response.json()["device_id"]

    # Then, update its location
    location_data = {"latitude": 12.34, "longitude": 56.78, "timestamp": datetime.now().isoformat()}
    client.post(f"/api/v1/devices/{device_id}/locations", json=location_data)

    # Now, get the current location
    response = client.get(f"/api/v1/devices/{device_id}/location")
    assert response.status_code == 200
    assert response.json()["latitude"] == location_data["latitude"]
    assert response.json()["longitude"] == location_data["longitude"]

def test_list_devices():
    # First, create a device
    device_data = {"user_id": "user123", "device_name": "Test Device"}
    client.post("/api/v1/devices", json=device_data)

    response = client.get("/api/v1/devices")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_remove_device():
    # First, create a device
    device_data = {"user_id": "user123", "device_name": "Test Device"}
    register_response = client.post("/api/v1/devices", json=device_data)
    device_id = register_response.json()["device_id"]

    # Second, remove the device
    response = client.delete(f"/api/v1/devices/{device_id}")
    assert response.status_code == 204

    # Verify the device was removed
    response_length = client.get("/api/v1/devices")
    devices = response_length.json()
    assert all(device["device_id"] != device_id for device in devices)