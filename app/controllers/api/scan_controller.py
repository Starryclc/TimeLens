from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.scan_service import scan_service
from app.views.api.photo_view import ScanRequest, ScanResponse


router = APIRouter(tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
def run_scan(payload: ScanRequest, db: Session = Depends(get_db)) -> ScanResponse:
    try:
        result = scan_service.scan_directory(db, payload.path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ScanResponse(**result.__dict__)
