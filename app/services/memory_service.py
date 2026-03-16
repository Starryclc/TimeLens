from sqlalchemy.orm import Session

from app.models import Photo
from app.services.photo_service import photo_service


class MemoryService:
    def get_homepage_sections(self, db: Session) -> dict[str, list[Photo] | Photo | None]:
        return {
            "recent_photos": photo_service.get_recent_photos(db, limit=12),
            "random_photo": photo_service.get_random_photo(db),
            "on_this_day": photo_service.get_on_this_day(db),
        }


memory_service = MemoryService()
