from typing import List, Dict, Tuple
from enum import Enum
import heapq
import math
from common.logger import logger


# --- 데이터 모델 ---
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
        self.category = category
        self.radius = CATEGORY_RADIUS.get(category, 100)
        self.score = score


# --- 유틸 함수 ---
def haversine(lat1, lon1, lat2, lon2):
    """위도/경도 거리 계산 (m 단위)"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def snap_to_nearest_node(graph, point):
    """그래프의 노드 중 point와 가장 가까운 노드를 반환"""
    if not graph:
        return point
    nodes = list(graph.keys())
    nearest = min(nodes, key=lambda n: haversine(point[0], point[1], n[0], n[1]))
    return nearest


def segment_circle_intersect(p1, p2, center, radius):
    """선분(p1-p2)와 원(center, radius)이 교차하는지 체크"""
    x1, y1 = p1[1], p1[0]
    x2, y2 = p2[1], p2[0]
    cx, cy = center[1], center[0]

    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy

    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = (fx * fx + fy * fy) - (radius / 111000) ** 2

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False

    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)
    return (0 <= t1 <= 1) or (0 <= t2 <= 1)


# --- 세그먼트 그래프 생성 ---
def build_graph(lines: List[List[Tuple[float, float]]], hazards: List[Hazard]):
    """
    TMap LineString 데이터를 기반으로 도로 그래프를 구성.
    각 세그먼트에 위험도 가중치를 추가함.
    """
    graph = {}

    for line in lines:
        for i in range(len(line) - 1):
            p1 = line[i]
            p2 = line[i + 1]
            dist = haversine(p1[0], p1[1], p2[0], p2[1])
            weight = dist  # 기본 거리 기반 가중치

            # 위험 구역과 교차하면 페널티 부여
            for hz in hazards:
                if segment_circle_intersect(p1, p2, (hz.lat, hz.lon), hz.radius):
                    weight += hz.score * 300  # 위험도 높은 세그먼트는 회피

            # 양방향 그래프 구성
            graph.setdefault(p1, []).append((p2, weight))
            graph.setdefault(p2, []).append((p1, weight))

    return graph


# --- A* 그래프 탐색 ---
def astar_graph(graph, start: Tuple[float, float], goal: Tuple[float, float]):
    """
    세그먼트 그래프 기반 A* 탐색
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        # 도착 기준: 100m 이내
        if haversine(current[0], current[1], goal[0], goal[1]) < 100:
            return reconstruct_path(came_from, current, start, goal)

        for neighbor, weight in graph.get(current, []):
            tentative_g = g_score[current] + weight

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + haversine(
                    neighbor[0], neighbor[1], goal[0], goal[1]
                )
                heapq.heappush(open_set, (f_score, neighbor))
                came_from[neighbor] = current

    logger.info(f"A* failed: explored {len(g_score)} nodes but no path reached goal")
    return []


def reconstruct_path(came_from, current, start, goal):
    """경로 역추적"""
    path = [goal]
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return [{"lat": lat, "lon": lon} for lat, lon in path]
