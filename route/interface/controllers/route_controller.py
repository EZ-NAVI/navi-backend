from fastapi import APIRouter, Body, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import List, Dict, Optional
from route.application.route_service import RouteService
from common.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/routes", tags=["routes"])


class RoutePreviewRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float


class RouteCreateRequest(RoutePreviewRequest):
    duration: int
    path_data: List[Dict[str, float]]


class RouteResponse(BaseModel):
    route_id: Optional[str] = None
    path: List[Dict[str, float]]


class RouteEvaluationRequest(BaseModel):
    evaluation: float


# 경로 미리보기 (저장 안 함)
@router.post("/preview", response_model=RouteResponse)
@inject
def preview_route(
    req: RoutePreviewRequest = Body(...),
    service: RouteService = Depends(Provide["container.route_service"]),
):
    path = service.generate_safe_route(
        origin_lat=req.origin_lat,
        origin_lng=req.origin_lng,
        dest_lat=req.dest_lat,
        dest_lng=req.dest_lng,
    )
    return RouteResponse(path=path)


# 실제 이동 후 저장
@router.post("/", response_model=RouteResponse)
@inject
def save_route(
    req: RouteCreateRequest = Body(...),
    service: RouteService = Depends(Provide["container.route_service"]),
    current: CurrentUser = Depends(get_current_user),
):
    route = service.save_route_if_traveled(
        user_id=current.id,
        origin_lat=req.origin_lat,
        origin_lng=req.origin_lng,
        dest_lat=req.dest_lat,
        dest_lng=req.dest_lng,
        duration=req.duration,
        path_data=req.path_data,
    )
    return RouteResponse(route_id=route.route_id, path=route.path_data)


# 이동 후 평가 (별점 등록)
@router.post("/{route_id}/evaluate")
@inject
def evaluate_route(
    route_id: str,
    req: RouteEvaluationRequest = Body(...),
    service: RouteService = Depends(Provide["container.route_service"]),
    current: CurrentUser = Depends(get_current_user),
):
    route = service.evaluate_route(route_id, req.evaluation)
    if not route:
        return {"message": "Route not found"}
    return {"message": "Evaluation saved", "evaluation": route.evaluation}
