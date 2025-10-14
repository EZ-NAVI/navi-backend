from report.domain.repository.report_repo import ReportRepository
from report.domain.report import Report as ReportVO
from report.infra.db_models.report import Report as ReportDB
from database import SessionLocal
from sqlalchemy import text
from route.algorithms.safe_path_finder import Hazard, HazardCategory


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

    # PostGIS 기반 공간쿼리
    def find_nearby(self, origin_lat, origin_lng, dest_lat, dest_lng, buffer_m=2000):
        """출발/도착 중심점을 기준으로 반경 buffer_m 내 제보만 가져옴"""
        with SessionLocal() as db:
            query = text(
                """
                SELECT report_id, location_lat, location_lng, category,
                    good_count, normal_count, bad_count, total_feedbacks
                FROM report
                WHERE ST_DWithin(
                    geography(ST_MakePoint(location_lng, location_lat)),
                    geography(ST_MakePoint(:center_lng, :center_lat)),
                    :buffer
                )
            """
            )

            center_lat = (origin_lat + dest_lat) / 2
            center_lng = (origin_lng + dest_lng) / 2

            rows = db.execute(
                query,
                {
                    "center_lat": center_lat,
                    "center_lng": center_lng,
                    "buffer": buffer_m,
                },
            ).fetchall()

            hazards = []
            valid_categories = {c.value for c in HazardCategory}

            for r in rows:
                if not r.category or r.category not in valid_categories:
                    continue

                total = max(r.total_feedbacks or 1, 1)
                score = (r.bad_count or 0) / total
                score = round(score * 2, 2) or 0.5

                try:
                    category_enum = HazardCategory(r.category)
                except ValueError:
                    continue

                hazards.append(
                    Hazard(
                        lat=r.location_lat,
                        lon=r.location_lng,
                        category=category_enum,
                        score=score,
                    )
                )

            return hazards
