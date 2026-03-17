import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { GalleryPage } from "./pages/GalleryPage";
import { HomePage } from "./pages/HomePage";
import { OnThisDayPage } from "./pages/OnThisDayPage";
import { PhotoDetailPage } from "./pages/PhotoDetailPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/gallery" element={<GalleryPage />} />
        <Route path="/photos/:photoId" element={<PhotoDetailPage />} />
        <Route path="/memories/on-this-day" element={<OnThisDayPage />} />
        <Route
          path="/timeline"
          element={
            <PlaceholderPage
              title="时间轴"
              message="下一阶段会在这里把照片按连续的人生时间线组织起来。"
            />
          }
        />
        <Route
          path="/people"
          element={
            <PlaceholderPage
              title="人物相册"
              message="下一阶段会在这里展示人脸识别、人物聚合与人物记忆入口。"
            />
          }
        />
        <Route
          path="/clusters"
          element={
            <PlaceholderPage
              title="智能聚类"
              message="下一阶段会在这里按旅行、活动、事件等主题组织照片。"
            />
          }
        />
        <Route
          path="/map"
          element={
            <PlaceholderPage
              title="人生地图"
              message="下一阶段会在这里按国家、城市和地标展示你的照片分布。"
            />
          }
        />
        <Route
          path="/stories"
          element={
            <PlaceholderPage
              title="人生时间线"
              message="下一阶段会在这里把照片聚合成有标题、有摘要的人生故事节点。"
            />
          }
        />
        <Route
          path="/recommendations"
          element={
            <PlaceholderPage
              title="AI 推荐"
              message="下一阶段会在这里提供今日推荐、相似回忆和事件重温。"
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
}
