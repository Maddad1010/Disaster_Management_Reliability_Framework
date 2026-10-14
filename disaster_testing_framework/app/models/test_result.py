from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .base import Base

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, index=True, unique=True)
    test_type = Column(String)
    users = Column(Integer)
    duration = Column(Integer)
    avg_response_time = Column(Float)
    success_rate = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    report_path = Column(String, nullable=True)
