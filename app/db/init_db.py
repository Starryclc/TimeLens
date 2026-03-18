from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine
from app.models import models  # noqa: F401


def _ensure_photo_columns() -> None:
    inspector = inspect(engine)
    if "photos" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("photos")}
    statements = {
        "device": "ALTER TABLE photos ADD COLUMN device VARCHAR(255)",
        "is_hidden": "ALTER TABLE photos ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT 0",
        "hidden_at": "ALTER TABLE photos ADD COLUMN hidden_at DATETIME",
        "hidden_reason": "ALTER TABLE photos ADD COLUMN hidden_reason VARCHAR(120)",
        "archived_file_path": "ALTER TABLE photos ADD COLUMN archived_file_path VARCHAR(2048)",
        "lens_model": "ALTER TABLE photos ADD COLUMN lens_model VARCHAR(255)",
        "focal_length": "ALTER TABLE photos ADD COLUMN focal_length VARCHAR(32)",
        "aperture": "ALTER TABLE photos ADD COLUMN aperture VARCHAR(32)",
        "exposure_time": "ALTER TABLE photos ADD COLUMN exposure_time VARCHAR(32)",
        "iso": "ALTER TABLE photos ADD COLUMN iso INTEGER",
    }

    with engine.begin() as connection:
        for column_name, statement in statements.items():
            if column_name not in existing_columns:
                connection.execute(text(statement))

        if "device" in existing_columns or "device" in statements:
            connection.execute(
                text(
                    """
                    UPDATE photos
                    SET device = TRIM(
                        COALESCE(device, '')
                    )
                    WHERE device IS NOT NULL
                    """
                )
            )
            if "device_make" in existing_columns or "device_model" in existing_columns:
                connection.execute(
                    text(
                        """
                        UPDATE photos
                        SET device = TRIM(
                            COALESCE(NULLIF(device_make, ''), '')
                            || CASE
                                WHEN COALESCE(NULLIF(device_make, ''), '') != ''
                                  AND COALESCE(NULLIF(device_model, ''), '') != ''
                                THEN ' '
                                ELSE ''
                            END
                            || COALESCE(NULLIF(device_model, ''), '')
                        )
                        WHERE (device IS NULL OR TRIM(device) = '')
                          AND (
                            COALESCE(NULLIF(device_make, ''), '') != ''
                            OR COALESCE(NULLIF(device_model, ''), '') != ''
                          )
                        """
                    )
                )


def init_db() -> None:
    """按当前模型定义创建数据库表。"""
    Base.metadata.create_all(bind=engine)
    _ensure_photo_columns()
