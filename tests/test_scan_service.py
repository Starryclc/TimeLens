from pathlib import Path

from PIL import Image

from app.services.scan_service import scan_service


def _create_image(path: Path) -> None:
    image = Image.new("RGB", (128, 96), color=(180, 120, 90))
    image.save(path, format="JPEG")


def test_scan_directory_creates_and_updates_records(db_session, tmp_path):
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
