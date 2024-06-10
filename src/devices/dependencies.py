from uuid import UUID
from collections.abc import Mapping
from fastapi import HTTPException
from src.devices.models import devices_db, locations_db

async def valid_device_id(device_id: UUID) -> Mapping:
    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

async def valid_device_location(device_id: UUID) -> Mapping:
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    if device_id not in locations_db or not locations_db[device_id]:
        raise HTTPException(status_code=404, detail="Location not found")
    return locations_db[device_id][-1]  # Return the latest location
