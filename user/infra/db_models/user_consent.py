from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime, timedelta, timezone
from database import Base


class UserConsent(Base):
    __tablename__ = "user_consent"

    consent_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    consent_code = Column(
        String, ForeignKey("consent_master.consent_code"), nullable=False
    )
    consent_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expire_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=365 * 3)
    )
    revoked_at = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
