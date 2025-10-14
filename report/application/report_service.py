from fastapi import HTTPException, status
from datetime import datetime
from typing import List

import ulid
import math

from user.domain.repository.user_repo import UserRepository
from report.domain.report import Report
from report.domain.repository.report_repo import ReportRepository


class ReportService:
    def __init__(self, repo: ReportRepository, user_repo: UserRepository):
        self.repo = repo
        self.user_repo = user_repo

    def create_report(
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
        now = datetime.utcnow()

        report = Report(
            report_id=str(ulid.new()),
            reporter_id=reporter_id,
            reporter_type=reporter_type,
            location_lat=location_lat,
            location_lng=location_lng,
            # cluster_id: 아직 클러스터링 미적용 → None으로 초기화
            cluster_id=None,
            image_url=image_url,
            category=category,
            description=description,
            status="pending",
            good_count=0,
            normal_count=0,
            bad_count=0,
            total_feedbacks=0,
            not_there=0,
            created_at=now,
            updated_at=now,
        )
        return self.repo.save(report)

    def get_report(self, report_id: str) -> Report | None:
        return self.repo.get(report_id)

    def list_reports(self) -> List[Report]:
        return self.repo.find_all()

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

        report.total_feedbacks = n
        report.updated_at = datetime.utcnow()

        return self.repo.update_feedback_counts(report)
