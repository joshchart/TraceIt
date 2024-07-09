from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Device as DeviceModel
from src.database import get_session


async def valid_device_id(id: UUID, db: AsyncSession = Depends(get_session)) -> UUID:
    result = await db.execute(select(DeviceModel.id).filter(DeviceModel.id == id))
    device_id = result.scalar_one_or_none()
    if not device_id:
        raise HTTPException(status_code=404, detail="Device not found")
    return id
