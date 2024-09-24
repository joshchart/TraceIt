from datetime import datetime
from uuid import UUID

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.dialects.postgresql import Any


class UserCreate(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class DeviceCreate(BaseModel):
    device_name: str = Field(min_length=1, max_length=128)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime


class DeviceData(BaseModel):
    id: UUID
    device_name: str = Field(min_length=1, max_length=128)
    user_id: UUID
    created_at: datetime
    latitude: float = Field(None, ge=-90, le=90)
    longitude: float = Field(None, ge=-180, le=180)
    timestamp: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

    @classmethod
    def from_orm(cls, obj: Any) -> "DeviceData":
        point = to_shape(obj.coordinates)
        latitude = point.y
        longitude = point.x

        return cls(
            id=obj.id,
            device_name=obj.name,
            user_id=obj.user_id,
            created_at=obj.created_at,
            latitude=latitude,
            longitude=longitude,
            timestamp=obj.timestamp,
        )


class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
