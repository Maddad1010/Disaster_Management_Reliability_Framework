"""Rescue request model."""

from __future__ import annotations

from datetime import datetime

from app.extensions import db


class RescueRequest(db.Model):
    """Citizen rescue request stored in SQLite (dummy names/phones)."""

    __tablename__ = "rescue_requests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    location = db.Column(db.String(160), nullable=False)
    people_count = db.Column(db.Integer, nullable=False, default=1)
    emergency_type = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "location": self.location,
            "people_count": self.people_count,
            "emergency_type": self.emergency_type,
            "priority": self.priority,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_demo": self.is_demo,
        }
