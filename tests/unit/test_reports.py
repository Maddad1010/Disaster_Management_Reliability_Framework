"""Report generation unit tests."""

from datetime import datetime, timezone
from pathlib import Path

from app.models.test_result import TestRun
from app.services.report_service import generate_reports
from app.services.scoring_service import ScoreResult


def test_generate_reports(tmp_path, monkeypatch) -> None:
    import app.services.report_service as rs

    monkeypatch.setattr(rs, "REPORT_DIR", tmp_path)
    run = TestRun(
        public_id="T999",
        test_type="load",
        users=10,
        duration_seconds=5,
        spawn_rate=5,
        target_endpoint="/api/alerts",
        started_at=datetime.now(timezone.utc),
        total_requests=100,
        successful_requests=98,
        failed_requests=2,
        avg_response_ms=120,
        min_response_ms=40,
        max_response_ms=300,
        requests_per_second=20,
        error_rate=2,
        success_rate=98,
        avg_cpu=30,
        max_cpu=40,
        avg_memory=50,
        max_memory=55,
        performance_score=88,
        reliability_score=98,
        performance_label="GOOD",
        overall_status="WARNING",
    )
    run.id = 999
    score = ScoreResult(
        performance_score=88,
        performance_label="GOOD",
        reliability_score=98,
        overall_status="WARNING",
        response_points=30,
        error_points=20,
        throughput_points=10,
        cpu_points=8,
        memory_points=5,
    )
    samples = [
        {
            "elapsed_seconds": 1,
            "active_users": 10,
            "total_requests": 20,
            "rps": 20,
            "avg_response_ms": 100,
            "error_rate": 0,
            "cpu_percent": 20,
            "memory_percent": 40,
        }
    ]
    paths = generate_reports(run, samples, score)
    assert (tmp_path / paths["html"]).exists()
    assert (tmp_path / paths["json"]).exists()
    assert (tmp_path / paths["csv"]).exists()
    assert (tmp_path / paths["pdf"]).exists()
    html = Path(tmp_path / paths["html"]).read_text(encoding="utf-8")
    assert "T999" in html
    assert "PERFORMANCE TEST REPORT" in html
