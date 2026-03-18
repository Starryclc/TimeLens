from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageOps

from app.core.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class ThumbnailService:
    def build_thumbnail(self, source_path: Path, file_hash: str | None) -> str | None:
        """为图片创建或复用缩略图。"""
        if not file_hash:
            return None

        relative_path = Path("data/thumbnails") / f"{file_hash}.jpg"
        output_path = settings.thumbnail_dir / f"{file_hash}.jpg"
        if output_path.exists():
            return str(relative_path).replace("\\", "/")

        try:
            with Image.open(source_path) as image:
                thumbnail = ImageOps.exif_transpose(image)
                thumbnail.thumbnail((512, 512))
                thumbnail = thumbnail.convert("RGB")
                thumbnail.save(output_path, format="JPEG", quality=88)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to create thumbnail for %s: %s", source_path, exc)
            return None

        return str(relative_path).replace("\\", "/")


thumbnail_service = ThumbnailService()
