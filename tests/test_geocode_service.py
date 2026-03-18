import json

from app.models import LocationCache, Photo
from app.services.geocode_service import NominatimGeocoder, geocode_service


def test_normalize_location_name_prefers_short_structured_values():
    assert (
        NominatimGeocoder.normalize_location_name(
            location_name="",
            city="香港",
            region="香港特别行政区",
            country="中国",
        )
        == "香港"
    )
    assert (
        NominatimGeocoder.normalize_location_name(
            location_name="北京市, 朝阳区, 三里屯街道",
            city="北京",
            region="北京",
            country="中国",
        )
        == "北京"
    )


def test_refresh_locations_from_current_data_updates_cache_and_photos(db_session):
    payload = {
        "name": "北京市, 朝阳区, 三里屯街道",
        "address": {
            "city": "北京",
            "state": "北京",
            "country": "中国",
        },
    }
    db_session.add(
        LocationCache(
            cache_key=geocode_service._cache_key(39.9341, 116.4523),
            latitude=39.9341,
            longitude=116.4523,
            location_name="北京市, 朝阳区, 三里屯街道",
            city="旧城市",
            region="旧区域",
            country="旧国家",
            provider="nominatim",
            raw_payload=json.dumps(payload, ensure_ascii=False),
        )
    )
    db_session.add(
        Photo(
            file_path="/tmp/example.jpg",
            file_name="example.jpg",
            file_size=1,
            gps_lat=39.9341,
            gps_lon=116.4523,
            location_source="manual",
            location_name="北京市, 朝阳区, 三里屯街道",
            city="旧城市",
            region="旧区域",
            country="旧国家",
            status="uploaded",
        )
    )
    db_session.add(
        Photo(
            file_path="/tmp/manual.jpg",
            file_name="manual.jpg",
            file_size=1,
            location_source="manual",
            location_name=None,
            city="香港",
            region="香港特别行政区",
            country="中国",
            status="uploaded",
        )
    )
    db_session.commit()

    cache_count, photo_count = geocode_service.refresh_locations_from_current_data(db_session)

    assert cache_count == 1
    assert photo_count == 2

    cached = db_session.query(LocationCache).one()
    assert cached.location_name == "北京"
    assert cached.city == "北京"
    assert cached.region == "北京"
    assert cached.country == "中国"

    gps_photo = db_session.query(Photo).filter_by(file_name="example.jpg").one()
    assert gps_photo.location_name == "北京"
    assert gps_photo.city == "北京"
    assert gps_photo.region == "北京"
    assert gps_photo.country == "中国"
    assert gps_photo.location_source == "exif"

    manual_photo = db_session.query(Photo).filter_by(file_name="manual.jpg").one()
    assert manual_photo.location_name == "香港"
