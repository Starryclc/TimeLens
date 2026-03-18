from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.views.api.photo_view import PhotoRead


class AlbumCreateRequest(BaseModel):
    title: str
    description: str | None = None


class AlbumAddPhotosRequest(BaseModel):
    photo_ids: list[int]


class PhotoArchiveRequest(BaseModel):
    reason: str = "duplicate"


class FavoriteToggleResponse(BaseModel):
    album_id: int
    is_favorited: bool


class FavoriteStatusResponse(BaseModel):
    album_id: int
    is_favorited: bool


class AlbumSummaryRead(BaseModel):
    id: int
    title: str
    description: str | None
    album_type: str
    photo_count: int
    cover_photo: PhotoRead | None = None
    created_at: datetime
    updated_at: datetime


class AlbumDetailRead(AlbumSummaryRead):
    photos: list[PhotoRead]


class TimelineAlbumRead(BaseModel):
    key: str
    title: str
    year: int
    start_month: int
    end_month: int
    month_label: str
    location_label: str
    photo_count: int
    preview_photos: list[PhotoRead]


class TimelineAlbumDetailRead(TimelineAlbumRead):
    photos: list[PhotoRead]


class TimelineYearRead(BaseModel):
    year: int
    albums: list[TimelineAlbumRead]


class TimelineResponse(BaseModel):
    years: list[TimelineYearRead]
