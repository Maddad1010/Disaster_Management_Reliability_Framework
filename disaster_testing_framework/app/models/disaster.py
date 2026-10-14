from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .base import Base

class Disaster(Base):
    __tablename__ = "disasters"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String, index=True)
    severity = Column(String)
    location = Column(String)
    description = Column(Text)
    reported_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Active")
