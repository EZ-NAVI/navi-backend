import ulid
from fastapi import HTTPException
from database import SessionLocal
from report.domain.report_not_there import ReportNotThere as NotThereVO
from report.infra.db_models.report_not_there import ReportNotThere as NotThereDB
from report.domain.repository.report_not_there_repo import ReportNotThereRepository


class PostgresReportNotThereRepository(ReportNotThereRepository):
    def save(self, record: NotThereVO) -> NotThereVO:
        with SessionLocal() as db:
            db_record = NotThereDB(
                id=record.id,
                report_id=record.report_id,
                user_id=record.user_id,
                created_at=record.created_at,
            )
            db.add(db_record)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                # 중복이면 400 에러로 리턴
                if "uq_report_user" in str(e):
                    raise HTTPException(status_code=400, detail="이미 눌렀습니다.")
                raise e

            db.refresh(db_record)
            return NotThereVO.from_orm(db_record)

    def has_user_marked(self, report_id: str, user_id: str) -> bool:
        with SessionLocal() as db:
            exists = (
                db.query(NotThereDB)
                .filter(
                    NotThereDB.report_id == report_id, NotThereDB.user_id == user_id
                )
                .first()
            )
            return exists is not None
