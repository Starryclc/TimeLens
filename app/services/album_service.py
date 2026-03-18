from __future__ import annotations

from datetime import datetime

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Album, AlbumPhoto, Photo
from app.services.file_service import compute_file_hash, detect_mime_type, save_uploaded_photo
from app.services.photo_service import photo_service
from app.services.thumbnail_service import thumbnail_service


class AlbumService:
    favorites_title = "我的收藏"

    def ensure_favorites_album(self, db: Session) -> Album:
        stmt = (
            select(Album)
            .where(Album.album_type == "favorites")
            .options(selectinload(Album.photos).selectinload(AlbumPhoto.photo))
        )
        existing = db.scalar(stmt)
        if existing is not None:
            return existing

        album = Album(
            title=self.favorites_title,
            description="系统默认收藏相册",
            album_type="favorites",
        )
        db.add(album)
        db.commit()
        db.refresh(album)
        return self.get_album(db, album.id) or album

    def list_albums(self, db: Session) -> list[Album]:
        self.ensure_favorites_album(db)
        stmt = select(Album).options(selectinload(Album.photos).selectinload(AlbumPhoto.photo))
        albums = list(db.scalars(stmt))
        return sorted(
            albums,
            key=lambda album: (album.album_type != "favorites", -(album.id or 0)),
        )

    def get_album(self, db: Session, album_id: int) -> Album | None:
        stmt = (
            select(Album)
            .where(Album.id == album_id)
            .options(selectinload(Album.photos).selectinload(AlbumPhoto.photo))
        )
        return db.scalar(stmt)

    def create_album(self, db: Session, title: str, description: str | None = None) -> Album:
        album = Album(title=title.strip(), description=description, album_type="custom")
        db.add(album)
        db.commit()
        db.refresh(album)
        return self.get_album(db, album.id) or album

    def add_photos_to_album(self, db: Session, album_id: int, photo_ids: list[int]) -> Album | None:
        album = self.get_album(db, album_id)
        if album is None:
            return None

        existing_ids = {link.photo_id for link in album.photos}
        current_rank = max((link.rank for link in album.photos), default=-1)
        for photo_id in photo_ids:
            if photo_id in existing_ids:
                continue
            current_rank += 1
            db.add(AlbumPhoto(album_id=album_id, photo_id=photo_id, rank=current_rank))
        db.commit()
        return self.get_album(db, album_id)

    def toggle_favorite_photo(self, db: Session, photo_id: int) -> tuple[Album, bool] | None:
        favorites_album = self.ensure_favorites_album(db)
        photo = db.scalar(select(Photo).where(Photo.id == photo_id))
        if photo is None:
            return None

        existing_link = db.scalar(
            select(AlbumPhoto).where(
                AlbumPhoto.album_id == favorites_album.id,
                AlbumPhoto.photo_id == photo_id,
            )
        )
        if existing_link is not None:
            db.delete(existing_link)
            db.commit()
            album = self.get_album(db, favorites_album.id) or favorites_album
            return album, False

        current_rank = max((link.rank for link in favorites_album.photos), default=-1)
        db.add(AlbumPhoto(album_id=favorites_album.id, photo_id=photo_id, rank=current_rank + 1))
        db.commit()
        album = self.get_album(db, favorites_album.id) or favorites_album
        return album, True

    def is_photo_favorited(self, db: Session, photo_id: int) -> bool:
        favorites_album = self.ensure_favorites_album(db)
        stmt = select(AlbumPhoto.id).where(
            AlbumPhoto.album_id == favorites_album.id,
            AlbumPhoto.photo_id == photo_id,
        )
        return db.scalar(stmt) is not None

    def upload_photo(
        self,
        db: Session,
        *,
        upload: UploadFile,
        target_type: str,
        album_id: int | None = None,
        taken_at: datetime | None = None,
        location_name: str | None = None,
        city: str | None = None,
        region: str | None = None,
        country: str | None = None,
        device: str | None = None,
    ) -> Photo:
        saved_path = save_uploaded_photo(upload)
        file_hash = compute_file_hash(saved_path)
        duplicate_of = db.scalar(select(Photo).where(Photo.file_hash == file_hash))
        stat = saved_path.stat()
        thumbnail_path = thumbnail_service.build_thumbnail(saved_path, file_hash)

        photo = Photo(
            file_path=str(saved_path),
            file_name=upload.filename or saved_path.name,
            file_hash=file_hash,
            file_size=stat.st_size,
            imported_at=datetime.utcnow(),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            photo_taken_at=taken_at,
            device=device,
            mime_type=detect_mime_type(saved_path),
            location_source="manual" if any([location_name, city, region, country]) else "unknown",
            location_name=location_name,
            city=city,
            region=region,
            country=country,
            thumbnail_path=thumbnail_path,
            status="uploaded",
            is_duplicate=duplicate_of is not None,
            duplicate_of_photo_id=duplicate_of.id if duplicate_of else None,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)

        if target_type == "album" and album_id is not None:
            self.add_photos_to_album(db, album_id, [photo.id])

        return photo_service.get_photo(db, photo.id) or photo

    def serialize_album_summary(self, album: Album) -> dict:
        visible_photos = [
            link.photo
            for link in sorted(album.photos, key=lambda item: (item.rank, item.id))
            if link.photo and not link.photo.is_hidden
        ]
        return {
            "id": album.id,
            "title": album.title,
            "description": album.description,
            "album_type": album.album_type,
            "photo_count": len(visible_photos),
            "cover_photo": visible_photos[0] if visible_photos else None,
            "created_at": album.created_at,
            "updated_at": album.updated_at,
        }

    def serialize_album_detail(self, album: Album) -> dict:
        summary = self.serialize_album_summary(album)
        summary["photos"] = [
            link.photo
            for link in sorted(album.photos, key=lambda item: (item.rank, item.id))
            if link.photo and not link.photo.is_hidden
        ]
        return summary


album_service = AlbumService()
