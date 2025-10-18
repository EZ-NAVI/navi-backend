from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from database import Base

class ReportNotThere(Base):
    __tablename__ = "report_not_there"

    id = Column(String, primary_key=True)
    report_id = Column(String, ForeignKey("report.report_id"), nullable=False)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("report_id", "user_id", name="uq_report_user"),)
