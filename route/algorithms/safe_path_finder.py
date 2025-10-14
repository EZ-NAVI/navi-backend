from typing import List, Dict
from enum import Enum
import heapq
import math


# --- 데이터 모델 ---
class Point:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon


class HazardCategory(str, Enum):
    """위험구역 카테고리"""

    FEAR = "공포"
    ROAD_CLOSED = "도로폐쇄"
    CONSTRUCTION = "공사장"
    OBSTACLE = "장애물"
    NO_SIDEWALK = "인도 없음"


# --- 카테고리별 고정 반경 (m 단위) ---
CATEGORY_RADIUS = {
    HazardCategory.FEAR: 100,
    HazardCategory.ROAD_CLOSED: 200,
    HazardCategory.CONSTRUCTION: 200,
    HazardCategory.OBSTACLE: 50,
    HazardCategory.NO_SIDEWALK: 100,
}


class Hazard:
    def __init__(self, lat: float, lon: float, category: HazardCategory, score: float):
        self.lat = lat
        self.lon = lon
        self.category = category  # 카테고리명
        self.radius = CATEGORY_RADIUS.get(category, 100)  # 고정 반경 적용
        self.score = score  # 백엔드 계산된 위험도 (float)


# --- 유틸 함수 ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구 반지름 (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def in_hazard(lat, lon, hazards: List[Hazard]):
    """해당 점이 위험구역 안에 있는지 체크"""
    for hz in hazards:
        d = haversine(lat, lon, hz.lat, hz.lon)
        if d <= hz.radius:
            return True
    return False


# --- A* 알고리즘 (격자 기반) ---
def astar_route(start: Point, end: Point, hazards: List[Hazard], grid_size=0.0005):
    open_set = []
    heapq.heappush(open_set, (0, (start.lat, start.lon)))
    came_from = {}
    g_score = {(start.lat, start.lon): 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        # 도착 조건: 30m 이내 도착
        if haversine(current[0], current[1], end.lat, end.lon) < 30:
            return reconstruct_path(came_from, current, start, end)

        for neighbor in get_neighbors(current, grid_size):
            tentative_g = g_score[current] + haversine(
                current[0], current[1], neighbor[0], neighbor[1]
            )

            # hazard 페널티 (거리 + 위험도 반영)
            for hz in hazards:
                d = haversine(neighbor[0], neighbor[1], hz.lat, hz.lon)
                if d <= hz.radius:
                    # 가까울수록 + score 높을수록 회피 강함
                    tentative_g += (hz.radius - d) * hz.score * 2

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + haversine(
                    neighbor[0], neighbor[1], end.lat, end.lon
                )
                heapq.heappush(open_set, (f_score, neighbor))
                came_from[neighbor] = current

    return []


def get_neighbors(pos, step):
    lat, lon = pos
    return [
        (lat + step, lon),
        (lat - step, lon),
        (lat, lon + step),
        (lat, lon - step),
        (lat + step, lon + step),
        (lat + step, lon - step),
        (lat - step, lon + step),
        (lat - step, lon - step),
    ]


def reconstruct_path(came_from, current, start, end):
    path = [(end.lat, end.lon)]
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append((start.lat, start.lon))
    path.reverse()
    return [{"lat": lat, "lon": lon} for lat, lon in path]


# --- 위험구역 카운트 ---
def count_hazards(path: List[Dict[str, float]], hazards: List[Hazard]) -> int:
    """경로(선분)와 hazard(원)가 교차하는지 검사"""
    count = 0
    for hz in hazards:
        radius = hz.radius
        center = (hz.lat, hz.lon)

        for i in range(len(path) - 1):
            p1 = (path[i]["lat"], path[i]["lon"])
            p2 = (path[i + 1]["lat"], path[i + 1]["lon"])

            if (
                haversine(p1[0], p1[1], center[0], center[1]) <= radius
                or haversine(p2[0], p2[1], center[0], center[1]) <= radius
            ):
                count += 1
                break

            if segment_circle_intersect(p1, p2, center, radius):
                count += 1
                break
    return count


def segment_circle_intersect(p1, p2, center, radius):
    """선분(p1-p2)과 원(center, radius)이 교차하는지 체크"""
    x1, y1 = p1[1], p1[0]  # (lon, lat)
    x2, y2 = p2[1], p2[0]
    cx, cy = center[1], center[0]

    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy

    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = (fx * fx + fy * fy) - (radius / 111000) ** 2  # 반경을 위도/경도로 변환

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False

    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)

    return (0 <= t1 <= 1) or (0 <= t2 <= 1)


# --- 거리 계산 ---
def total_distance(path: List[Dict[str, float]]) -> float:
    dist = 0.0
    for i in range(len(path) - 1):
        dist += haversine(
            path[i]["lat"], path[i]["lon"], path[i + 1]["lat"], path[i + 1]["lon"]
        )
    return dist
