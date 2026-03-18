from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT_DIR = Path("data/demo_photos/timeline_stress")
DEFAULT_DB_PATH = Path("data/db/timelens.db")

TEST_PHOTOS = [
    *[
        {
            "timestamp": f"2024-07-{day:02d} 10:{(day * 3) % 60:02d}:00",
            "label": f"Hong Kong July {day}",
            "color": (86 + day * 5, 132 + day * 3, 180 + day * 2),
            "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        }
        for day in range(1, 13)
    ],
    {
        "timestamp": "2024-08-03 18:20:00",
        "label": "Hong Kong August 1",
        "color": (118, 155, 206),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
    },
    {
        "timestamp": "2024-08-11 09:50:00",
        "label": "Hong Kong August 2",
        "color": (102, 146, 196),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
    },
    {
        "timestamp": "2024-11-08 16:10:00",
        "label": "New York November",
        "color": (150, 171, 190),
        "location": {"location_name": "纽约", "city": "纽约", "region": "纽约州", "country": "美国"},
    },
    {
        "timestamp": "2025-05-02 14:10:00",
        "label": "Xinjiang Spring 1",
        "color": (196, 179, 119),
        "location": {"location_name": "新疆", "city": "乌鲁木齐", "region": "新疆维吾尔自治区", "country": "中国"},
    },
    {
        "timestamp": "2025-05-18 08:40:00",
        "label": "Xinjiang Spring 2",
        "color": (184, 164, 102),
        "location": {"location_name": "新疆", "city": "伊犁", "region": "新疆维吾尔自治区", "country": "中国"},
    },
]


def build_exif(timestamp: str) -> Image.Exif:
    exif = Image.Exif()
    exif[271] = "TimeLens Lab"
    exif[272] = "Timeline Test Camera"
    exif[306] = timestamp
    exif[36867] = timestamp
    exif[36868] = timestamp
    return exif


def build_file_name(timestamp: str, label: str) -> str:
    slug = timestamp.replace(":", "").replace(" ", "_").replace("-", "")
    label_slug = label.lower().replace(" ", "_")
    return f"timeline_{slug}_{label_slug}.jpg"


def create_test_photo(output_path: Path, timestamp: str, label: str, color: tuple[int, int, int], location_name: str) -> None:
    image = Image.new("RGB", (1600, 1200), color=color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((56, 56, 1544, 1144), outline=(255, 255, 255), width=6)
    draw.text((120, 176), "TimeLens Timeline Test", fill=(255, 255, 255))
    draw.text((120, 308), label, fill=(255, 255, 255))
    draw.text((120, 440), timestamp, fill=(255, 255, 255))
    draw.text((120, 572), location_name, fill=(255, 255, 255))
    image.save(output_path, format="JPEG", quality=92, exif=build_exif(timestamp))


def generate_test_photos() -> list[tuple[str, dict[str, str]]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[tuple[str, dict[str, str]]] = []
    for item in TEST_PHOTOS:
        file_name = build_file_name(item["timestamp"], item["label"])
        output_path = OUTPUT_DIR / file_name
        location = item["location"]
        create_test_photo(
            output_path=output_path,
            timestamp=item["timestamp"],
            label=item["label"],
            color=item["color"],
            location_name=location["location_name"],
        )
        generated.append((file_name, location))
    return generated


def apply_test_locations(db_path: Path, generated: list[tuple[str, dict[str, str]]]) -> int:
    if not db_path.exists():
        return 0

    connection = sqlite3.connect(db_path)
    try:
        updated = 0
        for file_name, location in generated:
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
                    location["location_name"],
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
    parser = argparse.ArgumentParser(description="生成时间线测试图片，并可选把地点信息回填到数据库。")
    parser.add_argument("--apply-db", action="store_true", help="把预设地点信息写入本地 SQLite 数据库。")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="SQLite 数据库路径。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generated = generate_test_photos()
    print(f"Generated {len(generated)} photos in {OUTPUT_DIR}")

    if args.apply_db:
        updated = apply_test_locations(Path(args.db_path), generated)
        print(f"Applied preset locations to {updated} photos in {args.db_path}")


if __name__ == "__main__":
    main()
