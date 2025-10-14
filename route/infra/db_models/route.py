from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from datetime import datetime
from database import Base


class Route(Base):
    __tablename__ = "safe_route"

    route_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    path_data = Column(JSON, nullable=False)
    duration = Column(Integer, nullable=False)
    score = Column(Float, nullable=True, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
