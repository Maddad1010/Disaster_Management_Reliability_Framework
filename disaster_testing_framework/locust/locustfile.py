from locust import HttpUser, task, between

class PortalUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/health")

    @task(2)
    def view_alerts(self):
        self.client.get("/api/alerts")

    @task(2)
    def view_shelters(self):
        self.client.get("/api/shelters")

    @task(1)
    def submit_rescue(self):
        self.client.post("/api/rescue-requests", json={
            "name": "Locust User",
            "phone": "555-0000",
            "location": "Test Loc",
            "num_people": 2,
            "emergency_type": "Fire",
            "priority": "Medium",
            "description": "Load test generated request"
        })
