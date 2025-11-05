from abc import ABC, abstractmethod
from typing import Optional
from report.domain.report_evaluating import ReportEvaluating


class ReportEvaluatingRepository(ABC):
    @abstractmethod
    def find_user_evaluating(
        self, report_id: str, user_id: str
    ) -> Optional[ReportEvaluating]:
        pass

    @abstractmethod
    def add_evaluating(self, report_id: str, user_id: str, evaluation: str) -> None:
        pass

    @abstractmethod
    def update_evaluating(self, evaluating_id: str, evaluation: str) -> None:
        pass

    @abstractmethod
    def delete_evaluating(self, evaluating_id: str) -> None:
        pass
