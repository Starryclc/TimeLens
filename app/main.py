from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.media import router as media_router
from app.api.meta import router as meta_router
from app.api.phase2 import router as phase2_router
from app.api.photos import router as photos_router
from app.api.scan import router as scan_router
from app.api.web import router as web_router, templates
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.init_db import init_db
from app.services.template_helpers import format_datetime


settings = get_settings()
configure_logging(settings.debug)
init_db()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")
templates.env.filters["datetime"] = format_datetime

app.include_router(web_router)
app.include_router(photos_router)
app.include_router(scan_router)
app.include_router(media_router)
app.include_router(meta_router)
app.include_router(phase2_router)


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
