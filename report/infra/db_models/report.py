from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime
from database import Base


class Report(Base):
    __tablename__ = "report"

    report_id = Column(String, primary_key=True)
    reporter_id = Column(String, nullable=False)
    reporter_type = Column(String, nullable=False)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    cluster_id = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    score = Column(Float, nullable=True, default=0.0)
    not_there = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
