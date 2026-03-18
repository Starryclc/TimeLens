import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageIntro } from "../components/PageIntro";
import { apiGet } from "../lib/api";
import {
  formatDateTime,
  getPhotoDevice,
  getPhotoLocation,
  originalPhotoUrl,
} from "../lib/photos";
import { useApi } from "../lib/useApi";

export function PhotoDetailPage() {
  const { photoId } = useParams();
  const { data: photo, loading, error } = useApi(() => apiGet(`photos/${photoId}`), [photoId]);

  if (loading) {
    return <div className="loading-panel">正在载入照片详情...</div>;
  }

  if (error || !photo) {
    return (
      <EmptyState
        title="照片不存在"
        description="这张照片可能已被删除，或者当前前端无法从后端读取到对应记录。"
      />
    );
  }

  return (
    <div className="page-stack">
      <PageIntro
        eyebrow="Photo Detail"
        title="照片详情"
        description="查看这张照片被系统整理出的时间、地点、设备与元数据线索。"
        action={
          <Link className="button ghost" to="/photos">
            返回时间线
          </Link>
        }
      />

      <article className="detail-layout">
        <section className="detail-image">
          <img src={originalPhotoUrl(photo.id)} alt={photo.file_name} sizes="100vw" />
        </section>
        <section className="detail-panel">
          <div className="detail-hero-meta">
            <span className="pill">{getPhotoLocation(photo)}</span>
            <span className="pill">{getPhotoDevice(photo)}</span>
            <span className="pill">{formatDateTime(photo.photo_taken_at)}</span>
          </div>

          <dl className="detail-list">
            <div>
              <dt>拍摄时间</dt>
              <dd>{formatDateTime(photo.photo_taken_at)}</dd>
            </div>
            <div>
              <dt>导入时间</dt>
              <dd>{formatDateTime(photo.imported_at)}</dd>
            </div>
            <div>
              <dt>地点</dt>
              <dd>{getPhotoLocation(photo)}</dd>
            </div>
            <div>
              <dt>设备</dt>
              <dd>{getPhotoDevice(photo)}</dd>
            </div>
            <div>
              <dt>尺寸</dt>
              <dd>
                {photo.width || "-"} × {photo.height || "-"}
              </dd>
            </div>
            <div>
              <dt>文件大小</dt>
              <dd>{photo.file_size} bytes</dd>
            </div>
            <div>
              <dt>文件路径</dt>
              <dd className="path">{photo.file_path}</dd>
            </div>
            <div>
              <dt>状态</dt>
              <dd>{photo.status}</dd>
            </div>
            <div>
              <dt>重复照片</dt>
              <dd>{photo.is_duplicate ? "是" : "否"}</dd>
            </div>
          </dl>

          <section className="detail-section">
            <div className="detail-section-heading">
              <h2>标签</h2>
              <span className="mini-label">AI / 手工 / 规则</span>
            </div>
            <div className="tag-list">
              {photo.tags?.length ? (
                photo.tags.map((tag) => (
                  <span key={`${photo.id}-${tag.id}`} className="tag">
                    {tag.tag}
                  </span>
                ))
              ) : (
                <p className="empty">暂时没有标签。</p>
              )}
            </div>
          </section>

          <section className="detail-section">
            <div className="detail-section-heading">
              <h2>EXIF 摘要</h2>
              <span className="mini-label">相机元数据</span>
            </div>
            <p>{photo.exif_summary || "暂无 EXIF 摘要"}</p>
          </section>

          <section className="detail-section">
            <div className="detail-section-heading">
              <h2>AI 描述</h2>
              <span className="mini-label">Phase 3 预留</span>
            </div>
            <p>{photo.ai_description || "后续接入本地视觉模型后，这里会出现图片描述与场景理解。"}</p>
          </section>
        </section>
      </article>
    </div>
  );
}
