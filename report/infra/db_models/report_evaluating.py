from sqlalchemy import Column, String, Enum, ForeignKey, UniqueConstraint, DateTime
from datetime import datetime
from database import Base
import enum


class EvaluationType(str, enum.Enum):
    GOOD = "good"  # 이모지: 아쉬움
    NORMAL = "normal"  # 이모지: 보통
    BAD = "bad"  # 이모지: 좋음


class ReportEvaluating(Base):
    __tablename__ = "report_evaluating"

    id = Column(String, primary_key=True)
    report_id = Column(String, ForeignKey("report.report_id"), nullable=False)
    user_id = Column(String, ForeignKey("user.user_id"), nullable=False)
    evaluation = Column(Enum(EvaluationType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("report_id", "user_id", name="uix_report_user"),)
