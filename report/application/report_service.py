from fastapi import HTTPException, status
from datetime import datetime
import ulid
from typing import List

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
            score=0.0,
            not_there=0,
            created_at=now,
            updated_at=now,
        )
        return self.repo.save(report)

    def get_report(self, report_id: str) -> Report | None:
        return self.repo.get(report_id)

    def list_reports(self) -> List[Report]:
        return self.repo.find_all()
