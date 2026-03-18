function toDate(value) {
  return value ? new Date(value) : null;
}

function stableIndex(key, length) {
  if (length === 0) {
    return 0;
  }
  const total = Array.from(key).reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return total % length;
}

function sortPhotos(photos, direction = "asc") {
  return [...photos].sort((left, right) => {
    const leftTime = toDate(left.photo_taken_at)?.getTime() || 0;
    const rightTime = toDate(right.photo_taken_at)?.getTime() || 0;
    return direction === "asc" ? leftTime - rightTime : rightTime - leftTime;
  });
}

function getAlbumLocation(photos) {
  const coverPhoto = photos.find(Boolean);
  if (!coverPhoto) {
    return "";
  }
  return coverPhoto.region || "";
}

function buildAlbum(type, year, month, day, photos) {
  const sortedPhotos = sortPhotos(photos, "asc");
  const key = type === "day" ? `${year}-day-${month}-${day}` : `${year}-month-${month}`;
  const coverPhoto = sortedPhotos[stableIndex(key, sortedPhotos.length)];

  return {
    key,
    type,
    year,
    month,
    day,
    title: type === "day" ? `${year} 年今日` : `${year} 年 ${month} 月`,
    shortTitle: type === "day" ? `${year}年今天` : `${year}年本月`,
    subtitle:
      type === "day"
        ? `${year} 年 ${month} 月 ${day} 日`
        : `${year} 年 ${month} 月的照片时间线`,
    locationLabel: getAlbumLocation(sortedPhotos),
    photoCount: sortedPhotos.length,
    coverPhoto,
    photos: sortedPhotos,
  };
}

export function buildMemoryAlbums(photos, referenceDate = new Date()) {
  const month = referenceDate.getMonth() + 1;
  const day = referenceDate.getDate();
  const currentYear = referenceDate.getFullYear();
  const datedPhotos = photos.filter((photo) => photo.photo_taken_at);
  const years = Array.from(
    new Set(
      datedPhotos
        .map((photo) => toDate(photo.photo_taken_at)?.getFullYear())
        .filter((value) => value && value < currentYear),
    ),
  ).sort((left, right) => right - left);

  const albums = [];

  years.forEach((year) => {
    const yearPhotos = datedPhotos.filter(
      (photo) => toDate(photo.photo_taken_at)?.getFullYear() === year,
    );

    const sameDayPhotos = yearPhotos.filter((photo) => {
      const photoDate = toDate(photo.photo_taken_at);
      return photoDate && photoDate.getMonth() + 1 === month && photoDate.getDate() === day;
    });
    if (sameDayPhotos.length) {
      albums.push(buildAlbum("day", year, month, day, sameDayPhotos));
    }

    const sameMonthPhotos = yearPhotos.filter((photo) => {
      const photoDate = toDate(photo.photo_taken_at);
      return photoDate && photoDate.getMonth() + 1 === month;
    });
    if (sameMonthPhotos.length) {
      albums.push(buildAlbum("month", year, month, day, sameMonthPhotos));
    }
  });

  return albums;
}

export function buildHomepageMemoryAlbums(photos, referenceDate = new Date()) {
  const albums = buildMemoryAlbums(photos, referenceDate);
  const grouped = new Map();

  albums.forEach((album) => {
    const current = grouped.get(album.year) || {};
    grouped.set(album.year, {
      ...current,
      [album.type]: album,
    });
  });

  return Array.from(grouped.entries())
    .sort((left, right) => right[0] - left[0])
    .map(([, entry]) => entry.day || entry.month)
    .filter(Boolean);
}

export function groupAlbumPhotosByDate(photos) {
  const groups = new Map();

  sortPhotos(photos, "asc").forEach((photo) => {
    const photoDate = toDate(photo.photo_taken_at);
    const key = photoDate
      ? `${photoDate.getFullYear()}-${String(photoDate.getMonth() + 1).padStart(2, "0")}-${String(
          photoDate.getDate(),
        ).padStart(2, "0")}`
      : "未记录日期";
    const current = groups.get(key) || [];
    current.push(photo);
    groups.set(key, current);
  });

  return Array.from(groups.entries());
}
