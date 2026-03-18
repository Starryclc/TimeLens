import { Link, NavLink } from "react-router-dom";

const navigationItems = [
  { to: "/", label: "首页", icon: HomeIcon },
  { to: "/photos", label: "照片", icon: PhotoIcon },
  { to: "/albums", label: "相册", icon: AlbumIcon },
  { to: "/me", label: "我的", icon: ProfileIcon },
];

function navigationClassName({ isActive }) {
  return isActive ? "app-nav-link is-active" : "app-nav-link";
}

export function AppLayout({ children }) {
  return (
    <div className="app-frame">
      <header className="app-topbar">
        <div className="app-topbar-inner">
          <Link className="app-brand" to="/">
            TimeLens
          </Link>
          <nav className="app-nav desktop-only" aria-label="Primary">
            {navigationItems.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.to === "/"} className={navigationClassName}>
                <span className="app-nav-icon-shell" aria-hidden="true">
                  <span className="app-nav-icon">
                    <item.icon />
                  </span>
                </span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="app-main">{children}</main>

      <nav className="app-bottom-nav mobile-only" aria-label="Mobile Primary">
        {navigationItems.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === "/"} className={navigationClassName}>
            <span className="app-nav-icon-shell" aria-hidden="true">
              <span className="app-nav-icon">
                <item.icon />
              </span>
            </span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

function HomeIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3.5 10.5 12 4l8.5 6.5" />
      <path d="M6 9.5V20h12V9.5" />
      <path d="M9.5 20v-5.5h5V20" />
    </svg>
  );
}

function PhotoIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3.5" y="5" width="17" height="14.5" rx="4" />
      <path d="M8 5.5 9.2 3.8h5.6L16 5.5" />
      <circle cx="12" cy="12.2" r="3.2" />
    </svg>
  );
}

function AlbumIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 6.5h10.5a3.5 3.5 0 0 1 3.5 3.5v7a3.5 3.5 0 0 1-3.5 3.5H8.5A3.5 3.5 0 0 1 5 17V6.5Z" />
      <path d="M5 8.2H4.8A2.8 2.8 0 0 0 2 11v5.2A2.8 2.8 0 0 0 4.8 19H5" />
      <path d="M8.2 10.2h7.6" />
      <path d="M8.2 13.2h5.1" />
    </svg>
  );
}

function ProfileIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8.2" r="3.6" />
      <path d="M5.2 19.2a6.8 6.8 0 0 1 13.6 0" />
    </svg>
  );
}
