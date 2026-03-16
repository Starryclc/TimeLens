from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path

import exifread
from PIL import Image


logger = logging.getLogger(__name__)


@dataclass
class ExifData:
    photo_taken_at: datetime | None = None
    device_make: str | None = None
    device_model: str | None = None
    gps_lat: float | None = None
    gps_lon: float | None = None
    width: int | None = None
    height: int | None = None
    exif_summary: str | None = None


def _ratio_to_float(value) -> float:
    if isinstance(value, Fraction):
        return float(value)
    if hasattr(value, "num") and hasattr(value, "den"):
        return float(value.num) / float(value.den)
    return float(value)


def _parse_gps_coordinate(values, ref: str | None) -> float | None:
    if not values or len(values) != 3:
        return None
    degrees = _ratio_to_float(values[0])
    minutes = _ratio_to_float(values[1])
    seconds = _ratio_to_float(values[2])
    coordinate = degrees + minutes / 60 + seconds / 3600
    if ref in {"S", "W"}:
        coordinate *= -1
    return coordinate


def _parse_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


class ExifService:
    def extract(self, path: Path) -> ExifData:
        data = ExifData()
        try:
            with path.open("rb") as file_obj:
                tags = exifread.process_file(file_obj, details=False)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to read EXIF for %s: %s", path, exc)
            tags = {}

        try:
            with Image.open(path) as image:
                data.width, data.height = image.size
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to open image for size %s: %s", path, exc)

        data.photo_taken_at = _parse_datetime(
            str(tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime") or "")
        )
        data.device_make = _safe_str(tags.get("Image Make"))
        data.device_model = _safe_str(tags.get("Image Model"))

        lat_values = getattr(tags.get("GPS GPSLatitude"), "values", None)
        lon_values = getattr(tags.get("GPS GPSLongitude"), "values", None)
        lat_ref = _safe_str(tags.get("GPS GPSLatitudeRef"))
        lon_ref = _safe_str(tags.get("GPS GPSLongitudeRef"))
        data.gps_lat = _parse_gps_coordinate(lat_values, lat_ref)
        data.gps_lon = _parse_gps_coordinate(lon_values, lon_ref)

        parts = []
        if data.photo_taken_at:
            parts.append(f"拍摄于 {data.photo_taken_at:%Y-%m-%d %H:%M:%S}")
        if data.device_make or data.device_model:
            parts.append(
                "设备 "
                + " ".join(filter(None, [data.device_make, data.device_model]))
            )
        if data.gps_lat is not None and data.gps_lon is not None:
            parts.append(f"GPS {data.gps_lat:.5f}, {data.gps_lon:.5f}")
        if data.width and data.height:
            parts.append(f"尺寸 {data.width}x{data.height}")
        data.exif_summary = " | ".join(parts) if parts else None
        return data


def _safe_str(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


exif_service = ExifService()
