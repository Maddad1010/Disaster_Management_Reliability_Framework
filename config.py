"""Application configuration for the Disaster Management Testing Framework.

Demonstration thresholds in this file are academic project defaults.
They are not industry-standard SLOs.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
DB_PATH = INSTANCE_DIR / "disaster_portal.db"


class Config:
    """Flask configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "sep-academic-demo-key-not-for-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"check_same_thread": False}}
    JSON_SORT_KEYS = False

    HOST = os.environ.get("APP_HOST", "0.0.0.0")
    PORT = int(os.environ.get("APP_PORT", "5000"))
    BASE_URL = os.environ.get("APP_BASE_URL", f"http://{HOST}:{PORT}")

    # Maximum concurrent async workers used by the in-app load engine.
    # Higher requested user counts are represented by extra requests per worker.
    MAX_ENGINE_WORKERS = int(os.environ.get("MAX_ENGINE_WORKERS", "250"))

    # --- Demonstration evaluation thresholds (project-defined) ---
    PASS_MAX_AVG_RESPONSE_MS = 500.0
    PASS_MAX_ERROR_RATE = 2.0
    PASS_MIN_SUCCESS_RATE = 98.0

    WARNING_MAX_AVG_RESPONSE_MS = 1000.0
    WARNING_MAX_ERROR_RATE = 5.0

    STRESS_BREAK_AVG_RESPONSE_MS = 1000.0
    STRESS_BREAK_ERROR_RATE = 5.0

    DEMO_NOTICE = "Academic Demonstration System — Not for Real Emergency Operations."


# Mutable runtime overrides loaded from Settings (cloned from Config defaults).
THRESHOLD_DEFAULTS = {
    "pass_max_avg_response_ms": Config.PASS_MAX_AVG_RESPONSE_MS,
    "pass_max_error_rate": Config.PASS_MAX_ERROR_RATE,
    "pass_min_success_rate": Config.PASS_MIN_SUCCESS_RATE,
    "warning_max_avg_response_ms": Config.WARNING_MAX_AVG_RESPONSE_MS,
    "warning_max_error_rate": Config.WARNING_MAX_ERROR_RATE,
    "stress_break_avg_response_ms": Config.STRESS_BREAK_AVG_RESPONSE_MS,
    "stress_break_error_rate": Config.STRESS_BREAK_ERROR_RATE,
}
