from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.photo_service import photo_service


router = APIRouter(tags=["meta"])


@router.get("/locations", response_model=list[str])
def get_locations(db: Session = Depends(get_db)) -> list[str]:
    """返回前端筛选可用的地点列表。"""
    return photo_service.get_location_options(db)


@router.get("/devices", response_model=list[str])
def get_devices(db: Session = Depends(get_db)) -> list[str]:
    """返回前端筛选可用的设备列表。"""
    return photo_service.get_device_options(db)
