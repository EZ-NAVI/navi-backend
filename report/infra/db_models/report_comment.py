from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime, timezone
from database import Base


class ReportComment(Base):
    __tablename__ = "report_comment"

    comment_id = Column(String, primary_key=True)
    report_id = Column(String, ForeignKey("report.report_id"), nullable=False)
    author_id = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
