from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Photo


def _month_label(start_month: int, end_month: int) -> str:
    if start_month == end_month:
        return f"{start_month}月"
    return f"{start_month}月-{end_month}月"


def _build_location_label(photo: Photo) -> str:
    return photo.location_name or photo.city or photo.region or photo.country or "未命名事件"


@dataclass
class TimelineAlbumGroup:
    year: int
    start_month: int
    end_month: int
    location_label: str
    photos: list[Photo]

    @property
    def month_label(self) -> str:
        return _month_label(self.start_month, self.end_month)

    @property
    def title(self) -> str:
        return f"{self.month_label} {self.location_label}"


class TimelineService:
    def build_timeline(self, db: Session) -> dict:
        groups = self._build_album_groups(db)
        years_map: dict[int, list[dict]] = {}
        for group in groups:
            years_map.setdefault(group.year, []).append(self._serialize_group(group))

        years = [
            {
                "year": year,
                "albums": years_map[year],
            }
            for year in sorted(years_map.keys(), reverse=True)
        ]
        return {"years": years}

    def get_timeline_album(self, db: Session, album_key: str) -> dict | None:
        payload = self.decode_album_key(album_key)
        if payload is None:
            return None

        for group in self._build_album_groups(db):
            if (
                group.year == payload["year"]
                and group.start_month == payload["start_month"]
                and group.end_month == payload["end_month"]
                and group.location_label == payload["location_label"]
            ):
                result = self._serialize_group(group)
                result["photos"] = group.photos
                return result
        return None

    def _build_album_groups(self, db: Session) -> list[TimelineAlbumGroup]:
        photos = list(
            db.scalars(
                select(Photo)
                .options(selectinload(Photo.tags))
                .where(
                    Photo.is_hidden.is_(False),
                    Photo.is_duplicate.is_(False),
                    Photo.photo_taken_at.is_not(None),
                )
                .order_by(Photo.photo_taken_at.asc(), Photo.id.asc())
            )
        )

        groups_by_year_location: dict[tuple[int, str], list[TimelineAlbumGroup]] = {}
        for photo in photos:
            taken_at = photo.photo_taken_at
            if taken_at is None:
                continue

            year = taken_at.year
            month = taken_at.month
            location_label = _build_location_label(photo)
            key = (year, location_label)
            current_groups = groups_by_year_location.setdefault(key, [])

            if not current_groups:
                current_groups.append(
                    TimelineAlbumGroup(
                        year=year,
                        start_month=month,
                        end_month=month,
                        location_label=location_label,
                        photos=[photo],
                    )
                )
                continue

            current_group = current_groups[-1]
            if month <= current_group.end_month + 1:
                current_group.end_month = max(current_group.end_month, month)
                current_group.photos.append(photo)
            else:
                current_groups.append(
                    TimelineAlbumGroup(
                        year=year,
                        start_month=month,
                        end_month=month,
                        location_label=location_label,
                        photos=[photo],
                    )
                )

        all_groups = [
            group
            for groups in groups_by_year_location.values()
            for group in groups
        ]
        return sorted(
            all_groups,
            key=lambda group: (group.year, group.start_month, group.end_month, group.location_label),
            reverse=True,
        )

    def _serialize_group(self, group: TimelineAlbumGroup) -> dict:
        key = self.encode_album_key(
            year=group.year,
            start_month=group.start_month,
            end_month=group.end_month,
            location_label=group.location_label,
        )
        return {
            "key": key,
            "title": group.title,
            "year": group.year,
            "start_month": group.start_month,
            "end_month": group.end_month,
            "month_label": group.month_label,
            "location_label": group.location_label,
            "photo_count": len(group.photos),
            "preview_photos": list(reversed(group.photos[-10:])),
        }

    def encode_album_key(
        self,
        *,
        year: int,
        start_month: int,
        end_month: int,
        location_label: str,
    ) -> str:
        payload = {
            "year": year,
            "start_month": start_month,
            "end_month": end_month,
            "location_label": location_label,
        }
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    def decode_album_key(self, album_key: str) -> dict | None:
        try:
            padding = "=" * (-len(album_key) % 4)
            raw = base64.urlsafe_b64decode(f"{album_key}{padding}")
            payload = json.loads(raw.decode("utf-8"))
            if not {"year", "start_month", "end_month", "location_label"} <= set(payload):
                return None
            return payload
        except (ValueError, json.JSONDecodeError):
            return None


timeline_service = TimelineService()
