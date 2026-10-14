"""Flask application factory for the Disaster Management Portal."""

from __future__ import annotations

import logging
import random
import time
from flask import Flask, jsonify, request

from config import BASE_DIR, Config, INSTANCE_DIR, LOG_DIR, REPORT_DIR

logger = logging.getLogger("application")


def create_app(config_object: type[Config] | None = None) -> Flask:
    """Create and configure the Flask application."""
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "app" / "templates"),
        static_folder=str(BASE_DIR / "app" / "static"),
        instance_path=str(INSTANCE_DIR),
    )
    app.config.from_object(config_object or Config)

    from app.extensions import db

    db.init_app(app)

    from app.models import (  # noqa: F401
        Alert,
        AppSetting,
        Disaster,
        DisasterReport,
        RescueRequest,
        Shelter,
        TestRun,
        TestSample,
    )
    from app.routes.api import api_bp
    from app.routes.portal import portal_bp
    from app.routes.testing import testing_bp

    app.register_blueprint(portal_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(testing_bp, url_prefix="/testing")

    from app.services.simulation_state import simulation_state

    @app.before_request
    def apply_failure_simulation() -> tuple | None:
        """DEMO-only delays and failures for selected portal APIs."""
        path = request.path
        if not path.startswith("/api/"):
            return None
        if path in {"/api/health", "/api/simulation"}:
            return None

        delay_ms = simulation_state.api_delay_ms
        db_delay_ms = simulation_state.db_delay_ms
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
        if db_delay_ms > 0:
            time.sleep(db_delay_ms / 1000.0)

        if simulation_state.service_unavailable:
            return jsonify(
                {
                    "error": "Service temporarily unavailable",
                    "demo": True,
                    "notice": "DEMO / TESTING MODE ONLY",
                }
            ), 503

        if simulation_state.failure_probability > 0:
            roll = random.random() * 100.0
            if roll < simulation_state.failure_probability:
                logger.warning("Simulated API failure on %s", path)
                return jsonify(
                    {
                        "error": "Simulated random failure",
                        "demo": True,
                        "notice": "DEMO / TESTING MODE ONLY",
                    }
                ), 500
        return None

    @app.errorhandler(404)
    def not_found(_error):  # type: ignore[no-untyped-def]
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        from flask import render_template

        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(_error):  # type: ignore[no-untyped-def]
        logging.getLogger("errors").exception("Unhandled server error")
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        from flask import render_template

        return render_template("error.html", code=500, message="Internal server error"), 500

    @app.context_processor
    def inject_globals() -> dict:
        return {
            "demo_notice": Config.DEMO_NOTICE,
            "simulation": simulation_state.to_dict(),
        }

    with app.app_context():
        db.create_all()
        from app.services.settings_service import ensure_default_settings

        ensure_default_settings()

    return app
