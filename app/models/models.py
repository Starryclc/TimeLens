from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ScanTask(Base):
    __tablename__ = "scan_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    processed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class LocationCache(Base):
    __tablename__ = "location_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    provider: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Photo(Base, TimestampMixin):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_path: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    photo_taken_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    device_make: Mapped[str | None] = mapped_column(String(120), nullable=True)
    device_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lens_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    focal_length: Mapped[str | None] = mapped_column(String(32), nullable=True)
    aperture: Mapped[str | None] = mapped_column(String(32), nullable=True)
    exposure_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    iso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    gps_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_source: Mapped[str] = mapped_column(
        String(32),
        default="unknown",
        nullable=False,
    )
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    scene_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ai_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    exif_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hidden_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    archived_file_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    duplicate_of_photo_id: Mapped[int | None] = mapped_column(
        ForeignKey("photos.id"),
        nullable=True,
    )
    scan_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("scan_tasks.id"),
        nullable=True,
    )

    duplicate_of: Mapped[Photo | None] = relationship(remote_side=[id])
    tags: Mapped[list[PhotoTag]] = relationship(back_populates="photo")
    faces: Mapped[list[Face]] = relationship(back_populates="photo")
    album_links: Mapped[list[AlbumPhoto]] = relationship(back_populates="photo")


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False, index=True)
    tag: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), default="rule", nullable=False)

    photo: Mapped[Photo] = relationship(back_populates="tags")


class Person(Base, TimestampMixin):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cover_photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id"), nullable=True)

    faces: Mapped[list[Face]] = relationship(back_populates="person")


class Face(Base):
    __tablename__ = "faces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False, index=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    bbox_x: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_width: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_height: Mapped[float] = mapped_column(Float, nullable=False)
    embedding_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    photo: Mapped[Photo] = relationship(back_populates="faces")
    person: Mapped[Person | None] = relationship(back_populates="faces")


class PhotoCluster(Base, TimestampMixin):
    __tablename__ = "photo_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    cluster_type: Mapped[str] = mapped_column(String(64), nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cover_photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id"), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="rule", nullable=False)

    items: Mapped[list[PhotoClusterItem]] = relationship(back_populates="cluster")


class PhotoClusterItem(Base):
    __tablename__ = "photo_cluster_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cluster_id: Mapped[int] = mapped_column(
        ForeignKey("photo_clusters.id"),
        nullable=False,
        index=True,
    )
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False, index=True)
    rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    cluster: Mapped[PhotoCluster] = relationship(back_populates="items")


class PlaceSummary(Base):
    __tablename__ = "place_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    first_photo_taken_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_photo_taken_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cover_photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id"), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)


class MemoryRecommendation(Base):
    __tablename__ = "memory_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id"), nullable=True)
    related_cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("photo_clusters.id"),
        nullable=True,
    )
    related_person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class TimelineStory(Base, TimestampMixin):
    __tablename__ = "timeline_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="rule", nullable=False)


class Album(Base, TimestampMixin):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    album_type: Mapped[str] = mapped_column(String(32), default="custom", nullable=False)

    photos: Mapped[list[AlbumPhoto]] = relationship(
        back_populates="album",
        cascade="all, delete-orphan",
    )


class AlbumPhoto(Base):
    __tablename__ = "album_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"), nullable=False, index=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False, index=True)
    rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    album: Mapped[Album] = relationship(back_populates="photos")
    photo: Mapped[Photo] = relationship(back_populates="album_links")
