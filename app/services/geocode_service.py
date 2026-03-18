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
from app.models import LocationCache


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
        address: dict[str, Any] = payload.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village")
        region = address.get("state") or address.get("region")
        country = address.get("country")
        location_name = (
            payload.get("name")
            or address.get("attraction")
            or address.get("tourism")
            or address.get("road")
            or payload.get("display_name")
        )
        return ResolvedLocation(
            location_name=location_name,
            city=city,
            region=region,
            country=country,
            provider=self.provider_name,
            raw_payload=json.dumps(payload, ensure_ascii=False),
        )


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


geocode_service = GeocodeService()
