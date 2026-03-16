from datetime import datetime

from app.models import Photo
from app.services.photo_service import photo_service


def test_get_on_this_day_returns_matching_month_day(db_session):
    db_session.add_all(
        [
            Photo(
                file_path="/tmp/a.jpg",
                file_name="a.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2020, 3, 16, 12, 0, 0),
                status="analyzed",
            ),
            Photo(
                file_path="/tmp/b.jpg",
                file_name="b.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2021, 3, 16, 9, 0, 0),
                status="analyzed",
            ),
            Photo(
                file_path="/tmp/c.jpg",
                file_name="c.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2021, 4, 1, 9, 0, 0),
                status="analyzed",
            ),
        ]
    )
    db_session.commit()

    results = photo_service.get_on_this_day(db_session, today=datetime(2026, 3, 16, 8, 0, 0))

    assert [photo.file_name for photo in results] == ["b.jpg", "a.jpg"]
