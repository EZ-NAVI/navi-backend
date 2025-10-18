from abc import ABC, abstractmethod
from typing import List
from report.domain.report_not_there import ReportNotThere

class ReportNotThereRepository(ABC):
    @abstractmethod
    def save(self, record: ReportNotThere) -> ReportNotThere:
        raise NotImplementedError

    @abstractmethod
    def has_user_marked(self, report_id: str, user_id: str) -> bool:
        raise NotImplementedError
