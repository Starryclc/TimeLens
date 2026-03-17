import { Link } from "react-router-dom";

export function PlaceholderPage({ title, message }) {
  return (
    <section className="hero">
      <div className="hero-copy">
        <span className="eyebrow">Coming Next</span>
        <h1>{title}</h1>
        <p>{message}</p>
        <div className="hero-actions">
          <Link className="button" to="/gallery">
            先浏览照片
          </Link>
          <Link className="button ghost" to="/">
            返回首页
          </Link>
        </div>
      </div>
    </section>
  );
}
