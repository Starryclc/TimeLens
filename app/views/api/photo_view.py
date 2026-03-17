from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PhotoTagRead(BaseModel):
    id: int
    tag: str
    source: str

    model_config = {"from_attributes": True}


class PhotoRead(BaseModel):
    id: int
    file_path: str
    file_name: str
    photo_taken_at: datetime | None
    imported_at: datetime
    device_make: str | None
    device_model: str | None
    width: int | None
    height: int | None
    file_size: int
    mime_type: str | None
    gps_lat: float | None
    gps_lon: float | None
    location_source: str
    location_name: str | None
    city: str | None
    region: str | None
    country: str | None
    scene_label: str | None
    ai_description: str | None
    thumbnail_path: str | None
    status: str
    exif_summary: str | None
    is_duplicate: bool
    duplicate_of_photo_id: int | None
    tags: list[PhotoTagRead] = []

    model_config = {"from_attributes": True}


class ScanRequest(BaseModel):
    path: str


class ScanResponse(BaseModel):
    scan_task_id: int
    processed_count: int
    new_count: int
    updated_count: int
    duplicate_count: int
    status: str
