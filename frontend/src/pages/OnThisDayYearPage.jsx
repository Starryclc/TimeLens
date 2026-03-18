import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { apiGet } from "../lib/api";
import { formatDateTime, getPhotoDeviceText, getPhotoLocation, getPhotoLocationText, thumbnailUrl } from "../lib/photos";
import { useApi } from "../lib/useApi";

export function OnThisDayYearPage() {
  const { year } = useParams();
  const { data, loading, error } = useApi(
    async () => {
      const photos = await apiGet("photos/on-this-day");
      return photos.filter((photo) => photo.photo_taken_at && String(new Date(photo.photo_taken_at).getFullYear()) === year);
    },
    [year],
  );

  if (loading) {
    return <div className="loading-panel">正在载入这一天的照片...</div>;
  }

  if (error) {
    return <EmptyState title="载入失败" description="请稍后再试。" />;
  }

  if (!data || data.length === 0) {
    return <EmptyState title="没有找到照片" description="这一年的这一天暂时没有照片。" />;
  }

  return (
    <section className="content-section">
      <div className="section-header">
        <div>
          <span className="section-kicker">那年今日</span>
          <h2>{year}</h2>
        </div>
        <Link className="section-link" to="/">
          返回首页
        </Link>
      </div>

      <div className="simple-photo-grid">
        {data.map((photo) => (
          <article key={photo.id} className="simple-photo-card">
            {photo.thumbnail_path ? (
              <img src={thumbnailUrl(photo.thumbnail_path)} alt={getPhotoLocation(photo)} />
            ) : (
              <div className="image-fallback">No Preview</div>
            )}
            <div className="simple-photo-meta">
              <strong>{getPhotoLocationText(photo) || "未记录地点"}</strong>
              <span>{formatDateTime(photo.photo_taken_at)}</span>
              {getPhotoDeviceText(photo) ? <span>{getPhotoDeviceText(photo)}</span> : null}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
