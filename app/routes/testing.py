"""Performance testing dashboard and control APIs."""

from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from config import Config, REPORT_DIR
from app.models.test_result import TestRun
from app.services.metrics_service import health_to_dict, read_system_health
from app.services.settings_service import get_thresholds, update_thresholds
from app.services.simulation_state import simulation_state
from app.services.testing_service import TestConfig, engine

testing_bp = Blueprint("testing", __name__)

TEST_TYPES = [
    ("load", "Load Test"),
    ("stress", "Stress Test"),
    ("spike", "Spike Test"),
    ("endurance", "Endurance Test"),
    ("reliability", "Reliability Test"),
    ("smoke", "Smoke Test"),
]

USER_PRESETS = [10, 50, 100, 500, 1000, 5000]
DURATION_PRESETS = [15, 30, 60, 300, 600, 1800]
ENDPOINTS = [
    "/api/alerts",
    "/api/disasters",
    "/api/shelters",
    "/api/rescue-requests",
    "/api/reports",
    "/api/health",
    "all",
]


@testing_bp.record_once
def _attach(state) -> None:  # noqa: ANN001
    engine.attach_app(state.app)


@testing_bp.get("/")
def configure():
    return render_template(
        "testing.html",
        page="testing",
        test_types=TEST_TYPES,
        user_presets=USER_PRESETS,
        duration_presets=DURATION_PRESETS,
        endpoints=ENDPOINTS,
        running=engine.is_running(),
        simulation=simulation_state.to_dict(),
    )


@testing_bp.post("/start")
def start_test():
    if engine.is_running():
        flash("A test is already running.", "warning")
        return redirect(url_for("testing.live_monitor"))
    test_type = (request.form.get("test_type") or "load").lower()
    allowed = {item[0] for item in TEST_TYPES}
    if test_type not in allowed:
        flash("Invalid test type.", "danger")
        return redirect(url_for("testing.configure"))
    try:
        users = int(request.form.get("users") or 100)
        duration = int(request.form.get("duration") or 60)
        spawn_rate = float(request.form.get("spawn_rate") or 10)
    except ValueError:
        flash("Invalid numeric configuration.", "danger")
        return redirect(url_for("testing.configure"))
    users = max(1, min(users, 5000))
    duration = max(5, min(duration, 1800))
    spawn_rate = max(1.0, min(spawn_rate, 500.0))
    endpoint = request.form.get("target_endpoint") or "/api/alerts"
    if endpoint not in ENDPOINTS:
        endpoint = "/api/alerts"
    base = current_app.config.get("BASE_URL") or Config.BASE_URL
    config = TestConfig(
        test_type=test_type,
        users=users,
        duration_seconds=duration,
        spawn_rate=spawn_rate,
        target_endpoint=endpoint,
        base_url=base,
    )
    engine.start(config, current_app._get_current_object())
    flash("Test started. Live metrics use real HTTP traffic.", "success")
    return redirect(url_for("testing.live_monitor"))


@testing_bp.post("/stop")
def stop_test():
    engine.stop()
    flash("Stop requested.", "info")
    return redirect(url_for("testing.live_monitor"))


@testing_bp.get("/live")
def live_monitor():
    return render_template("live_report.html", page="live", running=engine.is_running())


@testing_bp.get("/health")
def system_health_page():
    health = health_to_dict(read_system_health())
    return render_template("system_health.html", page="health", health=health)


@testing_bp.get("/history")
def history():
    runs = TestRun.query.order_by(TestRun.id.desc()).all()
    return render_template("history.html", page="history", runs=runs)


@testing_bp.get("/history/<public_id>")
def history_detail(public_id: str):
    run = TestRun.query.filter_by(public_id=public_id).first_or_404()
    samples = [s.to_dict() for s in run.samples]
    return render_template("history_detail.html", page="history", run=run, samples=samples)


@testing_bp.get("/settings")
def settings_page():
    return render_template(
        "settings.html",
        page="settings",
        thresholds=get_thresholds(),
        simulation=simulation_state.to_dict(),
    )


@testing_bp.post("/settings")
def save_settings():
    try:
        values = {
            "pass_max_avg_response_ms": float(request.form.get("pass_max_avg_response_ms") or 500),
            "pass_max_error_rate": float(request.form.get("pass_max_error_rate") or 2),
            "pass_min_success_rate": float(request.form.get("pass_min_success_rate") or 98),
            "warning_max_avg_response_ms": float(request.form.get("warning_max_avg_response_ms") or 1000),
            "warning_max_error_rate": float(request.form.get("warning_max_error_rate") or 5),
            "stress_break_avg_response_ms": float(request.form.get("stress_break_avg_response_ms") or 1000),
            "stress_break_error_rate": float(request.form.get("stress_break_error_rate") or 5),
        }
    except ValueError:
        flash("Invalid threshold values.", "danger")
        return redirect(url_for("testing.settings_page"))
    update_thresholds(values)
    flash("Demonstration thresholds updated.", "success")
    return redirect(url_for("testing.settings_page"))


@testing_bp.post("/simulation")
def apply_simulation():
    simulation_state.apply(
        api_delay_ms=int(request.form.get("api_delay_ms") or 0),
        db_delay_ms=int(request.form.get("db_delay_ms") or 0),
        failure_probability=float(request.form.get("failure_probability") or 0),
        service_unavailable=bool(request.form.get("service_unavailable")),
    )
    flash("Failure simulation applied (DEMO / TESTING MODE ONLY).", "warning")
    next_page = request.form.get("next") or "testing.configure"
    if next_page == "settings":
        return redirect(url_for("testing.settings_page"))
    return redirect(url_for("testing.configure"))


@testing_bp.get("/api/live-metrics")
def live_metrics():
    return jsonify(engine.live())


@testing_bp.get("/api/health")
def live_health():
    return jsonify(health_to_dict(read_system_health()))


@testing_bp.get("/reports/<path:filename>")
def download_report(filename: str):
    return send_from_directory(REPORT_DIR, filename, as_attachment=True)
