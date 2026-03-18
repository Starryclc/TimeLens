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
  groupOnThisDay,
  getPhotoYear,
  originalPhotoUrl,
  thumbnailUrl,
} from "../lib/photos";

const DAILY_RANDOM_STORAGE_KEY = "timelens.daily-random.v1";
const ON_THIS_DAY_PREVIEW_LIMIT = 8;
const LIGHTBOX_EXIT_MS = 100;

export function HomePage() {
  const [onThisDayPhotos, setOnThisDayPhotos] = useState([]);
  const [expandedOnThisDayPhotoId, setExpandedOnThisDayPhotoId] = useState(null);
  const [lightboxState, setLightboxState] = useState(null);
  const [onThisDayLightboxClosing, setOnThisDayLightboxClosing] = useState(false);
  const [onThisDayLightboxInfoOpen, setOnThisDayLightboxInfoOpen] = useState(false);
  const [onThisDayLightboxEditing, setOnThisDayLightboxEditing] = useState(false);
  const [onThisDayLightboxDraft, setOnThisDayLightboxDraft] = useState(null);
  const [onThisDayLightboxSaving, setOnThisDayLightboxSaving] = useState(false);
  const [randomLightboxOpen, setRandomLightboxOpen] = useState(false);
  const [randomLightboxClosing, setRandomLightboxClosing] = useState(false);
  const [randomLightboxInfoOpen, setRandomLightboxInfoOpen] = useState(false);
  const [randomLightboxEditing, setRandomLightboxEditing] = useState(false);
  const [randomLightboxDraft, setRandomLightboxDraft] = useState(null);
  const [randomLightboxSaving, setRandomLightboxSaving] = useState(false);
  const [isMobileLayout, setIsMobileLayout] = useState(() => detectMobileLayout());
  const [randomPhoto, setRandomPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [randomRefreshing, setRandomRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoritePending, setFavoritePending] = useState(false);
  const midnightTimerRef = useRef(null);
  const onThisDayClickTimerRef = useRef(null);
  const onThisDayLightboxTimerRef = useRef(null);
  const randomLightboxTimerRef = useRef(null);
  const lightboxTouchStartRef = useRef(null);

  useEffect(() => {
    loadHomePage();

    return () => {
      if (midnightTimerRef.current) {
        window.clearTimeout(midnightTimerRef.current);
      }
      if (onThisDayClickTimerRef.current) {
        window.clearTimeout(onThisDayClickTimerRef.current);
      }
      if (onThisDayLightboxTimerRef.current) {
        window.clearTimeout(onThisDayLightboxTimerRef.current);
      }
      if (randomLightboxTimerRef.current) {
        window.clearTimeout(randomLightboxTimerRef.current);
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

  useEffect(() => {
    function updateLayoutMode() {
      setIsMobileLayout(detectMobileLayout());
    }

    updateLayoutMode();
    window.addEventListener("resize", updateLayoutMode);
    return () => window.removeEventListener("resize", updateLayoutMode);
  }, []);

  useEffect(() => {
    if (!lightboxState && !randomLightboxOpen) {
      return undefined;
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        closeAllLightboxes();
      }
      if (event.key === "ArrowLeft") {
        stepOnThisDayLightbox(-1);
      }
      if (event.key === "ArrowRight") {
        stepOnThisDayLightbox(1);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [lightboxState, randomLightboxOpen]);

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
  const onThisDayGroups = groupOnThisDay(onThisDayPhotos);
  const currentLightboxPhoto =
    lightboxState && lightboxState.photos[lightboxState.index]
      ? lightboxState.photos[lightboxState.index]
      : null;

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
    setRandomRefreshing(true);
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
      setRandomRefreshing(false);
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

  function openOnThisDayLightbox(year, photos, photoId) {
    const index = photos.findIndex((photo) => photo.id === photoId);
    if (index === -1) {
      return;
    }
    if (onThisDayLightboxTimerRef.current) {
      window.clearTimeout(onThisDayLightboxTimerRef.current);
      onThisDayLightboxTimerRef.current = null;
    }
    setOnThisDayLightboxClosing(false);
    setOnThisDayLightboxInfoOpen(false);
    setOnThisDayLightboxEditing(false);
    setOnThisDayLightboxDraft(createLightboxDraft(photos[index]));
    setLightboxState({ year, photos, index });
  }

  function closeOnThisDayLightbox() {
    if (!lightboxState || onThisDayLightboxClosing) {
      return;
    }
    setOnThisDayLightboxClosing(true);
    onThisDayLightboxTimerRef.current = window.setTimeout(() => {
      setLightboxState(null);
      setOnThisDayLightboxClosing(false);
      setOnThisDayLightboxInfoOpen(false);
      setOnThisDayLightboxEditing(false);
      setOnThisDayLightboxDraft(null);
      onThisDayLightboxTimerRef.current = null;
    }, LIGHTBOX_EXIT_MS);
  }

  function closeRandomLightbox() {
    if (!randomLightboxOpen || randomLightboxClosing) {
      return;
    }
    setRandomLightboxClosing(true);
    randomLightboxTimerRef.current = window.setTimeout(() => {
      setRandomLightboxOpen(false);
      setRandomLightboxClosing(false);
      setRandomLightboxInfoOpen(false);
      setRandomLightboxEditing(false);
      setRandomLightboxDraft(null);
      randomLightboxTimerRef.current = null;
    }, LIGHTBOX_EXIT_MS);
  }

  function closeAllLightboxes() {
    closeOnThisDayLightbox();
    closeRandomLightbox();
  }

  function openRandomLightbox() {
    if (randomLightboxTimerRef.current) {
      window.clearTimeout(randomLightboxTimerRef.current);
      randomLightboxTimerRef.current = null;
    }
    setRandomLightboxClosing(false);
    setRandomLightboxInfoOpen(false);
    setRandomLightboxEditing(false);
    setRandomLightboxDraft(createLightboxDraft(randomPhoto));
    setRandomLightboxOpen(true);
  }

  function stepOnThisDayLightbox(direction) {
    setLightboxState((current) => {
      if (!current) {
        return current;
      }
      const nextIndex = current.index + direction;
      if (nextIndex < 0 || nextIndex >= current.photos.length) {
        return current;
      }
      return { ...current, index: nextIndex };
    });
  }

  function handleLightboxTouchStart(event) {
    const touch = event.touches?.[0];
    if (!touch) {
      return;
    }
    lightboxTouchStartRef.current = { x: touch.clientX, y: touch.clientY };
  }

  function handleLightboxTouchEnd(event) {
    if (!isMobileLayout || !lightboxState || !lightboxTouchStartRef.current) {
      lightboxTouchStartRef.current = null;
      return;
    }

    const touch = event.changedTouches?.[0];
    if (!touch) {
      lightboxTouchStartRef.current = null;
      return;
    }

    const deltaX = touch.clientX - lightboxTouchStartRef.current.x;
    const deltaY = touch.clientY - lightboxTouchStartRef.current.y;
    lightboxTouchStartRef.current = null;

    if (Math.abs(deltaY) < 44 || Math.abs(deltaY) < Math.abs(deltaX)) {
      return;
    }

    if (deltaY < 0) {
      stepOnThisDayLightbox(1);
    } else {
      stepOnThisDayLightbox(-1);
    }
  }

  function handleOnThisDayPhotoKeyDown(event, year, photos, photoId) {
    if (event.key === "Enter") {
      event.preventDefault();
      openOnThisDayLightbox(year, photos, photoId);
    }
  }

  function handleOnThisDayPhotoClick(photoId) {
    if (isMobileLayout) {
      return;
    }
    if (onThisDayClickTimerRef.current) {
      window.clearTimeout(onThisDayClickTimerRef.current);
    }

    onThisDayClickTimerRef.current = window.setTimeout(() => {
      setExpandedOnThisDayPhotoId((current) => (current === photoId ? null : photoId));
      onThisDayClickTimerRef.current = null;
    }, 180);
  }

  function handleOnThisDayPhotoDoubleClick(year, photos, photoId) {
    if (isMobileLayout) {
      return;
    }
    if (onThisDayClickTimerRef.current) {
      window.clearTimeout(onThisDayClickTimerRef.current);
      onThisDayClickTimerRef.current = null;
    }
    openOnThisDayLightbox(year, photos, photoId);
  }

  function applyUpdatedPhoto(updatedPhoto) {
    setRandomPhoto((current) => (current?.id === updatedPhoto.id ? updatedPhoto : current));
    setOnThisDayPhotos((current) => current.map((photo) => (photo.id === updatedPhoto.id ? updatedPhoto : photo)));
    setLightboxState((current) =>
      current
        ? {
            ...current,
            photos: current.photos.map((photo) => (photo.id === updatedPhoto.id ? updatedPhoto : photo)),
          }
        : current,
    );
  }

  function startOnThisDayLightboxEdit() {
    if (!currentLightboxPhoto) {
      return;
    }
    setOnThisDayLightboxDraft(createLightboxDraft(currentLightboxPhoto));
    setOnThisDayLightboxInfoOpen(true);
    setOnThisDayLightboxEditing(true);
  }

  function startRandomLightboxEdit() {
    if (!randomPhoto) {
      return;
    }
    setRandomLightboxDraft(createLightboxDraft(randomPhoto));
    setRandomLightboxInfoOpen(true);
    setRandomLightboxEditing(true);
  }

  async function saveOnThisDayLightboxEdit() {
    if (!currentLightboxPhoto || !onThisDayLightboxDraft || onThisDayLightboxSaving) {
      return;
    }
    setOnThisDayLightboxSaving(true);
    try {
      await apiPatch(`photos/${currentLightboxPhoto.id}`, buildLightboxUpdatePayload(onThisDayLightboxDraft));
      const refreshedPhoto = await apiGet(`photos/${currentLightboxPhoto.id}`);
      applyUpdatedPhoto(refreshedPhoto);
      setOnThisDayLightboxDraft(createLightboxDraft(refreshedPhoto));
      setOnThisDayLightboxEditing(false);
    } finally {
      setOnThisDayLightboxSaving(false);
    }
  }

  async function saveRandomLightboxEdit() {
    if (!randomPhoto || !randomLightboxDraft || randomLightboxSaving) {
      return;
    }
    setRandomLightboxSaving(true);
    try {
      await apiPatch(`photos/${randomPhoto.id}`, buildLightboxUpdatePayload(randomLightboxDraft));
      const refreshedPhoto = await apiGet(`photos/${randomPhoto.id}`);
      applyUpdatedPhoto(refreshedPhoto);
      setRandomLightboxDraft(createLightboxDraft(refreshedPhoto));
      setRandomLightboxEditing(false);
    } finally {
      setRandomLightboxSaving(false);
    }
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
                  onClick={isMobileLayout ? openRandomLightbox : undefined}
                  onDoubleClick={!isMobileLayout ? openRandomLightbox : undefined}
                  title={isMobileLayout ? "点击可放大查看" : "双击可放大查看"}
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
                <button
                  type="button"
                  className="photo-icon-button"
                  aria-label="换一张随机照片"
                  onClick={handleShuffle}
                  disabled={randomRefreshing}
                >
                  <ShuffleIcon />
                </button>
                <button type="button" className="photo-icon-button" aria-label="下载原图" onClick={handleDownload}>
                  <DownloadIcon />
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

      <section className="content-section on-this-day-section">
        <div className="on-this-day-header">
          <span className="section-kicker">那年今日</span>
        </div>

        {onThisDayGroups.length > 0 ? (
          <div className="on-this-day-groups">
            {onThisDayGroups.map(([year, photos]) => (
              <section key={year} className="on-this-day-year-block">
                <div className="on-this-day-year-rail" aria-hidden="true">
                  <span className="on-this-day-year-dot" />
                  <span className="on-this-day-year-mark">{year}</span>
                  <span className="on-this-day-year-line" />
                </div>

                <div className="on-this-day-year-content">
                  <div className="on-this-day-year-header">
                    <div className="on-this-day-year-actions">
                      <span className="on-this-day-year-count">{photos.length} 张</span>
                      <Link
                        to={`/on-this-day/${year}`}
                        className="on-this-day-jump-button"
                        aria-label={`查看 ${year} 年这一天的全部照片`}
                      >
                        <ArrowRightIcon />
                      </Link>
                    </div>
                  </div>

                  <div className="on-this-day-strip">
                    {photos.slice(0, ON_THIS_DAY_PREVIEW_LIMIT).map((photo) => (
                      <button
                        key={photo.id}
                        type="button"
                        className={`on-this-day-photo-card ${expandedOnThisDayPhotoId === photo.id ? "is-expanded" : ""}`}
                        onClick={() => (isMobileLayout ? openOnThisDayLightbox(year, photos, photo.id) : handleOnThisDayPhotoClick(photo.id))}
                        onDoubleClick={() => handleOnThisDayPhotoDoubleClick(year, photos, photo.id)}
                        onKeyDown={(event) => handleOnThisDayPhotoKeyDown(event, year, photos, photo.id)}
                        aria-label={isMobileLayout ? `查看 ${getPhotoLocation(photo)} 的大图` : `查看 ${getPhotoLocation(photo)} 的照片信息`}
                        title={isMobileLayout ? "点击可放大查看" : "双击可放大查看"}
                      >
                        <div className="on-this-day-photo-frame">
                          {photo.thumbnail_path ? (
                            <img
                              className="on-this-day-photo-image"
                              src={thumbnailUrl(photo.thumbnail_path)}
                              alt={getPhotoLocation(photo)}
                            />
                          ) : (
                            <div className="image-fallback on-this-day-photo-image">No Preview</div>
                          )}
                          {expandedOnThisDayPhotoId === photo.id ? (
                            <div className="on-this-day-photo-overlay">
                              <div className="on-this-day-photo-overlay-content">
                                {photo.photo_taken_at ? (
                                  <div className="on-this-day-photo-info-block">
                                    <span className="random-photo-label">TIME</span>
                                    <strong className="on-this-day-photo-info-value">
                                      {formatDateTime(photo.photo_taken_at)}
                                    </strong>
                                  </div>
                                ) : null}
                                {getPhotoLocationText(photo) ? (
                                  <div className="on-this-day-photo-info-block">
                                    <span className="random-photo-label">PLACE</span>
                                    <strong className="on-this-day-photo-info-value">
                                      {getPhotoLocationText(photo)}
                                    </strong>
                                  </div>
                                ) : null}
                                {getPhotoDeviceText(photo) ? (
                                  <div className="on-this-day-photo-info-block">
                                    <span className="random-photo-label">DEVICE</span>
                                    <strong className="on-this-day-photo-info-value">
                                      {getPhotoDeviceText(photo)}
                                    </strong>
                                  </div>
                                ) : null}
                                {getPhotoParameterParts(photo).length > 0 ? (
                                  <div className="on-this-day-photo-info-block">
                                    <span className="random-photo-label">SETTINGS</span>
                                    <strong className="on-this-day-photo-info-value random-photo-parameter-list">
                                      {getPhotoParameterParts(photo).map((part) => (
                                        <span key={part} className="random-photo-parameter-item">
                                          {part}
                                        </span>
                                      ))}
                                    </strong>
                                  </div>
                                ) : null}
                              </div>
                            </div>
                          ) : null}
                        </div>
                      </button>
                    ))}

                    {photos.length > ON_THIS_DAY_PREVIEW_LIMIT ? (
                      <Link
                        to={`/on-this-day/${year}`}
                        className="on-this-day-more-card"
                        aria-label={`查看 ${year} 年这一天的全部照片`}
                      >
                        <span className="on-this-day-more-fade" aria-hidden="true" />
                        <span className="on-this-day-more-arrow">&gt;</span>
                      </Link>
                    ) : null}
                  </div>
                </div>
              </section>
            ))}
          </div>
        ) : (
          <EmptyState
            title="今天没有历史照片"
            description="继续导入往年照片后，这里会自动出现当天对应的历史回忆。"
          />
        )}
      </section>

      {currentLightboxPhoto ? (
        <div
          className={`on-this-day-lightbox-backdrop ${onThisDayLightboxClosing ? "is-closing" : ""}`}
          role="presentation"
          onClick={closeOnThisDayLightbox}
        >
          <section
            className={`on-this-day-lightbox ${onThisDayLightboxClosing ? "is-closing" : ""}`}
            role="dialog"
            aria-modal="true"
            aria-label={`${lightboxState.year} 年这一天的照片预览`}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="on-this-day-lightbox-header">
              <div className="on-this-day-lightbox-meta">
                <span className="on-this-day-lightbox-year">{lightboxState.year}</span>
                <span className="on-this-day-lightbox-count">
                  {lightboxState.index + 1} / {lightboxState.photos.length}
                </span>
              </div>
              <div className="on-this-day-lightbox-actions">
                <button
                  type="button"
                  className={`on-this-day-lightbox-info-toggle ${onThisDayLightboxInfoOpen ? "is-active" : ""}`}
                  aria-label={onThisDayLightboxInfoOpen ? "隐藏照片信息" : "查看照片信息"}
                  aria-pressed={onThisDayLightboxInfoOpen}
                  onClick={() => setOnThisDayLightboxInfoOpen((current) => !current)}
                >
                  <InfoIcon />
                </button>
                <button
                  type="button"
                  className="on-this-day-lightbox-close"
                  aria-label="关闭预览"
                  onClick={closeOnThisDayLightbox}
                >
                  <ChevronDownIcon />
                </button>
              </div>
            </div>

            <div className="on-this-day-lightbox-stage">
              <button
                type="button"
                className="on-this-day-lightbox-nav"
                aria-label="上一张"
                onClick={() => stepOnThisDayLightbox(-1)}
                disabled={lightboxState.index === 0}
              >
                <ChevronLeftIcon />
              </button>

              <div
                className="on-this-day-lightbox-photo-shell"
                onTouchStart={handleLightboxTouchStart}
                onTouchEnd={handleLightboxTouchEnd}
              >
                {currentLightboxPhoto ? (
                  <img
                    className="on-this-day-lightbox-image"
                    src={originalPhotoUrl(currentLightboxPhoto.id)}
                    alt={getPhotoLocation(currentLightboxPhoto)}
                  />
                ) : (
                  <div className="image-fallback on-this-day-lightbox-image">No Preview</div>
                )}
              </div>

              <button
                type="button"
                className="on-this-day-lightbox-nav"
                aria-label="下一张"
                onClick={() => stepOnThisDayLightbox(1)}
                disabled={lightboxState.index >= lightboxState.photos.length - 1}
              >
                <ChevronRightIcon />
              </button>
            </div>

            {onThisDayLightboxInfoOpen ? (
              <div className="lightbox-info-panel">
                <div className="lightbox-panel-toolbar">
                  {onThisDayLightboxEditing ? (
                    <>
                      <button
                        type="button"
                        className="lightbox-panel-icon-button is-secondary"
                        aria-label="取消编辑"
                        onClick={() => {
                          setOnThisDayLightboxEditing(false);
                          setOnThisDayLightboxDraft(createLightboxDraft(currentLightboxPhoto));
                        }}
                      >
                        <CloseXIcon />
                      </button>
                      <button
                        type="button"
                        className="lightbox-panel-icon-button"
                        aria-label="保存编辑"
                        onClick={saveOnThisDayLightboxEdit}
                        disabled={onThisDayLightboxSaving}
                      >
                        <CheckIcon />
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      className="lightbox-panel-icon-button"
                      aria-label="编辑照片信息"
                      onClick={startOnThisDayLightboxEdit}
                    >
                      <EditIcon />
                    </button>
                  )}
                </div>
                <LightboxInfoPanel
                  photo={currentLightboxPhoto}
                  editing={onThisDayLightboxEditing}
                  draft={onThisDayLightboxDraft}
                  saving={onThisDayLightboxSaving}
                  onDraftChange={setOnThisDayLightboxDraft}
                  onCancel={() => {
                    setOnThisDayLightboxEditing(false);
                    setOnThisDayLightboxDraft(createLightboxDraft(currentLightboxPhoto));
                  }}
                  onSave={saveOnThisDayLightboxEdit}
                />
              </div>
            ) : null}
          </section>
        </div>
      ) : null}

      {randomLightboxOpen && randomPhoto ? (
        <div
          className={`on-this-day-lightbox-backdrop ${randomLightboxClosing ? "is-closing" : ""}`}
          role="presentation"
          onClick={closeRandomLightbox}
        >
          <section
            className={`on-this-day-lightbox random-lightbox ${randomLightboxClosing ? "is-closing" : ""}`}
            role="dialog"
            aria-modal="true"
            aria-label="每日推荐照片预览"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="on-this-day-lightbox-header">
              <div className="on-this-day-lightbox-meta">
                <span className="on-this-day-lightbox-year">每日推荐</span>
              </div>
              <div className="on-this-day-lightbox-actions">
                <button
                  type="button"
                  className={`on-this-day-lightbox-info-toggle ${randomLightboxInfoOpen ? "is-active" : ""}`}
                  aria-label={randomLightboxInfoOpen ? "隐藏照片信息" : "查看照片信息"}
                  aria-pressed={randomLightboxInfoOpen}
                  onClick={() => setRandomLightboxInfoOpen((current) => !current)}
                >
                  <InfoIcon />
                </button>
                <button
                  type="button"
                  className="on-this-day-lightbox-close"
                  aria-label="关闭预览"
                  onClick={closeRandomLightbox}
                >
                  <ChevronDownIcon />
                </button>
              </div>
            </div>

            <div className="on-this-day-lightbox-stage random-lightbox-stage">
              <div className="on-this-day-lightbox-photo-shell">
                <img
                  className="on-this-day-lightbox-image"
                  src={originalPhotoUrl(randomPhoto.id)}
                  alt={getPhotoLocation(randomPhoto)}
                />
              </div>
            </div>

            {randomLightboxInfoOpen ? (
              <div className="lightbox-info-panel">
                <div className="lightbox-panel-toolbar">
                  {randomLightboxEditing ? (
                    <>
                      <button
                        type="button"
                        className="lightbox-panel-icon-button is-secondary"
                        aria-label="取消编辑"
                        onClick={() => {
                          setRandomLightboxEditing(false);
                          setRandomLightboxDraft(createLightboxDraft(randomPhoto));
                        }}
                      >
                        <CloseXIcon />
                      </button>
                      <button
                        type="button"
                        className="lightbox-panel-icon-button"
                        aria-label="保存编辑"
                        onClick={saveRandomLightboxEdit}
                        disabled={randomLightboxSaving}
                      >
                        <CheckIcon />
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      className="lightbox-panel-icon-button"
                      aria-label="编辑照片信息"
                      onClick={startRandomLightboxEdit}
                    >
                      <EditIcon />
                    </button>
                  )}
                </div>
                <LightboxInfoPanel
                  photo={randomPhoto}
                  editing={randomLightboxEditing}
                  draft={randomLightboxDraft}
                  saving={randomLightboxSaving}
                  onDraftChange={setRandomLightboxDraft}
                  onCancel={() => {
                    setRandomLightboxEditing(false);
                    setRandomLightboxDraft(createLightboxDraft(randomPhoto));
                  }}
                  onSave={saveRandomLightboxEdit}
                />
              </div>
            ) : null}
          </section>
        </div>
      ) : null}

    </div>
  );
}

function getTodayKey() {
  return new Intl.DateTimeFormat("sv-SE").format(new Date());
}

function detectMobileLayout() {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }
  return window.matchMedia("(max-width: 720px)").matches;
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

function createLightboxDraft(photo) {
  if (!photo) {
    return null;
  }
  return {
    photo_taken_at: formatEditableDateTime(photo.photo_taken_at),
    location_name: photo.location_name || "",
    city: photo.city || "",
    region: photo.region || "",
    country: photo.country || "",
    device: photo.device || "",
    lens_model: photo.lens_model || "",
    focal_length: photo.focal_length || "",
    aperture: photo.aperture || "",
    exposure_time: photo.exposure_time || "",
    iso: photo.iso ? String(photo.iso) : "",
  };
}

function buildLightboxUpdatePayload(draft) {
  return {
    photo_taken_at: normalizeDateTimeInput(draft.photo_taken_at || ""),
    location_name: normalizeOptionalText(draft.location_name || ""),
    city: normalizeOptionalText(draft.city || ""),
    region: normalizeOptionalText(draft.region || ""),
    country: normalizeOptionalText(draft.country || ""),
    device: normalizeOptionalText(draft.device || ""),
    lens_model: normalizeOptionalText(draft.lens_model || ""),
    focal_length: normalizeOptionalText(draft.focal_length || ""),
    aperture: normalizeOptionalText(draft.aperture || ""),
    exposure_time: normalizeOptionalText(draft.exposure_time || ""),
    iso: normalizeOptionalNumber(draft.iso || ""),
  };
}

function buildPhotoInfoItems(photo) {
  if (!photo) {
    return [];
  }

  const items = [
    { label: "TIME", value: photo.photo_taken_at ? formatDateTime(photo.photo_taken_at) : "" },
    { label: "PLACE", value: photo.location_name || "" },
    { label: "DEVICE", value: getPhotoDeviceText(photo) },
    { label: "LENS", value: photo.lens_model || "" },
    { label: "SETTINGS", value: getPhotoParameterParts(photo).join("   ") },
  ];

  if (photo.width && photo.height) {
    items.push({ label: "SIZE", value: `${photo.width} × ${photo.height}` });
  }

  items.push({ label: "CITY", value: photo.city || "" });
  items.push({ label: "REGION", value: photo.region || "" });
  items.push({ label: "COUNTRY", value: photo.country || "" });

  if (photo.mime_type) {
    items.push({ label: "TYPE", value: photo.mime_type });
  }

  if (photo.file_size) {
    items.push({ label: "FILE SIZE", value: formatFileSize(photo.file_size) });
  }

  if (photo.file_path) {
    items.push({ label: "PATH", value: photo.file_path, isPath: true });
  }

  return items;
}

function formatFileSize(value) {
  if (!value || value < 0) {
    return "";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  if (value < 1024 * 1024 * 1024) {
    return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  }
  return `${(value / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

function LightboxInfoPanel({ photo, editing, draft, onDraftChange }) {
  if (!photo) {
    return null;
  }

  const infoItems = buildPhotoInfoItems(photo);
  const settingsParts = [
    photo.focal_length || "",
    photo.aperture || "",
    photo.exposure_time || "",
    photo.iso ? `${photo.iso}` : "",
  ];
  const editableMap = {
    TIME: (
      <input
        className="lightbox-inline-input"
        value={draft?.photo_taken_at ?? ""}
        placeholder="YYYY-MM-DD HH:mm"
        onChange={(event) => onDraftChange((current) => ({ ...current, photo_taken_at: event.target.value }))}
      />
    ),
    PLACE: (
      <input
        className="lightbox-inline-input"
        value={draft?.location_name ?? ""}
        placeholder="地点"
        onChange={(event) => onDraftChange((current) => ({ ...current, location_name: event.target.value }))}
      />
    ),
    DEVICE: (
      <input
        className="lightbox-inline-input"
        value={draft?.device ?? ""}
        placeholder="设备"
        onChange={(event) => onDraftChange((current) => ({ ...current, device: event.target.value }))}
      />
    ),
    CITY: (
      <input
        className="lightbox-inline-input"
        value={draft?.city ?? ""}
        placeholder="城市"
        onChange={(event) => onDraftChange((current) => ({ ...current, city: event.target.value }))}
      />
    ),
    REGION: (
      <input
        className="lightbox-inline-input"
        value={draft?.region ?? ""}
        placeholder="地区"
        onChange={(event) => onDraftChange((current) => ({ ...current, region: event.target.value }))}
      />
    ),
    COUNTRY: (
      <input
        className="lightbox-inline-input"
        value={draft?.country ?? ""}
        placeholder="国家"
        onChange={(event) => onDraftChange((current) => ({ ...current, country: event.target.value }))}
      />
    ),
    LENS: (
      <input
        className="lightbox-inline-input"
        value={draft?.lens_model ?? ""}
        placeholder="镜头"
        onChange={(event) => onDraftChange((current) => ({ ...current, lens_model: event.target.value }))}
      />
    ),
    SETTINGS: (
      <div className="lightbox-settings-grid is-editing">
        <input
          className="lightbox-inline-input is-compact"
          value={draft?.focal_length ?? ""}
          placeholder="焦段"
          onChange={(event) => onDraftChange((current) => ({ ...current, focal_length: event.target.value }))}
        />
        <input
          className="lightbox-inline-input is-compact"
          value={draft?.aperture ?? ""}
          placeholder="光圈"
          onChange={(event) => onDraftChange((current) => ({ ...current, aperture: event.target.value }))}
        />
        <input
          className="lightbox-inline-input is-compact"
          value={draft?.exposure_time ?? ""}
          placeholder="快门"
          onChange={(event) => onDraftChange((current) => ({ ...current, exposure_time: event.target.value }))}
        />
        <input
          className="lightbox-inline-input is-compact"
          value={draft?.iso ?? ""}
          placeholder="ISO"
          onChange={(event) => onDraftChange((current) => ({ ...current, iso: event.target.value }))}
        />
      </div>
    ),
  };

  return (
    <>
      {infoItems.map((item) => (
        <div key={item.label} className={`lightbox-info-item ${item.isPath ? "is-path" : ""}`}>
          <span className="lightbox-info-label">{item.label}</span>
          {item.label === "SETTINGS" && !editing ? (
            <div className="lightbox-settings-grid">
              {settingsParts.map((part, index) => (
                <span key={`${item.label}-${index}`} className="lightbox-settings-value">
                  {part}
                </span>
              ))}
            </div>
          ) : editing && editableMap[item.label] ? (
            editableMap[item.label]
          ) : (
            <span className="lightbox-info-value">{item.value}</span>
          )}
        </div>
      ))}
    </>
  );
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

function ArrowRightIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </svg>
  );
}

function ChevronLeftIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="m15 6-6 6 6 6" />
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="m9 6 6 6-6 6" />
    </svg>
  );
}

function ChevronDownIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="m6 9 6 6 6-6" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 10.2v5.4" />
      <circle cx="12" cy="7.3" r="0.8" fill="currentColor" stroke="none" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m5 12.5 4.2 4.2L19 7.4" />
    </svg>
  );
}

function CloseXIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="m7 7 10 10" />
      <path d="M17 7 7 17" />
    </svg>
  );
}
