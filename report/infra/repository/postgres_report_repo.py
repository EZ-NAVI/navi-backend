from report.domain.repository.report_repo import ReportRepository
from report.domain.report import Report as ReportVO
from report.infra.db_models.report import Report as ReportDB
from database import SessionLocal
from sqlalchemy import text


class PostgresReportRepository(ReportRepository):
    def save(self, report: ReportVO) -> ReportVO:
        with SessionLocal() as db:
            db_report = ReportDB(
                report_id=report.report_id,
                reporter_id=report.reporter_id,
                reporter_type=report.reporter_type,
                location_lat=report.location_lat,
                location_lng=report.location_lng,
                cluster_id=report.cluster_id,
                image_url=report.image_url,
                category=report.category,
                description=report.description,
                status=report.status,
                not_there=report.not_there,
                created_at=report.created_at,
                updated_at=report.updated_at,
            )
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

    def update_feedback_counts(self, report: ReportVO) -> ReportVO:
        with SessionLocal() as db:
            db_report = (
                db.query(ReportDB)
                .filter(ReportDB.report_id == report.report_id)
                .first()
            )
            if not db_report:
                return None

            db_report.good_count = report.good_count
            db_report.normal_count = report.normal_count
            db_report.bad_count = report.bad_count
            db_report.total_feedbacks = report.total_feedbacks
            db_report.updated_at = report.updated_at

            db.commit()
            db.refresh(db_report)
            return ReportVO.from_orm(db_report)

    def find_nearby_reports(self, lat, lng, radius_m):
        with SessionLocal() as db:
            query = text(
                """
                SELECT *
                FROM report
                WHERE 6371000 * 2 * ASIN(
                    SQRT(
                        POWER(SIN(RADIANS(:lat - location_lat)/2), 2)
                        + COS(RADIANS(:lat)) * COS(RADIANS(location_lat))
                        * POWER(SIN(RADIANS(:lng - location_lng)/2), 2)
                    )
                ) <= :radius
            """
            )
            result = db.execute(query, {"lat": lat, "lng": lng, "radius": radius_m})
            rows = result.fetchall()
            return [ReportVO.from_orm(ReportDB(**dict(row))) for row in rows]
