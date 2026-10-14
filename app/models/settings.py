"""Key/value settings stored in SQLite."""

from __future__ import annotations

from app.extensions import db


class AppSetting(db.Model):
    """Persistent configuration such as evaluation thresholds."""

    __tablename__ = "app_settings"

    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.String(200), nullable=False)
