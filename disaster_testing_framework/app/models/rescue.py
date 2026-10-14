from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .base import Base

class RescueRequest(Base):
    __tablename__ = "rescue_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    location = Column(String)
    num_people = Column(Integer)
    emergency_type = Column(String)
    priority = Column(String)
    description = Column(Text)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
