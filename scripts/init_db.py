from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.init_db import init_db


if __name__ == "__main__":
    """通过命令行初始化本地数据库。"""
    init_db()
    print("Database initialized.")
