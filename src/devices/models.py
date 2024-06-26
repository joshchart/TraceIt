from datetime import datetime
from typing import Dict, List
from uuid import UUID

from src.devices.schemas import DeviceData, Location

default_device_id = UUID("00000000-0000-0000-0000-000000000000")

devices_db: Dict[UUID, DeviceData] = {
    default_device_id: DeviceData(
        device_id=default_device_id,
        device_name="Default Device",
        user_id="default_user",
        created_at=datetime.now(),
    )
}
locations_db: Dict[UUID, List[Location]] = {
    default_device_id: [Location(latitude=0.0, longitude=0.0, timestamp=datetime.now())]
}


# devices_db: Dict[UUID, DeviceData] = {}
# locations_db: Dict[UUID, List[Location]] = {}
