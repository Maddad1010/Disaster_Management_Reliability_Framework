from locust import HttpUser, between, task


class DisasterPortalUser(HttpUser):
    """Locust user that exercises the demo disaster portal APIs."""

    wait_time = between(0.1, 0.4)

    @task(4)
    def alerts(self) -> None:
        self.client.get("/api/alerts")

    @task(3)
    def disasters(self) -> None:
        self.client.get("/api/disasters")

    @task(2)
    def shelters(self) -> None:
        self.client.get("/api/shelters")

    @task(2)
    def rescue_list(self) -> None:
        self.client.get("/api/rescue-requests")

    @task(1)
    def reports(self) -> None:
        self.client.get("/api/reports")

    @task(1)
    def health(self) -> None:
        self.client.get("/api/health")
