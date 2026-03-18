from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Photo, ScanTask
from app.services.ai_service import vision_analyzer
from app.services.exif_service import exif_service
from app.services.file_service import (
    compute_file_hash,
    detect_mime_type,
    is_skipped_photo,
    is_supported_photo,
)
from app.services.geocode_service import geocode_service
from app.services.thumbnail_service import thumbnail_service


logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    scan_task_id: int
    processed_count: int
    new_count: int
    updated_count: int
    duplicate_count: int
    status: str


class ScanService:
    def scan_directory(self, db: Session, scan_path: str) -> ScanResult:
        """扫描目录并以增量方式更新照片记录。"""
        root = Path(scan_path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Scan path does not exist or is not a directory: {scan_path}")

        task = ScanTask(scan_path=str(root), status="running")
        db.add(task)
        db.commit()
        db.refresh(task)

        processed_count = 0
        new_count = 0
        updated_count = 0
        duplicate_count = 0

        try:
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                if is_skipped_photo(path):
                    continue
                if not is_supported_photo(path):
                    continue

                processed_count += 1
                created, updated, is_duplicate = self._upsert_photo(db, path, task.id)
                if created:
                    new_count += 1
                if updated:
                    updated_count += 1
                if is_duplicate:
                    duplicate_count += 1

            task.status = "completed"
            task.finished_at = datetime.utcnow()
            task.processed_count = processed_count
            task.new_count = new_count
            task.updated_count = updated_count
            task.duplicate_count = duplicate_count
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("Scan task failed for %s", root)
            task.status = "error"
            task.finished_at = datetime.utcnow()
            task.error_message = str(exc)
            task.processed_count = processed_count
            task.new_count = new_count
            task.updated_count = updated_count
            task.duplicate_count = duplicate_count
            db.add(task)
            db.commit()
            raise

        return ScanResult(
            scan_task_id=task.id,
            processed_count=processed_count,
            new_count=new_count,
            updated_count=updated_count,
            duplicate_count=duplicate_count,
            status=task.status,
        )

    def _upsert_photo(self, db: Session, path: Path, scan_task_id: int) -> tuple[bool, bool, bool]:
        """根据磁盘文件插入或刷新单张照片记录。"""
        stat = path.stat()
        existing = db.scalar(select(Photo).where(Photo.file_path == str(path)))
        needs_refresh = existing is None or existing.modified_at != datetime.fromtimestamp(stat.st_mtime)

        if existing and not needs_refresh:
            existing.scan_task_id = scan_task_id
            db.add(existing)
            db.commit()
            return False, False, existing.is_duplicate

        file_hash = compute_file_hash(path)
        duplicate_of = db.scalar(
            select(Photo).where(Photo.file_hash == file_hash, Photo.file_path != str(path))
        )
        exif = exif_service.extract(path)
        resolved_location = geocode_service.reverse_geocode(db, exif.gps_lat, exif.gps_lon)
        ai_result = vision_analyzer.analyze(path)
        thumbnail_path = thumbnail_service.build_thumbnail(path, file_hash)

        photo = existing or Photo(
            file_path=str(path),
            file_name=path.name,
            file_size=stat.st_size,
        )
        photo.file_name = path.name
        photo.file_hash = file_hash
        photo.file_size = stat.st_size
        photo.modified_at = datetime.fromtimestamp(stat.st_mtime)
        photo.imported_at = existing.imported_at if existing else datetime.utcnow()
        photo.photo_taken_at = exif.photo_taken_at
        photo.device = exif.device
        photo.lens_model = exif.lens_model
        photo.focal_length = exif.focal_length
        photo.aperture = exif.aperture
        photo.exposure_time = exif.exposure_time
        photo.iso = exif.iso
        photo.width = exif.width
        photo.height = exif.height
        photo.mime_type = detect_mime_type(path)
        photo.gps_lat = exif.gps_lat
        photo.gps_lon = exif.gps_lon
        photo.location_source = "exif" if resolved_location else "unknown"
        photo.location_name = resolved_location.location_name if resolved_location else None
        photo.city = resolved_location.city if resolved_location else None
        photo.region = resolved_location.region if resolved_location else None
        photo.country = resolved_location.country if resolved_location else None
        photo.scene_label = ai_result.scene_label
        photo.ai_description = ai_result.description
        photo.thumbnail_path = thumbnail_path
        photo.status = "analyzed"
        photo.exif_summary = exif.exif_summary
        photo.is_duplicate = duplicate_of is not None
        photo.duplicate_of_photo_id = duplicate_of.id if duplicate_of else None
        photo.scan_task_id = scan_task_id
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return existing is None, existing is not None, photo.is_duplicate


scan_service = ScanService()
