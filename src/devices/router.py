from collections.abc import Mapping
from uuid import UUID
from fastapi import APIRouter, Depends
from src.devices.schemas import Device, Location, DeviceData
from src.devices.service import register_device, remove_device, update_device_location, list_devices
from src.devices.dependencies import valid_device_id, valid_device_location

router = APIRouter()

@router.post("/devices", response_model=DeviceData, status_code=201)
async def register_device_endpoint(device: Device):
    return await register_device(device)

@router.post("/devices/{device_id}/locations", status_code=200)
async def update_device_location_endpoint(
    device_id: UUID,
    location: Location,
):
    return await update_device_location(device_id, location)

@router.get("/devices/{device_id}/location", response_model=Location, status_code=200)
async def get_current_location_endpoint(
    location: Mapping = Depends(valid_device_location) 
):
    return location

@router.get("/devices/{device_id}", response_model=DeviceData)
async def get_device_info_endpoint(
    device: Mapping = Depends(valid_device_id)  
):
    return device

@router.get("/devices", response_model=list[DeviceData])
async def list_devices_endpoint():
    return await list_devices()

@router.delete("/devices/{device_id}", status_code=204)
async def remove_device_endpoint(
    device: DeviceData = Depends(valid_device_id)
):  
    return await remove_device(device.device_id)