import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { apiGet, apiPatch, apiPost } from "../lib/api";
import {
  formatDateTime,
  getPhotoDeviceText,
  getPhotoLocation,
  getPhotoLocationText,
  getPhotoParameterParts,
  originalPhotoUrl,
  thumbnailUrl,
} from "../lib/photos";

const DAILY_RANDOM_STORAGE_KEY = "timelens.daily-random.v1";

export function HomePage() {
  const [onThisDayPhotos, setOnThisDayPhotos] = useState([]);
  const [randomPhoto, setRandomPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoritePending, setFavoritePending] = useState(false);
  const midnightTimerRef = useRef(null);

  useEffect(() => {
    loadHomePage();

    return () => {
      if (midnightTimerRef.current) {
        window.clearTimeout(midnightTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!randomPhoto) {
      return undefined;
    }

    const msUntilMidnight = getMsUntilNextMidnight();
    midnightTimerRef.current = window.setTimeout(() => {
      void loadHomePage({ forceNewRandom: true });
    }, msUntilMidnight);

    return () => {
      if (midnightTimerRef.current) {
        window.clearTimeout(midnightTimerRef.current);
      }
    };
  }, [randomPhoto?.id]);

  if (loading) {
    return <div className="loading-panel">正在载入首页...</div>;
  }

  if (error) {
    return (
      <EmptyState
        title="首页加载失败"
        description="请确认随机照片和那年今日接口可正常访问。"
      />
    );
  }

  const locationText = randomPhoto ? getPhotoLocationText(randomPhoto) : "";
  const deviceText = randomPhoto ? getPhotoDeviceText(randomPhoto) : "";
  const parameterParts = randomPhoto ? getPhotoParameterParts(randomPhoto) : [];

  async function loadHomePage({ forceNewRandom = false } = {}) {
    setLoading(true);
    setError(null);
    try {
      const [nextOnThisDayPhotos, nextRandomPhoto] = await Promise.all([
        apiGet("photos/on-this-day"),
        resolveDailyRandomPhoto({ forceNew: forceNewRandom }),
      ]);
      setOnThisDayPhotos(nextOnThisDayPhotos);
      setRandomPhoto(nextRandomPhoto);
      if (nextRandomPhoto) {
        const favoriteStatus = await apiGet(`albums/favorites/photos/${nextRandomPhoto.id}/status`);
        setIsFavorited(Boolean(favoriteStatus.is_favorited));
      } else {
        setIsFavorited(false);
      }
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  }

  async function resolveDailyRandomPhoto({ forceNew = false } = {}) {
    const todayKey = getTodayKey();
    if (!forceNew) {
      const cachedPhotoId = readDailyRandomPhotoId(todayKey);
      if (cachedPhotoId) {
        try {
          return await apiGet(`photos/${cachedPhotoId}`);
        } catch {
          clearDailyRandomPhotoId();
        }
      }
    }

    const nextPhoto = await apiGet("photos/random", { exclude_on_this_day: true });
    if (nextPhoto?.id) {
      writeDailyRandomPhotoId(todayKey, nextPhoto.id);
    } else {
      clearDailyRandomPhotoId();
    }
    return nextPhoto;
  }

  async function handleFavoriteToggle() {
    if (!randomPhoto || favoritePending) {
      return;
    }

    setFavoritePending(true);
    try {
      const response = await apiPost(`albums/favorites/photos/${randomPhoto.id}/toggle`, {});
      setIsFavorited(Boolean(response.is_favorited));
    } finally {
      setFavoritePending(false);
    }
  }

  async function handleShuffle() {
    setLoading(true);
    setError(null);
    try {
      const nextRandomPhoto = await resolveDailyRandomPhoto({ forceNew: true });
      setRandomPhoto(nextRandomPhoto);
      if (nextRandomPhoto) {
        const favoriteStatus = await apiGet(`albums/favorites/photos/${nextRandomPhoto.id}/status`);
        setIsFavorited(Boolean(favoriteStatus.is_favorited));
      } else {
        setIsFavorited(false);
      }
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload() {
    if (!randomPhoto) {
      return;
    }

    const response = await fetch(originalPhotoUrl(randomPhoto.id));
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = randomPhoto.file_name || `photo-${randomPhoto.id}.jpg`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(objectUrl);
  }

  async function handleEdit() {
    if (!randomPhoto) {
      return;
    }

    const nextTakenAt = window.prompt("拍摄时间（YYYY-MM-DD HH:mm，可留空）", formatEditableDateTime(randomPhoto.photo_taken_at));
    if (nextTakenAt === null) {
      return;
    }

    const nextLocation = window.prompt("地点（可留空）", randomPhoto.location_name || "");
    if (nextLocation === null) {
      return;
    }

    const nextDevice = window.prompt("设备（可留空）", randomPhoto.device_model || "");
    if (nextDevice === null) {
      return;
    }

    const nextFocalLength = window.prompt("焦段（可留空）", randomPhoto.focal_length || "");
    if (nextFocalLength === null) {
      return;
    }

    const nextAperture = window.prompt("光圈（可留空）", randomPhoto.aperture || "");
    if (nextAperture === null) {
      return;
    }

    const nextExposureTime = window.prompt("快门速度（可留空）", randomPhoto.exposure_time || "");
    if (nextExposureTime === null) {
      return;
    }

    const nextIso = window.prompt("ISO（可留空）", randomPhoto.iso ? String(randomPhoto.iso) : "");
    if (nextIso === null) {
      return;
    }

    await apiPatch(`photos/${randomPhoto.id}`, {
      photo_taken_at: normalizeDateTimeInput(nextTakenAt),
      location_name: normalizeOptionalText(nextLocation),
      device_model: normalizeOptionalText(nextDevice),
      focal_length: normalizeOptionalText(nextFocalLength),
      aperture: normalizeOptionalText(nextAperture),
      exposure_time: normalizeOptionalText(nextExposureTime),
      iso: normalizeOptionalNumber(nextIso),
    });
    const refreshedPhoto = await apiGet(`photos/${randomPhoto.id}`);
    setRandomPhoto(refreshedPhoto);
  }

  return (
    <div className="page-shell-simple">
      {randomPhoto ? (
        <section className="random-photo-section">
          <div className="random-photo-header">
            <span className="section-kicker">每日推荐</span>
          </div>
          <div className="random-photo-shell">
            <div className="random-photo-frame">
              {randomPhoto.thumbnail_path ? (
                <img
                  className="random-photo-image"
                  src={thumbnailUrl(randomPhoto.thumbnail_path)}
                  alt={getPhotoLocation(randomPhoto)}
                />
              ) : (
                <div className="image-fallback image-fallback-large">No Preview</div>
              )}
            </div>

            <div className="random-photo-info">
              <div className="random-photo-meta">
                <div className="random-photo-info-row">
                  {randomPhoto.photo_taken_at ? (
                    <div className="random-photo-info-block">
                      <span className="random-photo-label">TIME</span>
                      <strong className="random-photo-value">{formatDateTime(randomPhoto.photo_taken_at)}</strong>
                    </div>
                  ) : null}
                  {locationText ? (
                    <div className="random-photo-info-block">
                      <span className="random-photo-label">PLACE</span>
                      <strong className="random-photo-value">{locationText}</strong>
                    </div>
                  ) : null}
                </div>

                <div className="random-photo-info-row">
                  {deviceText ? (
                    <div className="random-photo-info-block">
                      <span className="random-photo-label">DEVICE</span>
                      <strong className="random-photo-value">{deviceText}</strong>
                    </div>
                  ) : null}
                  {parameterParts.length > 0 ? (
                    <div className="random-photo-info-block">
                      <span className="random-photo-label">SETTINGS</span>
                      <strong className="random-photo-value random-photo-parameter-list">
                        {parameterParts.map((part) => (
                          <span key={part} className="random-photo-parameter-item">
                            {part}
                          </span>
                        ))}
                      </strong>
                    </div>
                  ) : null}
                </div>
              </div>

              <div className="random-photo-toolbar" aria-label="Photo Actions">
                <button type="button" className="photo-icon-button" aria-label="换一张随机照片" onClick={handleShuffle}>
                  <ShuffleIcon />
                </button>
                <button type="button" className="photo-icon-button" aria-label="下载原图" onClick={handleDownload}>
                  <DownloadIcon />
                </button>
                <button type="button" className="photo-icon-button" aria-label="编辑照片信息" onClick={handleEdit}>
                  <EditIcon />
                </button>
                <button
                  type="button"
                  className={`photo-icon-button favorite-toggle ${isFavorited ? "is-favorited" : ""}`}
                  aria-label={isFavorited ? "取消收藏" : "加入收藏"}
                  aria-pressed={isFavorited}
                  onClick={handleFavoriteToggle}
                  disabled={favoritePending}
                >
                  <StarIcon filled={isFavorited} />
                </button>
              </div>
            </div>
          </div>
        </section>
      ) : (
        <EmptyState title="还没有照片" description="先导入照片后，首页会先显示一张随机照片。" />
      )}

      <section className="content-section">
        <div className="section-header">
          <div>
            <span className="section-kicker">那年今日</span>
            <h2>继续下滑，回到同一天</h2>
          </div>
          <Link className="section-link" to="/photos">
            查看全部时间线
          </Link>
        </div>

        {onThisDayPhotos.length > 0 ? (
          <div className="simple-photo-grid">
            {onThisDayPhotos.map((photo) => (
              <Link key={photo.id} className="simple-photo-card" to={`/photos/${photo.id}`}>
                {photo.thumbnail_path ? (
                  <img src={thumbnailUrl(photo.thumbnail_path)} alt={getPhotoLocation(photo)} />
                ) : (
                  <div className="image-fallback">No Preview</div>
                )}
                <div className="simple-photo-meta">
                  <strong>{getPhotoLocation(photo)}</strong>
                  <span>{formatDateTime(photo.photo_taken_at)}</span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            title="今天没有历史照片"
            description="继续导入往年照片后，这里会自动出现当天对应的历史回忆。"
          />
        )}
      </section>
    </div>
  );
}

function getTodayKey() {
  return new Intl.DateTimeFormat("sv-SE").format(new Date());
}

function getMsUntilNextMidnight() {
  const now = new Date();
  const nextMidnight = new Date(now);
  nextMidnight.setHours(24, 0, 0, 0);
  return Math.max(1000, nextMidnight.getTime() - now.getTime() + 1000);
}

function readDailyRandomPhotoId(todayKey) {
  try {
    const raw = window.localStorage.getItem(DAILY_RANDOM_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (parsed.date !== todayKey || !parsed.photoId) {
      return null;
    }
    return parsed.photoId;
  } catch {
    return null;
  }
}

function writeDailyRandomPhotoId(todayKey, photoId) {
  window.localStorage.setItem(
    DAILY_RANDOM_STORAGE_KEY,
    JSON.stringify({ date: todayKey, photoId }),
  );
}

function clearDailyRandomPhotoId() {
  window.localStorage.removeItem(DAILY_RANDOM_STORAGE_KEY);
}

function normalizeOptionalText(value) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function normalizeOptionalNumber(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatEditableDateTime(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hour = String(date.getHours()).padStart(2, "0");
  const minute = String(date.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day} ${hour}:${minute}`;
}

function normalizeDateTimeInput(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  return trimmed.includes("T") ? trimmed : trimmed.replace(" ", "T");
}

function StarIcon({ filled }) {
  return (
    <svg viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3.8 14.5 8.9l5.6.8-4 4 1 5.5L12 16.6l-5.1 2.6 1-5.5-4-4 5.6-.8L12 3.8Z" />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 4.5v10.2" />
      <path d="m8.4 11.6 3.6 3.7 3.6-3.7" />
      <path d="M5 18.5h14" />
    </svg>
  );
}

function ShuffleIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="shuffle-icon">
      <path d="M16.5 4.5h3v3" />
      <path d="M4.5 18.5 19.5 4.5" />
      <path d="M12.2 11.8 19.5 19.1" />
      <path d="M16.5 19.5h3v-3" />
      <path d="M4.5 5.5 8 9" />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="m4 20 4.1-.9L18.6 8.6a1.7 1.7 0 0 0 0-2.4l-.8-.8a1.7 1.7 0 0 0-2.4 0L4.9 15.9 4 20Z" />
      <path d="m13.9 6.9 3.2 3.2" />
    </svg>
  );
}
