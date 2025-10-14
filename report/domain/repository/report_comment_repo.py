from abc import ABC, abstractmethod
from typing import Optional, List
from report.domain.report_comment import ReportComment


class ReportCommentRepository(ABC):
    @abstractmethod
    def save(self, comment: ReportComment) -> ReportComment:
        raise NotImplementedError

    @abstractmethod
    def find_by_report_id(self, report_id: str) -> List[ReportComment]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, comment_id: str) -> None:
        raise NotImplementedError
