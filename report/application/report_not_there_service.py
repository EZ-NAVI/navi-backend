from datetime import datetime
import ulid
from fastapi import HTTPException
from report.domain.report_not_there import ReportNotThere
from report.domain.repository.report_not_there_repo import ReportNotThereRepository
from report.domain.repository.report_repo import ReportRepository

class ReportNotThereService:
    def __init__(self, repo: ReportNotThereRepository, report_repo: ReportRepository):
        self.repo = repo
        self.report_repo = report_repo

    def mark_not_there(self, report_id: str, user_id: str):
        if self.repo.has_user_marked(report_id, user_id):
            raise HTTPException(status_code=400, detail="이미 '이제 없어요'를 누른 제보입니다.")

        record = ReportNotThere(
            id=str(ulid.new()),
            report_id=report_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
        self.repo.save(record)

        # 제보의 not_there 카운트 증가
        report = self.report_repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="제보를 찾을 수 없습니다.")

        report.not_there = (report.not_there or 0) + 1
        self.report_repo.update_feedback_counts(report)
        return {"message": "'이제 없어요'가 반영되었습니다."}
