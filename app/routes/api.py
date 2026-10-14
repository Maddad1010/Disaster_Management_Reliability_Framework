"""JSON REST API for the demo disaster portal."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.models.disaster import Alert, Disaster
from app.models.report import DisasterReport
from app.models.rescue import RescueRequest
from app.models.shelter import Shelter
from app.services.disaster_service import create_disaster_report, create_rescue_request, dashboard_stats
from app.services.metrics_service import health_to_dict, read_system_health
from app.services.simulation_state import simulation_state

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    stats = dashboard_stats()
    sys_health = health_to_dict(read_system_health())
    return jsonify(
        {
            "status": "ok",
            "portal": stats["system_status"],
            "system": sys_health,
            "demo": True,
        }
    )


@api_bp.get("/disasters")
def disasters():
    items = Disaster.query.order_by(Disaster.occurred_at.desc()).all()
    return jsonify({"count": len(items), "demo": True, "items": [d.to_dict() for d in items]})


@api_bp.get("/alerts")
def alerts():
    items = Alert.query.order_by(Alert.created_at.desc()).all()
    return jsonify({"count": len(items), "demo": True, "items": [a.to_dict() for a in items]})


@api_bp.get("/shelters")
def shelters():
    items = Shelter.query.order_by(Shelter.name).all()
    return jsonify({"count": len(items), "demo": True, "items": [s.to_dict() for s in items]})


@api_bp.get("/rescue-requests")
def list_rescue():
    items = RescueRequest.query.order_by(RescueRequest.created_at.desc()).all()
    return jsonify({"count": len(items), "demo": True, "items": [r.to_dict() for r in items]})


@api_bp.post("/rescue-requests")
def post_rescue():
    payload = request.get_json(silent=True) or {}
    try:
        record = create_rescue_request(payload)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc), "demo": True}), 400
    return jsonify({"demo": True, "item": record.to_dict()}), 201


@api_bp.get("/reports")
def list_reports():
    items = DisasterReport.query.order_by(DisasterReport.created_at.desc()).all()
    return jsonify({"count": len(items), "demo": True, "items": [r.to_dict() for r in items]})


@api_bp.post("/reports")
def post_reports():
    payload = request.get_json(silent=True) or {}
    try:
        record = create_disaster_report(payload)
    except (ValueError, TypeError) as extra:
        return jsonify({"error": str(extra), "demo": True}), 400
    return jsonify({"demo": True, "item": record.to_dict()}), 201


@api_bp.get("/stats")
def stats():
    return jsonify({**dashboard_stats(), "demo": True})


@api_bp.get("/simulation")
def get_simulation():
    return jsonify(simulation_state.to_dict())


@api_bp.post("/simulation")
def post_simulation():
    payload = request.get_json(silent=True) or {}
    simulation_state.apply(
        api_delay_ms=int(payload.get("api_delay_ms") or 0),
        db_delay_ms=int(payload.get("db_delay_ms") or 0),
        failure_probability=float(payload.get("failure_probability") or 0),
        service_unavailable=bool(payload.get("service_unavailable")),
    )
    return jsonify(simulation_state.to_dict())
