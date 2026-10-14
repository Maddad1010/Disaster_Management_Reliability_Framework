"""HTML, JSON, CSV, and PDF report generation from real test metrics."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from config import REPORT_DIR
from app.models.test_result import TestRun
from app.services.scoring_service import ScoreResult


def generate_reports(run: TestRun, samples: list[dict], score: ScoreResult) -> dict[str, str]:
    """Write report files and return relative paths."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{run.public_id}_{run.test_type}_{run.id}"
    html_path = REPORT_DIR / f"{stem}.html"
    json_path = REPORT_DIR / f"{stem}.json"
    csv_path = REPORT_DIR / f"{stem}.csv"
    pdf_path = REPORT_DIR / f"{stem}.pdf"

    payload = _payload(run, samples, score)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_csv(csv_path, run, samples)
    html_path.write_text(_html(payload, samples), encoding="utf-8")
    _write_pdf(pdf_path, payload)
    return {
        "html": str(html_path.name),
        "json": str(json_path.name),
        "csv": str(csv_path.name),
        "pdf": str(pdf_path.name),
    }


def _payload(run: TestRun, samples: list[dict], score: ScoreResult) -> dict:
    return {
        "title": "PERFORMANCE TEST REPORT",
        "notice": "Academic Demonstration System — Not for Real Emergency Operations.",
        "scoring_notice": (
            "Performance Score and PASS/WARNING/FAIL thresholds are project-defined "
            "demonstration metrics, not industry standards."
        ),
        "test_id": run.public_id,
        "test_type": run.test_type,
        "date": (run.started_at or datetime.utcnow()).isoformat(),
        "duration_seconds": run.duration_seconds,
        "users": run.users,
        "spawn_rate": run.spawn_rate,
        "target_endpoint": run.target_endpoint,
        "request_metrics": {
            "total_requests": run.total_requests,
            "successful_requests": run.successful_requests,
            "failed_requests": run.failed_requests,
            "success_rate": run.success_rate,
            "error_rate": run.error_rate,
        },
        "performance": {
            "average_response_ms": run.avg_response_ms,
            "minimum_response_ms": run.min_response_ms,
            "maximum_response_ms": run.max_response_ms,
            "requests_per_second": run.requests_per_second,
        },
        "system_resources": {
            "average_cpu": run.avg_cpu,
            "maximum_cpu": run.max_cpu,
            "average_memory": run.avg_memory,
            "maximum_memory": run.max_memory,
        },
        "result": {
            "performance_score": run.performance_score,
            "performance_label": run.performance_label,
            "reliability_score": run.reliability_score,
            "overall_status": run.overall_status,
            "breaking_point_users": run.breaking_point_users,
            "score_breakdown": {
                "response_points": score.response_points,
                "error_points": score.error_points,
                "throughput_points": score.throughput_points,
                "cpu_points": score.cpu_points,
                "memory_points": score.memory_points,
            },
        },
        "samples": samples,
    }


def _write_csv(path: Path, run: TestRun, samples: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["PERFORMANCE TEST REPORT", run.public_id])
        writer.writerow(["Notice", "Academic Demonstration System — Not for Real Emergency Operations."])
        writer.writerow([])
        writer.writerow(["Field", "Value"])
        writer.writerow(["Test Type", run.test_type])
        writer.writerow(["Users", run.users])
        writer.writerow(["Duration (s)", run.duration_seconds])
        writer.writerow(["Total Requests", run.total_requests])
        writer.writerow(["Successful", run.successful_requests])
        writer.writerow(["Failed", run.failed_requests])
        writer.writerow(["Success Rate %", run.success_rate])
        writer.writerow(["Error Rate %", run.error_rate])
        writer.writerow(["Avg Response ms", run.avg_response_ms])
        writer.writerow(["Min Response ms", run.min_response_ms])
        writer.writerow(["Max Response ms", run.max_response_ms])
        writer.writerow(["Requests/Second", run.requests_per_second])
        writer.writerow(["Avg CPU %", run.avg_cpu])
        writer.writerow(["Max CPU %", run.max_cpu])
        writer.writerow(["Avg Memory %", run.avg_memory])
        writer.writerow(["Max Memory %", run.max_memory])
        writer.writerow(["Performance Score", run.performance_score])
        writer.writerow(["Reliability Score", run.reliability_score])
        writer.writerow(["Overall Status", run.overall_status])
        writer.writerow([])
        writer.writerow(
            [
                "elapsed_seconds",
                "active_users",
                "total_requests",
                "rps",
                "avg_response_ms",
                "error_rate",
                "cpu_percent",
                "memory_percent",
            ]
        )
        for sample in samples:
            writer.writerow(
                [
                    sample.get("elapsed_seconds"),
                    sample.get("active_users"),
                    sample.get("total_requests"),
                    sample.get("rps"),
                    sample.get("avg_response_ms"),
                    sample.get("error_rate"),
                    sample.get("cpu_percent"),
                    sample.get("memory_percent"),
                ]
            )


def _html(payload: dict, samples: list[dict]) -> str:
    times = [s.get("elapsed_seconds", 0) for s in samples]
    resp = [s.get("avg_response_ms", 0) for s in samples]
    rps = [s.get("rps", 0) for s in samples]
    err = [s.get("error_rate", 0) for s in samples]
    cpu = [s.get("cpu_percent", 0) for s in samples]
    mem = [s.get("memory_percent", 0) for s in samples]
    result = payload["result"]
    req = payload["request_metrics"]
    perf = payload["performance"]
    sysr = payload["system_resources"]
    status = result["overall_status"]
    color = {"PASS": "#1b8a4a", "WARNING": "#d4a017", "FAIL": "#c0392b"}.get(status, "#4a6fa5")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Report {payload["test_id"]}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
  <style>
    body {{ font-family: Segoe UI, sans-serif; background: #0b1d36; color: #e8eef7; margin: 0; padding: 24px; }}
    .card {{ background: #132844; border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
    h1, h2 {{ margin-top: 0; }}
    .badge {{ display: inline-block; padding: 6px 14px; border-radius: 999px; background: {color}; font-weight: 700; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    .notice {{ color: #f0c36d; font-size: 0.9rem; }}
    table {{ width: 100%; border-collapse: collapse; }}
    td {{ padding: 6px 8px; border-bottom: 1px solid #234; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>PERFORMANCE TEST REPORT</h1>
    <p class="notice">{payload["notice"]}</p>
    <p class="notice">{payload["scoring_notice"]}</p>
    <p>Test ID: <strong>{payload["test_id"]}</strong> &nbsp; Type: <strong>{payload["test_type"]}</strong></p>
    <p>Date: {payload["date"]} &nbsp; Duration: {payload["duration_seconds"]}s &nbsp; Users: {payload["users"]}</p>
    <p>Overall Status: <span class="badge">{status}</span></p>
  </div>
  <div class="grid">
    <div class="card">
      <h2>Request Metrics</h2>
      <table>
        <tr><td>Total Requests</td><td>{req["total_requests"]}</td></tr>
        <tr><td>Successful</td><td>{req["successful_requests"]}</td></tr>
        <tr><td>Failed</td><td>{req["failed_requests"]}</td></tr>
        <tr><td>Success Rate</td><td>{req["success_rate"]}%</td></tr>
        <tr><td>Error Rate</td><td>{req["error_rate"]}%</td></tr>
      </table>
    </div>
    <div class="card">
      <h2>Performance</h2>
      <table>
        <tr><td>Average Response</td><td>{perf["average_response_ms"]} ms</td></tr>
        <tr><td>Minimum</td><td>{perf["minimum_response_ms"]} ms</td></tr>
        <tr><td>Maximum</td><td>{perf["maximum_response_ms"]} ms</td></tr>
        <tr><td>Requests/Second</td><td>{perf["requests_per_second"]}</td></tr>
      </table>
    </div>
    <div class="card">
      <h2>System Resources</h2>
      <table>
        <tr><td>Average CPU</td><td>{sysr["average_cpu"]}%</td></tr>
        <tr><td>Maximum CPU</td><td>{sysr["maximum_cpu"]}%</td></tr>
        <tr><td>Average Memory</td><td>{sysr["average_memory"]}%</td></tr>
        <tr><td>Maximum Memory</td><td>{sysr["maximum_memory"]}%</td></tr>
      </table>
    </div>
    <div class="card">
      <h2>Result</h2>
      <p>Performance Score: <strong>{result["performance_score"]}/100</strong> ({result["performance_label"]})</p>
      <p>Reliability Score: <strong>{result["reliability_score"]}%</strong></p>
      <p>Reliability = Successful Requests / Total Requests × 100</p>
    </div>
  </div>
  <div class="grid">
    <div class="card"><canvas id="rt"></canvas></div>
    <div class="card"><canvas id="rps"></canvas></div>
    <div class="card"><canvas id="err"></canvas></div>
    <div class="card"><canvas id="cpu"></canvas></div>
    <div class="card"><canvas id="mem"></canvas></div>
    <div class="card"><canvas id="pie"></canvas></div>
  </div>
  <script>
    const times = {json.dumps(times)};
    const line = (id, label, data, color) => new Chart(document.getElementById(id), {{
      type: 'line', data: {{ labels: times, datasets: [{{ label, data, borderColor: color, tension: 0.25, fill: false }}] }},
      options: {{ plugins: {{ legend: {{ labels: {{ color: '#e8eef7' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#9bb' }} }}, y: {{ ticks: {{ color: '#9bb' }} }} }} }}
    }});
    line('rt', 'Response Time (ms)', {json.dumps(resp)}, '#f39c12');
    line('rps', 'Requests / Second', {json.dumps(rps)}, '#2ecc71');
    line('err', 'Error Rate %', {json.dumps(err)}, '#e74c3c');
    line('cpu', 'CPU %', {json.dumps(cpu)}, '#5dade2');
    line('mem', 'Memory %', {json.dumps(mem)}, '#af7ac5');
    new Chart(document.getElementById('pie'), {{
      type: 'doughnut',
      data: {{ labels: ['Success', 'Failure'], datasets: [{{ data: [{req["successful_requests"]}, {req["failed_requests"]}], backgroundColor: ['#27ae60', '#c0392b'] }}] }},
      options: {{ plugins: {{ legend: {{ labels: {{ color: '#e8eef7' }} }} }} }}
    }});
  </script>
</body>
</html>
"""


def _write_pdf(path: Path, payload: dict) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - inch
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, y, "PERFORMANCE TEST REPORT")
    y -= 22
    c.setFont("Helvetica", 9)
    c.drawString(inch, y, payload["notice"])
    y -= 28
    lines = [
        f"Test ID: {payload['test_id']}",
        f"Test Type: {payload['test_type']}",
        f"Date: {payload['date']}",
        f"Duration: {payload['duration_seconds']} s",
        f"Users: {payload['users']}",
        "",
        "REQUEST METRICS",
        f"Total Requests: {payload['request_metrics']['total_requests']}",
        f"Successful: {payload['request_metrics']['successful_requests']}",
        f"Failed: {payload['request_metrics']['failed_requests']}",
        f"Success Rate: {payload['request_metrics']['success_rate']}%",
        f"Error Rate: {payload['request_metrics']['error_rate']}%",
        "",
        "PERFORMANCE",
        f"Average Response Time: {payload['performance']['average_response_ms']} ms",
        f"Minimum: {payload['performance']['minimum_response_ms']} ms",
        f"Maximum: {payload['performance']['maximum_response_ms']} ms",
        f"Requests/Second: {payload['performance']['requests_per_second']}",
        "",
        "SYSTEM RESOURCES",
        f"Average CPU: {payload['system_resources']['average_cpu']}%",
        f"Maximum CPU: {payload['system_resources']['maximum_cpu']}%",
        f"Average Memory: {payload['system_resources']['average_memory']}%",
        f"Maximum Memory: {payload['system_resources']['maximum_memory']}%",
        "",
        "RESULT",
        f"Performance Score: {payload['result']['performance_score']}/100 ({payload['result']['performance_label']})",
        f"Reliability Score: {payload['result']['reliability_score']}%",
        f"Overall Status: {payload['result']['overall_status']}",
        "",
        payload["scoring_notice"],
    ]
    c.setFont("Helvetica", 11)
    for line in lines:
        if y < inch:
            c.showPage()
            y = height - inch
            c.setFont("Helvetica", 11)
        c.drawString(inch, y, line[:110])
        y -= 16
    c.save()
