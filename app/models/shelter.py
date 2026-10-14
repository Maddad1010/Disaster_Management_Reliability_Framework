"""Shelter model."""

from __future__ import annotations

from app.extensions import db


class Shelter(db.Model):
    """Emergency shelter (dummy academic data)."""

    __tablename__ = "shelters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    occupied = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="OPEN")
    is_demo = db.Column(db.Boolean, default=True)

    @property
    def available(self) -> int:
        return max(0, self.capacity - self.occupied)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "capacity": self.capacity,
            "occupied": self.occupied,
            "available": self.available,
            "status": self.status,
            "is_demo": self.is_demo,
        }
