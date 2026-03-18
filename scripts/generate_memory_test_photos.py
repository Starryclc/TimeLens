from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT_DIR = Path("data/demo_photos/memory_strip")
DEFAULT_DB_PATH = Path("data/db/timelens.db")

TEST_PHOTOS = [
    {
        "timestamp": "2025-03-17 09:12:00",
        "label": "Tokyo Street",
        "color": (126, 164, 212),
        "location": {"region": "东京都", "city": "东京", "country": "日本"},
    },
    {
        "timestamp": "2025-03-05 14:30:00",
        "label": "March Walk",
        "color": (195, 210, 232),
        "location": None,
    },
    {
        "timestamp": "2025-03-22 18:05:00",
        "label": "City Lights",
        "color": (112, 141, 186),
        "location": {"region": "上海市", "city": "上海", "country": "中国"},
    },
    {
        "timestamp": "2024-03-17 08:45:00",
        "label": "Osaka Morning",
        "color": (184, 208, 226),
        "location": {"region": "大阪府", "city": "大阪", "country": "日本"},
    },
    {
        "timestamp": "2024-03-09 16:40:00",
        "label": "Museum Day",
        "color": (220, 230, 238),
        "location": None,
    },
    {
        "timestamp": "2024-03-28 11:18:00",
        "label": "Spring River",
        "color": (154, 182, 215),
        "location": {"region": "浙江省", "city": "杭州", "country": "中国"},
    },
    {
        "timestamp": "2023-03-17 10:10:00",
        "label": "Old Town",
        "color": (171, 195, 222),
        "location": {"region": "云南省", "city": "丽江", "country": "中国"},
    },
    {
        "timestamp": "2023-03-04 13:20:00",
        "label": "Morning Coffee",
        "color": (231, 237, 244),
        "location": None,
    },
    {
        "timestamp": "2023-03-25 19:08:00",
        "label": "Night Crossing",
        "color": (100, 132, 176),
        "location": {"region": "香港特别行政区", "city": "香港", "country": "中国"},
    },
    {
        "timestamp": "2022-03-17 07:56:00",
        "label": "Harbor Wind",
        "color": (146, 177, 203),
        "location": {"region": "福建省", "city": "厦门", "country": "中国"},
    },
    {
        "timestamp": "2022-03-12 15:48:00",
        "label": "Afternoon Notes",
        "color": (206, 219, 230),
        "location": None,
    },
    {
        "timestamp": "2021-03-17 12:16:00",
        "label": "Blue Hill",
        "color": (137, 160, 193),
        "location": {"region": "北海道", "city": "札幌", "country": "日本"},
    },
    {
        "timestamp": "2021-03-26 17:34:00",
        "label": "Riverlight",
        "color": (167, 188, 212),
        "location": None,
    },
]


def build_exif(timestamp: str) -> Image.Exif:
    """构建用于测试图片的基础 EXIF 信息。"""
    exif = Image.Exif()
    exif[271] = "TimeLens Lab"
    exif[272] = "Memory Test Camera"
    exif[306] = timestamp
    exif[36867] = timestamp
    exif[36868] = timestamp
    return exif


def build_file_name(timestamp: str) -> str:
    """根据拍摄时间生成稳定的测试图片文件名。"""
    slug = timestamp.replace(":", "").replace(" ", "_").replace("-", "")
    return f"memory_{slug}.jpg"


def create_test_photo(
    output_path: Path,
    timestamp: str,
    label: str,
    color: tuple[int, int, int],
    region: str | None,
) -> None:
    """创建一张带拍摄时间 EXIF 的测试图片。"""
    image = Image.new("RGB", (1600, 1200), color=color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((56, 56, 1544, 1144), outline=(255, 255, 255), width=6)
    draw.text((120, 176), "TimeLens", fill=(255, 255, 255))
    draw.text((120, 308), label, fill=(255, 255, 255))
    draw.text((120, 440), timestamp, fill=(255, 255, 255))
    if region:
        draw.text((120, 572), region, fill=(255, 255, 255))
    image.save(output_path, format="JPEG", quality=92, exif=build_exif(timestamp))


def generate_test_photos() -> list[tuple[str, dict[str, str] | None]]:
    """生成用于测试回忆栏位的一组本地图片。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[tuple[str, dict[str, str] | None]] = []
    for item in TEST_PHOTOS:
        file_name = build_file_name(item["timestamp"])
        output_path = OUTPUT_DIR / file_name
        location = item["location"]
        create_test_photo(
            output_path=output_path,
            timestamp=item["timestamp"],
            label=item["label"],
            color=item["color"],
            region=location["region"] if location else None,
        )
        generated.append((file_name, location))
    return generated


def apply_test_locations(db_path: Path, generated: list[tuple[str, dict[str, str] | None]]) -> int:
    """把测试图片的预设地点信息回填到照片数据库。"""
    if not db_path.exists():
        return 0

    connection = sqlite3.connect(db_path)
    try:
        updated = 0
        for file_name, location in generated:
            if not location:
                continue
            cursor = connection.execute(
                """
                UPDATE photos
                SET location_source = 'manual',
                    location_name = ?,
                    city = ?,
                    region = ?,
                    country = ?
                WHERE file_name = ?
                """,
                (
                    location["city"],
                    location["city"],
                    location["region"],
                    location["country"],
                    file_name,
                ),
            )
            updated += cursor.rowcount
        connection.commit()
        return updated
    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    """解析测试图片生成脚本的命令行参数。"""
    parser = argparse.ArgumentParser(description="生成回忆栏位测试图片，并可选回填地点信息。")
    parser.add_argument(
        "--apply-db",
        action="store_true",
        help="尝试把预设地点信息写入本地 SQLite 数据库。",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="需要写入地点信息的 SQLite 数据库路径。",
    )
    return parser.parse_args()


def main() -> None:
    """生成测试图片，并在需要时把测试地点同步到数据库。"""
    args = parse_args()
    generated = generate_test_photos()
    print(f"Generated {len(generated)} photos in {OUTPUT_DIR}")

    if args.apply_db:
        updated = apply_test_locations(Path(args.db_path), generated)
        print(f"Applied preset locations to {updated} photos in {args.db_path}")


if __name__ == "__main__":
    main()
