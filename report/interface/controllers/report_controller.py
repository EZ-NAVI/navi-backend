from fastapi import APIRouter, Body, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import List
from containers import Container
from report.application.report_service import ReportService
from report.domain.report import Report
from common.auth import get_current_user, CurrentUser
from common.logger import logger

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreateRequest(BaseModel):
    location_lat: float
    location_lng: float
    image_url: str | None = None
    category: str | None = None
    description: str | None = None


@router.post("/", response_model=Report)
@inject
def create_report(
    req: ReportCreateRequest = Body(...),
    service: ReportService = Depends(Provide[Container.report_service]),
    current: CurrentUser = Depends(get_current_user),
):
    logger.info(f"신고 생성 요청 uid={current.id}")
    report = service.create_report(
        reporter_id=current.id,
        reporter_type=current.user_type,
        location_lat=req.location_lat,
        location_lng=req.location_lng,
        image_url=req.image_url,
        category=req.category,
        description=req.description,
    )
    return report


@router.get("/", response_model=List[Report])
@inject
def list_reports(
    service: ReportService = Depends(Provide[Container.report_service]),
):
    return service.list_reports()


@router.get("/{report_id}", response_model=Report)
@inject
def get_report(
    report_id: str,
    service: ReportService = Depends(Provide[Container.report_service]),
):
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
