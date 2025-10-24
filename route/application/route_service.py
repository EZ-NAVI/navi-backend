import ulid
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
from route.domain.route import Route
from route.domain.repository.route_repo import RouteRepository
from report.domain.repository.report_repo import ReportRepository
from route.algorithms.safe_path_finder import build_graph, astar_graph, Hazard
from config import get_settings


class RouteService:
    def __init__(self, repo: RouteRepository, report_repo: ReportRepository):
        self.repo = repo
        self.report_repo = report_repo
        self.settings = get_settings()

    # 미리보기 (경로 생성만, 저장 X)
    def generate_safe_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> List[Dict[str, float]]:
        """
        1. TMap 보행자 경로를 요청해 기본 좌표 경로를 받는다.
        2. PostGIS를 이용해 근처 위험 제보만 불러와 Hazard 리스트를 만든다.
        3. 위험도 기반으로 A* 알고리즘을 돌려 안전한 경로를 반환한다.
        """
        # PostGIS로 반경 내 위험 제보 조회
        hazards = self.report_repo.find_nearby(
            origin_lat, origin_lng, dest_lat, dest_lng, buffer_m=2000
        )

        # TMap 보행자 경로 API 호출
        url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json"

        headers = {
            "appKey": self.settings.tmap_app_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "startX": origin_lng,
            "startY": origin_lat,
            "endX": dest_lng,
            "endY": dest_lat,
            "reqCoordType": "WGS84GEO",
            "resCoordType": "WGS84GEO",
            "startName": "출발지",
            "endName": "도착지",
        }

        response = requests.post(url, headers=headers, data=data)

        response.raise_for_status()
        features = response.json().get("features", [])

        # LineString 좌표 추출 (기본 경로)
        base_lines = []
        for f in features:
            geom = f.get("geometry")
            if geom and geom.get("type") == "LineString":
                coords = geom["coordinates"]
                # [lon, lat] → (lat, lon)
                line = [(c[1], c[0]) for c in coords]
                base_lines.append(line)

        # 위험구역이 없으면 기본 경로 반환
        if not hazards:
            print("No hazards nearby — returning base route directly.")
            flat_path = [
                {"lat": lat, "lon": lon} for line in base_lines for lat, lon in line
            ]
            return flat_path

        # 위험구역 객체 변환
        hazard_objs = [
            Hazard(h.location_lat, h.location_lng, h.category, score=1.0)
            for h in hazards
        ]

        # 그래프 구성
        graph = build_graph(base_lines, hazard_objs)

        # A* 기반 위험 회피 경로 생성
        start = (origin_lat, origin_lng)
        end = (dest_lat, dest_lng)
        safe_path = astar_graph(graph, start, end)

        return safe_path

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
