from __future__ import annotations

from datetime import datetime
from random import choice
from pathlib import Path

from sqlalchemy import extract, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Photo, PhotoTag
from app.services.file_service import archive_photo_file


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
        include_duplicates: bool = False,
        include_hidden: bool = False,
    ) -> list[Photo]:
        """按支持的画廊筛选条件返回照片列表。"""
        stmt = select(Photo).options(selectinload(Photo.tags))

        if not include_hidden:
            stmt = stmt.where(Photo.is_hidden.is_(False))
        if not include_duplicates:
            stmt = stmt.where(Photo.is_duplicate.is_(False))

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
        """返回加载了关联详情数据的单张照片。"""
        stmt = (
            select(Photo)
            .where(Photo.id == photo_id)
            .options(selectinload(Photo.tags), selectinload(Photo.faces))
        )
        return db.scalar(stmt)

    def get_recent_photos(self, db: Session, limit: int = 24) -> list[Photo]:
        """返回最近导入的照片列表。"""
        stmt = (
            select(Photo)
            .options(selectinload(Photo.tags))
            .order_by(Photo.imported_at.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt))

    def get_random_photo(
        self,
        db: Session,
        *,
        exclude_on_this_day: bool = True,
        today: datetime | None = None,
    ) -> Photo | None:
        """在存在照片时返回一张随机照片，可排除那年今日照片。"""
        stmt = select(Photo.id).where(Photo.is_hidden.is_(False), Photo.is_duplicate.is_(False))
        current = today or datetime.now()
        if exclude_on_this_day:
            stmt = stmt.where(
                or_(
                    Photo.photo_taken_at.is_(None),
                    extract("month", Photo.photo_taken_at) != current.month,
                    extract("day", Photo.photo_taken_at) != current.day,
                )
            )
        ids = list(db.scalars(stmt))
        if not ids:
            return None
        return self.get_photo(db, choice(ids))

    def get_on_this_day(self, db: Session, today: datetime | None = None) -> list[Photo]:
        """返回与当天同月同日的历史照片。"""
        current = today or datetime.now()
        stmt = (
            select(Photo)
            .options(selectinload(Photo.tags))
            .where(Photo.is_hidden.is_(False), Photo.is_duplicate.is_(False))
            .where(extract("month", Photo.photo_taken_at) == current.month)
            .where(extract("day", Photo.photo_taken_at) == current.day)
            .order_by(Photo.photo_taken_at.desc())
        )
        return list(db.scalars(stmt))

    def list_duplicate_photos(self, db: Session) -> list[Photo]:
        """返回当前待处理的重复照片。"""
        stmt = (
            select(Photo)
            .options(selectinload(Photo.tags))
            .where(Photo.is_duplicate.is_(True), Photo.is_hidden.is_(False))
            .order_by(Photo.photo_taken_at.desc().nullslast(), Photo.id.desc())
        )
        return list(db.scalars(stmt))

    def archive_photo(self, db: Session, photo_id: int, reason: str = "duplicate") -> Photo | None:
        """把照片从系统中隐藏，并将文件移动到归档目录。"""
        photo = db.scalar(select(Photo).where(Photo.id == photo_id))
        if photo is None:
            return None
        if photo.is_hidden:
            return photo

        path = Path(photo.file_path)
        archived_path = archive_photo_file(path) if path.exists() else None

        photo.is_hidden = True
        photo.hidden_at = datetime.utcnow()
        photo.hidden_reason = reason
        if archived_path is not None:
            photo.archived_file_path = str(archived_path)
            photo.file_path = str(archived_path)
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return self.get_photo(db, photo_id)

    def get_location_options(self, db: Session) -> list[str]:
        """返回前端筛选使用的去重地点名称。"""
        stmt = (
            select(Photo.location_name)
            .where(
                Photo.location_name.is_not(None),
                Photo.is_hidden.is_(False),
                Photo.is_duplicate.is_(False),
            )
            .distinct()
        )
        return [value for value in db.scalars(stmt) if value]

    def get_device_options(self, db: Session) -> list[str]:
        """返回前端筛选使用的去重设备型号。"""
        stmt = (
            select(Photo.device_model)
            .where(
                Photo.device_model.is_not(None),
                Photo.is_hidden.is_(False),
                Photo.is_duplicate.is_(False),
            )
            .distinct()
        )
        return [value for value in db.scalars(stmt) if value]


photo_service = PhotoService()
