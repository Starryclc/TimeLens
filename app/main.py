from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.media import router as media_router
from app.api.meta import router as meta_router
from app.api.phase2 import router as phase2_router
from app.api.photos import router as photos_router
from app.api.scan import router as scan_router
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.init_db import init_db


settings = get_settings()
configure_logging(settings.debug)
init_db()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_dev_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(photos_router)
api_router.include_router(scan_router)
api_router.include_router(media_router)
api_router.include_router(meta_router)
api_router.include_router(phase2_router)
app.include_router(api_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "mode": "api",
        "message": "TimeLens backend is running. Start the separate frontend app to browse photos.",
    }


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development",
    )


if __name__ == "__main__":
    main()
