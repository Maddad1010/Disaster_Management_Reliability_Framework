"""Citizen disaster report model."""

from __future__ import annotations

from datetime import datetime

from app.extensions import db


class DisasterReport(db.Model):
    """User-submitted disaster report (dummy academic data)."""

    __tablename__ = "disaster_reports"

    id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(160), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    affected_people = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="Submitted")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "disaster_type": self.disaster_type,
            "location": self.location,
            "severity": self.severity,
            "description": self.description,
            "affected_people": self.affected_people,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_demo": self.is_demo,
        }
