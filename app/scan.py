from __future__ import annotations

import argparse

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.scan_service import scan_service


def main() -> None:
    """通过命令行扫描目标照片目录。"""
    parser = argparse.ArgumentParser(description="Scan photos into the TimeLens database.")
    parser.add_argument("path", help="Directory containing photos to scan")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        result = scan_service.scan_directory(db, args.path)
    finally:
        db.close()

    print(
        "Scan completed:",
        f"task={result.scan_task_id}",
        f"processed={result.processed_count}",
        f"new={result.new_count}",
        f"updated={result.updated_count}",
        f"duplicates={result.duplicate_count}",
        f"status={result.status}",
    )


if __name__ == "__main__":
    main()
