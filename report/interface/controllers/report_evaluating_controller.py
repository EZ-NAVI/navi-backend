from fastapi import APIRouter, Body, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from containers import Container
from common.auth import get_current_user, CurrentUser
from report.application.report_evaluating_service import ReportEvaluatingService

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportEvaluateRequest(BaseModel):
    evaluation: str  # "good" | "normal" | "bad"


@router.post("/{report_id}/evaluate")
@inject
async def evaluate_report(
    report_id: str,
    req: ReportEvaluateRequest = Body(...),
    service: ReportEvaluatingService = Depends(
        Provide[Container.report_evaluating_service]
    ),
    current: CurrentUser = Depends(get_current_user),
):
    result = await service.evaluate_report(report_id, current.uid, req.evaluation)
    return {
        "message": f"이모지 평가가 {result['action']} 되었습니다.",
        "reportId": result["report_id"],
        "evaluation": result["evaluation"],
        "updatedAt": result["updated_at"],
    }
