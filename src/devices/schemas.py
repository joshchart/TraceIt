from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class Device(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    device_name: str = Field(min_length=1, max_length=128)

class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime

class DeviceData(BaseModel):
    device_id: UUID
    device_name: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    created_at: datetime