from datetime import datetime, timezone
import ulid
from typing import List
from route.domain.route import Route
from route.domain.repository.route_repo import RouteRepository
from report.domain.repository.report_repo import ReportRepository
from route.algorithms.safe_path_finder import (
    astar_route,
    total_distance,
    count_hazards,
    Hazard,
    HazardCategory,
    Point,
)


class RouteService:
    def __init__(self, repo: RouteRepository, report_repo: ReportRepository):
        self.repo = repo
        self.report_repo = report_repo

    def create_route(
        self,
        user_id: str,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        duration: int,
    ) -> Route:
        reports = self.report_repo.find_all()
        hazards = [
            Hazard(
                lat=r.location_lat,
                lon=r.location_lng,
                category=(
                    HazardCategory(r.category) if r.category else HazardCategory.FEAR
                ),
                score=r.score or 0.5,
            )
            for r in reports
        ]

        start = Point(origin_lat, origin_lng)
        end = Point(dest_lat, dest_lng)
        path = astar_route(start, end, hazards)
        total_dist = total_distance(path)
        hz_count = count_hazards(path, hazards)

        route = Route(
            route_id=str(ulid.new()),
            user_id=user_id,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            path_data=path,
            duration=duration,
            score=hz_count / (len(hazards) + 1),
            created_at=datetime.now(timezone.utc),
        )
        return self.repo.save(route)
