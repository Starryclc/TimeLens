from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from hashlib import sha1
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models import LocationCache, Photo


logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ResolvedLocation:
    location_name: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    provider: str = "unknown"
    raw_payload: str | None = None


class BaseGeocoder:
    provider_name = "base"

    def reverse_geocode(self, latitude: float, longitude: float) -> ResolvedLocation | None:
        """把经纬度解析为结构化地点信息。"""
        raise NotImplementedError


class NominatimGeocoder(BaseGeocoder):
    provider_name = "nominatim"

    @staticmethod
    def _clean_short_candidate(candidate: Any) -> str | None:
        text = str(candidate).strip() if candidate is not None else ""
        if not text:
            return None
        if "," in text or len(text) > 80:
            return None
        return text

    @classmethod
    def normalize_location_name(
        cls,
        *,
        location_name: str | None = None,
        city: str | None = None,
        region: str | None = None,
        country: str | None = None,
    ) -> str | None:
        """从结构化地点字段里选择一个稳定、适合展示的短地点名。"""
        candidates = [location_name, city, region, country]
        for candidate in candidates:
            text = cls._clean_short_candidate(candidate)
            if text is None:
                continue
            return text
        return None

    @classmethod
    def _pick_location_name(cls, payload: dict[str, Any], address: dict[str, Any]) -> str | None:
        """选择稳定、适合展示的短地点名。"""
        return cls.normalize_location_name(
            location_name=payload.get("name")
            or address.get("attraction")
            or address.get("tourism")
            or address.get("leisure")
            or address.get("suburb")
            or address.get("neighbourhood")
            or address.get("quarter")
            or address.get("borough"),
            city=address.get("city") or address.get("town") or address.get("village"),
            region=address.get("county") or address.get("state") or address.get("region"),
            country=address.get("country"),
        )

    @classmethod
    def resolve_from_payload(cls, payload: dict[str, Any]) -> ResolvedLocation:
        address: dict[str, Any] = payload.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village")
        region = address.get("state") or address.get("region")
        country = address.get("country")
        location_name = cls._pick_location_name(payload, address)
        return ResolvedLocation(
            location_name=location_name,
            city=city,
            region=region,
            country=country,
            provider=cls.provider_name,
            raw_payload=json.dumps(payload, ensure_ascii=False),
        )

    def reverse_geocode(self, latitude: float, longitude: float) -> ResolvedLocation | None:
        """调用 Nominatim 执行逆地理编码。"""
        if not settings.geocoder_enabled:
            return None

        try:
            response = httpx.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "jsonv2",
                    "zoom": 18,
                    "addressdetails": 1,
                },
                headers={"User-Agent": settings.geocoder_user_agent},
                timeout=settings.geocoder_timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Reverse geocode failed for %s,%s: %s", latitude, longitude, exc)
            return None

        payload = response.json()
        return self.resolve_from_payload(payload)


class GeocodeService:
    def __init__(self) -> None:
        """初始化当前启用的地理编码实现。"""
        self.geocoder = NominatimGeocoder()

    @staticmethod
    def _cache_key(latitude: float, longitude: float) -> str:
        """为归一化后的经纬度生成稳定缓存键。"""
        normalized = f"{latitude:.5f},{longitude:.5f}"
        return sha1(normalized.encode("utf-8")).hexdigest()

    def reverse_geocode(
        self,
        db: Session,
        latitude: float | None,
        longitude: float | None,
    ) -> ResolvedLocation | None:
        """结合缓存查询和持久化执行逆地理编码。"""
        if latitude is None or longitude is None:
            return None

        cache_key = self._cache_key(latitude, longitude)
        cached = db.scalar(select(LocationCache).where(LocationCache.cache_key == cache_key))
        if cached:
            return ResolvedLocation(
                location_name=cached.location_name,
                city=cached.city,
                region=cached.region,
                country=cached.country,
                provider=cached.provider,
                raw_payload=cached.raw_payload,
            )

        resolved = self.geocoder.reverse_geocode(latitude, longitude)
        if resolved is None:
            return None

        db.add(
            LocationCache(
                cache_key=cache_key,
                latitude=latitude,
                longitude=longitude,
                location_name=resolved.location_name,
                city=resolved.city,
                region=resolved.region,
                country=resolved.country,
                provider=resolved.provider,
                raw_payload=resolved.raw_payload,
            )
        )
        db.flush()
        return resolved

    def refresh_locations_from_current_data(self, db: Session) -> tuple[int, int]:
        """按当前规则批量重算缓存与照片上的地点展示名。"""
        refreshed_cache_count = 0
        for cache in db.scalars(select(LocationCache)):
            refreshed = None
            if cache.raw_payload:
                try:
                    refreshed = self.geocoder.resolve_from_payload(json.loads(cache.raw_payload))
                except Exception:  # noqa: BLE001
                    refreshed = None

            if refreshed is not None:
                cache.location_name = refreshed.location_name
                cache.city = refreshed.city
                cache.region = refreshed.region
                cache.country = refreshed.country
            else:
                cache.location_name = self.geocoder.normalize_location_name(
                    location_name=cache.location_name,
                    city=cache.city,
                    region=cache.region,
                    country=cache.country,
                )
            refreshed_cache_count += 1

        cache_by_key = {
            cache.cache_key: cache
            for cache in db.scalars(select(LocationCache))
        }

        refreshed_photo_count = 0
        for photo in db.scalars(select(Photo)):
            cache = None
            if photo.gps_lat is not None and photo.gps_lon is not None:
                cache = cache_by_key.get(self._cache_key(photo.gps_lat, photo.gps_lon))

            if cache is not None:
                photo.location_name = cache.location_name
                photo.city = cache.city
                photo.region = cache.region
                photo.country = cache.country
                photo.location_source = "exif"
            else:
                photo.location_name = self.geocoder.normalize_location_name(
                    location_name=photo.location_name,
                    city=photo.city,
                    region=photo.region,
                    country=photo.country,
                )
            refreshed_photo_count += 1

        db.commit()
        return refreshed_cache_count, refreshed_photo_count


geocode_service = GeocodeService()
