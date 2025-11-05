from abc import ABC, abstractmethod
from typing import Optional, List
from report.domain.report import Report


class ReportRepository(ABC):
    @abstractmethod
    def save(self, report: Report) -> Report:
        """새로운 제보 저장"""
        raise NotImplementedError

    @abstractmethod
    def get(self, report_id: str) -> Optional[Report]:
        """report_id로 제보 단건 조회"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, report_id: str) -> None:
        """report_id로 제보 삭제"""
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> List[Report]:
        """cluster_id별 제보 조회 (최신순)"""
        raise NotImplementedError

    @abstractmethod
    def update_feedback_counts(self, report: Report) -> Report:
        """제보 피드백 카운트 및 점수 업데이트"""
        raise NotImplementedError

    @abstractmethod
    def find_nearby_reports(
        self, lat: float, lng: float, radius_m: float
    ) -> List[Report]:
        """지정 반경 내 제보 리스트 반환"""
        raise NotImplementedError

    @abstractmethod
    def find_by_cluster_and_category(
        self, cluster_id: str, category: str
    ) -> List[Report]:
        raise NotImplementedError

    @abstractmethod
    def increment_feedback(self, report_id: str, evaluation: str):
        """평가 카운트 증가"""
        raise NotImplementedError

    @abstractmethod
    def decrement_feedback(self, report_id: str, evaluation: str):
        """평가 카운트 감소"""
        raise NotImplementedError
