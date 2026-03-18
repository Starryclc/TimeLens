import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { AlbumsPage } from "./pages/AlbumsPage";
import { HomePage } from "./pages/HomePage";
import { MePage } from "./pages/MePage";
import { OnThisDayYearPage } from "./pages/OnThisDayYearPage";
import { PhotoDetailPage } from "./pages/PhotoDetailPage";
import { TimelinePage } from "./pages/TimelinePage";

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/on-this-day/:year" element={<OnThisDayYearPage />} />
        <Route path="/photos" element={<TimelinePage />} />
        <Route path="/photos/:photoId" element={<PhotoDetailPage />} />
        <Route path="/albums" element={<AlbumsPage />} />
        <Route path="/me" element={<MePage />} />
        <Route path="/gallery" element={<Navigate to="/photos" replace />} />
        <Route path="/timeline" element={<Navigate to="/photos" replace />} />
        <Route path="/memories" element={<Navigate to="/" replace />} />
        <Route path="/memories/*" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
}
