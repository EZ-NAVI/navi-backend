from datetime import datetime, timezone
import ulid
from typing import List, Dict, Optional
from route.domain.route import Route
from route.domain.repository.route_repo import RouteRepository
from report.domain.repository.report_repo import ReportRepository
from route.algorithms.safe_path_finder import (
    astar_route,
    Hazard,
    HazardCategory,
    Point,
)


class RouteService:
    def __init__(self, repo: RouteRepository, report_repo: ReportRepository):
        self.repo = repo
        self.report_repo = report_repo

    # 미리보기 (경로 생성만, 저장 X)
    def generate_safe_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> List[Dict[str, float]]:
        reports = self.report_repo.find_all()
        valid_categories = {c.value for c in HazardCategory}
        hazards: List[Hazard] = []

        for r in reports:
            if not r.category or r.category not in valid_categories:
                continue
            if not r.location_lat or not r.location_lng:
                continue

            total_feedbacks = max(r.total_feedbacks or 1, 1)
            risk_score = (r.bad_count or 0) / total_feedbacks
            risk_score = round(risk_score * 2, 2) or 0.5

            hazards.append(
                Hazard(
                    lat=r.location_lat,
                    lon=r.location_lng,
                    category=HazardCategory(r.category),
                    score=risk_score,
                )
            )

        start = Point(origin_lat, origin_lng)
        end = Point(dest_lat, dest_lng)
        return astar_route(start, end, hazards)

    # 실제 이동 시 DB 저장
    def save_route_if_traveled(
        self,
        user_id: str,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        duration: int,
        path_data: List[Dict[str, float]],
    ) -> Route:
        route = Route(
            route_id=str(ulid.new()),
            user_id=user_id,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            path_data=path_data,
            duration=duration,
            created_at=datetime.now(timezone.utc),
        )
        return self.repo.save(route)

    # 아동 후 평가 (별점 등록)
    def evaluate_route(self, route_id: str, evaluation: float) -> Optional[Route]:
        route = self.repo.get(route_id)
        if not route:
            return None
        route.evaluation = evaluation
        return self.repo.save(route)
