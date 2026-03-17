from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.photo_service import photo_service
from app.views.api.photo_view import PhotoRead


router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("", response_model=list[PhotoRead])
def list_photos(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
    location: str | None = Query(default=None),
    device: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort: str = Query(default="taken_desc"),
    db: Session = Depends(get_db),
) -> list[PhotoRead]:
    return photo_service.list_photos(
        db,
        year=year,
        month=month,
        location=location,
        device=device,
        tag=tag,
        sort=sort,
    )


@router.get("/random", response_model=PhotoRead | None)
def get_random_photo(db: Session = Depends(get_db)) -> PhotoRead | None:
    return photo_service.get_random_photo(db)


@router.get("/on-this-day", response_model=list[PhotoRead])
def get_on_this_day(db: Session = Depends(get_db)) -> list[PhotoRead]:
    return photo_service.get_on_this_day(db)


@router.get("/{photo_id}", response_model=PhotoRead)
def get_photo(photo_id: int, db: Session = Depends(get_db)) -> PhotoRead:
    photo = photo_service.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo
