from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.services.testing_service import engine
from app.database import get_db
from app.models.test_result import TestResult
from app.config import settings
from app.services.report_service import generate_reports
from sqlalchemy.orm import Session
import json

router = APIRouter(prefix="/testing")
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def testing_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="testing.html")

@router.post("/start")
async def start_test(config: dict):
    test_id = engine.start_test(config)
    if not test_id:
        return {"error": "Test already running"}
    return {"status": "started", "test_id": test_id}

@router.post("/stop")
def stop_test(db: Session = Depends(get_db)):
    summary = engine.stop_test()
    engine._last_summary = summary  # ensure it's cached for the metrics endpoint
    # Save to db
    if summary.get("test_id"):
        res = TestResult(
            test_id=summary["test_id"],
            test_type=engine.config.get("type", "Load"),
            users=summary["users"],
            duration=int(summary["elapsed"]),
            avg_response_time=summary["avg_response_ms"],
            success_rate=summary["reliability_score"],
            status="PASS" if summary["performance_score"] > 80 else "WARNING"
        )
        db.add(res)
        db.commit()
        generate_reports(summary, summary["test_id"])
    return summary

@router.get("/metrics")
async def get_metrics():
    if engine.is_running:
        return engine.get_live_metrics()
    # Test finished (either naturally or stopped) - return cached summary with final scores
    if engine._last_summary is not None:
        return {**engine._last_summary, "running": False, "finished": True}
    return {"running": False, "finished": False}

@router.get("/history")
def get_history(request: Request, db: Session = Depends(get_db)):
    history = db.query(TestResult).order_by(TestResult.id.desc()).all()
    return templates.TemplateResponse(request=request, name="history.html", context={"history": history})

@router.post("/finalize")
def finalize_test(db: Session = Depends(get_db)):
    """Called by the frontend when it detects test has finished naturally.
    Saves the result to DB and generates report if not already done."""
    summary = engine._last_summary
    if not summary or not summary.get("test_id"):
        return {"status": "no_result"}
    # Check if already saved
    existing = db.query(TestResult).filter(TestResult.test_id == summary["test_id"]).first()
    if not existing:
        res = TestResult(
            test_id=summary["test_id"],
            test_type=engine.config.get("type", "Load"),
            users=summary["users"],
            duration=int(summary["elapsed"]),
            avg_response_time=summary["avg_response_ms"],
            success_rate=summary["reliability_score"],
            status="PASS" if summary["performance_score"] > 80 else "WARNING"
        )
        db.add(res)
        db.commit()
        generate_reports(summary, summary["test_id"])
    return {**summary, "status": "saved"}

@router.post("/simulate")
async def set_simulation(config: dict):
    settings.SIMULATION_DELAY_MS = config.get("delay", 0)
    settings.SIMULATION_FAILURE_PROB = config.get("probability", 0)
    return {"status": "updated"}
