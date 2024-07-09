from typing import List
from uuid import UUID

from fastapi import HTTPException
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Device as DeviceModel
from src.app.models import User as UserModel
from src.app.schemas import DeviceCreate, DeviceData
from src.app.schemas import Location as LocationSchema
from src.app.schemas import UserCreate, UserResponse


async def create_user(session: AsyncSession, user: UserCreate) -> UserResponse:
    db_user = UserModel(email=user.email)
    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return UserResponse.from_orm(db_user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )


async def get_users(db: AsyncSession) -> List[UserResponse]:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]


async def get_specific_user(db: AsyncSession, user_id: UUID) -> UserResponse:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)


async def remove_user(db: AsyncSession, user_id: UUID):
    try:
        result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Device not found")

        await db.delete(user)
        await db.flush()
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def register_device(
    db: AsyncSession, user_id: UUID, device: DeviceCreate
) -> DeviceData:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    coordinates = f"SRID=4326;POINT({device.longitude} {device.latitude})"

    db_device = DeviceModel(
        name=device.device_name,
        user_id=user_id,
        coordinates=coordinates,
        timestamp=device.timestamp,
    )

    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return DeviceData.from_orm(db_device)


async def remove_device(db: AsyncSession, device_id: UUID):
    try:
        result = await db.execute(
            select(DeviceModel).filter(DeviceModel.id == device_id)
        )
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        await db.delete(device)
        await db.flush()
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def update_device_location(
    db: AsyncSession, device_id: UUID, location: LocationSchema
) -> LocationSchema:
    result = await db.execute(select(DeviceModel).filter(DeviceModel.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    coordinates = f"SRID=4326;POINT({location.longitude} {location.latitude})"
    device.coordinates = coordinates
    device.timestamp = location.timestamp

    await db.commit()
    await db.refresh(device)

    return LocationSchema(
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=device.timestamp,
    )


async def get_device_location(db: AsyncSession, device_id: UUID) -> LocationSchema:
    result = await db.execute(select(DeviceModel).filter(DeviceModel.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if not device.coordinates:
        raise HTTPException(status_code=404, detail="Location for device not found")

    point = to_shape(device.coordinates)

    return LocationSchema(
        latitude=point.y, longitude=point.x, timestamp=device.timestamp
    )


async def device_info_endpoint(db: AsyncSession, device_id: UUID) -> DeviceData:
    result = await db.execute(select(DeviceModel).filter(DeviceModel.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return DeviceData.from_orm(device)


async def list_devices(db: AsyncSession) -> List[DeviceData]:
    result = await db.execute(select(DeviceModel))
    devices = result.scalars().all()
    return [DeviceData.from_orm(device) for device in devices]
