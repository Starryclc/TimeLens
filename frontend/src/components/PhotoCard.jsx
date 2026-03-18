import { Link } from "react-router-dom";

import { formatDateTime, getPhotoLocation, getPhotoYear, thumbnailUrl } from "../lib/photos";

export function PhotoCard({ photo, compactLabel }) {
  return (
    <Link className="photo-card" to={`/photos/${photo.id}`}>
      {photo.thumbnail_path ? (
        <img
          src={thumbnailUrl(photo.thumbnail_path)}
          alt={photo.file_name}
          sizes="(max-width: 980px) 50vw, 280px"
        />
      ) : (
        <div className="image-fallback">No Preview</div>
      )}
      <div className="photo-meta">
        <span className="mini-label">{compactLabel || getPhotoYear(photo)}</span>
        <span>{formatDateTime(photo.photo_taken_at)}</span>
        <span>{getPhotoLocation(photo)}</span>
      </div>
    </Link>
  );
}
