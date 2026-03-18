from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw
from PIL.TiffImagePlugin import IFDRational


OUTPUT_DIR = Path("data/demo_photos/timeline_stress")
DEFAULT_DB_PATH = Path("data/db/timelens.db")

TEST_PHOTOS = [
    {
        "timestamp": "2024-07-01 10:03:00",
        "label": "Hong Kong July 1",
        "color": (94, 132, 184),
        "size": (1920, 1080),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Sony", "model": "ZV-E10", "lens": "E 16-50mm F3.5-5.6 OSS", "focal_length": (16, 1), "aperture": (35, 10), "exposure_time": (1, 125), "iso": 125},
    },
    {
        "timestamp": "2024-07-03 10:09:00",
        "label": "Hong Kong July 3",
        "color": (108, 144, 194),
        "size": (1600, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Sony", "model": "A7C II", "lens": "FE 35mm F1.8", "focal_length": (35, 1), "aperture": (18, 10), "exposure_time": (1, 160), "iso": 200},
    },
    {
        "timestamp": "2024-07-05 10:15:00",
        "label": "Hong Kong July 5",
        "color": (120, 152, 201),
        "size": (1080, 1920),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Apple", "model": "iPhone 15 Pro", "lens": "Main Camera", "focal_length": (24, 1), "aperture": (178, 100), "exposure_time": (1, 80), "iso": 320},
    },
    {
        "timestamp": "2024-07-07 10:21:00",
        "label": "Hong Kong July 7",
        "color": (128, 158, 204),
        "size": (1200, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "FUJIFILM", "model": "X100V", "lens": "FUJINON 23mm F2", "focal_length": (23, 1), "aperture": (2, 1), "exposure_time": (1, 250), "iso": 160},
    },
    {
        "timestamp": "2024-07-09 10:27:00",
        "label": "Hong Kong July 9",
        "color": (138, 165, 210),
        "size": (1440, 1080),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Canon", "model": "EOS R8", "lens": "RF 50mm F1.8", "focal_length": (50, 1), "aperture": (18, 10), "exposure_time": (1, 200), "iso": 250},
    },
    {
        "timestamp": "2024-07-10 10:30:00",
        "label": "Hong Kong July 10",
        "color": (142, 168, 214),
        "size": (1200, 1600),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Nikon", "model": "Zf", "lens": "NIKKOR Z 40mm f/2", "focal_length": (40, 1), "aperture": (2, 1), "exposure_time": (1, 125), "iso": 400},
    },
    {
        "timestamp": "2024-07-11 10:33:00",
        "label": "Hong Kong July 11",
        "color": (148, 173, 218),
        "size": (1920, 1080),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Leica", "model": "M11", "lens": "Summicron-M 35 f/2", "focal_length": (35, 1), "aperture": (2, 1), "exposure_time": (1, 180), "iso": 200},
    },
    {
        "timestamp": "2024-07-12 10:36:00",
        "label": "Hong Kong July 12",
        "color": (154, 177, 222),
        "size": (1600, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Sony", "model": "A6700", "lens": "E 70-350mm F4.5-6.3 G OSS", "focal_length": (85, 1), "aperture": (45, 10), "exposure_time": (1, 500), "iso": 500},
    },
    {
        "timestamp": "2024-08-03 18:20:00",
        "label": "Hong Kong August 1",
        "color": (118, 155, 206),
        "size": (1080, 1920),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Apple", "model": "iPhone 15 Pro", "lens": "Telephoto Camera", "focal_length": (77, 1), "aperture": (28, 10), "exposure_time": (1, 60), "iso": 640},
    },
    {
        "timestamp": "2024-08-11 09:50:00",
        "label": "Hong Kong August 2",
        "color": (102, 146, 196),
        "size": (1200, 1200),
        "location": {"location_name": "香港", "city": "香港", "region": "香港特别行政区", "country": "中国"},
        "capture": {"make": "Ricoh", "model": "GR IIIx", "lens": "GR LENS 26.1mm F2.8", "focal_length": (26, 1), "aperture": (28, 10), "exposure_time": (1, 100), "iso": 250},
    },
    {
        "timestamp": "2024-11-08 16:10:00",
        "label": "New York November",
        "color": (150, 171, 190),
        "size": (1920, 1080),
        "location": {"location_name": "纽约", "city": "纽约", "region": "纽约州", "country": "美国"},
        "capture": {"make": "Canon", "model": "EOS R6", "lens": "RF 24-70mm F2.8L", "focal_length": (42, 1), "aperture": (28, 10), "exposure_time": (1, 320), "iso": 200},
    },
    {
        "timestamp": "2025-05-02 14:10:00",
        "label": "Xinjiang Spring 1",
        "color": (196, 179, 119),
        "size": (1600, 1200),
        "location": {"location_name": "新疆", "city": "乌鲁木齐", "region": "新疆维吾尔自治区", "country": "中国"},
        "capture": {"make": "Nikon", "model": "Z6 II", "lens": "NIKKOR Z 24-120mm f/4 S", "focal_length": (32, 1), "aperture": (4, 1), "exposure_time": (1, 250), "iso": 100},
    },
    {
        "timestamp": "2025-05-18 08:40:00",
        "label": "Xinjiang Spring 2",
        "color": (184, 164, 102),
        "size": (1080, 1920),
        "location": {"location_name": "新疆", "city": "伊犁", "region": "新疆维吾尔自治区", "country": "中国"},
        "capture": {"make": "Sony", "model": "ZV-E10", "lens": "E 11mm F1.8", "focal_length": (11, 1), "aperture": (18, 10), "exposure_time": (1, 640), "iso": 160},
    },
]


def _rational(value: tuple[int, int]) -> IFDRational:
    return IFDRational(value[0], value[1])


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
    return f"timeline_{slug}_{label_slug}.jpg"


def _format_fraction(value: tuple[int, int], prefix: str = "", suffix: str = "") -> str:
    numerator, denominator = value
    if denominator == 0:
        return ""
    decimal = numerator / denominator
    text = f"{decimal:.2f}".rstrip("0").rstrip(".")
    return f"{prefix}{text}{suffix}"


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
    draw.rectangle((margin, margin, width - margin, height - margin), outline=(255, 255, 255), width=max(4, min(width, height) // 220))
    draw.text((margin * 1.3, margin * 1.8), "TimeLens Timeline Test", fill=(255, 255, 255))
    draw.text((margin * 1.3, margin * 3.2), label, fill=(255, 255, 255))
    draw.text((margin * 1.3, margin * 4.6), timestamp, fill=(255, 255, 255))
    draw.text((margin * 1.3, margin * 6.0), location_name, fill=(255, 255, 255))
    ratio_label = f"{width}:{height}"
    draw.text((margin * 1.3, margin * 7.4), ratio_label, fill=(255, 255, 255))
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


def apply_test_locations(db_path: Path, generated: list[tuple[str, dict[str, object]]]) -> int:
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
