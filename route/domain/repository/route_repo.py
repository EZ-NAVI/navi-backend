from abc import ABC, abstractmethod
from typing import Optional, List
from route.domain.route import Route


class RouteRepository(ABC):
    @abstractmethod
    def save(self, route: Route) -> Route:
        """새로운 경로 저장"""
        raise NotImplementedError

    @abstractmethod
    def get(self, route_id: str) -> Optional[Route]:
        """route_id로 경로 단건 조회"""
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> List[Route]:
        """전체 경로 조회 (최신순)"""
        raise NotImplementedError
