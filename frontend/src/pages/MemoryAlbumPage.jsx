import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageIntro } from "../components/PageIntro";
import { PhotoCard } from "../components/PhotoCard";
import { apiGet } from "../lib/api";
import { buildMemoryAlbums, groupAlbumPhotosByDate } from "../lib/memories";
import { useApi } from "../lib/useApi";

export function MemoryAlbumPage() {
  const { albumKey } = useParams();
  const [size, setSize] = useState(2);
  const { data, loading, error } = useApi(async () => apiGet("photos"), []);

  const album = useMemo(() => {
    if (!data) {
      return null;
    }
    return buildMemoryAlbums(data).find((item) => item.key === albumKey) || null;
  }, [albumKey, data]);

  if (loading) {
    return <div className="loading-panel">正在整理相册时间线...</div>;
  }

  if (error || !album) {
    return (
      <EmptyState
        title="相册不存在"
        description="这个回忆相册可能不存在，或者当前还没有足够的照片生成它。"
      />
    );
  }

  const groups = groupAlbumPhotosByDate(album.photos);
  const gridClassName =
    size === 1
      ? "album-photo-grid compact"
      : size === 2
        ? "album-photo-grid"
        : "album-photo-grid spacious";

  return (
    <div className="page-stack">
      <PageIntro
        eyebrow={album.type === "day" ? "On This Day Album" : "Month Album"}
        title={album.title}
        description={`${album.subtitle}，默认按时间线排序。`}
        action={
          <Link className="button ghost" to="/memories">
            返回回忆页面
          </Link>
        }
      />

      <section className="dashboard-panel album-controls">
        <div>
          <span className="mini-label">图片大小</span>
          <strong>{size === 1 ? "紧凑" : size === 2 ? "标准" : "宽松"}</strong>
        </div>
        <input
          className="size-slider"
          type="range"
          min="1"
          max="3"
          step="1"
          value={size}
          onChange={(event) => setSize(Number(event.target.value))}
          aria-label="调整图片大小"
        />
      </section>

      {groups.map(([date, photos]) => (
        <section key={date} className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Timeline</span>
              <h2>{date}</h2>
            </div>
            <span className="stat-chip">{photos.length} 张</span>
          </div>
          <div className={gridClassName}>
            {photos.map((photo) => (
              <PhotoCard key={photo.id} photo={photo} compactLabel={date} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
