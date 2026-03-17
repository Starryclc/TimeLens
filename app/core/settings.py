from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="TimeLens", alias="TIMELENS_APP_NAME")
    env: str = Field(default="development", alias="TIMELENS_ENV")
    debug: bool = Field(default=True, alias="TIMELENS_DEBUG")
    database_url: str = Field(
        default="sqlite:///./data/db/timelens.db",
        alias="TIMELENS_DATABASE_URL",
    )
    data_dir: Path = Field(default=Path("./data"), alias="TIMELENS_DATA_DIR")
    thumbnail_dir: Path = Field(
        default=Path("./data/thumbnails"),
        alias="TIMELENS_THUMBNAIL_DIR",
    )
    cache_dir: Path = Field(default=Path("./data/cache"), alias="TIMELENS_CACHE_DIR")
    default_scan_dir: Path | None = Field(
        default=None,
        alias="TIMELENS_DEFAULT_SCAN_DIR",
    )
    geocoder_provider: str = Field(
        default="nominatim",
        alias="TIMELENS_GEOCODER_PROVIDER",
    )
    geocoder_enabled: bool = Field(
        default=True,
        alias="TIMELENS_GEOCODER_ENABLED",
    )
    geocoder_user_agent: str = Field(
        default="TimeLens/0.1",
        alias="TIMELENS_GEOCODER_USER_AGENT",
    )
    geocoder_timeout_seconds: int = Field(
        default=8,
        alias="TIMELENS_GEOCODER_TIMEOUT_SECONDS",
    )
    frontend_dev_url: str = Field(
        default="http://127.0.0.1:5173",
        alias="TIMELENS_FRONTEND_DEV_URL",
    )
    host: str = Field(default="127.0.0.1", alias="TIMELENS_HOST")
    port: int = Field(default=8000, alias="TIMELENS_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if lowered in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return bool(value)

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
