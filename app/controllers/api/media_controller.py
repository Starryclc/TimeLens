from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.photo_service import photo_service


router = APIRouter(prefix="/media", tags=["media"])


@router.get("/photos/{photo_id}")
def get_original_photo(photo_id: int, db: Session = Depends(get_db)) -> FileResponse:
    """返回指定照片记录对应的原图文件。"""
    photo = photo_service.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    path = Path(photo.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Original file missing")

    return FileResponse(path)
