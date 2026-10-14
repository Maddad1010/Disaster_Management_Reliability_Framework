"""Persisted test run results and time-series samples."""

from __future__ import annotations

from datetime import datetime

from app.extensions import db


class TestRun(db.Model):
    """One performance/reliability test execution."""

    __tablename__ = "test_runs"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(20), unique=True, nullable=False)
    test_type = db.Column(db.String(40), nullable=False)
    users = db.Column(db.Integer, nullable=False, default=1)
    duration_seconds = db.Column(db.Integer, nullable=False, default=30)
    spawn_rate = db.Column(db.Float, nullable=False, default=10.0)
    target_endpoint = db.Column(db.String(120), nullable=False, default="/api/alerts")
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    run_status = db.Column(db.String(20), nullable=False, default="RUNNING")
    overall_status = db.Column(db.String(20), nullable=True)

    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    avg_response_ms = db.Column(db.Float, default=0.0)
    min_response_ms = db.Column(db.Float, default=0.0)
    max_response_ms = db.Column(db.Float, default=0.0)
    requests_per_second = db.Column(db.Float, default=0.0)
    error_rate = db.Column(db.Float, default=0.0)
    success_rate = db.Column(db.Float, default=0.0)

    avg_cpu = db.Column(db.Float, default=0.0)
    max_cpu = db.Column(db.Float, default=0.0)
    avg_memory = db.Column(db.Float, default=0.0)
    max_memory = db.Column(db.Float, default=0.0)

    performance_score = db.Column(db.Float, default=0.0)
    reliability_score = db.Column(db.Float, default=0.0)
    performance_label = db.Column(db.String(30), default="")
    breaking_point_users = db.Column(db.Integer, nullable=True)

    html_report = db.Column(db.String(260), nullable=True)
    json_report = db.Column(db.String(260), nullable=True)
    csv_report = db.Column(db.String(260), nullable=True)
    pdf_report = db.Column(db.String(260), nullable=True)

    samples = db.relationship(
        "TestSample", backref="test_run", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "public_id": self.public_id,
            "test_type": self.test_type,
            "users": self.users,
            "duration_seconds": self.duration_seconds,
            "spawn_rate": self.spawn_rate,
            "target_endpoint": self.target_endpoint,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "run_status": self.run_status,
            "overall_status": self.overall_status,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "avg_response_ms": self.avg_response_ms,
            "min_response_ms": self.min_response_ms,
            "max_response_ms": self.max_response_ms,
            "requests_per_second": self.requests_per_second,
            "error_rate": self.error_rate,
            "success_rate": self.success_rate,
            "avg_cpu": self.avg_cpu,
            "max_cpu": self.max_cpu,
            "avg_memory": self.avg_memory,
            "max_memory": self.max_memory,
            "performance_score": self.performance_score,
            "reliability_score": self.reliability_score,
            "performance_label": self.performance_label,
            "breaking_point_users": self.breaking_point_users,
            "html_report": self.html_report,
            "json_report": self.json_report,
            "csv_report": self.csv_report,
            "pdf_report": self.pdf_report,
        }


class TestSample(db.Model):
    """One-second snapshot of live metrics for charts and reports."""

    __tablename__ = "test_samples"

    id = db.Column(db.Integer, primary_key=True)
    test_run_id = db.Column(db.Integer, db.ForeignKey("test_runs.id"), nullable=False)
    elapsed_seconds = db.Column(db.Float, nullable=False)
    active_users = db.Column(db.Integer, default=0)
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    rps = db.Column(db.Float, default=0.0)
    avg_response_ms = db.Column(db.Float, default=0.0)
    error_rate = db.Column(db.Float, default=0.0)
    cpu_percent = db.Column(db.Float, default=0.0)
    memory_percent = db.Column(db.Float, default=0.0)
    memory_mb = db.Column(db.Float, default=0.0)

    def to_dict(self) -> dict:
        return {
            "elapsed_seconds": self.elapsed_seconds,
            "active_users": self.active_users,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "rps": self.rps,
            "avg_response_ms": self.avg_response_ms,
            "error_rate": self.error_rate,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_mb": self.memory_mb,
        }
