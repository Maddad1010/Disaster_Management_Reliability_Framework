"""Spike load shape for Locust (optional standalone run)."""

from locust import HttpUser, LoadTestShape, between, task


class SpikeUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task
    def alerts(self) -> None:
        self.client.get("/api/alerts")

    @task
    def health(self) -> None:
        self.client.get("/api/health")


class SpikeShape(LoadTestShape):
    """50 users, then a sudden jump to 200 users (laptop-safe spike demo)."""

    def tick(self):  # type: ignore[no-untyped-def]
        t = self.get_run_time()
        if t < 20:
            return (50, 25)
        if t < 50:
            return (200, 150)
        if t < 70:
            return (50, 50)
        return None
