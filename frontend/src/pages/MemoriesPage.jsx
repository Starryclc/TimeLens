import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageIntro } from "../components/PageIntro";
import { apiGet } from "../lib/api";
import {
  formatDateTime,
  getPhotoDevice,
  getPhotoLocation,
  thumbnailUrl,
} from "../lib/photos";

function MemoryPhotoPanel({ title, photo, actions }) {
  if (!photo) {
    return (
      <div className="dashboard-panel">
        <h3>{title}</h3>
        <EmptyState title="暂无照片" description="当前接口没有返回可展示的照片。" />
      </div>
    );
  }

  return (
    <div className="dashboard-panel">
      <h3>{title}</h3>
      {photo.thumbnail_path ? (
        <img className="detail-hero-image" src={thumbnailUrl(photo.thumbnail_path)} alt={photo.file_name} />
      ) : (
        <div className="image-fallback image-fallback-large">No Preview</div>
      )}
      <div className="detail-meta-list">
        <div>
          <span>拍摄时间</span>
          <strong>{formatDateTime(photo.photo_taken_at)}</strong>
        </div>
        <div>
          <span>地点</span>
          <strong>{getPhotoLocation(photo)}</strong>
        </div>
        <div>
          <span>设备</span>
          <strong>{getPhotoDevice(photo)}</strong>
        </div>
      </div>
      <div className="filter-actions">
        {actions}
        <Link className="inline-link" to={`/photos/${photo.id}`}>
          查看详情
        </Link>
      </div>
    </div>
  );
}

export function MemoriesPage() {
  const [randomPhoto, setRandomPhoto] = useState(null);
  const [onThisDayPhotos, setOnThisDayPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadMemories() {
    setLoading(true);
    setError(null);
    try {
      const [randomResult, onThisDayResult] = await Promise.all([
        apiGet("photos/random", { exclude_on_this_day: true }),
        apiGet("photos/on-this-day"),
      ]);
      setRandomPhoto(randomResult);
      setOnThisDayPhotos(onThisDayResult);
    } catch (loadError) {
      setError(loadError);
    } finally {
      setLoading(false);
    }
  }

  async function refreshRandomPhoto() {
    try {
      const nextPhoto = await apiGet("photos/random", { exclude_on_this_day: true });
      setRandomPhoto(nextPhoto);
    } catch (loadError) {
      setError(loadError);
    }
  }

  useEffect(() => {
    loadMemories();
  }, []);

  if (loading) {
    return <div className="loading-panel">正在载入回忆相关接口...</div>;
  }

  if (error) {
    return (
      <EmptyState
        title="回忆接口加载失败"
        description="请确认 `/api/photos/random` 和 `/api/photos/on-this-day` 可访问。"
      />
    );
  }

  return (
    <div className="page-stack">
      <PageIntro
        eyebrow="Memories"
        title="回忆能力测试"
        description="这里先用最简单的前端把随机照片和那年今日接口接起来，方便我们验证功能。"
        meta={`那年今日 ${onThisDayPhotos.length} 张`}
      />

      <MemoryPhotoPanel
        title="随机照片展示"
        photo={randomPhoto}
        actions={
          <button type="button" onClick={refreshRandomPhoto}>
            换一张
          </button>
        }
      />

      <section className="dashboard-panel">
        <h3>那年今日</h3>
        {onThisDayPhotos.length > 0 ? (
          <div className="photo-grid">
            {onThisDayPhotos.map((photo) => (
              <Link key={photo.id} className="photo-card" to={`/photos/${photo.id}`}>
                {photo.thumbnail_path ? (
                  <img src={thumbnailUrl(photo.thumbnail_path)} alt={photo.file_name} />
                ) : (
                  <div className="image-fallback">No Preview</div>
                )}
                <div className="photo-card-copy">
                  <span className="mini-label">{formatDateTime(photo.photo_taken_at)}</span>
                  <strong>{getPhotoLocation(photo)}</strong>
                  <p>{getPhotoDevice(photo)}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            title="今天没有历史照片"
            description="导入更多往年照片后，这里会自动出现当天对应的历史照片。"
          />
        )}
      </section>
    </div>
  );
}
