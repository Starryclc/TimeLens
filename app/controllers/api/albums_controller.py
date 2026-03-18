from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.album_service import album_service
from app.views.api.album_view import (
    AlbumAddPhotosRequest,
    AlbumCreateRequest,
    AlbumDetailRead,
    AlbumSummaryRead,
)
from app.views.api.photo_view import PhotoRead


router = APIRouter(prefix="/albums", tags=["albums"])


@router.get("", response_model=list[AlbumSummaryRead])
def list_albums(db: Session = Depends(get_db)) -> list[AlbumSummaryRead]:
    """返回所有自定义相册。"""
    albums = album_service.list_albums(db)
    return [album_service.serialize_album_summary(album) for album in albums]


@router.post("", response_model=AlbumDetailRead)
def create_album(payload: AlbumCreateRequest, db: Session = Depends(get_db)) -> AlbumDetailRead:
    """创建新的自定义相册。"""
    album = album_service.create_album(db, payload.title, payload.description)
    return album_service.serialize_album_detail(album)


@router.get("/{album_id}", response_model=AlbumDetailRead)
def get_album(album_id: int, db: Session = Depends(get_db)) -> AlbumDetailRead:
    """返回自定义相册详情。"""
    album = album_service.get_album(db, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return album_service.serialize_album_detail(album)


@router.post("/{album_id}/photos", response_model=AlbumDetailRead)
def add_photos_to_album(
    album_id: int,
    payload: AlbumAddPhotosRequest,
    db: Session = Depends(get_db),
) -> AlbumDetailRead:
    """向自定义相册中追加已有照片。"""
    album = album_service.add_photos_to_album(db, album_id, payload.photo_ids)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return album_service.serialize_album_detail(album)


@router.post("/upload", response_model=PhotoRead)
def upload_photo(
    file: UploadFile = File(...),
    target_type: str = Form(...),
    album_id: int | None = Form(default=None),
    taken_at: str | None = Form(default=None),
    location_name: str | None = Form(default=None),
    city: str | None = Form(default=None),
    region: str | None = Form(default=None),
    country: str | None = Form(default=None),
    device_make: str | None = Form(default=None),
    device_model: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> PhotoRead:
    """上传本地照片到时间线或自定义相册。"""
    if target_type not in {"timeline", "album"}:
        raise HTTPException(status_code=400, detail="target_type must be timeline or album")
    if target_type == "album" and album_id is None:
        raise HTTPException(status_code=400, detail="album_id is required for album uploads")

    parsed_taken_at = None
    if taken_at:
        try:
            parsed_taken_at = datetime.fromisoformat(taken_at)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="taken_at must be ISO datetime") from exc

    photo = album_service.upload_photo(
        db,
        upload=file,
        target_type=target_type,
        album_id=album_id,
        taken_at=parsed_taken_at,
        location_name=location_name,
        city=city,
        region=region,
        country=country,
        device_make=device_make,
        device_model=device_model,
    )
    return photo
