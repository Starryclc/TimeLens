from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.controllers import api_router
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
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/data", StaticFiles(directory="data"), name="data")
app.include_router(api_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    """返回当前后端服务的简要说明。"""
    return {
        "name": settings.app_name,
        "mode": "api",
        "message": "TimeLens backend is running. Start the separate frontend app to browse photos.",
    }


def main() -> None:
    """按本地开发默认配置启动 FastAPI 后端。"""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development",
    )


if __name__ == "__main__":
    main()
