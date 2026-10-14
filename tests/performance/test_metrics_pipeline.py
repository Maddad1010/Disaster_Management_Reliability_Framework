"""Lightweight in-process performance helper checks.

Full concurrent load is demonstrated via the running app and Locust.
These tests confirm metric wiring without requiring a live TCP server.
"""

from app.services.scoring_service import build_score_result
from app.services.testing_service import LOAD_ENDPOINTS, SMOKE_ENDPOINTS, demo_metrics_payload


def test_smoke_and_load_endpoint_lists() -> None:
    assert any(path == "/api/health" for _, path in SMOKE_ENDPOINTS)
    assert "/api/alerts" in LOAD_ENDPOINTS


def test_demo_metrics_are_labeled() -> None:
    payload = demo_metrics_payload()
    assert payload["data_mode"] == "DEMO DATA"
    assert "DEMO" in payload["message"]


def test_scores_come_from_metrics_not_constants() -> None:
    a = build_score_result(
        avg_response_ms=100,
        error_rate=0.5,
        success_rate=99.5,
        requests_per_second=40,
        avg_cpu=30,
        avg_memory=40,
        configured_users=50,
        successful=995,
        total=1000,
        thresholds={
            "pass_max_avg_response_ms": 500,
            "pass_max_error_rate": 2,
            "pass_min_success_rate": 98,
            "warning_max_avg_response_ms": 1000,
            "warning_max_error_rate": 5,
        },
    )
    b = build_score_result(
        avg_response_ms=900,
        error_rate=4,
        success_rate=96,
        requests_per_second=5,
        avg_cpu=80,
        avg_memory=80,
        configured_users=500,
        successful=960,
        total=1000,
        thresholds={
            "pass_max_avg_response_ms": 500,
            "pass_max_error_rate": 2,
            "pass_min_success_rate": 98,
            "warning_max_avg_response_ms": 1000,
            "warning_max_error_rate": 5,
        },
    )
    assert a.performance_score != b.performance_score
    assert a.reliability_score == 99.5
    assert b.reliability_score == 96.0
    assert a.overall_status == "PASS"
    assert b.overall_status == "WARNING"
