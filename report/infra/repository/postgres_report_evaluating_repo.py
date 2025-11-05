from report.domain.repository.report_evaluating_repo import ReportEvaluatingRepository
from report.domain.report_evaluating import ReportEvaluating as ReportEvaluatingVO
from report.infra.db_models.report_evaluating import (
    ReportEvaluating as ReportEvaluatingDB,
)
from database import SessionLocal
from uuid import uuid4


class PostgresReportEvaluatingRepository(ReportEvaluatingRepository):
    def find_user_evaluating(self, report_id: str, user_id: str):
        with SessionLocal() as db:
            record = (
                db.query(ReportEvaluatingDB)
                .filter(
                    ReportEvaluatingDB.report_id == report_id,
                    ReportEvaluatingDB.user_id == user_id,
                )
                .first()
            )
            return ReportEvaluatingVO.from_orm(record) if record else None

    def add_evaluating(self, report_id: str, user_id: str, evaluation: str):
        with SessionLocal() as db:
            new_eval = ReportEvaluatingDB(
                id=str(uuid4()),
                report_id=report_id,
                user_id=user_id,
                evaluation=evaluation,
            )
            db.add(new_eval)
            db.commit()

    def update_evaluating(self, evaluating_id: str, evaluation: str):
        with SessionLocal() as db:
            record = (
                db.query(ReportEvaluatingDB)
                .filter(ReportEvaluatingDB.id == evaluating_id)
                .first()
            )
            if record:
                record.evaluation = evaluation
                db.commit()

    def delete_evaluating(self, evaluating_id: str):
        with SessionLocal() as db:
            db.query(ReportEvaluatingDB).filter(
                ReportEvaluatingDB.id == evaluating_id
            ).delete()
            db.commit()
