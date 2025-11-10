from sqlalchemy import Column, String
from database import Base


class ConsentMaster(Base):
    __tablename__ = "consent_master"

    consent_code = Column(String, primary_key=True)
