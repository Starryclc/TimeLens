import { EmptyState } from "../components/EmptyState";
import { PageIntro } from "../components/PageIntro";
import { PhotoCard } from "../components/PhotoCard";
import { apiGet } from "../lib/api";
import { groupOnThisDay } from "../lib/photos";
import { useApi } from "../lib/useApi";

export function OnThisDayPage() {
  const { data, loading, error } = useApi(() => apiGet("photos/on-this-day"), []);

  if (loading) {
    return <div className="loading-panel">正在载入那年今日...</div>;
  }

  if (error || !data) {
    return (
      <EmptyState
        title="那年今日加载失败"
        description="请确认后端服务已经启动，并且 `/api/photos/on-this-day` 可以正常访问。"
      />
    );
  }

  const groups = groupOnThisDay(data);

  return (
    <div className="page-stack">
      <PageIntro
        eyebrow="On This Day"
        title="那年今日"
        description="把不同年份同一天拍下的照片重新拼接，让时间在同一个页面里重叠出现。"
      />

      {groups.length > 0 ? (
        groups.map(([year, photos]) => (
          <section key={year} className="year-group">
            <div className="section-heading year-heading">
              <div>
                <span className="eyebrow">Year {year}</span>
                <h2>{year}</h2>
              </div>
              <div className="stat-chip">{photos.length} 张照片</div>
            </div>
            <div className="photo-grid">
              {photos.map((photo) => (
                <PhotoCard key={photo.id} photo={photo} compactLabel={photo.photo_taken_at} />
              ))}
            </div>
          </section>
        ))
      ) : (
        <EmptyState
          title="今天还没有可展示的历史照片"
          description="等你继续导入照片后，这里会自动按同一天、跨年份形成回看入口。"
        />
      )}
    </div>
  );
}
