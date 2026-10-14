"""Portal HTML workflow tests."""


def test_dashboard_renders(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"DISASTER" in response.data.upper() or b"Disaster" in response.data
    assert b"Academic Demonstration System" in response.data


def test_alerts_and_shelters_pages(client) -> None:
    assert client.get("/alerts").status_code == 200
    assert client.get("/shelters").status_code == 200
    assert client.get("/rescue").status_code == 200
    assert client.get("/reports").status_code == 200
    assert client.get("/contacts").status_code == 200


def test_submit_rescue_form(client) -> None:
    response = client.post(
        "/rescue",
        data={
            "name": "Portal Demo",
            "phone": "9000000100",
            "location": "Central Area",
            "people_count": "3",
            "emergency_type": "Flood",
            "priority": "Medium",
            "description": "Form workflow test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Portal Demo" in response.data


def test_testing_pages(client) -> None:
    assert client.get("/testing/").status_code == 200
    assert client.get("/testing/live").status_code == 200
    assert client.get("/testing/history").status_code == 200
    assert client.get("/testing/health").status_code == 200
    assert client.get("/testing/settings").status_code == 200
    metrics = client.get("/testing/api/live-metrics")
    assert metrics.status_code == 200
    body = metrics.get_json()
    assert "data_mode" in body
