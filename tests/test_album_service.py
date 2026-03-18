from datetime import datetime

from app.models import Photo
from app.services.album_service import album_service


def test_add_photos_to_album_keeps_existing_timeline_photos(db_session):
    """确保时间线照片加入自定义相册后，原照片记录仍然保留。"""
    photo = Photo(
        file_path="/tmp/album-photo.jpg",
        file_name="album-photo.jpg",
        file_size=1,
        imported_at=datetime.utcnow(),
        photo_taken_at=datetime(2025, 5, 1, 10, 0, 0),
        location_name="纽约",
        status="analyzed",
    )
    db_session.add(photo)
    db_session.commit()
    db_session.refresh(photo)

    album = album_service.create_album(db_session, "旅行收藏", "测试")
    updated_album = album_service.add_photos_to_album(db_session, album.id, [photo.id])

    assert updated_album is not None
    assert len(updated_album.photos) == 1
    assert updated_album.photos[0].photo_id == photo.id
    assert db_session.get(Photo, photo.id) is not None
