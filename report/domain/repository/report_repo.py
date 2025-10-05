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
    def find_all(self) -> List[Report]:
        """전체 제보 조회 (최신순)"""
        raise NotImplementedError
