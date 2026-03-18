from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.photo_service import photo_service
from app.views.api.album_view import PhotoArchiveRequest
from app.views.api.photo_view import PhotoRead, PhotoUpdateRequest


router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("", response_model=list[PhotoRead])
def list_photos(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
    location: str | None = Query(default=None),
    device: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort: str = Query(default="taken_desc"),
    include_duplicates: bool = Query(default=False),
    include_hidden: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[PhotoRead]:
    """按支持的筛选和排序条件返回照片列表。"""
    return photo_service.list_photos(
        db,
        year=year,
        month=month,
        location=location,
        device=device,
        tag=tag,
        sort=sort,
        include_duplicates=include_duplicates,
        include_hidden=include_hidden,
    )


@router.get("/random", response_model=PhotoRead | None)
def get_random_photo(
    exclude_on_this_day: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> PhotoRead | None:
    """返回一张用于探索浏览的随机照片。"""
    return photo_service.get_random_photo(db, exclude_on_this_day=exclude_on_this_day)


@router.get("/on-this-day", response_model=list[PhotoRead])
def get_on_this_day(db: Session = Depends(get_db)) -> list[PhotoRead]:
    """返回历年同月同日拍摄的照片。"""
    return photo_service.get_on_this_day(db)


@router.get("/duplicates", response_model=list[PhotoRead])
def list_duplicate_photos(db: Session = Depends(get_db)) -> list[PhotoRead]:
    """返回当前识别出的重复照片。"""
    return photo_service.list_duplicate_photos(db)


@router.post("/{photo_id}/archive", response_model=PhotoRead)
def archive_photo(
    photo_id: int,
    payload: PhotoArchiveRequest,
    db: Session = Depends(get_db),
) -> PhotoRead:
    """把照片归档隐藏，避免继续在系统中展示。"""
    photo = photo_service.archive_photo(db, photo_id, payload.reason)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.patch("/{photo_id}", response_model=PhotoRead)
def update_photo(
    photo_id: int,
    payload: PhotoUpdateRequest,
    db: Session = Depends(get_db),
) -> PhotoRead:
    """更新单张照片的基础信息。"""
    photo = photo_service.update_photo(db, photo_id, payload.model_dump(exclude_unset=True))
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.get("/{photo_id}", response_model=PhotoRead)
def get_photo(photo_id: int, db: Session = Depends(get_db)) -> PhotoRead:
    """返回单张照片的详情数据。"""
    photo = photo_service.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo
