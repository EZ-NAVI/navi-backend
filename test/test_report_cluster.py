from report.application.report_service import ReportService
from report.domain.repository.report_repo import ReportRepository
from user.domain.repository.user_repo import UserRepository
from report.domain.report import Report
import math


# --- Report용 Fake Repository ---
class FakeRepo(ReportRepository):
    def __init__(self):
        self.reports = []

    def save(self, report):
        self.reports.append(report)
        return report

    def get(self, report_id):
        return next((r for r in self.reports if r.report_id == report_id), None)

    def find_all(self):
        return self.reports

    def update_feedback_counts(self, report):
        return report

    def find_nearby_reports(self, lat, lng, radius_m):
        """500m 이내 제보 검색 (Haversine 이용)"""

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = (
                math.sin(dphi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            )
            return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return [
            r
            for r in self.reports
            if haversine(lat, lng, r.location_lat, r.location_lng) <= radius_m
        ]


# --- User용 Fake Repository ---
class FakeUserRepo(UserRepository):
    def save(self, user):
        return user

    def find_by_email(self, email):
        return None

    def find_children_by_parent_id(self, parent_id):
        return []

    def get(self, user_id):
        # 항상 보호자 연결된 가짜 유저 반환
        return type("User", (), {"user_type": "child", "parent_id": "dummy"})()


# --- 테스트 ---
def test_cluster_assignment():
    repo = FakeRepo()
    user_repo = FakeUserRepo()
    service = ReportService(repo, user_repo)

    # 첫 제보
    report1 = service.create_report(
        reporter_id="test",
        reporter_type="child",
        location_lat=37.5665,
        location_lng=126.9780,
    )

    # 두 번째 제보 (약 40m 차이)
    report2 = service.create_report(
        reporter_id="test",
        reporter_type="child",
        location_lat=37.5668,
        location_lng=126.9783,
    )

    # 클러스터 ID 같아야 성공
    assert report1.cluster_id == report2.cluster_id
