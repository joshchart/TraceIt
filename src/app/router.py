from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas import DeviceCreate, DeviceData
from src.app.schemas import Location as LocationModel
from src.app.schemas import Location as LocationSchema
from src.app.schemas import UserCreate, UserResponse
from src.app.service import (
    create_user,
    device_info_endpoint,
    get_device_location,
    get_specific_user,
    get_users,
    list_devices,
    register_device,
    remove_device,
    remove_user,
    update_device_location,
)
from src.database import get_session

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user_endpoint(
    user: UserCreate, db: AsyncSession = Depends(get_session)
):
    return await create_user(db, user)


# NOTE: ADMIN ONLY
@router.get("/users", response_model=List[UserResponse])
async def read_users(db: AsyncSession = Depends(get_session)):
    return await get_users(db)


@router.get("/users/{user_id}", response_model=UserResponse, status_code=201)
async def get_specific_user_endpoint(
    user_id: UUID, db: AsyncSession = Depends(get_session)
):
    return await get_specific_user(db, user_id)


@router.post("/users/{user_id}/devices", response_model=DeviceData, status_code=201)
async def register_device_endpoint(
    user_id: UUID, device: DeviceCreate, db: AsyncSession = Depends(get_session)
):
    return await register_device(db, user_id, device)


@router.delete("/users/{user_id}", status_code=204)
async def remove_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_session)):
    await remove_user(db, user_id)


@router.delete("/devices/{device_id}", status_code=204)
async def remove_device_endpoint(
    device_id: UUID, db: AsyncSession = Depends(get_session)
):
    await remove_device(db, device_id)


@router.post("/devices/{device_id}/locations", status_code=200)
async def update_device_location_endpoint(
    device_id: UUID,
    location: LocationModel,
    db: AsyncSession = Depends(get_session),
):
    return await update_device_location(db, device_id, location)


@router.get(
    "/devices/{device_id}/location", response_model=LocationSchema, status_code=200
)
async def get_current_location_endpoint(
    device_id: UUID,
    db: AsyncSession = Depends(get_session),
):
    return await get_device_location(db, device_id)


@router.get("/devices/{device_id}", response_model=DeviceData)
async def get_device_info_endpoint(
    device_id: UUID,
    db: AsyncSession = Depends(get_session),
):
    return await device_info_endpoint(db, device_id)


@router.get("/devices", response_model=List[DeviceData])
async def list_devices_endpoint(db: AsyncSession = Depends(get_session)):
    return await list_devices(db)
