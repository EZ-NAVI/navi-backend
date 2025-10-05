from datetime import datetime
import ulid
from typing import List

from report.domain.report import Report
from report.domain.repository.report_repo import ReportRepository


class ReportService:
    def __init__(self, repo: ReportRepository):
        self.repo = repo

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
        now = datetime.utcnow()

        report = Report(
            report_id=str(ulid.new()),
            reporter_id=reporter_id,
            reporter_type=reporter_type,
            location_lat=location_lat,
            location_lng=location_lng,
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
