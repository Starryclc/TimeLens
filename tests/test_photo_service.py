from datetime import datetime, timedelta

from app.models import Photo
from app.services.photo_service import photo_service
from app.services.timeline_service import timeline_service


def test_get_on_this_day_returns_matching_month_day(db_session):
    """确保那年今日只返回同一日历日的照片。"""
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


def test_get_random_photo_excludes_on_this_day_entries(db_session):
    """确保随机回忆默认不会返回那年今日中的照片。"""
    db_session.add_all(
        [
            Photo(
                file_path="/tmp/random-a.jpg",
                file_name="random-a.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2024, 3, 18, 9, 0, 0),
                status="analyzed",
            ),
            Photo(
                file_path="/tmp/random-b.jpg",
                file_name="random-b.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2024, 3, 17, 9, 0, 0),
                status="analyzed",
            ),
        ]
    )
    db_session.commit()

    result = photo_service.get_random_photo(
        db_session,
        exclude_on_this_day=True,
        today=datetime(2026, 3, 18, 8, 0, 0),
    )

    assert result is not None
    assert result.file_name == "random-b.jpg"


def test_timeline_groups_photos_by_year_month_and_location(db_session):
    """确保时间线会把同年同地的连续月份合并成事件相册。"""
    db_session.add_all(
        [
            Photo(
                file_path="/tmp/timeline-a.jpg",
                file_name="timeline-a.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2025, 5, 1, 10, 0, 0),
                location_name="纽约",
                status="analyzed",
            ),
            Photo(
                file_path="/tmp/timeline-b.jpg",
                file_name="timeline-b.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2025, 5, 2, 10, 0, 0),
                location_name="纽约",
                status="analyzed",
            ),
            Photo(
                file_path="/tmp/timeline-c.jpg",
                file_name="timeline-c.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2024, 7, 2, 10, 0, 0),
                location_name="香港",
                status="analyzed",
            ),
            Photo(
                file_path="/tmp/timeline-d.jpg",
                file_name="timeline-d.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=datetime(2024, 8, 2, 10, 0, 0),
                location_name="香港",
                status="analyzed",
            ),
        ]
    )
    db_session.commit()

    result = timeline_service.build_timeline(db_session)

    assert len(result["years"]) == 2
    assert result["years"][0]["year"] == 2025
    assert result["years"][0]["albums"][0]["location_label"] == "纽约"
    assert result["years"][0]["albums"][0]["photo_count"] == 2
    assert result["years"][1]["albums"][0]["title"] == "7月-8月 香港"
    assert result["years"][1]["albums"][0]["start_month"] == 7
    assert result["years"][1]["albums"][0]["end_month"] == 8


def test_timeline_preview_is_limited_to_ten_photos(db_session):
    """确保时间线相册预览最多只返回 10 张照片。"""
    start = datetime(2024, 7, 1, 10, 0, 0)
    for index in range(13):
        db_session.add(
            Photo(
                file_path=f"/tmp/preview-{index}.jpg",
                file_name=f"preview-{index}.jpg",
                file_size=1,
                imported_at=datetime.utcnow(),
                photo_taken_at=start + timedelta(days=index),
                location_name="香港",
                status="analyzed",
            )
        )
    db_session.commit()

    result = timeline_service.build_timeline(db_session)
    album = result["years"][0]["albums"][0]

    assert album["title"] == "7月 香港"
    assert album["photo_count"] == 13
    assert len(album["preview_photos"]) == 10
