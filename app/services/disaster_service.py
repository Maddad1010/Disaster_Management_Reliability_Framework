"""Portal data helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db
from app.models.disaster import Alert, Disaster
from app.models.report import DisasterReport
from app.models.rescue import RescueRequest
from app.models.shelter import Shelter

VALID_RESCUE_STATUSES = {"Pending", "Assigned", "In Progress", "Resolved"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}
VALID_DISASTER_TYPES = {
    "Flood",
    "Earthquake",
    "Cyclone",
    "Forest Fire",
    "Landslide",
    "Other",
}
VALID_SEVERITIES = {"Low", "Moderate", "High", "Severe", "Critical"}


def dashboard_stats() -> dict:
    """Aggregate counts for the home dashboard."""
    active_disasters = Disaster.query.filter_by(status="Active").count()
    alerts = Alert.query.filter_by(status="Active").count()
    shelters = Shelter.query.count()
    pending_rescue = RescueRequest.query.filter_by(status="Pending").count()
    affected_areas = db.session.query(Disaster.location).distinct().count()
    return {
        "system_status": "ONLINE",
        "active_disasters": active_disasters,
        "emergency_alerts": alerts,
        "available_shelters": shelters,
        "pending_rescue_requests": pending_rescue,
        "affected_areas": affected_areas,
        "is_demo": True,
    }


def create_rescue_request(payload: dict) -> RescueRequest:
    """Validate and persist a rescue request."""
    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    location = (payload.get("location") or "").strip()
    description = (payload.get("description") or "").strip()
    emergency_type = (payload.get("emergency_type") or "Other").strip()
    priority = (payload.get("priority") or "Medium").strip()
    people_count = int(payload.get("people_count") or 1)

    if not name or not phone or not location or not description:
        raise ValueError("name, phone, location, and description are required")
    if people_count < 1 or people_count > 500:
        raise ValueError("people_count must be between 1 and 500")
    if priority not in VALID_PRIORITIES:
        raise ValueError("invalid priority")
    if emergency_type not in VALID_DISASTER_TYPES:
        emergency_type = "Other"

    record = RescueRequest(
        name=name,
        phone=phone,
        location=location,
        people_count=people_count,
        emergency_type=emergency_type,
        priority=priority,
        description=description,
        status="Pending",
        created_at=datetime.now(timezone.utc),
        is_demo=True,
    )
    db.session.add(record)
    db.session.commit()
    return record


def create_disaster_report(payload: dict) -> DisasterReport:
    """Validate and persist a citizen disaster report."""
    disaster_type = (payload.get("disaster_type") or "").strip()
    location = (payload.get("location") or "").strip()
    severity = (payload.get("severity") or "Moderate").strip()
    description = (payload.get("description") or "").strip()
    affected_people = int(payload.get("affected_people") or 0)

    if disaster_type not in VALID_DISASTER_TYPES:
        raise ValueError("invalid disaster_type")
    if not location or not description:
        raise ValueError("location and description are required")
    if severity not in VALID_SEVERITIES:
        raise ValueError("invalid severity")
    if affected_people < 0 or affected_people > 1_000_000:
        raise ValueError("affected_people out of range")

    record = DisasterReport(
        disaster_type=disaster_type,
        location=location,
        severity=severity,
        description=description,
        affected_people=affected_people,
        status="Submitted",
        created_at=datetime.now(timezone.utc),
        is_demo=True,
    )
    db.session.add(record)
    db.session.commit()
    return record
