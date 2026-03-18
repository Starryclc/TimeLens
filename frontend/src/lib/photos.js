import { getApiBaseUrl } from "./api";

const backendOrigin = getApiBaseUrl().replace(/\/api\/?$/, "");

export function thumbnailUrl(path) {
  return `${backendOrigin}/${path}`;
}

export function originalPhotoUrl(photoId) {
  return `${backendOrigin}/api/media/photos/${photoId}`;
}

export function formatDateTime(value) {
  if (!value) {
    return "未记录时间";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function getPhotoLocation(photo) {
  return photo.location_name || photo.city || photo.region || photo.country || "未知地点";
}

export function getPhotoProvince(photo) {
  return photo.region || "";
}

export function getPhotoDevice(photo) {
  return photo.device || "未知设备";
}

export function getPhotoLocationText(photo) {
  return photo.location_name || photo.city || photo.region || photo.country || "";
}

export function getPhotoDeviceText(photo) {
  return photo.device || "";
}

export function getPhotoParameterText(photo) {
  return getPhotoParameterParts(photo).join("   ");
}

export function getPhotoParameterParts(photo) {
  const parts = [];
  if (photo.focal_length) {
    parts.push(photo.focal_length);
  }
  if (photo.aperture) {
    parts.push(photo.aperture);
  }
  if (photo.exposure_time) {
    parts.push(photo.exposure_time);
  }
  if (photo.iso) {
    parts.push(`ISO ${photo.iso}`);
  }
  return parts;
}

export function getPhotoYear(photo) {
  if (!photo.photo_taken_at) {
    return "未标记时间";
  }
  return new Date(photo.photo_taken_at).getFullYear().toString();
}

export function groupOnThisDay(photos) {
  const groups = new Map();
  photos.forEach((photo) => {
    if (!photo.photo_taken_at) {
      return;
    }
    const year = new Date(photo.photo_taken_at).getFullYear();
    const current = groups.get(year) || [];
    current.push(photo);
    groups.set(year, current);
  });
  return Array.from(groups.entries()).sort((a, b) => b[0] - a[0]);
}
