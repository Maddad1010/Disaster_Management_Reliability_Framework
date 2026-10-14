"""Project-defined performance and reliability scoring.

These formulas are academic demonstration metrics. They are not
industry-standard scores such as Apdex or official SLOs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScoreResult:
    performance_score: float
    performance_label: str
    reliability_score: float
    overall_status: str
    response_points: float
    error_points: float
    throughput_points: float
    cpu_points: float
    memory_points: float


def calculate_error_rate(failed: int, total: int) -> float:
    """Return error rate as a percentage."""
    if total <= 0:
        return 0.0
    return round((failed / total) * 100.0, 4)


def calculate_success_rate(successful: int, total: int) -> float:
    """Return success rate as a percentage."""
    if total <= 0:
        return 0.0
    return round((successful / total) * 100.0, 4)


def calculate_reliability(successful: int, total: int) -> float:
    """Reliability = successful / total * 100 (project-defined)."""
    return calculate_success_rate(successful, total)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def calculate_performance_score(
    avg_response_ms: float,
    error_rate: float,
    requests_per_second: float,
    avg_cpu: float,
    avg_memory: float,
    configured_users: int,
) -> tuple[float, str, dict[str, float]]:
    """Compute a 0–100 project-defined performance score.

    Weights:
      - Average response time: 40 points
      - Error rate: 30 points
      - Throughput vs expected users: 15 points
      - CPU usage: 10 points
      - Memory usage: 5 points
    """
    # Response: 40 at <= 80ms, 0 at >= 2000ms (linear in between).
    if avg_response_ms <= 80:
        response_points = 40.0
    elif avg_response_ms >= 2000:
        response_points = 0.0
    else:
        response_points = 40.0 * (1.0 - (avg_response_ms - 80.0) / (2000.0 - 80.0))

    # Error: 30 at 0%, 0 at >= 15%.
    if error_rate <= 0:
        error_points = 30.0
    elif error_rate >= 15:
        error_points = 0.0
    else:
        error_points = 30.0 * (1.0 - error_rate / 15.0)

    # Expected rough throughput: ~2 requests/user/second under light think-time.
    expected_rps = max(1.0, configured_users * 0.5)
    throughput_ratio = _clamp(requests_per_second / expected_rps, 0.0, 1.0)
    throughput_points = 15.0 * throughput_ratio

    # CPU: 10 at <= 40%, 0 at >= 95%.
    if avg_cpu <= 40:
        cpu_points = 10.0
    elif avg_cpu >= 95:
        cpu_points = 0.0
    else:
        cpu_points = 10.0 * (1.0 - (avg_cpu - 40.0) / 55.0)

    # Memory: 5 at <= 50%, 0 at >= 95%.
    if avg_memory <= 50:
        memory_points = 5.0
    elif avg_memory >= 95:
        memory_points = 0.0
    else:
        memory_points = 5.0 * (1.0 - (avg_memory - 50.0) / 45.0)

    score = round(
        _clamp(
            response_points + error_points + throughput_points + cpu_points + memory_points,
            0.0,
            100.0,
        ),
        1,
    )
    if score >= 90:
        label = "EXCELLENT"
    elif score >= 75:
        label = "GOOD"
    elif score >= 60:
        label = "FAIR"
    else:
        label = "POOR"

    breakdown = {
        "response_points": round(response_points, 2),
        "error_points": round(error_points, 2),
        "throughput_points": round(throughput_points, 2),
        "cpu_points": round(cpu_points, 2),
        "memory_points": round(memory_points, 2),
    }
    return score, label, breakdown


def evaluate_overall_status(
    avg_response_ms: float,
    error_rate: float,
    success_rate: float,
    thresholds: dict[str, float],
) -> str:
    """PASS / WARNING / FAIL using demonstration thresholds."""
    pass_rt = thresholds.get("pass_max_avg_response_ms", 500.0)
    pass_err = thresholds.get("pass_max_error_rate", 2.0)
    pass_ok = thresholds.get("pass_min_success_rate", 98.0)
    warn_rt = thresholds.get("warning_max_avg_response_ms", 1000.0)
    warn_err = thresholds.get("warning_max_error_rate", 5.0)

    if avg_response_ms < pass_rt and error_rate < pass_err and success_rate > pass_ok:
        return "PASS"
    if avg_response_ms > warn_rt or error_rate > warn_err:
        return "FAIL"
    return "WARNING"


def build_score_result(
    avg_response_ms: float,
    error_rate: float,
    success_rate: float,
    requests_per_second: float,
    avg_cpu: float,
    avg_memory: float,
    configured_users: int,
    successful: int,
    total: int,
    thresholds: dict[str, float],
) -> ScoreResult:
    """Combine scoring helpers into one result object."""
    perf, label, breakdown = calculate_performance_score(
        avg_response_ms,
        error_rate,
        requests_per_second,
        avg_cpu,
        avg_memory,
        configured_users,
    )
    reliability = calculate_reliability(successful, total)
    status = evaluate_overall_status(avg_response_ms, error_rate, success_rate, thresholds)
    return ScoreResult(
        performance_score=perf,
        performance_label=label,
        reliability_score=reliability,
        overall_status=status,
        **breakdown,
    )
