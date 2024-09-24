from datetime import datetime
import uuid
from src.devices.schemas import Device, DeviceData, Location
from src.devices.models import devices_db, locations_db

async def register_device(device: Device) -> DeviceData:
    device_id = uuid.uuid4()
    created_at = datetime.now()
    device_data = DeviceData(
        device_id=device_id,
        device_name=device.device_name,
        user_id=device.user_id,
        created_at=created_at
    )
    devices_db[device_id] = device_data
    return device_data

async def update_device_location(device_id: uuid.UUID, location: Location) -> Location:
    if device_id not in locations_db:
        locations_db[device_id] = []
    locations_db[device_id].append(location.dict())
    return location

async def list_devices() -> list[DeviceData]:
    return list(devices_db.values())

async def remove_device(device_id: uuid.UUID) -> None:
    del devices_db[device_id]

