import pytest


# ============================================================================
# User Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_and_get_user(client):
    """Test creating a user and then retrieving it."""
    # Create a new user
    request_body = {"email": "test_user@example.com"}
    response = await client.post("/api/v1/users", json=request_body)
    assert response.status_code == 201

    response_data = response.json()
    assert "id" in response_data
    assert response_data["email"] == request_body["email"]
    assert "created_at" in response_data

    user_id = response_data["id"]

    # Retrieve the user
    get_response = await client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["email"] == request_body["email"]


@pytest.mark.asyncio
async def test_get_users_list(client):
    """Test listing all users."""
    # Create a user first
    request_body = {"email": "list_test@example.com"}
    create_response = await client.post("/api/v1/users", json=request_body)
    assert create_response.status_code == 201

    # List users
    response = await client.get("/api/v1/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    
    # Find our user in the list
    emails = [u["email"] for u in users]
    assert "list_test@example.com" in emails


@pytest.mark.asyncio
async def test_create_delete_user(client):
    """Test creating and deleting a user."""
    request_body = {"email": "delete_test@example.com"}

    # Create the new user
    response = await client.post("/api/v1/users", json=request_body)
    assert response.status_code == 201

    response_data = response.json()
    assert "id" in response_data
    user_id = response_data["id"]

    # Delete the user
    delete_response = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_response.status_code == 204

    # Verify the user has been deleted
    get_response = await client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/users/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# Device Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_device(client):
    """Test creating a device for a user."""
    # First create a user
    user_response = await client.post(
        "/api/v1/users", 
        json={"email": "device_owner@example.com"}
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    # Create a device
    device_request = {
        "device_name": "test_device",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    response = await client.post(
        f"/api/v1/users/{user_id}/devices", 
        json=device_request
    )
    assert response.status_code == 201

    device_data = response.json()
    assert "id" in device_data
    assert device_data["device_name"] == device_request["device_name"]
    assert device_data["latitude"] == device_request["latitude"]
    assert device_data["longitude"] == device_request["longitude"]
    assert device_data["user_id"] == user_id


@pytest.mark.asyncio
async def test_get_device_list(client):
    """Test listing all devices."""
    # Create a user and device first
    user_response = await client.post(
        "/api/v1/users",
        json={"email": "device_list_owner@example.com"}
    )
    user_id = user_response.json()["id"]

    device_request = {
        "device_name": "list_test_device",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    await client.post(f"/api/v1/users/{user_id}/devices", json=device_request)

    # List devices
    response = await client.get("/api/v1/devices")
    assert response.status_code == 200
    devices = response.json()
    assert isinstance(devices, list)
    assert len(devices) >= 1


@pytest.mark.asyncio
async def test_get_device_info(client):
    """Test getting a specific device."""
    # Create user and device
    user_response = await client.post(
        "/api/v1/users",
        json={"email": "device_info_owner@example.com"}
    )
    user_id = user_response.json()["id"]

    device_request = {
        "device_name": "info_test_device",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    device_response = await client.post(
        f"/api/v1/users/{user_id}/devices",
        json=device_request
    )
    device_id = device_response.json()["id"]

    # Get device info
    response = await client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    device_data = response.json()
    assert device_data["device_name"] == device_request["device_name"]
    assert device_data["latitude"] == device_request["latitude"]
    assert device_data["longitude"] == device_request["longitude"]


@pytest.mark.asyncio
async def test_get_device_location(client):
    """Test getting a device's location."""
    # Create user and device
    user_response = await client.post(
        "/api/v1/users",
        json={"email": "device_location_owner@example.com"}
    )
    user_id = user_response.json()["id"]

    device_request = {
        "device_name": "location_test_device",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    device_response = await client.post(
        f"/api/v1/users/{user_id}/devices",
        json=device_request
    )
    device_id = device_response.json()["id"]

    # Get device location
    response = await client.get(f"/api/v1/devices/{device_id}/location")
    assert response.status_code == 200
    location_data = response.json()
    assert location_data["latitude"] == device_request["latitude"]
    assert location_data["longitude"] == device_request["longitude"]
    assert "timestamp" in location_data


@pytest.mark.asyncio
async def test_update_device_location(client):
    """Test updating a device's location."""
    # Create user and device
    user_response = await client.post(
        "/api/v1/users",
        json={"email": "update_location_owner@example.com"}
    )
    user_id = user_response.json()["id"]

    device_request = {
        "device_name": "update_location_device",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    device_response = await client.post(
        f"/api/v1/users/{user_id}/devices",
        json=device_request
    )
    device_id = device_response.json()["id"]

    # Update location
    new_location = {
        "latitude": 0.0,
        "longitude": 0.0,
        "timestamp": "2024-07-12T15:48:57.639Z",
    }
    update_response = await client.post(
        f"/api/v1/devices/{device_id}/locations",
        json=new_location
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["latitude"] == new_location["latitude"]
    assert updated_data["longitude"] == new_location["longitude"]


@pytest.mark.asyncio
async def test_delete_device(client):
    """Test deleting a device."""
    # Create user and device
    user_response = await client.post(
        "/api/v1/users",
        json={"email": "delete_device_owner@example.com"}
    )
    user_id = user_response.json()["id"]

    device_request = {
        "device_name": "delete_test_device",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    device_response = await client.post(
        f"/api/v1/users/{user_id}/devices",
        json=device_request
    )
    device_id = device_response.json()["id"]

    # Delete device
    delete_response = await client.delete(f"/api/v1/devices/{device_id}")
    assert delete_response.status_code == 204

    # Verify deleted
    get_response = await client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cascade_delete_user_with_devices(client):
    """Test that deleting a user also deletes their devices."""
    # Create user
    user_response = await client.post(
        "/api/v1/users",
        json={"email": "cascade_delete@example.com"}
    )
    user_id = user_response.json()["id"]

    # Create device
    device_request = {
        "device_name": "cascade_device",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }
    device_response = await client.post(
        f"/api/v1/users/{user_id}/devices",
        json=device_request
    )
    device_id = device_response.json()["id"]

    # Delete user
    delete_response = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_response.status_code == 204

    # Verify user deleted
    get_user_response = await client.get(f"/api/v1/users/{user_id}")
    assert get_user_response.status_code == 404

    # Verify device also deleted (cascade)
    get_device_response = await client.get(f"/api/v1/devices/{device_id}")
    assert get_device_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_device(client):
    """Test getting a device that doesn't exist."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/devices/{fake_id}")
    assert response.status_code == 404
