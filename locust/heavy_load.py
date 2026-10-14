"""Heavy load Locust shape."""

from locust import HttpUser, LoadTestShape, between, task


class HeavyUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task(3)
    def alerts(self) -> None:
        self.client.get("/api/alerts")

    @task(2)
    def disasters(self) -> None:
        self.client.get("/api/disasters")

    @task(1)
    def shelters(self) -> None:
        self.client.get("/api/shelters")


class HeavyLoadShape(LoadTestShape):
    def tick(self):  # type: ignore[no-untyped-def]
        t = self.get_run_time()
        if t < 30:
            return (100, 20)
        if t < 90:
            return (400, 40)
        return None
