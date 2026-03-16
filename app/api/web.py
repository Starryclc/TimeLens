from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.memory_service import memory_service
from app.services.photo_service import photo_service


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    sections = memory_service.get_homepage_sections(db)
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request,
            "recent_photos": sections["recent_photos"],
            "random_photo": sections["random_photo"],
            "on_this_day": sections["on_this_day"],
        },
    )


@router.get("/gallery")
def gallery(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    location: str | None = None,
    device: str | None = None,
    tag: str | None = None,
    sort: str = "taken_desc",
    db: Session = Depends(get_db),
):
    photos = photo_service.list_photos(
        db,
        year=year,
        month=month,
        location=location,
        device=device,
        tag=tag,
        sort=sort,
    )
    return templates.TemplateResponse(
        request,
        "gallery.html",
        {
            "request": request,
            "photos": photos,
            "filters": {
                "year": year,
                "month": month,
                "location": location or "",
                "device": device or "",
                "tag": tag or "",
                "sort": sort,
            },
            "locations": photo_service.get_location_options(db),
            "devices": photo_service.get_device_options(db),
        },
    )


@router.get("/photos/{photo_id}")
def photo_detail(request: Request, photo_id: int, db: Session = Depends(get_db)):
    photo = photo_service.get_photo(db, photo_id)
    return templates.TemplateResponse(
        request,
        "photo_detail.html",
        {"request": request, "photo": photo},
        status_code=200 if photo else 404,
    )


@router.get("/memories/on-this-day")
def on_this_day_page(request: Request, db: Session = Depends(get_db)):
    photos = photo_service.get_on_this_day(db)
    grouped: dict[int, list] = {}
    for photo in photos:
        if photo.photo_taken_at is None:
            continue
        grouped.setdefault(photo.photo_taken_at.year, []).append(photo)

    ordered = sorted(grouped.items(), key=lambda item: item[0], reverse=True)
    return templates.TemplateResponse(
        request,
        "on_this_day.html",
        {"request": request, "groups": ordered},
    )


@router.get("/timeline")
def timeline_page(request: Request):
    return templates.TemplateResponse(
        request,
        "placeholder.html",
        {"request": request, "title": "时间轴", "message": "Phase 2 将在这里提供连续人生时间轴浏览。"},
    )


@router.get("/people")
def people_page(request: Request):
    return templates.TemplateResponse(
        request,
        "placeholder.html",
        {"request": request, "title": "人物相册", "message": "Phase 2 将在这里提供人物识别与聚合浏览。"},
    )


@router.get("/clusters")
def clusters_page(request: Request):
    return templates.TemplateResponse(
        request,
        "placeholder.html",
        {"request": request, "title": "智能聚类", "message": "Phase 2 将在这里提供事件与旅行聚类浏览。"},
    )


@router.get("/map")
def map_page(request: Request):
    return templates.TemplateResponse(
        request,
        "placeholder.html",
        {"request": request, "title": "人生地图", "message": "Phase 2 将在这里提供地图式回忆浏览。"},
    )


@router.get("/stories")
def stories_page(request: Request):
    return templates.TemplateResponse(
        request,
        "placeholder.html",
        {"request": request, "title": "人生时间线", "message": "Phase 2 将在这里组织人生故事节点。"},
    )


@router.get("/recommendations")
def recommendations_page(request: Request):
    return templates.TemplateResponse(
        request,
        "placeholder.html",
        {"request": request, "title": "AI 推荐", "message": "Phase 2/3 将在这里展示值得重温的回忆推荐。"},
    )
