import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { apiGet } from "../lib/api";
import {
  formatDateTime,
  getPhotoDeviceText,
  getPhotoLocation,
  getPhotoLocationText,
  getPhotoParameterText,
  thumbnailUrl,
} from "../lib/photos";
import { useApi } from "../lib/useApi";

export function HomePage() {
  const { data, loading, error } = useApi(
    async () => {
      const [randomPhoto, onThisDayPhotos] = await Promise.all([
        apiGet("photos/random", { exclude_on_this_day: true }),
        apiGet("photos/on-this-day"),
      ]);
      return { randomPhoto, onThisDayPhotos };
    },
    [],
  );

  if (loading) {
    return <div className="loading-panel">正在载入首页...</div>;
  }

  if (error || !data) {
    return (
      <EmptyState
        title="首页加载失败"
        description="请确认随机照片和那年今日接口可正常访问。"
      />
    );
  }

  const { randomPhoto, onThisDayPhotos } = data;
  const locationText = randomPhoto ? getPhotoLocationText(randomPhoto) : "";
  const deviceText = randomPhoto ? getPhotoDeviceText(randomPhoto) : "";
  const parameterText = randomPhoto ? getPhotoParameterText(randomPhoto) : "";

  return (
    <div className="page-shell-simple">
      {randomPhoto ? (
        <section className="random-photo-section">
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
              <div className="random-photo-info-column">
                {randomPhoto.photo_taken_at ? (
                  <div className="random-photo-info-block">
                    <span className="random-photo-label">时间</span>
                    <strong>{formatDateTime(randomPhoto.photo_taken_at)}</strong>
                  </div>
                ) : null}
                {locationText ? (
                  <div className="random-photo-info-block">
                    <span className="random-photo-label">地点</span>
                    <strong>{locationText}</strong>
                  </div>
                ) : null}
              </div>

              <div className="random-photo-info-column align-end">
                {deviceText ? (
                  <div className="random-photo-info-block">
                    <span className="random-photo-label">设备</span>
                    <strong>{deviceText}</strong>
                  </div>
                ) : null}
                {parameterText ? (
                  <div className="random-photo-info-block">
                    <span className="random-photo-label">参数</span>
                    <strong>{parameterText}</strong>
                  </div>
                ) : null}
              </div>
            </div>

            <div className="random-photo-actions">
              <Link className="app-link-button" to={`/photos/${randomPhoto.id}`}>
                查看照片
              </Link>
              <Link className="app-link-button secondary" to="/photos">
                进入时间线
              </Link>
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
