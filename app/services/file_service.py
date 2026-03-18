from __future__ import annotations

import hashlib
import mimetypes
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.settings import get_settings


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
SKIPPED_EXTENSIONS = {".heic", ".heif"}


def is_supported_photo(path: Path) -> bool:
    """判断文件扩展名是否在支持扫描的范围内。"""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_skipped_photo(path: Path) -> bool:
    """判断文件是否属于当前需要跳过的类型。"""
    return path.suffix.lower() in SKIPPED_EXTENSIONS


def compute_file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """为文件计算稳定的 SHA-256 哈希值。"""
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def detect_mime_type(path: Path) -> str | None:
    """根据文件名猜测 MIME 类型。"""
    mime_type, _ = mimetypes.guess_type(path.name)
    return mime_type


def save_uploaded_photo(upload: UploadFile) -> Path:
    """把前端上传的照片保存到本地托管目录。"""
    settings = get_settings()
    extension = Path(upload.filename or "upload.jpg").suffix.lower() or ".jpg"
    uploads_dir = settings.data_dir / "uploads" / datetime.utcnow().strftime("%Y%m")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    target_path = uploads_dir / f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}{extension}"

    with target_path.open("wb") as output:
        shutil.copyfileobj(upload.file, output)

    return target_path


def archive_photo_file(path: Path) -> Path:
    """把照片文件移动到归档目录，保留原始文件内容但不再在系统中展示。"""
    settings = get_settings()
    archive_dir = settings.archived_photo_dir / datetime.utcnow().strftime("%Y%m")
    archive_dir.mkdir(parents=True, exist_ok=True)
    target_path = archive_dir / path.name

    if target_path.exists():
        stem = path.stem
        suffix = path.suffix
        target_path = archive_dir / f"{stem}_{datetime.utcnow().strftime('%H%M%S%f')}{suffix}"

    shutil.move(str(path), str(target_path))
    return target_path
