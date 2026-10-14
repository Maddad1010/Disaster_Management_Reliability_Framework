"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db
from app.models.disaster import Alert, Disaster
from app.models.shelter import Shelter
from config import Config


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
    }


@pytest.fixture()
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(
            Disaster(
                disaster_type="Flood",
                severity="High",
                location="Test Ward",
                description="Unit-test flood [DEMO DATA]",
                affected_people=10,
                status="Active",
            )
        )
        db.session.add(
            Alert(
                title="Test alert",
                disaster_type="Flood",
                severity="High",
                location="Test Ward",
                description="Unit-test alert [DEMO DATA]",
                status="Active",
            )
        )
        db.session.add(
            Shelter(
                name="Test Shelter",
                location="Test Ward",
                capacity=100,
                occupied=40,
                status="OPEN",
            )
        )
        db.session.commit()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
