# TimeLens

TimeLens 是一个本地优先的“个人照片智能浏览器 / 记忆系统”项目。当前仓库已经完成 Phase 1 MVP 主链路，并为 Phase 2/3 的 AI 扩展预留了数据结构、服务接口和页面入口。

## 当前已实现

- 扫描指定目录中的 `jpg / jpeg / png` 照片
- 增量扫描：基于文件路径和修改时间避免重复处理
- 重复检测：基于文件 `SHA-256` hash 标记重复照片
- EXIF 解析：拍摄时间、设备、GPS、图片尺寸
- GPS 逆地理编码：默认支持可替换的 Nominatim 实现，失败时不会阻塞扫描
- 缩略图生成
- SQLite 持久化
- FastAPI REST API
- Jinja2 Web 页面
  - 首页
  - 照片列表页
  - 照片详情页
  - 那年今日
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
- Jinja2
- Pillow
- exifread
- httpx

## 项目结构

```text
app/
  api/                REST API 与页面路由
  core/               settings / logging
  db/                 数据库基类、会话、初始化
  models/             ORM 模型
  schemas/            API schema
  services/           扫描、EXIF、地理编码、缩略图、查询与扩展服务
  templates/          Jinja 页面
  static/             CSS / JS
  main.py             FastAPI 入口
  scan.py             CLI 扫描入口
scripts/
  init_db.py          初始化数据库
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

## 启动服务

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

启动后访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)。

## 扫描照片

```bash
source .venv/bin/activate
python -m app.scan /path/to/photos
```

也可以通过 API：

```bash
curl -X POST http://127.0.0.1:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"path":"/path/to/photos"}'
```

## 核心接口

- `GET /photos`
- `GET /photos/{id}`
- `GET /photos/random`
- `GET /photos/on-this-day`
- `POST /scan`
- `GET /locations`
- `GET /devices`

已预留但暂未实现完整能力的接口：

- `GET /timeline`
- `GET /timeline/stories`
- `GET /clusters`
- `GET /clusters/{id}`
- `GET /people`
- `GET /people/{id}`
- `GET /map/places`
- `GET /recommendations`
- `POST /analyze/faces`
- `POST /analyze/clusters`
- `POST /analyze/recommendations`
- `POST /analyze/timeline`

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

## 设计说明

- 本地优先：数据库、图片、缩略图全部默认保存在本地。
- 稳定优先：GPS 逆地理编码失败不会让扫描失败。
- 可扩展优先：AI 能力通过抽象接口隔离，未来可替换为本地模型。
- 不过度设计：MVP 采用同步扫描和 SQLite，后续可平滑迁移到异步任务队列。

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
