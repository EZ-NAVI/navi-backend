from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import List
from containers import Container
from report.application.report_comment_service import ReportCommentService
from report.domain.report_comment import ReportComment
from common.auth import get_current_user, CurrentUser
from common.logger import logger


router = APIRouter(prefix="/reports/{report_id}/comments", tags=["report-comments"])


class CommentCreateRequest(BaseModel):
    content: str


@router.post("/", response_model=ReportComment)
@inject
def add_comment(
    report_id: str,
    req: CommentCreateRequest,
    service: ReportCommentService = Depends(Provide[Container.report_comment_service]),
    current: CurrentUser = Depends(get_current_user),
):
    logger.info(f"댓글 생성 요청 uid={current.id}")
    return service.add_comment(report_id, current.id, req.content)


@router.get("/", response_model=List[ReportComment])
@inject
def list_comments(
    report_id: str,
    service: ReportCommentService = Depends(Provide[Container.report_comment_service]),
):
    return service.get_comments(report_id)


@router.delete("/{comment_id}")
@inject
def delete_comment(
    comment_id: str,
    service: ReportCommentService = Depends(Provide[Container.report_comment_service]),
):
    service.delete_comment(comment_id)
    return {"message": "Comment deleted"}
