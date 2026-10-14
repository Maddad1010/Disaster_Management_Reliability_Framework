"""Persistent evaluation threshold settings."""

from __future__ import annotations

from config import THRESHOLD_DEFAULTS
from app.extensions import db
from app.models.settings import AppSetting


def ensure_default_settings() -> None:
    """Insert default demonstration thresholds if missing."""
    for key, value in THRESHOLD_DEFAULTS.items():
        existing = db.session.get(AppSetting, key)
        if existing is None:
            db.session.add(AppSetting(key=key, value=str(value)))
    db.session.commit()


def get_thresholds() -> dict[str, float]:
    """Return current demonstration thresholds."""
    ensure_default_settings()
    result: dict[str, float] = {}
    for key, default in THRESHOLD_DEFAULTS.items():
        row = db.session.get(AppSetting, key)
        try:
            result[key] = float(row.value) if row else float(default)
        except (TypeError, ValueError):
            result[key] = float(default)
    return result


def update_thresholds(values: dict[str, float]) -> dict[str, float]:
    """Update allowed threshold keys and return the new map."""
    ensure_default_settings()
    for key, value in values.items():
        if key not in THRESHOLD_DEFAULTS:
            continue
        row = db.session.get(AppSetting, key)
        if row is None:
            row = AppSetting(key=key, value=str(value))
            db.session.add(row)
        else:
            row.value = str(value)
    db.session.commit()
    return get_thresholds()
