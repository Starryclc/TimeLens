# TimeLens

TimeLens 是一个本地优先的“个人照片智能浏览器 / 记忆系统”项目。当前仓库已经整理为更适合前后端分离演进的后端 API 结构，后端采用 MVC 风格分层：`controllers` 负责 HTTP 接口，`models` 负责数据模型，`views` 负责 API 响应视图，`services` 承载业务逻辑。

## 当前已实现

- 扫描指定目录中的 `jpg / jpeg / png` 照片
- 增量扫描：基于文件路径和修改时间避免重复处理
- 重复检测：基于文件 `SHA-256` hash 标记重复照片
- EXIF 解析：拍摄时间、设备、GPS、图片尺寸
- GPS 逆地理编码：默认支持可替换的 Nominatim 实现，失败时不会阻塞扫描
- 缩略图生成
- SQLite 持久化
- FastAPI REST API 后端
- React + Vite 独立前端
- Phase 2 预留
  - 时间轴
  - 人物
  - 聚类
  - 人生地图
  - AI 推荐

## 技术栈

- Python 3.9.6
- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- React
- Vite
- Pillow
- exifread
- httpx

## 项目结构

```text
app/
  controllers/        MVC Controller：API 路由与请求分发
  core/               settings / logging
  db/                 数据库基类、会话、初始化
  models/             MVC Model：ORM 模型
  views/              MVC View：API 响应模型
  services/           业务服务层：扫描、EXIF、地理编码、缩略图、查询与扩展服务
  main.py             FastAPI API 入口
  scan.py             CLI 扫描入口
frontend/
  src/                React 前端源码
  package.json        前端依赖与脚本
scripts/
  init_db.py          初始化数据库
  dev.sh              启动后端
  dev-frontend.sh     启动前端
tests/                基础测试
data/
  db/                 SQLite 数据库
  thumbnails/         缩略图
  cache/              预留缓存目录
```

## 安装

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 初始化数据库

```bash
source .venv/bin/activate
python scripts/init_db.py
```

## 启动后端

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

也可以使用更顺手的项目入口：

```bash
source .venv/bin/activate
python -m app.main
```

或者：

```bash
./scripts/dev.sh
```

后端启动后访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)，默认返回 API 模式说明，核心接口统一挂载在 `/api/*` 下。

## 启动前端

```bash
./scripts/dev-frontend.sh
```

或者：

```bash
cd frontend
npm run dev
```

前端默认运行在 [http://127.0.0.1:5173](http://127.0.0.1:5173)，默认会请求 `http://127.0.0.1:8000/api`，可以在 [frontend/.env.example](/Users/xy/Documents/Code/TimeLens/frontend/.env.example) 的同名 `.env` 中调整。

## 扫描照片

```bash
source .venv/bin/activate
python -m app.scan /path/to/photos
```

也可以通过 API：

```bash
curl -X POST http://127.0.0.1:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"path":"/path/to/photos"}'
```

## 核心接口

- `GET /api/photos`
- `GET /api/photos/{id}`
- `GET /api/photos/random`
- `GET /api/photos/on-this-day`
- `POST /api/scan`
- `GET /api/locations`
- `GET /api/devices`
- `GET /api/media/photos/{id}`

已预留但暂未实现完整能力的接口：

- `GET /api/timeline`
- `GET /api/timeline/stories`
- `GET /api/clusters`
- `GET /api/clusters/{id}`
- `GET /api/people`
- `GET /api/people/{id}`
- `GET /api/map/places`
- `GET /api/recommendations`
- `POST /api/analyze/faces`
- `POST /api/analyze/clusters`
- `POST /api/analyze/recommendations`
- `POST /api/analyze/timeline`

## 配置说明

主要配置来自 `.env`：

- `TIMELENS_DATABASE_URL`
- `TIMELENS_DATA_DIR`
- `TIMELENS_THUMBNAIL_DIR`
- `TIMELENS_DEFAULT_SCAN_DIR`
- `TIMELENS_GEOCODER_ENABLED`
- `TIMELENS_GEOCODER_PROVIDER`
- `TIMELENS_GEOCODER_USER_AGENT`
- `TIMELENS_GEOCODER_TIMEOUT_SECONDS`
- `TIMELENS_FRONTEND_DEV_URL`

## 设计说明

- 本地优先：数据库、图片、缩略图全部默认保存在本地。
- 稳定优先：GPS 逆地理编码失败不会让扫描失败。
- 可扩展优先：AI 能力通过抽象接口隔离，未来可替换为本地模型。
- 前后端分离：后端统一输出 `/api/*`，前端独立负责路由、页面和交互。
- MVC 分层：Controller 处理 HTTP，Model 管理数据结构，View 管理 API 响应，Service 承担业务编排。
- 不过度设计：数据层仍然保持 SQLite + 同步扫描，后续可平滑迁移到异步任务队列。

## 路线图

### Phase 1

- 扫描、EXIF、GPS 地点解析、缩略图
- 首页 / 列表 / 详情 / 那年今日
- 增量扫描
- 重复检测

### Phase 2

- 规则版时间轴
- 规则版事件聚类
- 人物、地图、推荐页面与 API 实装
- `PlaceSummary`、`TimelineStory` 聚合任务

### Phase 3

- 本地视觉模型接入
- 无 GPS 地点猜测
- AI 标签与描述
- 人脸检测与聚类
- 语义搜索与 embedding

### Phase 4

- 人生地图
- 人生时间线
- 旅行 / 事件 / 人物相册
- AI 回忆推荐系统
