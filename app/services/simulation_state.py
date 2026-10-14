"""DEMO-only failure simulation controls."""

from __future__ import annotations

import threading


class SimulationState:
    """In-memory failure simulation (never affects real emergency systems)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.api_delay_ms: int = 0
        self.db_delay_ms: int = 0
        self.failure_probability: float = 0.0
        self.service_unavailable: bool = False

    def apply(
        self,
        api_delay_ms: int = 0,
        db_delay_ms: int = 0,
        failure_probability: float = 0.0,
        service_unavailable: bool = False,
    ) -> None:
        with self._lock:
            self.api_delay_ms = max(0, min(int(api_delay_ms), 5000))
            self.db_delay_ms = max(0, min(int(db_delay_ms), 5000))
            self.failure_probability = max(0.0, min(float(failure_probability), 100.0))
            self.service_unavailable = bool(service_unavailable)

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "api_delay_ms": self.api_delay_ms,
                "db_delay_ms": self.db_delay_ms,
                "failure_probability": self.failure_probability,
                "service_unavailable": self.service_unavailable,
                "notice": "DEMO / TESTING MODE ONLY",
            }


simulation_state = SimulationState()
