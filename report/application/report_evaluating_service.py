from fastapi import HTTPException
from datetime import datetime, timezone


class ReportEvaluatingService:
    def __init__(self, report_repo, evaluating_repo):
        self.report_repo = report_repo
        self.evaluating_repo = evaluating_repo

    async def evaluate_report(self, report_id: str, user_id: str, evaluation: str):
        report = self.report_repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        existing = self.evaluating_repo.find_user_evaluating(report_id, user_id)

        if existing and existing.evaluation == evaluation:
            # 동일 이모지 → 취소
            self.evaluating_repo.delete_evaluating(existing.id)
            self.report_repo.decrement_feedback(report_id, evaluation)
            action = "cancelled"

        elif existing and existing.evaluation != evaluation:
            # 다른 이모지로 변경
            self.report_repo.decrement_feedback(report_id, existing.evaluation)
            self.report_repo.increment_feedback(report_id, evaluation)
            self.evaluating_repo.update_evaluating(existing.id, evaluation)
            action = "changed"

        else:
            # 첫 평가 등록
            self.evaluating_repo.add_evaluating(report_id, user_id, evaluation)
            self.report_repo.increment_feedback(report_id, evaluation)
            action = "added"

        return {
            "report_id": report_id,
            "evaluation": evaluation,
            "action": action,
            "updated_at": datetime.now(timezone.utc),
        }
