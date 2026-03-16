from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
SKIPPED_EXTENSIONS = {".heic", ".heif"}


def is_supported_photo(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_skipped_photo(path: Path) -> bool:
    return path.suffix.lower() in SKIPPED_EXTENSIONS


def compute_file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def detect_mime_type(path: Path) -> str | None:
    mime_type, _ = mimetypes.guess_type(path.name)
    return mime_type
