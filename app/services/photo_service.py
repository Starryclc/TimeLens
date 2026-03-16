from __future__ import annotations

from datetime import datetime
from random import choice

from sqlalchemy import extract, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Photo, PhotoTag


class PhotoService:
    def list_photos(
        self,
        db: Session,
        *,
        year: int | None = None,
        month: int | None = None,
        location: str | None = None,
        device: str | None = None,
        tag: str | None = None,
        sort: str = "taken_desc",
    ) -> list[Photo]:
        stmt = select(Photo).options(selectinload(Photo.tags))

        if year is not None:
            stmt = stmt.where(extract("year", Photo.photo_taken_at) == year)
        if month is not None:
            stmt = stmt.where(extract("month", Photo.photo_taken_at) == month)
        if location:
            pattern = f"%{location}%"
            stmt = stmt.where(
                or_(
                    Photo.location_name.ilike(pattern),
                    Photo.city.ilike(pattern),
                    Photo.region.ilike(pattern),
                    Photo.country.ilike(pattern),
                )
            )
        if device:
            pattern = f"%{device}%"
            stmt = stmt.where(
                or_(Photo.device_make.ilike(pattern), Photo.device_model.ilike(pattern))
            )
        if tag:
            stmt = stmt.join(PhotoTag).where(func.lower(PhotoTag.tag) == tag.lower())

        if sort == "imported_desc":
            stmt = stmt.order_by(Photo.imported_at.desc())
        else:
            stmt = stmt.order_by(Photo.photo_taken_at.desc().nullslast(), Photo.id.desc())

        return list(db.scalars(stmt))

    def get_photo(self, db: Session, photo_id: int) -> Photo | None:
        stmt = (
            select(Photo)
            .where(Photo.id == photo_id)
            .options(selectinload(Photo.tags), selectinload(Photo.faces))
        )
        return db.scalar(stmt)

    def get_recent_photos(self, db: Session, limit: int = 24) -> list[Photo]:
        stmt = (
            select(Photo)
            .options(selectinload(Photo.tags))
            .order_by(Photo.imported_at.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt))

    def get_random_photo(self, db: Session) -> Photo | None:
        stmt = select(Photo.id)
        ids = list(db.scalars(stmt))
        if not ids:
            return None
        return self.get_photo(db, choice(ids))

    def get_on_this_day(self, db: Session, today: datetime | None = None) -> list[Photo]:
        current = today or datetime.now()
        stmt = (
            select(Photo)
            .options(selectinload(Photo.tags))
            .where(extract("month", Photo.photo_taken_at) == current.month)
            .where(extract("day", Photo.photo_taken_at) == current.day)
            .order_by(Photo.photo_taken_at.desc())
        )
        return list(db.scalars(stmt))

    def get_location_options(self, db: Session) -> list[str]:
        stmt = select(Photo.location_name).where(Photo.location_name.is_not(None)).distinct()
        return [value for value in db.scalars(stmt) if value]

    def get_device_options(self, db: Session) -> list[str]:
        stmt = select(Photo.device_model).where(Photo.device_model.is_not(None)).distinct()
        return [value for value in db.scalars(stmt) if value]


photo_service = PhotoService()
