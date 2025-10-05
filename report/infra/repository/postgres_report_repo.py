from report.domain.repository.report_repo import ReportRepository
from report.domain.report import Report as ReportVO
from report.infra.db_models.report import Report as ReportDB
from database import SessionLocal


class PostgresReportRepository(ReportRepository):
    def save(self, report: ReportVO) -> ReportVO:
        with SessionLocal() as db:
            db_report = ReportDB(**report.dict(by_alias=True))
            db.add(db_report)
            db.commit()
            db.refresh(db_report)
            return ReportVO.from_orm(db_report)

    def get(self, report_id: str) -> ReportVO | None:
        with SessionLocal() as db:
            report = db.query(ReportDB).filter(ReportDB.report_id == report_id).first()
            return ReportVO.from_orm(report) if report else None

    def find_all(self):
        with SessionLocal() as db:
            reports = db.query(ReportDB).order_by(ReportDB.created_at.desc()).all()
            return [ReportVO.from_orm(r) for r in reports]
