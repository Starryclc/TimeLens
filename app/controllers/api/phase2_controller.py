from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.timeline_service import timeline_service
from app.views.api.album_view import TimelineAlbumDetailRead, TimelineResponse


router = APIRouter(tags=["phase2"])


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(db: Session = Depends(get_db)) -> TimelineResponse:
    """返回按年月和地点组织的时间轴相册。"""
    return timeline_service.build_timeline(db)


@router.get("/timeline/albums/{album_key}")
def get_timeline_album(album_key: str, db: Session = Depends(get_db)) -> TimelineAlbumDetailRead:
    """返回单个时间线相册中的全部照片。"""
    album = timeline_service.get_timeline_album(db, album_key)
    if album is None:
        raise HTTPException(status_code=404, detail="Timeline album not found")
    return album


@router.get("/timeline/stories")
def get_timeline_stories() -> dict:
    """返回人生故事时间轴接口的占位数据。"""
    return {"items": [], "todo": "Phase 2 timeline story summary service"}


@router.get("/clusters")
def get_clusters() -> dict:
    """返回聚类列表接口的占位数据。"""
    return {"items": [], "todo": "Phase 2 photo clustering service"}


@router.get("/clusters/{cluster_id}")
def get_cluster(cluster_id: int) -> dict:
    """返回聚类详情接口的占位数据。"""
    return {"id": cluster_id, "todo": "Phase 2 cluster detail service"}


@router.get("/people")
def get_people() -> dict:
    """返回人物列表接口的占位数据。"""
    return {"items": [], "todo": "Phase 2 person aggregation service"}


@router.get("/people/{person_id}")
def get_person(person_id: int) -> dict:
    """返回人物详情接口的占位数据。"""
    return {"id": person_id, "todo": "Phase 2 person detail service"}


@router.get("/map/places")
def get_map_places() -> dict:
    """返回地图地点接口的占位数据。"""
    return {"items": [], "todo": "Phase 2 map browsing service"}


@router.get("/recommendations")
def get_recommendations() -> dict:
    """返回推荐接口的占位数据。"""
    return {"items": [], "todo": "Phase 2 recommendations service"}


@router.post("/analyze/faces")
def analyze_faces() -> dict:
    """返回人脸分析任务的占位状态。"""
    return {"status": "queued", "todo": "Phase 3 face analysis pipeline"}


@router.post("/analyze/clusters")
def analyze_clusters() -> dict:
    """返回聚类分析任务的占位状态。"""
    return {"status": "queued", "todo": "Phase 2/3 clustering pipeline"}


@router.post("/analyze/recommendations")
def analyze_recommendations() -> dict:
    """返回推荐分析任务的占位状态。"""
    return {"status": "queued", "todo": "Phase 3 recommendation pipeline"}


@router.post("/analyze/timeline")
def analyze_timeline() -> dict:
    """返回时间轴分析任务的占位状态。"""
    return {"status": "queued", "todo": "Phase 3 timeline generation pipeline"}
