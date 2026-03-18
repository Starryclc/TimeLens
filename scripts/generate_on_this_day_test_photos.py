from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw
from PIL.TiffImagePlugin import IFDRational


OUTPUT_DIR = Path("data/demo_photos/on_this_day")
DEFAULT_DB_PATH = Path("data/db/timelens.db")

TEST_PHOTOS = [
    {
        "timestamp": "2021-03-18 08:16:00",
        "label": "Spring Morning Walk",
        "color": (197, 215, 183),
        "size": (1600, 1200),
        "location": {"location_name": "杭州", "city": "杭州", "region": "浙江", "country": "中国"},
        "capture": {"make": "FUJIFILM", "model": "X100V", "lens": "FUJINON 23mm F2", "focal_length": (23, 1), "aperture": (2, 1), "exposure_time": (1, 250), "iso": 160},
    },
    {
        "timestamp": "2021-03-18 17:28:00",
        "label": "Spring Evening Window",
        "color": (182, 198, 168),
        "size": (1080, 1920),
        "location": {"location_name": "杭州", "city": "杭州", "region": "浙江", "country": "中国"},
        "capture": {"make": "Apple", "model": "iPhone 13 Pro", "lens": "Wide Camera", "focal_length": (26, 1), "aperture": (15, 10), "exposure_time": (1, 120), "iso": 200},
    },
    {
        "timestamp": "2023-03-18 10:10:00",
        "label": "Campus Breeze",
        "color": (169, 188, 208),
        "size": (1080, 1920),
        "location": {"location_name": "北京", "city": "北京", "region": "北京", "country": "中国"},
        "capture": {"make": "Apple", "model": "iPhone 14 Pro", "lens": "Main Camera", "focal_length": (24, 1), "aperture": (178, 100), "exposure_time": (1, 120), "iso": 320},
    },
    {
        "timestamp": "2023-03-18 14:36:00",
        "label": "Library Table",
        "color": (152, 177, 196),
        "size": (1440, 1080),
        "location": {"location_name": "北京", "city": "北京", "region": "北京", "country": "中国"},
        "capture": {"make": "Ricoh", "model": "GR IIIx", "lens": "GR LENS 26.1mm F2.8", "focal_length": (26, 1), "aperture": (28, 10), "exposure_time": (1, 100), "iso": 250},
    },
    {
        "timestamp": "2024-03-18 17:42:00",
        "label": "Afterglow Street",
        "color": (197, 171, 146),
        "size": (1920, 1080),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Sony", "model": "A7C II", "lens": "FE 35mm F1.8", "focal_length": (35, 1), "aperture": (18, 10), "exposure_time": (1, 200), "iso": 250},
    },
    {
        "timestamp": "2024-03-18 20:18:00",
        "label": "Night Neon",
        "color": (110, 121, 153),
        "size": (1200, 1200),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Canon", "model": "EOS R8", "lens": "RF 50mm F1.8", "focal_length": (50, 1), "aperture": (18, 10), "exposure_time": (1, 80), "iso": 800},
    },
    {
        "timestamp": "2024-03-18 08:12:00",
        "label": "Metro Door",
        "color": (166, 162, 176),
        "size": (1600, 1200),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "FUJIFILM", "model": "X-S20", "lens": "XF 27mm F2.8 R WR", "focal_length": (27, 1), "aperture": (28, 10), "exposure_time": (1, 180), "iso": 250},
    },
    {
        "timestamp": "2024-03-18 09:24:00",
        "label": "Cafe Tray",
        "color": (201, 182, 160),
        "size": (1080, 1440),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Ricoh", "model": "GR III", "lens": "18.3mm F2.8", "focal_length": (18, 1), "aperture": (28, 10), "exposure_time": (1, 125), "iso": 320},
    },
    {
        "timestamp": "2024-03-18 11:48:00",
        "label": "Window Seat",
        "color": (168, 186, 177),
        "size": (1920, 1080),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Sony", "model": "A7 IV", "lens": "FE 40mm F2.5 G", "focal_length": (40, 1), "aperture": (25, 10), "exposure_time": (1, 160), "iso": 200},
    },
    {
        "timestamp": "2024-03-18 13:10:00",
        "label": "Bridge Wind",
        "color": (146, 164, 182),
        "size": (1080, 1920),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Apple", "model": "iPhone 15 Pro", "lens": "Wide Camera", "focal_length": (24, 1), "aperture": (178, 100), "exposure_time": (1, 240), "iso": 160},
    },
    {
        "timestamp": "2024-03-18 15:06:00",
        "label": "Book Spine",
        "color": (181, 170, 153),
        "size": (1200, 1200),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Leica", "model": "Q3", "lens": "Summilux 28 f/1.7 ASPH.", "focal_length": (28, 1), "aperture": (17, 10), "exposure_time": (1, 125), "iso": 500},
    },
    {
        "timestamp": "2024-03-18 18:32:00",
        "label": "Blue Hour Wall",
        "color": (118, 132, 160),
        "size": (1440, 1080),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Canon", "model": "EOS R6 II", "lens": "RF 35mm F1.8", "focal_length": (35, 1), "aperture": (18, 10), "exposure_time": (1, 90), "iso": 640},
    },
    {
        "timestamp": "2024-03-18 22:04:00",
        "label": "Rain Reflection",
        "color": (89, 101, 127),
        "size": (1200, 1600),
        "location": {"location_name": "上海", "city": "上海", "region": "上海", "country": "中国"},
        "capture": {"make": "Nikon", "model": "Zf", "lens": "40mm f/2", "focal_length": (40, 1), "aperture": (2, 1), "exposure_time": (1, 50), "iso": 1250},
    },
    {
        "timestamp": "2025-03-18 19:05:00",
        "label": "Night by the River",
        "color": (95, 113, 142),
        "size": (1200, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Leica", "model": "M11", "lens": "Summicron-M 35 f/2", "focal_length": (35, 1), "aperture": (2, 1), "exposure_time": (1, 90), "iso": 640},
    },
    {
        "timestamp": "2025-03-18 21:12:00",
        "label": "Moon Over Harbor",
        "color": (78, 98, 132),
        "size": (1920, 1080),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Sony", "model": "A7R V", "lens": "FE 90mm F2.8 Macro G OSS", "focal_length": (90, 1), "aperture": (28, 10), "exposure_time": (1, 60), "iso": 1000},
    },
    {
        "timestamp": "2025-03-18 07:35:00",
        "label": "Harbor Mist",
        "color": (142, 157, 176),
        "size": (1600, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Sony", "model": "ZV-E10", "lens": "E 11mm F1.8", "focal_length": (11, 1), "aperture": (18, 10), "exposure_time": (1, 320), "iso": 125},
    },
    {
        "timestamp": "2025-03-18 08:48:00",
        "label": "Market Corner",
        "color": (178, 154, 126),
        "size": (1080, 1920),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Apple", "model": "iPhone 15 Pro", "lens": "Main Camera", "focal_length": (24, 1), "aperture": (178, 100), "exposure_time": (1, 120), "iso": 200},
    },
    {
        "timestamp": "2025-03-18 10:02:00",
        "label": "Blue Tram",
        "color": (112, 133, 172),
        "size": (1440, 1080),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Ricoh", "model": "GR IIIx", "lens": "GR LENS 26.1mm F2.8", "focal_length": (26, 1), "aperture": (28, 10), "exposure_time": (1, 160), "iso": 250},
    },
    {
        "timestamp": "2025-03-18 11:26:00",
        "label": "Coffee Glass",
        "color": (195, 174, 146),
        "size": (1200, 1600),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Canon", "model": "EOS R8", "lens": "RF 35mm F1.8", "focal_length": (35, 1), "aperture": (18, 10), "exposure_time": (1, 100), "iso": 400},
    },
    {
        "timestamp": "2025-03-18 13:08:00",
        "label": "Shadow Balcony",
        "color": (156, 166, 152),
        "size": (1920, 1080),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Leica", "model": "M11", "lens": "Summicron-M 35 f/2", "focal_length": (35, 1), "aperture": (2, 1), "exposure_time": (1, 180), "iso": 200},
    },
    {
        "timestamp": "2025-03-18 15:16:00",
        "label": "Green Window",
        "color": (146, 171, 154),
        "size": (1200, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "FUJIFILM", "model": "X-T5", "lens": "XF 33mm F1.4 R LM WR", "focal_length": (33, 1), "aperture": (14, 10), "exposure_time": (1, 250), "iso": 320},
    },
    {
        "timestamp": "2025-03-18 16:42:00",
        "label": "Quiet Ferry",
        "color": (120, 135, 151),
        "size": (1080, 1440),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Sony", "model": "A7C II", "lens": "FE 24mm F2.8 G", "focal_length": (24, 1), "aperture": (28, 10), "exposure_time": (1, 200), "iso": 160},
    },
    {
        "timestamp": "2025-03-18 17:58:00",
        "label": "Stone Steps",
        "color": (164, 155, 149),
        "size": (1600, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Nikon", "model": "Z6 II", "lens": "NIKKOR Z 24-120mm f/4 S", "focal_length": (32, 1), "aperture": (4, 1), "exposure_time": (1, 125), "iso": 500},
    },
]


def _rational(value: tuple[int, int]) -> IFDRational:
    return IFDRational(value[0], value[1])


def _format_fraction(value: tuple[int, int], prefix: str = "", suffix: str = "") -> str:
    numerator, denominator = value
    if denominator == 0:
        return ""
    decimal = numerator / denominator
    text = f"{decimal:.2f}".rstrip("0").rstrip(".")
    return f"{prefix}{text}{suffix}"


def build_exif(timestamp: str, capture: dict[str, object]) -> Image.Exif:
    exif = Image.Exif()
    exif[271] = capture["make"]
    exif[272] = capture["model"]
    exif[306] = timestamp
    exif[36867] = timestamp
    exif[36868] = timestamp
    exif[33434] = _rational(capture["exposure_time"])
    exif[33437] = _rational(capture["aperture"])
    exif[34855] = int(capture["iso"])
    exif[37386] = _rational(capture["focal_length"])
    exif[42036] = capture["lens"]
    return exif


def build_file_name(timestamp: str, label: str) -> str:
    slug = timestamp.replace(":", "").replace(" ", "_").replace("-", "")
    label_slug = label.lower().replace(" ", "_")
    return f"on_this_day_{slug}_{label_slug}.jpg"


def create_test_photo(
    output_path: Path,
    timestamp: str,
    label: str,
    color: tuple[int, int, int],
    size: tuple[int, int],
    location_name: str,
    capture: dict[str, object],
) -> None:
    image = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(image)
    width, height = size
    margin = max(32, min(width, height) // 18)
    draw.rectangle(
        (margin, margin, width - margin, height - margin),
        outline=(255, 255, 255),
        width=max(4, min(width, height) // 220),
    )
    draw.text((margin * 1.2, margin * 1.7), "TimeLens On This Day", fill=(255, 255, 255))
    draw.text((margin * 1.2, margin * 3.0), label, fill=(255, 255, 255))
    draw.text((margin * 1.2, margin * 4.3), timestamp, fill=(255, 255, 255))
    draw.text((margin * 1.2, margin * 5.6), location_name, fill=(255, 255, 255))
    draw.text((margin * 1.2, margin * 6.9), f"{width}:{height}", fill=(255, 255, 255))
    image.save(output_path, format="JPEG", quality=92, exif=build_exif(timestamp, capture))


def generate_test_photos() -> list[tuple[str, dict[str, object]]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[tuple[str, dict[str, object]]] = []
    for item in TEST_PHOTOS:
        file_name = build_file_name(item["timestamp"], item["label"])
        output_path = OUTPUT_DIR / file_name
        location = item["location"]
        create_test_photo(
            output_path=output_path,
            timestamp=item["timestamp"],
            label=item["label"],
            color=item["color"],
            size=item["size"],
            location_name=location["location_name"],
            capture=item["capture"],
        )
        generated.append((file_name, {"location": location, "capture": item["capture"]}))
    return generated


def apply_test_metadata(db_path: Path, generated: list[tuple[str, dict[str, object]]]) -> int:
    if not db_path.exists():
        return 0

    connection = sqlite3.connect(db_path)
    try:
        updated = 0
        for file_name, payload in generated:
            location = payload["location"]
            capture = payload["capture"]
            cursor = connection.execute(
                """
                UPDATE photos
                SET location_source = 'manual',
                    location_name = ?,
                    city = ?,
                    region = ?,
                    country = ?,
                    device = ?,
                    lens_model = ?,
                    focal_length = ?,
                    aperture = ?,
                    exposure_time = ?,
                    iso = ?
                WHERE file_name = ?
                """,
                (
                    location["location_name"],
                    location["city"],
                    location["region"],
                    location["country"],
                    " ".join(
                        part for part in [capture["make"], capture["model"]] if part
                    ),
                    capture["lens"],
                    _format_fraction(capture["focal_length"], suffix="mm"),
                    _format_fraction(capture["aperture"], prefix="f/"),
                    _format_fraction(capture["exposure_time"], suffix="s"),
                    int(capture["iso"]),
                    file_name,
                ),
            )
            updated += cursor.rowcount
        connection.commit()
        return updated
    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成那年今日测试图片，并可选回填元数据到数据库。")
    parser.add_argument("--apply-db", action="store_true", help="把预设元数据写入本地 SQLite 数据库。")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="SQLite 数据库路径。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generated = generate_test_photos()
    print(f"Generated {len(generated)} photos in {OUTPUT_DIR}")

    if args.apply_db:
        updated = apply_test_metadata(Path(args.db_path), generated)
        print(f"Applied preset metadata to {updated} photos in {args.db_path}")


if __name__ == "__main__":
    main()
