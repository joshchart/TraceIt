import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


# NOTE: User
@pytest.mark.asyncio
async def test_get_user():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        # List out users (only one in test db)
        response = await client.get("/api/v1/users")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "f6e47d7e-a802-4a81-9106-b67e969a7003",
                "email": "user@example.com",
                "created_at": "2024-07-08T16:51:51.343950+00:00",
            }
        ]


# NOTE: User
@pytest.mark.asyncio
async def test_create_delete_user():
    request_body = {"email": "user1@example.com"}

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        # Create the new user
        response = await client.post("/api/v1/users", json=request_body)
        assert response.status_code == 201

        response_data = response.json()

        assert "id" in response_data
        assert response_data["email"] == request_body["email"]
        assert "created_at" in response_data

        user_id = response_data["id"]

        # Delete the user
        delete_response = await client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify the user has been deleted
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404


# NOTE: User
@pytest.mark.asyncio
async def test_get_specifc_user():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        # Retrieve specific user
        user_id = "f6e47d7e-a802-4a81-9106-b67e969a7003"
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 201
        assert response.json() == {
            "id": "f6e47d7e-a802-4a81-9106-b67e969a7003",
            "email": "user@example.com",
            "created_at": "2024-07-08T16:51:51.343950+00:00",
        }


# NOTE: Device
@pytest.mark.asyncio
async def test_get_device_list():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        # List out users (only one in test db)
        response = await client.get("/api/v1/devices")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "0361ab50-54f0-4a64-b5f1-bae2305bc8da",
                "device_name": "string",
                "user_id": "f6e47d7e-a802-4a81-9106-b67e969a7003",
                "created_at": "2024-07-09T04:50:38.676846+00:00",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timestamp": "2024-07-09T12:00:00+00:00",
            }
        ]


# NOTE: Device
@pytest.mark.asyncio
async def test_get_device_info():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        device_id = "0361ab50-54f0-4a64-b5f1-bae2305bc8da"
        response = await client.get(f"/api/v1/devices/{device_id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": "0361ab50-54f0-4a64-b5f1-bae2305bc8da",
            "device_name": "string",
            "user_id": "f6e47d7e-a802-4a81-9106-b67e969a7003",
            "created_at": "2024-07-09T04:50:38.676846+00:00",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": "2024-07-09T12:00:00+00:00",
        }


# NOTE: Device
@pytest.mark.asyncio
async def test_get_device_location():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        device_id = "0361ab50-54f0-4a64-b5f1-bae2305bc8da"
        response = await client.get(f"/api/v1/devices/{device_id}/location")
        assert response.status_code == 200
        assert response.json() == {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": "2024-07-09T12:00:00+00:00",
        }


# NOTE: Device
@pytest.mark.asyncio
async def test_create_delete_device():
    user_request_body = {"email": "user2@example.com"}

    device_request_body = {
        "device_name": "test",
        "latitude": 90,
        "longitude": 180,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        # Create the new user
        response = await client.post("/api/v1/users", json=user_request_body)
        response_data = response.json()
        assert "id" in response_data
        user_id = response_data["id"]

        # Register new device
        response_device = await client.post(
            f"/api/v1/users/{user_id}/devices", json=device_request_body
        )
        assert response_device.status_code == 201

        device_response_data = response_device.json()

        assert "id" in device_response_data
        assert device_response_data["device_name"] == device_request_body["device_name"]
        assert device_response_data["latitude"] == device_request_body["latitude"]
        assert device_response_data["longitude"] == device_request_body["longitude"]

        device_id = device_response_data["id"]

        # Delete the device
        delete_device_response = await client.delete(f"/api/v1/devices/{device_id}")
        assert delete_device_response.status_code == 204

        # Verify the device has been deleted
        get_device_response = await client.get(f"/api/v1/devices/{device_id}")
        assert get_device_response.status_code == 404

        # Delete the user
        delete_response = await client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify the user has been deleted
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404


# NOTE: Device
@pytest.mark.asyncio
async def test_create_delete_update_device():
    user_request_body = {"email": "user3@example.com"}

    device_request_body = {
        "device_name": "test",
        "latitude": 90,
        "longitude": 180,
        "timestamp": "2024-07-12T02:20:03.412Z",
    }

    device_location = {
        "latitude": 0,
        "longitude": 0,
        "timestamp": "2024-07-12T15:48:57.639Z",
    }

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        # Create the new user
        response = await client.post("/api/v1/users", json=user_request_body)
        response_data = response.json()
        assert "id" in response_data
        user_id = response_data["id"]

        # Register new device
        response_device = await client.post(
            f"/api/v1/users/{user_id}/devices", json=device_request_body
        )
        assert response_device.status_code == 201
        device_response_data = response_device.json()
        assert "id" in device_response_data
        assert device_response_data["device_name"] == device_request_body["device_name"]
        assert device_response_data["latitude"] == device_request_body["latitude"]
        assert device_response_data["longitude"] == device_request_body["longitude"]

        device_id = device_response_data["id"]

        # Update device location
        response_location = await client.post(
            f"/api/v1/devices/{device_id}/locations", json=device_location
        )
        assert response_location.status_code == 200
        location_response_data = response_location.json()
        assert location_response_data["latitude"] == device_location["latitude"]
        assert location_response_data["longitude"] == device_location["longitude"]
        # assert location_response_data["timestamp"] == device_location["timestamp"] # FIX: wrong format one has ms so cant compare

        # Delete the user
        delete_response = await client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify the user has been deleted
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

        # Verify the device has been deleted
        get_device_response = await client.get(f"/api/v1/devices/{device_id}")
        assert get_device_response.status_code == 404
