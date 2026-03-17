export function PageIntro({ eyebrow, title, description, action, meta }) {
  return (
    <section className="page-intro">
      <div>
        {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      <div className="page-intro-side">
        {meta ? <div className="stat-chip">{meta}</div> : null}
        {action}
      </div>
    </section>
  );
}
