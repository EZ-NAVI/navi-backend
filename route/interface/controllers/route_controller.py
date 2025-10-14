from fastapi import APIRouter, Body, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from route.application.route_service import RouteService
from common.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/routes", tags=["routes"])


class RouteCreateRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    duration: int


@router.post("/")
@inject
def create_route(
    req: RouteCreateRequest = Body(...),
    service: RouteService = Depends(Provide["container.route_service"]),
    current: CurrentUser = Depends(get_current_user),
):
    route = service.create_route(
        user_id=current.id,
        origin_lat=req.origin_lat,
        origin_lng=req.origin_lng,
        dest_lat=req.dest_lat,
        dest_lng=req.dest_lng,
        duration=req.duration,
    )
    return route
