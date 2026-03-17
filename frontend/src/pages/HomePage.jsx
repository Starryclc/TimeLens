import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PhotoCard } from "../components/PhotoCard";
import { apiGet } from "../lib/api";
import { formatDateTime, getPhotoLocation, thumbnailUrl } from "../lib/photos";
import { useApi } from "../lib/useApi";

export function HomePage() {
  const { data, loading, error } = useApi(
    async () => {
      const [recentPhotos, randomPhoto, onThisDay] = await Promise.all([
        apiGet("photos", { sort: "imported_desc" }),
        apiGet("photos/random"),
        apiGet("photos/on-this-day"),
      ]);
      return {
        recentPhotos: recentPhotos.slice(0, 12),
        randomPhoto,
        onThisDay: onThisDay.slice(0, 8),
      };
    },
    [],
  );

  if (loading) {
    return <div className="loading-panel">正在载入首页记忆入口...</div>;
  }

  if (error) {
    return (
      <EmptyState
        title="首页加载失败"
        description="前端已经启动，但暂时无法从后端读取首页数据。请确认后端服务正在运行。"
      />
    );
  }

  const { recentPhotos, randomPhoto, onThisDay } = data;

  return (
    <div className="page-stack">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Separated Frontend</span>
          <h1>
            照片浏览，
            <br />
            现在正式成为独立前端产品。
          </h1>
          <p>
            前后端分离后，TimeLens 的前端将专注于浏览体验、复杂交互和未来地图、时间轴、人物聚类等能力，
            后端则专注索引、分析、检索与媒体访问。
          </p>
          <div className="hero-actions">
            <Link className="button" to="/gallery">
              浏览全部照片
            </Link>
            <Link className="button ghost" to="/memories/on-this-day">
              打开那年今日
            </Link>
          </div>
        </div>
        <div className="memory-panel">
          <div className="memory-panel-card">
            <span className="mini-label">今日回看</span>
            <strong>{onThisDay.length} 张历史照片</strong>
            <p>跨年份同一天的照片，会在这里重新形成回忆入口。</p>
          </div>
          <div className="memory-panel-card">
            <span className="mini-label">最近导入</span>
            <strong>{recentPhotos.length} 张最近进入系统</strong>
            <p>你能在前端立刻看到最新扫描进来的照片，不再依赖服务端模板。</p>
          </div>
          <div className="memory-panel-card accent">
            <span className="mini-label">架构升级</span>
            <strong>FastAPI API + React Frontend</strong>
            <p>这一步为时间轴、地图、人物聚类和语义交互留出了更大的前端空间。</p>
          </div>
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Random Memory</span>
            <h2>随机照片</h2>
          </div>
        </div>
        {randomPhoto ? (
          <Link className="featured-card" to={`/photos/${randomPhoto.id}`}>
            {randomPhoto.thumbnail_path ? (
              <img
                src={thumbnailUrl(randomPhoto.thumbnail_path)}
                alt={randomPhoto.file_name}
                sizes="(max-width: 980px) 100vw, 40vw"
              />
            ) : (
              <div className="image-fallback image-fallback-large">No Preview</div>
            )}
            <div className="featured-copy">
              <span className="mini-label">随机回忆</span>
              <h3>{randomPhoto.file_name}</h3>
              <p>{formatDateTime(randomPhoto.photo_taken_at)}</p>
              <p>{getPhotoLocation(randomPhoto)}</p>
              <span className="inline-link">进入照片详情</span>
            </div>
          </Link>
        ) : (
          <EmptyState
            title="还没有照片"
            description="先用扫描命令导入照片，前端首页会自动开始长出回忆入口。"
          />
        )}
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <span className="eyebrow">On This Day</span>
            <h2>那年今日</h2>
          </div>
          <Link className="inline-link" to="/memories/on-this-day">
            查看全部
          </Link>
        </div>
        <div className="photo-grid compact-grid">
          {onThisDay.length > 0 ? (
            onThisDay.map((photo) => (
              <PhotoCard
                key={photo.id}
                photo={photo}
                compactLabel={photo.photo_taken_at ? new Date(photo.photo_taken_at).getFullYear() : "未知年份"}
              />
            ))
          ) : (
            <EmptyState
              title="今天还没有历史照片"
              description="当你导入更多照片后，这里会自动按日期重组值得回看的历史时刻。"
            />
          )}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Recently Imported</span>
            <h2>最近导入</h2>
          </div>
          <Link className="inline-link" to="/gallery?sort=imported_desc">
            按导入时间查看
          </Link>
        </div>
        <div className="photo-grid">
          {recentPhotos.map((photo) => (
            <PhotoCard key={photo.id} photo={photo} compactLabel="新进入记忆库" />
          ))}
        </div>
      </section>
    </div>
  );
}
