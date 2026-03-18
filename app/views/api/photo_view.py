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
    device: str | None
    lens_model: str | None
    focal_length: str | None
    aperture: str | None
    exposure_time: str | None
    iso: int | None
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
    is_hidden: bool
    hidden_at: datetime | None
    hidden_reason: str | None
    archived_file_path: str | None
    duplicate_of_photo_id: int | None
    tags: list[PhotoTagRead] = []

    model_config = {"from_attributes": True}


class PhotoUpdateRequest(BaseModel):
    photo_taken_at: datetime | None = None
    location_name: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    device: str | None = None
    lens_model: str | None = None
    focal_length: str | None = None
    aperture: str | None = None
    exposure_time: str | None = None
    iso: int | None = None


class ScanRequest(BaseModel):
    path: str


class ScanResponse(BaseModel):
    scan_task_id: int
    processed_count: int
    new_count: int
    updated_count: int
    duplicate_count: int
    status: str
