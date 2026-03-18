from datetime import datetime
from pathlib import Path

from PIL import Image

from app.models import Photo
from app.services.exif_service import ExifData
from app.services.scan_service import scan_service


def _create_image(path: Path) -> None:
    """在磁盘上创建一张小型测试图片。"""
    image = Image.new("RGB", (128, 96), color=(180, 120, 90))
    image.save(path, format="JPEG")


def test_scan_directory_creates_and_updates_records(db_session, tmp_path):
    """确保扫描首次入库，后续可跳过未变化文件。"""
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    image_path = photo_dir / "sample.jpg"
    _create_image(image_path)

    first = scan_service.scan_directory(db_session, str(photo_dir))
    second = scan_service.scan_directory(db_session, str(photo_dir))

    assert first.processed_count == 1
    assert first.new_count == 1
    assert second.processed_count == 1
    assert second.new_count == 0


def test_scan_directory_persists_capture_fields(db_session, tmp_path, monkeypatch):
    """确保扫描会把镜头、焦距、光圈、快门和 ISO 写入数据库。"""
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    image_path = photo_dir / "capture.jpg"
    _create_image(image_path)

    monkeypatch.setattr(
        "app.services.scan_service.exif_service.extract",
        lambda _path: ExifData(
            photo_taken_at=datetime(2024, 5, 1, 9, 30, 0),
            device_make="Sony",
            device_model="ZV-E10",
            lens_model="Sigma 56mm F1.4 DC DN",
            focal_length="56mm",
            aperture="f/1.4",
            exposure_time="1/125s",
            iso=320,
            width=128,
            height=96,
            exif_summary="参数 56mm f/1.4 1/125s ISO 320",
        ),
    )
    monkeypatch.setattr(
        "app.services.scan_service.geocode_service.reverse_geocode",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.scan_service.vision_analyzer.analyze",
        lambda _path: type("AiResult", (), {"scene_label": None, "description": None})(),
    )
    monkeypatch.setattr(
        "app.services.scan_service.thumbnail_service.build_thumbnail",
        lambda _path, _hash: "data/thumbnails/mock.jpg",
    )

    scan_service.scan_directory(db_session, str(photo_dir))
    photo = db_session.query(Photo).filter_by(file_name="capture.jpg").one()

    assert photo.lens_model == "Sigma 56mm F1.4 DC DN"
    assert photo.focal_length == "56mm"
    assert photo.aperture == "f/1.4"
    assert photo.exposure_time == "1/125s"
    assert photo.iso == 320
