import json
import csv
import os
from datetime import datetime

def generate_reports(summary: dict, test_id: str):
    os.makedirs("reports", exist_ok=True)
    
    # Text/JSON
    report_data = {
        "test_id": test_id,
        "test_type": summary.get("type", "Load"),
        "date": datetime.now().isoformat(),
        "duration": summary.get("elapsed"),
        "users": summary.get("users"),
        "metrics": {
            "total_requests": summary.get("requests"),
            "successful_requests": summary.get("success"),
            "failed_requests": summary.get("failed"),
            "success_rate": summary.get("reliability_score"),
            "error_rate": summary.get("error_rate")
        },
        "performance": {
            "avg_response_time": summary.get("avg_response_ms"),
            "requests_per_second": summary.get("rps")
        },
        "resources": {
            "cpu": summary.get("cpu_usage"),
            "memory": summary.get("memory_usage")
        },
        "results": {
            "performance_score": summary.get("performance_score"),
            "reliability_score": summary.get("reliability_score")
        }
    }

    # Save JSON
    with open(f"reports/{test_id}.json", "w") as f:
        json.dump(report_data, f, indent=4)

    # Save CSV
    with open(f"reports/{test_id}.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Test ID", "Type", "Date", "Duration", "Users", "Requests", "Success Rate", "Avg Response", "CPU", "Memory", "Perf Score", "Rel Score"])
        writer.writerow([
            test_id, summary.get("type", "Load"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary.get("elapsed"), summary.get("users"), summary.get("requests"),
            f"{summary.get('reliability_score')}%", f"{summary.get('avg_response_ms')}ms",
            f"{summary.get('cpu_usage')}%", f"{summary.get('memory_usage')}%",
            summary.get('performance_score'), summary.get('reliability_score')
        ])

    # Save HTML
    html_content = f"""
    <html>
    <head><title>Test Report {test_id}</title></head>
    <body style="font-family: sans-serif;">
        <h1>Performance Test Report</h1>
        <hr/>
        <p><strong>Test ID:</strong> {test_id}</p>
        <p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Duration:</strong> {summary.get('elapsed')} seconds</p>
        <p><strong>Users:</strong> {summary.get('users')}</p>
        <hr/>
        <h3>Request Metrics</h3>
        <ul>
            <li>Total Requests: {summary.get('requests')}</li>
            <li>Successful: {summary.get('success')}</li>
            <li>Failed: {summary.get('failed')}</li>
            <li>Success Rate: {summary.get('reliability_score')}%</li>
        </ul>
        <hr/>
        <h3>Performance</h3>
        <ul>
            <li>Avg Response Time: {summary.get('avg_response_ms')} ms</li>
            <li>Requests per Second: {summary.get('rps')}</li>
        </ul>
        <hr/>
        <h3>Results</h3>
        <h2>Performance Score: {summary.get('performance_score')}/100</h2>
        <h2>Reliability Score: {summary.get('reliability_score')}%</h2>
    </body>
    </html>
    """
    with open(f"reports/{test_id}.html", "w") as f:
        f.write(html_content)
