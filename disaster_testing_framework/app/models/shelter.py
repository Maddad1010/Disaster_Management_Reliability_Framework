from sqlalchemy import Column, Integer, String
from .base import Base

class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    capacity = Column(Integer)
    occupied = Column(Integer)
    status = Column(String, default="OPEN")

    @property
    def available(self):
        return max(0, self.capacity - self.occupied)
