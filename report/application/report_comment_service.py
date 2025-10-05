from datetime import datetime
import ulid
from typing import List
from report.domain.report_comment import ReportComment
from report.domain.repository.report_comment_repo import ReportCommentRepository


class ReportCommentService:
    def __init__(self, repo: ReportCommentRepository):
        self.repo = repo

    def add_comment(self, report_id: str, user_id: str, content: str) -> ReportComment:
        comment = ReportComment(
            comment_id=str(ulid.new()),
            report_id=report_id,
            user_id=user_id,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.repo.save(comment)

    def get_comments(self, report_id: str) -> List[ReportComment]:
        return self.repo.find_by_report_id(report_id)

    def delete_comment(self, comment_id: str):
        self.repo.delete(comment_id)
