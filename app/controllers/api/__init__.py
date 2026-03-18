from fastapi import APIRouter

from app.controllers.api.albums_controller import router as albums_router
from app.controllers.api.media_controller import router as media_router
from app.controllers.api.meta_controller import router as meta_router
from app.controllers.api.phase2_controller import router as phase2_router
from app.controllers.api.photos_controller import router as photos_router
from app.controllers.api.scan_controller import router as scan_router
from app.controllers.api.system_controller import router as system_router


api_router = APIRouter(prefix="/api")
api_router.include_router(system_router)
api_router.include_router(photos_router)
api_router.include_router(albums_router)
api_router.include_router(scan_router)
api_router.include_router(media_router)
api_router.include_router(meta_router)
api_router.include_router(phase2_router)

__all__ = ["api_router"]
