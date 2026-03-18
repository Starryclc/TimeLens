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
    lens_model: str | None = None
    focal_length: str | None = None
    aperture: str | None = None
    exposure_time: str | None = None
    iso: int | None = None
    gps_lat: float | None = None
    gps_lon: float | None = None
    width: int | None = None
    height: int | None = None
    exif_summary: str | None = None


def _ratio_to_float(value) -> float:
    """把 EXIF 比例值转换为普通浮点数。"""
    if isinstance(value, Fraction):
        return float(value)
    if hasattr(value, "num") and hasattr(value, "den"):
        return float(value.num) / float(value.den)
    return float(value)


def _parse_gps_coordinate(values, ref: str | None) -> float | None:
    """把 EXIF GPS 分量解析为带符号的十进制度数。"""
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
    """解析支持的 EXIF 时间格式。"""
    if not raw:
        return None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _clean_number(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text


def _format_aperture(value) -> str | None:
    if value is None:
        return None
    try:
        return f"f/{_clean_number(_ratio_to_float(value))}"
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _format_exposure_time(value) -> str | None:
    if value is None:
        return None
    try:
        if hasattr(value, "num") and hasattr(value, "den"):
            numerator = int(value.num)
            denominator = int(value.den)
            if denominator == 0:
                return None
            if numerator < denominator:
                return f"{numerator}/{denominator}s"
            return f"{_clean_number(numerator / denominator)}s"
        seconds = _ratio_to_float(value)
        return f"{_clean_number(seconds)}s"
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _format_focal_length(value) -> str | None:
    if value is None:
        return None
    try:
        return f"{_clean_number(_ratio_to_float(value))}mm"
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _parse_iso(value) -> int | None:
    if value is None:
        return None
    if hasattr(value, "values") and getattr(value, "values", None):
        return _parse_iso(value.values[0])
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


class ExifService:
    def extract(self, path: Path) -> ExifData:
        """从图片文件中提取支持的 EXIF 和尺寸信息。"""
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
        data.lens_model = _safe_str(tags.get("EXIF LensModel"))
        data.focal_length = _format_focal_length(
            getattr(tags.get("EXIF FocalLength"), "values", [None])[0]
        )
        data.aperture = _format_aperture(getattr(tags.get("EXIF FNumber"), "values", [None])[0])
        data.exposure_time = _format_exposure_time(
            getattr(tags.get("EXIF ExposureTime"), "values", [tags.get("EXIF ExposureTime")])[0]
        )
        data.iso = _parse_iso(
            tags.get("EXIF ISOSpeedRatings") or tags.get("EXIF PhotographicSensitivity")
        )

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
        if data.lens_model:
            parts.append(f"镜头 {data.lens_model}")
        capture_parts = [
            value
            for value in [data.focal_length, data.aperture, data.exposure_time]
            if value
        ]
        if data.iso is not None:
            capture_parts.append(f"ISO {data.iso}")
        if capture_parts:
            parts.append("参数 " + " ".join(capture_parts))
        if data.gps_lat is not None and data.gps_lon is not None:
            parts.append(f"GPS {data.gps_lat:.5f}, {data.gps_lon:.5f}")
        if data.width and data.height:
            parts.append(f"尺寸 {data.width}x{data.height}")
        data.exif_summary = " | ".join(parts) if parts else None
        return data


def _safe_str(value) -> str | None:
    """把 EXIF 标签值规范化为干净的可选字符串。"""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


exif_service = ExifService()
