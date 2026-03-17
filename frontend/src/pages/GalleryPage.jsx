import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageIntro } from "../components/PageIntro";
import { PhotoCard } from "../components/PhotoCard";
import { apiGet } from "../lib/api";
import { useApi } from "../lib/useApi";

export function GalleryPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo(
    () => ({
      year: searchParams.get("year") || "",
      month: searchParams.get("month") || "",
      location: searchParams.get("location") || "",
      device: searchParams.get("device") || "",
      tag: searchParams.get("tag") || "",
      sort: searchParams.get("sort") || "taken_desc",
    }),
    [searchParams],
  );

  const { data, loading, error } = useApi(
    async () => {
      const [photos, locations, devices] = await Promise.all([
        apiGet("photos", filters),
        apiGet("locations"),
        apiGet("devices"),
      ]);
      return { photos, locations, devices };
    },
    [filters.year, filters.month, filters.location, filters.device, filters.tag, filters.sort],
  );

  function updateFilter(name, value) {
    const next = new URLSearchParams(searchParams);
    if (!value) {
      next.delete(name);
    } else {
      next.set(name, value);
    }
    setSearchParams(next);
  }

  function clearFilters() {
    setSearchParams({ sort: "taken_desc" });
  }

  if (loading) {
    return <div className="loading-panel">正在载入照片列表...</div>;
  }

  if (error || !data) {
    return (
      <EmptyState
        title="照片列表加载失败"
        description="请确认后端 API 已启动，并且浏览器可以访问 `/api/photos`。"
      />
    );
  }

  const { photos, locations, devices } = data;

  return (
    <div className="page-stack">
      <PageIntro
        eyebrow="Gallery"
        title="照片列表"
        description="按时间、地点、设备与标签筛选，把照片从文件夹重新整理成你的人生切片。"
        meta={`${photos.length} 张结果`}
      />

      <section className="filter-shell">
        <div className="filters">
          <label>
            <span>年份</span>
            <input
              type="number"
              value={filters.year}
              onChange={(event) => updateFilter("year", event.target.value)}
              placeholder="例如 2024"
            />
          </label>
          <label>
            <span>月份</span>
            <input
              type="number"
              min="1"
              max="12"
              value={filters.month}
              onChange={(event) => updateFilter("month", event.target.value)}
              placeholder="1-12"
            />
          </label>
          <label>
            <span>地点</span>
            <input
              list="location-options"
              value={filters.location}
              onChange={(event) => updateFilter("location", event.target.value)}
              placeholder="城市 / 地标 / 国家"
            />
            <datalist id="location-options">
              {locations.map((item) => (
                <option key={item} value={item} />
              ))}
            </datalist>
          </label>
          <label>
            <span>设备</span>
            <input
              list="device-options"
              value={filters.device}
              onChange={(event) => updateFilter("device", event.target.value)}
              placeholder="iPhone / Sony / Canon"
            />
            <datalist id="device-options">
              {devices.map((item) => (
                <option key={item} value={item} />
              ))}
            </datalist>
          </label>
          <label>
            <span>标签</span>
            <input
              value={filters.tag}
              onChange={(event) => updateFilter("tag", event.target.value)}
              placeholder="旅行 / 夜景 / 人像"
            />
          </label>
          <label>
            <span>排序</span>
            <select
              value={filters.sort}
              onChange={(event) => updateFilter("sort", event.target.value)}
            >
              <option value="taken_desc">按拍摄时间</option>
              <option value="imported_desc">按导入时间</option>
            </select>
          </label>
          <div className="filter-actions">
            <button type="button" onClick={clearFilters}>
              清空条件
            </button>
          </div>
        </div>
      </section>

      <div className="photo-grid">
        {photos.length > 0 ? (
          photos.map((photo) => <PhotoCard key={photo.id} photo={photo} />)
        ) : (
          <EmptyState
            title="当前筛选条件下没有照片"
            description="你可以放宽年份、地点或设备条件，重新找回这一段回忆。"
          />
        )}
      </div>
    </div>
  );
}
