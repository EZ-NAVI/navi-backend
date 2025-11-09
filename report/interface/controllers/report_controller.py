from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from containers import Container
from typing import List
from aws import s3_client
from config import get_settings
from datetime import datetime
from report.application.report_service import ReportService
from report.domain.report import Report
from common.auth import get_current_user, CurrentUser
from common.logger import logger

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)],  # 모든 API 인증 필요
)

settings = get_settings()


class ReportCreateRequest(BaseModel):
    location_lat: float
    location_lng: float
    image_url: str | None = None
    category: str | None = None
    description: str | None = None


class PresignedResponse(BaseModel):
    upload_url: str
    file_url: str


class ReportUpdateRequest(BaseModel):
    image_url: str | None = None
    category: str | None = None
    description: str | None = None


@router.post("/", response_model=Report)
@inject
async def create_report(
    req: ReportCreateRequest = Body(...),
    service: ReportService = Depends(Provide[Container.report_service]),
    current: CurrentUser = Depends(get_current_user),
):
    logger.info(f"신고 생성 요청 uid={current.uid}")
    report = await service.create_report(
        reporter_id=current.uid,
        reporter_type=current.user_type,
        location_lat=req.location_lat,
        location_lng=req.location_lng,
        image_url=req.image_url,
        category=req.category,
        description=req.description,
    )
    return report


@router.post("/{report_id}/review")
@inject
async def review_report(
    report_id: str,
    action: str = Body(
        ..., embed=True, description="승인 또는 반려 ('approve' or 'reject')"
    ),
    service: ReportService = Depends(Provide[Container.report_service]),
    current: CurrentUser = Depends(get_current_user),
):
    # 보호자 권한 확인
    if current.user_type != "parent":
        raise HTTPException(status_code=403, detail="보호자 계정만 접근 가능합니다.")

    updated_report = await service.review_report(report_id, current.uid, action)
    if not updated_report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "message": f"Report {action} 처리 완료",
        "report_id": updated_report.report_id,
        "status": updated_report.status,
    }


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
    current: CurrentUser = Depends(get_current_user),
):
    report = service.get_report(report_id, current.uid if current else None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/presigned-url", response_model=PresignedResponse, dependencies=[])
def get_presigned_url(
    file_name: str = Query(..., description="파일 이름 (예: photo.jpg)"),
    file_type: str = Query(..., description="MIME 타입 (예: image/jpeg)"),
):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        key = f"reports/{timestamp}_{file_name}"

        upload_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.aws_s3_bucket_name,
                "Key": key,
                "ContentType": file_type,
            },
            ExpiresIn=3600,
        )

        file_url = f"https://{settings.aws_s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"

        return {"upload_url": upload_url, "file_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest-by-cluster", response_model=List[Report])
@inject
def get_latest_reports_by_cluster(
    service: ReportService = Depends(Provide[Container.report_service]),
):
    """
    클러스터별로 최신 제보 1개씩만 반환
    """
    return service.get_latest_reports_by_cluster()


@router.get("/filter", response_model=List[Report])
@inject
def filter_reports(
    cluster_id: str = Query(..., description="클러스터 ID"),
    category: str | None = Query(None, description="카테고리 (선택)"),
    service: ReportService = Depends(Provide[Container.report_service]),
):
    """
    특정 클러스터 내 제보 리스트 조회
    - cluster_id는 필수
    - category를 지정하면 필터링
    - total_count 필드로 해당 클러스터 내 제보 총 개수 반환
    """
    return service.get_reports_by_cluster_and_category(cluster_id, category)


@router.patch("/{report_id}")
@inject
async def update_report(
    report_id: str = Path(...),
    req: ReportUpdateRequest = Body(...),
    service: ReportService = Depends(Provide[Container.report_service]),
    current: CurrentUser = Depends(get_current_user),
):
    updated = await service.update_report(
        report_id=report_id,
        requester_id=current.uid,
        image_url=req.image_url,
        category=req.category,
        description=req.description,
    )
    return updated


@router.delete("/{report_id}")
@inject
async def delete_report(
    report_id: str = Path(...),
    service: ReportService = Depends(Provide[Container.report_service]),
    current: CurrentUser = Depends(get_current_user),
):
    result = await service.delete_report(report_id=report_id, requester_id=current.uid)
    return result
