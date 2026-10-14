"""Disaster and alert models."""

from __future__ import annotations

from datetime import datetime

from app.extensions import db


class Disaster(db.Model):
    """Active or historical disaster event (dummy academic data)."""

    __tablename__ = "disasters"

    id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    affected_people = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), nullable=False, default="Active")
    occurred_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "disaster_type": self.disaster_type,
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "affected_people": self.affected_people,
            "status": self.status,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "is_demo": self.is_demo,
        }


class Alert(db.Model):
    """Emergency alert broadcast (dummy academic data)."""

    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    disaster_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "disaster_type": self.disaster_type,
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_demo": self.is_demo,
        }
