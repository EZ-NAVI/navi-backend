from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)  # ULID 문자열 저장
    user_type = Column(String, nullable=False)  # "parent" | "child"
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    parent_id = Column(String, nullable=True)  # 부모 user_id (ULID 문자열)
    birth_year = Column(Integer, nullable=True)
    fcm_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
