from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from containers import Container
from common.auth import get_current_user, CurrentUser
from report.application.report_not_there_service import ReportNotThereService
from common.logger import logger

router = APIRouter(
    prefix="/reports/{report_id}/not-there",
    tags=["report-not-there"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/")
@inject
def mark_not_there(
    report_id: str,
    service: ReportNotThereService = Depends(
        Provide[Container.report_not_there_service]
    ),
    current: CurrentUser = Depends(get_current_user),
):
    logger.info(f"'이제 없어요' 클릭 uid={current.uid}, report={report_id}")
    return service.mark_not_there(report_id, current.uid)
