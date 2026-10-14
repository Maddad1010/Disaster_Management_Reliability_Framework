"""Seed dummy disaster-management data for the academic demonstration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.logging_config import setup_logging
from app.models.disaster import Alert, Disaster
from app.models.report import DisasterReport
from app.models.rescue import RescueRequest
from app.models.shelter import Shelter

setup_logging()


DISASTERS = [
    ("Flood", "Severe", "Riverside Ward", "Dummy flood along the demonstration riverbank.", 4200, "Active", 2),
    ("Earthquake", "High", "North Hills", "Simulated magnitude event for academic testing.", 1800, "Active", 1),
    ("Cyclone", "Critical", "Coastal Belt", "Dummy cyclone watch for the demo coastal zone.", 9500, "Monitoring", 5),
    ("Forest Fire", "High", "Pine Ridge", "Controlled dummy wildfire scenario.", 320, "Active", 3),
    ("Landslide", "Moderate", "Hill Road KM 12", "Dummy slope failure blocking a demo highway.", 90, "Active", 4),
    ("Flood", "Moderate", "East Market", "Sample urban waterlogging record.", 1100, "Contained", 8),
    ("Earthquake", "Low", "Old Town", "Aftershock simulation only.", 40, "Resolved", 10),
    ("Cyclone", "High", "Harbor District", "Dummy storm surge advisory.", 2700, "Monitoring", 6),
    ("Forest Fire", "Moderate", "West Woodland", "Dummy smoke advisory.", 60, "Contained", 7),
    ("Landslide", "High", "Valley Pass", "Dummy debris flow affecting a demo village.", 210, "Active", 2),
    ("Flood", "Low", "South Canal", "Minor dummy overflow.", 25, "Resolved", 12),
    ("Earthquake", "Moderate", "University Area", "Training drill earthquake record.", 150, "Resolved", 15),
]

ALERTS = [
    ("Flood warning — Riverside Ward", "Flood", "Severe", "Riverside Ward", "Dummy evacuation advisory for low-lying demo streets."),
    ("Seismic monitoring — North Hills", "Earthquake", "High", "North Hills", "Dummy aftershock watch for academic use."),
    ("Cyclone watch — Coastal Belt", "Cyclone", "Critical", "Coastal Belt", "Simulated wind and surge alert."),
    ("Wildfire smoke — Pine Ridge", "Forest Fire", "High", "Pine Ridge", "Dummy air-quality warning."),
    ("Road closed — Hill Road KM 12", "Landslide", "Moderate", "Hill Road KM 12", "Dummy landslide road closure."),
    ("Shelter capacity notice", "Flood", "Moderate", "East Market", "Municipal School No. 3 approaching dummy capacity."),
    ("Harbor high-wave advisory", "Cyclone", "High", "Harbor District", "Dummy marine warning."),
    ("Valley Pass access limited", "Landslide", "High", "Valley Pass", "Dummy debris blocking access road."),
    ("Heat and smoke combination", "Forest Fire", "Moderate", "West Woodland", "Dummy combined hazard notice."),
    ("Canal overflow watch", "Flood", "Low", "South Canal", "Dummy drainage alert."),
    ("University drill complete", "Earthquake", "Low", "University Area", "Dummy all-clear after drill."),
    ("Coastal fishermen advisory", "Cyclone", "High", "Coastal Belt", "Dummy do-not-sail notice."),
]

SHELTERS = [
    ("Municipal School No. 3", "Central Area", 500, 320, "OPEN"),
    ("Community Hall East", "East Market", 300, 210, "OPEN"),
    ("Sports Complex Arena", "North Hills", 800, 640, "OPEN"),
    ("Harbor Relief Camp", "Harbor District", 450, 400, "LIMITED"),
    ("Valley Pass Tent Site", "Valley Pass", 200, 180, "LIMITED"),
    ("University Indoor Stadium", "University Area", 700, 120, "OPEN"),
    ("Riverside Transit Hub", "Riverside Ward", 350, 350, "FULL"),
    ("Pine Ridge Fire Camp", "Pine Ridge", 150, 40, "OPEN"),
    ("South Canal Warehouse", "South Canal", 250, 90, "OPEN"),
    ("Coastal Belt School", "Coastal Belt", 400, 275, "OPEN"),
    ("West Woodland Lodge", "West Woodland", 180, 20, "OPEN"),
    ("Old Town Library", "Old Town", 120, 15, "STANDBY"),
]

RESCUES = [
    ("Asha Demo", "9000000001", "Riverside Ward Block B", 4, "Flood", "High", "Family on first floor of dummy apartment."),
    ("Rahul Sample", "9000000002", "North Hills Lane 4", 2, "Earthquake", "Critical", "Trapped in simulated debris drill."),
    ("Meera Test", "9000000003", "Coastal Belt Jetty", 6, "Cyclone", "High", "Dummy fishing crew needs transport."),
    ("Imran Dummy", "9000000004", "Pine Ridge Cabin 2", 3, "Forest Fire", "High", "Smoke inhalation scenario."),
    ("Kavya Example", "9000000005", "Hill Road KM 12", 5, "Landslide", "Critical", "Vehicle blocked by dummy slide."),
    ("Omar Demo", "9000000006", "East Market Lane", 8, "Flood", "Medium", "Shop staff on rooftop (dummy)."),
    ("Nina Sample", "9000000007", "Harbor District Pier", 2, "Cyclone", "Medium", "Dummy stranded tourists."),
    ("Vikram Test", "9000000008", "Valley Pass Hamlet", 11, "Landslide", "High", "Cut off by dummy debris."),
    ("Sara Dummy", "9000000009", "University Hostel C", 1, "Earthquake", "Low", "Minor injury drill."),
    ("Lee Example", "9000000010", "South Canal Bridge", 3, "Flood", "Medium", "Dummy stalled bus passengers."),
    ("Priya Demo", "9000000011", "West Woodland Trail", 2, "Forest Fire", "High", "Hikers in dummy smoke zone."),
    ("Arun Sample", "9000000012", "Old Town Square", 4, "Earthquake", "Low", "Need welfare check (dummy)."),
]

REPORTS = [
    ("Flood", "Riverside Ward", "Severe", "Water entered dummy ground-floor shops.", 80),
    ("Earthquake", "North Hills", "High", "Cracks reported on demo municipal building.", 12),
    ("Cyclone", "Coastal Belt", "Critical", "Dummy roof sheets flying in high wind.", 40),
    ("Forest Fire", "Pine Ridge", "High", "Dummy fire spotted on west slope.", 0),
    ("Landslide", "Hill Road KM 12", "Moderate", "Boulders on dummy carriageway.", 0),
    ("Flood", "East Market", "Moderate", "Knee-deep dummy waterlogging.", 15),
    ("Cyclone", "Harbor District", "High", "Dummy boats torn from moorings.", 6),
    ("Landslide", "Valley Pass", "High", "Hamlet access lost in dummy scenario.", 25),
    ("Forest Fire", "West Woodland", "Moderate", "Smoke reducing dummy visibility.", 0),
    ("Earthquake", "University Area", "Low", "Drill report — no real damage.", 0),
]


def seed() -> None:
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        now = datetime.now(timezone.utc)
        for dtype, sev, loc, desc, people, status, days in DISASTERS:
            db.session.add(
                Disaster(
                    disaster_type=dtype,
                    severity=sev,
                    location=loc,
                    description=desc + " [DEMO DATA]",
                    affected_people=people,
                    status=status,
                    occurred_at=now - timedelta(days=days),
                    is_demo=True,
                )
            )
        for title, dtype, sev, loc, desc in ALERTS:
            db.session.add(
                Alert(
                    title=title,
                    disaster_type=dtype,
                    severity=sev,
                    location=loc,
                    description=desc + " [DEMO DATA]",
                    status="Active",
                    created_at=now - timedelta(hours=len(title) % 12),
                    is_demo=True,
                )
            )
        for name, loc, cap, occ, status in SHELTERS:
            db.session.add(
                Shelter(
                    name=name,
                    location=loc,
                    capacity=cap,
                    occupied=occ,
                    status=status,
                    is_demo=True,
                )
            )
        statuses = ["Pending", "Assigned", "In Progress", "Resolved"]
        for i, row in enumerate(RESCUES):
            name, phone, loc, people, etype, pri, desc = row
            db.session.add(
                RescueRequest(
                    name=name,
                    phone=phone,
                    location=loc,
                    people_count=people,
                    emergency_type=etype,
                    priority=pri,
                    description=desc + " [DEMO DATA]",
                    status=statuses[i % len(statuses)],
                    created_at=now - timedelta(hours=i),
                    is_demo=True,
                )
            )
        for dtype, loc, sev, desc, people in REPORTS:
            db.session.add(
                DisasterReport(
                    disaster_type=dtype,
                    location=loc,
                    severity=sev,
                    description=desc + " [DEMO DATA]",
                    affected_people=people,
                    status="Submitted",
                    created_at=now,
                    is_demo=True,
                )
            )
        db.session.commit()
        from app.services.settings_service import ensure_default_settings

        ensure_default_settings()
        print("Database seeded with dummy disaster data.")
        print("Academic Demonstration System — Not for Real Emergency Operations.")


if __name__ == "__main__":
    seed()
