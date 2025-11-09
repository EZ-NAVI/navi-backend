from report.domain.repository.report_repo import ReportRepository
from report.domain.report import Report as ReportVO
from report.infra.db_models.report import Report as ReportDB
from database import SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import aliased
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

    def delete(self, report_id: str) -> None:
        with SessionLocal() as db:
            report = db.query(ReportDB).filter(ReportDB.report_id == report_id).first()
            if report:
                db.delete(report)
                db.commit()

    def find_all(self):
        with SessionLocal() as db:
            query = text(
                """
                SELECT DISTINCT ON (cluster_id) *
                FROM report
                WHERE cluster_id IS NOT NULL
                ORDER BY cluster_id, created_at DESC
            """
            )
            result = db.execute(query).mappings().all()

            return [ReportVO(**dict(row)) for row in result]

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

    def update_status(self, report: ReportDB):
        with SessionLocal() as db:
            db_report = (
                db.query(ReportDB)
                .filter(ReportDB.report_id == report.report_id)
                .first()
            )
            if not db_report:
                return None
            db_report.status = report.status
            db_report.updated_at = report.updated_at
            db.commit()
            db.refresh(db_report)
            return db_report

    def update(self, report: ReportVO) -> ReportVO:
        """제보 전체 정보 수정 (description, category, image_url 포함)"""
        with SessionLocal() as db:
            db_report = (
                db.query(ReportDB)
                .filter(ReportDB.report_id == report.report_id)
                .first()
            )
            if not db_report:
                return None

            # 수정 가능한 필드 반영
            db_report.category = report.category
            db_report.description = report.description
            db_report.image_url = report.image_url
            db_report.status = report.status
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
                WHERE status = 'APPROVED'
                  AND ST_DWithin(
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

    def find_nearby_reports(self, lat: float, lng: float, radius_m: float):
        """특정 좌표 반경 내 기존 제보 조회 (cluster_id 판별용)"""
        with SessionLocal() as db:
            query = text(
                """
                SELECT *
                FROM report
                WHERE ST_DWithin(
                    geography(ST_MakePoint(location_lng, location_lat)),
                    geography(ST_MakePoint(:lng, :lat)),
                    :radius
                )
                ORDER BY created_at DESC
                """
            )

            rows = db.execute(
                query,
                {"lat": lat, "lng": lng, "radius": radius_m},
            ).fetchall()

            # SQLAlchemy Text query는 ORM 매핑이 아니므로 수동으로 VO 변환
            nearby_reports = []
            for row in rows:
                nearby_reports.append(
                    ReportVO(
                        report_id=row.report_id,
                        reporter_id=row.reporter_id,
                        reporter_type=row.reporter_type,
                        location_lat=row.location_lat,
                        location_lng=row.location_lng,
                        cluster_id=row.cluster_id,
                        image_url=row.image_url,
                        category=row.category,
                        description=row.description,
                        status=row.status,
                        good_count=row.good_count,
                        normal_count=row.normal_count,
                        bad_count=row.bad_count,
                        total_feedbacks=row.total_feedbacks,
                        not_there=row.not_there,
                        created_at=row.created_at,
                        updated_at=row.updated_at,
                    )
                )

            return nearby_reports

    def find_by_cluster_and_category(self, cluster_id: str, category: str):
        with SessionLocal() as db:
            reports = (
                db.query(ReportDB)
                .filter(
                    ReportDB.cluster_id == cluster_id, ReportDB.category == category
                )
                .order_by(ReportDB.created_at.desc())
                .all()
            )
            return [ReportVO.from_orm(r) for r in reports]

    def find_latest_per_cluster(self):
        with SessionLocal() as db:
            reports = (
                db.query(ReportDB)
                .filter(ReportDB.cluster_id.isnot(None))
                .distinct(ReportDB.cluster_id)
                .order_by(ReportDB.cluster_id, ReportDB.created_at.desc())
                .all()
            )
            return [Report.model_validate(r) for r in reports]

    def increment_feedback(self, report_id: str, evaluation: str):
        """좋음/보통/아쉬움 평가 카운트 업데이트"""
        with SessionLocal() as db:
            report = db.query(ReportDB).filter(ReportDB.report_id == report_id).first()
            if not report:
                return

            # 평가별 카운트 증가
            if evaluation == "good":
                report.good_count += 1
            elif evaluation == "normal":
                report.normal_count += 1
            elif evaluation == "bad":
                report.bad_count += 1

            # 전체 피드백 수 증가
            report.total_feedbacks += 1

            db.commit()
            db.refresh(report)

    def decrement_feedback(self, report_id: str, evaluation: str):
        """좋음/보통/아쉬움 평가 카운트 감소"""
        with SessionLocal() as db:
            report = db.query(ReportDB).filter(ReportDB.report_id == report_id).first()
            if not report:
                return

            # 평가별 카운트 감소
            if evaluation == "good" and report.good_count > 0:
                report.good_count -= 1
            elif evaluation == "normal" and report.normal_count > 0:
                report.normal_count -= 1
            elif evaluation == "bad" and report.bad_count > 0:
                report.bad_count -= 1

            # 전체 피드백 수 감소
            if report.total_feedbacks > 0:
                report.total_feedbacks -= 1

            db.commit()
            db.refresh(report)
