"""Disaster portal HTML routes."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models.disaster import Alert, Disaster
from app.models.report import DisasterReport
from app.models.rescue import RescueRequest
from app.models.shelter import Shelter
from app.services.disaster_service import (
    VALID_DISASTER_TYPES,
    VALID_PRIORITIES,
    VALID_SEVERITIES,
    create_disaster_report,
    create_rescue_request,
    dashboard_stats,
)

portal_bp = Blueprint("portal", __name__)

EMERGENCY_CONTACTS = [
    {"service": "Police", "number": "100", "note": "DEMO DATA"},
    {"service": "Fire", "number": "101", "note": "DEMO DATA"},
    {"service": "Ambulance", "number": "108", "note": "DEMO DATA"},
    {"service": "Disaster Management", "number": "1077", "note": "DEMO DATA"},
]


@portal_bp.route("/")
def dashboard():
    stats = dashboard_stats()
    disasters = Disaster.query.filter_by(status="Active").order_by(Disaster.occurred_at.desc()).all()
    alerts = Alert.query.filter_by(status="Active").order_by(Alert.created_at.desc()).limit(6).all()
    return render_template(
        "dashboard.html",
        stats=stats,
        disasters=disasters,
        alerts=alerts,
        page="dashboard",
    )


@portal_bp.route("/alerts")
def alerts():
    items = Alert.query.order_by(Alert.created_at.desc()).all()
    return render_template("alerts.html", alerts=items, page="alerts")


@portal_bp.route("/shelters")
def shelters():
    items = Shelter.query.order_by(Shelter.name).all()
    return render_template("shelters.html", shelters=items, page="shelters")


@portal_bp.route("/rescue", methods=["GET", "POST"])
def rescue():
    if request.method == "POST":
        try:
            create_rescue_request(
                {
                    "name": request.form.get("name"),
                    "phone": request.form.get("phone"),
                    "location": request.form.get("location"),
                    "people_count": request.form.get("people_count") or 1,
                    "emergency_type": request.form.get("emergency_type"),
                    "priority": request.form.get("priority"),
                    "description": request.form.get("description"),
                }
            )
            flash("Rescue request submitted (DEMO DATA — not a real dispatch).", "success")
            return redirect(url_for("portal.rescue"))
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
    items = RescueRequest.query.order_by(RescueRequest.created_at.desc()).all()
    return render_template(
        "rescue.html",
        requests=items,
        disaster_types=sorted(VALID_DISASTER_TYPES),
        priorities=sorted(VALID_PRIORITIES),
        page="rescue",
    )


@portal_bp.route("/reports", methods=["GET", "POST"])
def reports():
    if request.method == "POST":
        try:
            create_disaster_report(
                {
                    "disaster_type": request.form.get("disaster_type"),
                    "location": request.form.get("location"),
                    "severity": request.form.get("severity"),
                    "description": request.form.get("description"),
                    "affected_people": request.form.get("affected_people") or 0,
                }
            )
            flash("Disaster report recorded as DEMO DATA.", "success")
            return redirect(url_for("portal.reports"))
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
    items = DisasterReport.query.order_by(DisasterReport.created_at.desc()).all()
    return render_template(
        "reports.html",
        reports=items,
        disaster_types=sorted(VALID_DISASTER_TYPES),
        severities=list(VALID_SEVERITIES),
        page="reports",
    )


@portal_bp.route("/contacts")
def contacts():
    return render_template("contacts.html", contacts=EMERGENCY_CONTACTS, page="contacts")
