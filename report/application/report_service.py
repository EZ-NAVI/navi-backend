from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from uuid import uuid4
import ulid
import math
import asyncio

from user.domain.repository.user_repo import UserRepository
from report.domain.report import Report
from report.domain.repository.report_repo import ReportRepository

CLUSTER_RADIUS = 500


class ReportService:
    def __init__(self, repo: ReportRepository, user_repo: UserRepository, event_bus):
        self.repo = repo
        self.user_repo = user_repo
        self.event_bus = event_bus

    async def create_report(
        self,
        reporter_id: str,
        reporter_type: str,
        location_lat: float,
        location_lng: float,
        image_url: str | None = None,
        category: str | None = None,
        description: str | None = None,
    ) -> Report:

        user = self.user_repo.get(reporter_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 보호자 매칭 검증
        if user.user_type == "child" and not user.parent_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="보호자 연결이 필요한 계정입니다.",
            )

        # 제보 객체 생성
        now = datetime.now(timezone.utc)

        # 반경 500m 이내 기존 제보 조회
        nearby_reports = self.repo.find_nearby_reports(
            lat=location_lat, lng=location_lng, radius_m=CLUSTER_RADIUS
        )

        # 기존 클러스터 존재하면 동일 cluster_id 부여, 없으면 새로 생성
        if nearby_reports:
            cluster_id = nearby_reports[0].cluster_id or nearby_reports[0].report_id
        else:
            cluster_id = str(uuid4())

        report = Report(
            report_id=str(ulid.new()),
            reporter_id=reporter_id,
            reporter_type=reporter_type,
            location_lat=location_lat,
            location_lng=location_lng,
            cluster_id=cluster_id,
            image_url=image_url,
            category=category,
            description=description,
            status="PENDING",
            good_count=0,
            normal_count=0,
            bad_count=0,
            total_feedbacks=0,
            not_there=0,
            created_at=now,
            updated_at=now,
        )

        saved = self.repo.save(report)

        # 자녀가 제보 생성 → 부모에게 실시간 이벤트 발행
        if user.user_type == "child" and user.parent_id:
            await self.event_bus.publish(
                "report.created",
                {
                    "reportId": saved.report_id,
                    "parentId": user.parent_id,
                    "childId": user.user_id,
                    "category": saved.category,
                    "description": saved.description,
                    "imageUrl": saved.image_url,
                },
                exchange="navi_exchange",
            )

        return saved

    def get_report(self, report_id: str) -> Report | None:
        return self.repo.get(report_id)

    def list_reports(self) -> List[Report]:
        return self.repo.find_all()

    async def review_report(self, report_id: str, reviewer_id: str, action: str):
        """
        action: "승인" | "반려"
        보호자가 자녀 제보를 승인 또는 반려한다.
        """
        report = self.repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="제보를 찾을 수 없습니다.")

        reviewer = self.user_repo.get(reviewer_id)
        if not reviewer:
            raise HTTPException(
                status_code=404, detail="리뷰어(보호자) 정보를 찾을 수 없습니다."
            )

        # 보호자 권한 확인
        child = self.user_repo.get(report.reporter_id)
        if not child or child.parent_id != reviewer.user_id:
            raise HTTPException(
                status_code=403, detail="이 제보를 검토할 권한이 없습니다."
            )

        if report.status != "PENDING":
            raise HTTPException(status_code=400, detail="이미 처리된 제보입니다.")

        # 상태 업데이트
        if action == "승인":
            report.status = "APPROVED"
        elif action == "반려":
            report.status = "REJECTED"
        else:
            raise HTTPException(
                status_code=400, detail="잘못된 action 값입니다. (approve/reject)"
            )

        report.updated_at = datetime.now(timezone.utc)
        updated = self.repo.update_status(report)

        # 부모가 승인/반려 → 자녀에게 실시간 이벤트 발행
        await self.event_bus.publish(
            "report.reviewed",
            {
                "reportId": updated.report_id,
                "childId": child.user_id,
                "status": updated.status,
            },
            exchange="navi_exchange",
        )

        return updated

    def update_feedback(self, report_id: str, feedback: str):
        """
        feedback: "good" | "normal" | "bad"
        """
        report = self.repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # 기존 count 업데이트
        report.good_count = (report.good_count or 0) + (1 if feedback == "good" else 0)
        report.normal_count = (report.normal_count or 0) + (
            1 if feedback == "normal" else 0
        )
        report.bad_count = (report.bad_count or 0) + (1 if feedback == "bad" else 0)

        # 위험도 재계산
        n_good = report.good_count
        n_mid = report.normal_count
        n_bad = report.bad_count
        n = n_good + n_mid + n_bad

        def risk_score_simplified_scaled(n_good, n_mid, n_bad):
            n = n_good + n_mid + n_bad
            if n == 0:
                return 0.5

            # 기본 평균 위험도
            avg = (n_bad * 1.0 + n_mid * 0.5 + n_good * 0.0) / n

            # 제보 수 기반 신뢰도 (데이터 많을수록 확신 ↑)
            reliability = 1 - math.exp(-n / 10)

            # 가변 스케일링 (데이터 많을수록 민감도 ↑)
            scale = 0.5 + 0.5 * (1 - math.exp(-0.1 * n))

            # 최종 점수: 중립 보정 + 신뢰도 반영 + 스케일 조정
            return (avg * reliability + 0.5 * (1 - reliability)) * scale

        report.score = risk_score_simplified_scaled(n_good, n_mid, n_bad)
        report.total_feedbacks = n
        report.updated_at = datetime.now(timezone.utc)

        return self.repo.update_feedback_counts(report)

    def get_reports_by_cluster_and_category(self, cluster_id: str, category: str):
        return self.repo.find_by_cluster_and_category(cluster_id, category)
