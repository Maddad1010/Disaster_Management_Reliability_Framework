"""API integration tests."""


def test_health_api(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["demo"] is True


def test_disasters_alerts_shelters(client) -> None:
    for path in ("/api/disasters", "/api/alerts", "/api/shelters", "/api/rescue-requests", "/api/reports"):
        response = client.get(path)
        assert response.status_code == 200
        body = response.get_json()
        assert "items" in body
        assert body["demo"] is True


def test_post_rescue_validation(client) -> None:
    bad = client.post("/api/rescue-requests", json={})
    assert bad.status_code == 400
    ok = client.post(
        "/api/rescue-requests",
        json={
            "name": "Demo User",
            "phone": "9000000999",
            "location": "Test Ward",
            "people_count": 2,
            "emergency_type": "Flood",
            "priority": "High",
            "description": "Dummy rescue for tests",
        },
    )
    assert ok.status_code == 201
    assert ok.get_json()["item"]["status"] == "Pending"


def test_post_report_validation(client) -> None:
    bad = client.post("/api/reports", json={"disaster_type": "Unknown"})
    assert bad.status_code == 400
    ok = client.post(
        "/api/reports",
        json={
            "disaster_type": "Flood",
            "location": "Test Ward",
            "severity": "High",
            "description": "Dummy report",
            "affected_people": 3,
        },
    )
    assert ok.status_code == 201


def test_simulation_endpoint(client) -> None:
    response = client.post(
        "/api/simulation",
        json={"api_delay_ms": 5, "failure_probability": 0, "db_delay_ms": 0},
    )
    assert response.status_code == 200
    assert response.get_json()["api_delay_ms"] == 5
    client.post("/api/simulation", json={"api_delay_ms": 0, "failure_probability": 0})
