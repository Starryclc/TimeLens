from fastapi import APIRouter

from app.core.settings import get_settings


router = APIRouter(tags=["system"])
settings = get_settings()


@router.get("/")
def api_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "mode": "api",
        "message": "TimeLens backend API is running.",
    }


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
