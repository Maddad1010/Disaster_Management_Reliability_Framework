"""Unit tests for scoring and reliability helpers."""

from app.services.scoring_service import (
    calculate_error_rate,
    calculate_performance_score,
    calculate_reliability,
    calculate_success_rate,
    evaluate_overall_status,
)


def test_reliability_calculation() -> None:
    assert calculate_reliability(9950, 10000) == 99.5
    assert calculate_reliability(0, 0) == 0.0
    assert calculate_reliability(10, 10) == 100.0


def test_error_rate_calculation() -> None:
    assert calculate_error_rate(50, 10000) == 0.5
    assert calculate_error_rate(0, 100) == 0.0
    assert calculate_error_rate(5, 0) == 0.0


def test_success_rate() -> None:
    assert calculate_success_rate(98, 100) == 98.0


def test_performance_score_bounds() -> None:
    excellent, label, breakdown = calculate_performance_score(
        avg_response_ms=50,
        error_rate=0,
        requests_per_second=80,
        avg_cpu=20,
        avg_memory=30,
        configured_users=50,
    )
    assert excellent >= 90
    assert label == "EXCELLENT"
    assert breakdown["response_points"] == 40.0

    poor, poor_label, _ = calculate_performance_score(
        avg_response_ms=2500,
        error_rate=20,
        requests_per_second=0.1,
        avg_cpu=99,
        avg_memory=99,
        configured_users=1000,
    )
    assert poor < 20
    assert poor_label == "POOR"


def test_pass_warning_fail_thresholds() -> None:
    thresholds = {
        "pass_max_avg_response_ms": 500,
        "pass_max_error_rate": 2,
        "pass_min_success_rate": 98,
        "warning_max_avg_response_ms": 1000,
        "warning_max_error_rate": 5,
    }
    assert evaluate_overall_status(180, 0.2, 99.8, thresholds) == "PASS"
    assert evaluate_overall_status(650, 3.0, 97.0, thresholds) == "WARNING"
    assert evaluate_overall_status(1200, 8.0, 90.0, thresholds) == "FAIL"
