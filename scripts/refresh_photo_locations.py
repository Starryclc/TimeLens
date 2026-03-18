from __future__ import annotations

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.geocode_service import geocode_service


def main() -> None:
    init_db()
    with SessionLocal() as db:
        refreshed_cache_count, refreshed_photo_count = geocode_service.refresh_locations_from_current_data(db)
        print(
            f"Refreshed location cache rows: {refreshed_cache_count}, "
            f"photo rows: {refreshed_photo_count}"
        )


if __name__ == "__main__":
    main()
