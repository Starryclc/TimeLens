import { Link, useLocation } from "react-router-dom";

const navigation = [
  { to: "/gallery", label: "照片" },
  { to: "/memories/on-this-day", label: "那年今日" },
  { to: "/timeline", label: "时间轴" },
  { to: "/map", label: "人生地图" },
  { to: "/people", label: "人物" },
  { to: "/recommendations", label: "推荐" },
];

export function AppLayout({ children }) {
  const location = useLocation();

  return (
    <div className="page-shell">
      <header className="site-header">
        <div className="brand">
          <Link to="/">TimeLens</Link>
          <p>前后端分离后的照片记忆系统前端，专注浏览体验与后续复杂交互能力。</p>
        </div>
        <nav className="site-nav" aria-label="Primary">
          {navigation.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={active ? "nav-link active" : "nav-link"}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>
      <main className="page-content">{children}</main>
    </div>
  );
}
