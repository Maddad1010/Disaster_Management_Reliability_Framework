"""In-process performance and reliability testing engine.

Generates real HTTP requests against the running portal APIs, collects
latency/error metrics, samples CPU/RAM, and persists results.
"""

from __future__ import annotations

import asyncio
import logging
import math
import statistics
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

from config import Config
from app.services.metrics_service import health_to_dict, read_system_health
from app.services.scoring_service import (
    calculate_error_rate,
    calculate_success_rate,
    build_score_result,
)

logger = logging.getLogger("testing")

SMOKE_ENDPOINTS = [
    ("GET", "/api/health"),
    ("GET", "/api/disasters"),
    ("GET", "/api/alerts"),
    ("GET", "/api/shelters"),
    ("GET", "/api/rescue-requests"),
    ("GET", "/api/reports"),
]

LOAD_ENDPOINTS = [
    "/api/health",
    "/api/disasters",
    "/api/alerts",
    "/api/shelters",
    "/api/rescue-requests",
    "/api/reports",
]

STRESS_STAGES = [100, 500, 1000, 2000, 5000]


@dataclass
class TestConfig:
    test_type: str
    users: int = 100
    duration_seconds: int = 60
    spawn_rate: float = 10.0
    target_endpoint: str = "/api/alerts"
    base_url: str = ""


@dataclass
class LiveMetrics:
    data_mode: str = "DEMO DATA"
    state: str = "idle"
    test_id: str | None = None
    test_type: str = ""
    active_users: int = 0
    configured_users: int = 0
    elapsed_seconds: float = 0.0
    duration_seconds: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_ms: float = 0.0
    min_response_ms: float = 0.0
    max_response_ms: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 0.0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_percent: float = 0.0
    net_mb_s: float = 0.0
    system_status: str = "HEALTHY"
    performance_score: float = 0.0
    performance_label: str = ""
    reliability_score: float = 0.0
    overall_status: str = ""
    breaking_point_users: int | None = None
    smoke_results: list[dict] = field(default_factory=list)
    series: dict[str, list] = field(default_factory=dict)
    message: str = "No live test is running. Charts show labeled demo samples."

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_mode": self.data_mode,
            "state": self.state,
            "test_id": self.test_id,
            "test_type": self.test_type,
            "active_users": self.active_users,
            "configured_users": self.configured_users,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "duration_seconds": self.duration_seconds,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "avg_response_ms": round(self.avg_response_ms, 2),
            "min_response_ms": round(self.min_response_ms, 2),
            "max_response_ms": round(self.max_response_ms, 2),
            "requests_per_second": round(self.requests_per_second, 2),
            "error_rate": round(self.error_rate, 3),
            "success_rate": round(self.success_rate, 3),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_mb": self.memory_mb,
            "disk_percent": self.disk_percent,
            "net_mb_s": self.net_mb_s,
            "system_status": self.system_status,
            "performance_score": self.performance_score,
            "performance_label": self.performance_label,
            "reliability_score": self.reliability_score,
            "overall_status": self.overall_status,
            "breaking_point_users": self.breaking_point_users,
            "smoke_results": self.smoke_results,
            "series": self.series,
            "message": self.message,
        }


def demo_metrics_payload() -> dict[str, Any]:
    """Labeled sample metrics so the dashboard is never empty when idle."""
    times = list(range(0, 30))
    return LiveMetrics(
        data_mode="DEMO DATA",
        state="idle",
        test_type="sample",
        active_users=0,
        series={
            "time": times,
            "response": [120 + int(40 * math.sin(i / 4)) for i in times],
            "rps": [40 + int(10 * math.cos(i / 3)) for i in times],
            "error_rate": [0.8 + 0.4 * math.sin(i / 5) for i in times],
            "cpu": [28 + int(8 * math.sin(i / 6)) for i in times],
            "memory": [45 + int(4 * math.cos(i / 7)) for i in times],
            "users": [0 for _ in times],
        },
        cpu_percent=32.0,
        memory_percent=48.0,
        memory_mb=0.0,
        success_rate=99.0,
        error_rate=1.0,
        avg_response_ms=145.0,
        message="DEMO DATA — start a test to replace this with LIVE TEST DATA.",
    ).to_dict()


class TestingEngine:
    """Singleton-style engine executed in a background thread."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._user_stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._flask_app = None
        self.metrics = demo_metrics_payload()
        self.latencies: deque[float] = deque(maxlen=20000)
        self.recent_window: deque[tuple[float, bool]] = deque(maxlen=5000)
        self.samples: list[dict] = []
        self.config: TestConfig | None = None
        self.db_run_id: int | None = None

    def attach_app(self, app) -> None:  # noqa: ANN001
        self._flask_app = app

    def is_running(self) -> bool:
        with self._lock:
            return self.metrics.get("state") == "running"

    def start(self, config: TestConfig, flask_app) -> dict:  # noqa: ANN001
        if self.is_running():
            raise RuntimeError("A test is already running")
        self._flask_app = flask_app
        self.config = config
        self._stop.clear()
        self._user_stop.clear()
        self.latencies.clear()
        self.recent_window.clear()
        self.samples = []
        self._thread = threading.Thread(
            target=self._thread_main, name="testing-engine", daemon=True
        )
        self._thread.start()
        logger.info(
            "Test started type=%s users=%s duration=%s endpoint=%s",
            config.test_type,
            config.users,
            config.duration_seconds,
            config.target_endpoint,
        )
        return {"ok": True, "message": "Test started"}

    def stop(self) -> dict:
        if not self.is_running():
            return {"ok": False, "message": "No test is running"}
        self._stop.set()
        self._user_stop.set()
        logger.info("Test stop requested")
        return {"ok": True, "message": "Stop requested"}

    def live(self) -> dict:
        with self._lock:
            payload = dict(self.metrics)
        if payload.get("state") != "running":
            health = health_to_dict(read_system_health())
            payload["cpu_percent"] = health["cpu_percent"]
            payload["memory_percent"] = health["memory_percent"]
            payload["memory_mb"] = health["memory_used_mb"]
            payload["disk_percent"] = health["disk_percent"]
            payload["net_mb_s"] = health["net_mb_s"]
            payload["system_status"] = health["status"]
            if payload.get("state") == "idle":
                payload["data_mode"] = "DEMO DATA"
        return payload

    def _thread_main(self) -> None:
        try:
            asyncio.run(self._async_main())
        except Exception:
            logger.exception("Testing engine crashed")
            logging.getLogger("errors").exception("Testing engine crashed")
            with self._lock:
                self.metrics["state"] = "error"
                self.metrics["message"] = "Testing engine encountered an error"

    async def _async_main(self) -> None:
        assert self.config is not None
        cfg = self.config
        public_id = self._create_db_run(cfg)
        start = time.perf_counter()

        with self._lock:
            self.metrics = {
                "data_mode": "LIVE TEST DATA",
                "state": "running",
                "test_id": public_id,
                "test_type": cfg.test_type,
                "active_users": 0,
                "configured_users": cfg.users,
                "elapsed_seconds": 0,
                "duration_seconds": cfg.duration_seconds,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_ms": 0,
                "min_response_ms": 0,
                "max_response_ms": 0,
                "requests_per_second": 0,
                "error_rate": 0,
                "success_rate": 100,
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_mb": 0,
                "disk_percent": 0,
                "net_mb_s": 0,
                "system_status": "HEALTHY",
                "performance_score": 0,
                "performance_label": "",
                "reliability_score": 0,
                "overall_status": "",
                "breaking_point_users": None,
                "smoke_results": [],
                "series": {
                    "time": [],
                    "response": [],
                    "rps": [],
                    "error_rate": [],
                    "cpu": [],
                    "memory": [],
                    "users": [],
                },
                "message": "LIVE TEST DATA — generating real HTTP requests.",
            }

        totals = {"ok": 0, "fail": 0, "min": math.inf, "max": 0.0}
        breaking_point: int | None = None

        sampler = asyncio.create_task(
            self._sampler(start, cfg, totals)
        )
        try:
            if cfg.test_type == "smoke":
                await self._run_smoke(cfg, totals)
            elif cfg.test_type == "stress":
                breaking_point = await self._run_stress(cfg, totals)
            elif cfg.test_type == "spike":
                await self._run_spike(cfg, totals)
            elif cfg.test_type == "endurance":
                await self._run_constant_load(cfg, totals, cfg.users, cfg.duration_seconds)
            elif cfg.test_type == "reliability":
                await self._run_reliability(cfg, totals)
            else:
                await self._run_constant_load(cfg, totals, cfg.users, cfg.duration_seconds)
        finally:
            self._stop.set()
            sampler.cancel()
            try:
                await sampler
            except asyncio.CancelledError:
                pass

        self._finalize(cfg, totals, breaking_point, time.perf_counter() - start)

    async def _run_smoke(self, cfg: TestConfig, totals: dict) -> None:
        results = []
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(base_url=cfg.base_url, timeout=timeout) as client:
            for method, path in SMOKE_ENDPOINTS:
                ok, latency, status = await self._one_request(client, method, path)
                totals["ok" if ok else "fail"] += 1
                totals["min"] = min(totals["min"], latency)
                totals["max"] = max(totals["max"], latency)
                self.latencies.append(latency)
                results.append(
                    {
                        "endpoint": path,
                        "method": method,
                        "pass": ok,
                        "status_code": status,
                        "latency_ms": round(latency, 2),
                    }
                )
                logger.info("Smoke %s %s -> %s (%.1f ms)", method, path, "PASS" if ok else "FAIL", latency)
                await asyncio.sleep(0.05)
        with self._lock:
            self.metrics["smoke_results"] = results

    async def _run_constant_load(
        self, cfg: TestConfig, totals: dict, users: int, duration: float
    ) -> None:
        workers = max(1, min(users, Config.MAX_ENGINE_WORKERS))
        multiplier = max(1, math.ceil(users / workers))
        stop_at = time.perf_counter() + duration
        timeout = httpx.Timeout(15.0)
        limits = httpx.Limits(max_connections=workers + 20, max_keepalive_connections=workers)
        async with httpx.AsyncClient(base_url=cfg.base_url, timeout=timeout, limits=limits) as client:
            spawned = 0
            tasks = []
            spawn_interval = 1.0 / max(cfg.spawn_rate, 1.0)

            async def user_loop() -> None:
                idx = 0
                while not self._stop.is_set() and time.perf_counter() < stop_at:
                    for _ in range(multiplier):
                        if self._stop.is_set() or time.perf_counter() >= stop_at:
                            break
                        path = self._pick_path(cfg, idx)
                        idx += 1
                        ok, latency, _status = await self._one_request(client, "GET", path)
                        self._record(totals, ok, latency)
                    await asyncio.sleep(0.15)

            while spawned < workers and not self._stop.is_set() and time.perf_counter() < stop_at:
                tasks.append(asyncio.create_task(user_loop()))
                spawned += 1
                with self._lock:
                    self.metrics["active_users"] = min(users, spawned * multiplier)
                await asyncio.sleep(spawn_interval)

            with self._lock:
                self.metrics["active_users"] = users
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_stress(self, cfg: TestConfig, totals: dict) -> int | None:
        stages = [s for s in STRESS_STAGES if s <= max(cfg.users, STRESS_STAGES[-1])]
        if cfg.users not in stages:
            stages.append(cfg.users)
            stages = sorted(set(stages))
        stage_duration = max(8.0, cfg.duration_seconds / max(len(stages), 1))
        breaking: int | None = None
        thresholds = self._thresholds()
        for stage_users in stages:
            if self._stop.is_set():
                break
            logger.info("Stress stage %s users", stage_users)
            stage_start_ok = totals["ok"]
            stage_start_fail = totals["fail"]
            lat_before = len(self.latencies)
            await self._run_constant_load(cfg, totals, stage_users, stage_duration)
            stage_ok = totals["ok"] - stage_start_ok
            stage_fail = totals["fail"] - stage_start_fail
            stage_total = stage_ok + stage_fail
            stage_lats = list(self.latencies)[lat_before:]
            avg_rt = statistics.mean(stage_lats) if stage_lats else 0.0
            err = calculate_error_rate(stage_fail, stage_total)
            if (
                avg_rt > thresholds.get("stress_break_avg_response_ms", 1000)
                or err > thresholds.get("stress_break_error_rate", 5)
            ):
                breaking = stage_users
                logger.info("Approximate breaking point: %s users (avg=%.1f err=%.2f)", stage_users, avg_rt, err)
                break
        return breaking

    async def _run_spike(self, cfg: TestConfig, totals: dict) -> None:
        baseline = min(50, max(5, cfg.users // 10))
        spike = max(cfg.users, 200)
        half = max(5.0, cfg.duration_seconds / 2.0)
        logger.info("Spike baseline=%s then spike=%s", baseline, spike)
        await self._run_constant_load(cfg, totals, baseline, half)
        if not self._stop.is_set():
            await self._run_constant_load(cfg, totals, spike, half)

    async def _run_reliability(self, cfg: TestConfig, totals: dict) -> None:
        target_requests = max(cfg.users * 20, 200)
        timeout = httpx.Timeout(15.0)
        concurrency = max(1, min(cfg.users, Config.MAX_ENGINE_WORKERS))
        limits = httpx.Limits(max_connections=concurrency + 10, max_keepalive_connections=concurrency)
        counter = {"n": 0}
        lock = asyncio.Lock()

        async with httpx.AsyncClient(base_url=cfg.base_url, timeout=timeout, limits=limits) as client:

            async def worker() -> None:
                idx = 0
                while not self._stop.is_set():
                    async with lock:
                        if counter["n"] >= target_requests:
                            return
                        counter["n"] += 1
                    path = self._pick_path(cfg, idx)
                    idx += 1
                    ok, latency, _status = await self._one_request(client, "GET", path)
                    self._record(totals, ok, latency)

            with self._lock:
                self.metrics["active_users"] = concurrency
                self.metrics["duration_seconds"] = 0
            await asyncio.gather(*[worker() for _ in range(concurrency)])

    def _pick_path(self, cfg: TestConfig, idx: int) -> str:
        if cfg.target_endpoint and cfg.target_endpoint != "all":
            return cfg.target_endpoint
        return LOAD_ENDPOINTS[idx % len(LOAD_ENDPOINTS)]

    async def _one_request(
        self, client: httpx.AsyncClient, method: str, path: str
    ) -> tuple[bool, float, int]:
        started = time.perf_counter()
        status = 0
        try:
            response = await client.request(method, path)
            status = response.status_code
            ok = 200 <= status < 400
        except Exception as exc:  # noqa: BLE001
            logger.debug("Request error %s %s: %s", method, path, exc)
            ok = False
        latency = (time.perf_counter() - started) * 1000.0
        return ok, latency, status

    def _record(self, totals: dict, ok: bool, latency: float) -> None:
        if ok:
            totals["ok"] += 1
        else:
            totals["fail"] += 1
        totals["min"] = min(totals["min"], latency)
        totals["max"] = max(totals["max"], latency)
        self.latencies.append(latency)
        now = time.perf_counter()
        self.recent_window.append((now, ok))

    async def _sampler(self, start: float, cfg: TestConfig, totals: dict) -> None:
        while not self._stop.is_set():
            await asyncio.sleep(1.0)
            elapsed = time.perf_counter() - start
            health = health_to_dict(read_system_health())
            now = time.perf_counter()
            window = [item for item in self.recent_window if now - item[0] <= 1.2]
            rps = float(len(window))
            total = totals["ok"] + totals["fail"]
            avg = statistics.mean(self.latencies) if self.latencies else 0.0
            err = calculate_error_rate(totals["fail"], total)
            ok_rate = calculate_success_rate(totals["ok"], total)
            sample = {
                "elapsed_seconds": round(elapsed, 1),
                "active_users": self.metrics.get("active_users", 0) if isinstance(self.metrics, dict) else 0,
                "total_requests": total,
                "successful_requests": totals["ok"],
                "failed_requests": totals["fail"],
                "rps": round(rps, 2),
                "avg_response_ms": round(avg, 2),
                "error_rate": round(err, 3),
                "cpu_percent": health["cpu_percent"],
                "memory_percent": health["memory_percent"],
                "memory_mb": health["memory_used_mb"],
            }
            self.samples.append(sample)
            with self._lock:
                series = self.metrics.setdefault(
                    "series",
                    {
                        "time": [],
                        "response": [],
                        "rps": [],
                        "error_rate": [],
                        "cpu": [],
                        "memory": [],
                        "users": [],
                    },
                )
                series["time"].append(sample["elapsed_seconds"])
                series["response"].append(sample["avg_response_ms"])
                series["rps"].append(sample["rps"])
                series["error_rate"].append(sample["error_rate"])
                series["cpu"].append(sample["cpu_percent"])
                series["memory"].append(sample["memory_percent"])
                series["users"].append(sample["active_users"])
                self.metrics.update(
                    {
                        "data_mode": "LIVE TEST DATA",
                        "elapsed_seconds": round(elapsed, 1),
                        "total_requests": total,
                        "successful_requests": totals["ok"],
                        "failed_requests": totals["fail"],
                        "avg_response_ms": round(avg, 2),
                        "min_response_ms": 0.0 if totals["min"] == math.inf else round(totals["min"], 2),
                        "max_response_ms": round(totals["max"], 2),
                        "requests_per_second": round(rps, 2),
                        "error_rate": round(err, 3),
                        "success_rate": round(ok_rate, 3),
                        "cpu_percent": health["cpu_percent"],
                        "memory_percent": health["memory_percent"],
                        "memory_mb": health["memory_used_mb"],
                        "disk_percent": health["disk_percent"],
                        "net_mb_s": health["net_mb_s"],
                        "system_status": health["status"],
                    }
                )

    def _thresholds(self) -> dict[str, float]:
        if not self._flask_app:
            from config import THRESHOLD_DEFAULTS

            return dict(THRESHOLD_DEFAULTS)
        from app.services.settings_service import get_thresholds

        with self._flask_app.app_context():
            return get_thresholds()

    def _create_db_run(self, cfg: TestConfig) -> str:
        from app.extensions import db
        from app.models.test_result import TestRun

        assert self._flask_app is not None
        with self._flask_app.app_context():
            count = TestRun.query.count() + 1
            public_id = f"T{count:03d}"
            run = TestRun(
                public_id=public_id,
                test_type=cfg.test_type,
                users=cfg.users,
                duration_seconds=cfg.duration_seconds,
                spawn_rate=cfg.spawn_rate,
                target_endpoint=cfg.target_endpoint,
                started_at=datetime.now(timezone.utc),
                run_status="RUNNING",
            )
            db.session.add(run)
            db.session.commit()
            self.db_run_id = run.id
            return public_id

    def _finalize(
        self, cfg: TestConfig, totals: dict, breaking_point: int | None, elapsed: float
    ) -> None:
        from app.extensions import db
        from app.models.test_result import TestRun, TestSample
        from app.services.report_service import generate_reports

        total = totals["ok"] + totals["fail"]
        avg = statistics.mean(self.latencies) if self.latencies else 0.0
        min_rt = 0.0 if totals["min"] == math.inf else totals["min"]
        max_rt = totals["max"]
        rps = total / elapsed if elapsed > 0 else 0.0
        err = calculate_error_rate(totals["fail"], total)
        ok_rate = calculate_success_rate(totals["ok"], total)

        cpu_vals = [s["cpu_percent"] for s in self.samples] or [0.0]
        mem_vals = [s["memory_percent"] for s in self.samples] or [0.0]
        avg_cpu = statistics.mean(cpu_vals)
        max_cpu = max(cpu_vals)
        avg_mem = statistics.mean(mem_vals)
        max_mem = max(mem_vals)

        thresholds = self._thresholds()
        score = build_score_result(
            avg_response_ms=avg,
            error_rate=err,
            success_rate=ok_rate,
            requests_per_second=rps,
            avg_cpu=avg_cpu,
            avg_memory=avg_mem,
            configured_users=max(cfg.users, 1),
            successful=totals["ok"],
            total=total,
            thresholds=thresholds,
        )

        run_status = "STOPPED" if self._user_stop.is_set() else "COMPLETED"

        html_path = json_path = csv_path = pdf_path = None
        public_id = self.metrics.get("test_id") or "T000"

        assert self._flask_app is not None
        with self._flask_app.app_context():
            run = db.session.get(TestRun, self.db_run_id)
            if run:
                run.finished_at = datetime.now(timezone.utc)
                run.run_status = run_status
                run.overall_status = score.overall_status
                run.total_requests = total
                run.successful_requests = totals["ok"]
                run.failed_requests = totals["fail"]
                run.avg_response_ms = round(avg, 2)
                run.min_response_ms = round(min_rt, 2)
                run.max_response_ms = round(max_rt, 2)
                run.requests_per_second = round(rps, 2)
                run.error_rate = round(err, 3)
                run.success_rate = round(ok_rate, 3)
                run.avg_cpu = round(avg_cpu, 2)
                run.max_cpu = round(max_cpu, 2)
                run.avg_memory = round(avg_mem, 2)
                run.max_memory = round(max_mem, 2)
                run.performance_score = score.performance_score
                run.reliability_score = score.reliability_score
                run.performance_label = score.performance_label
                run.breaking_point_users = breaking_point
                for sample in self.samples:
                    db.session.add(
                        TestSample(
                            test_run_id=run.id,
                            elapsed_seconds=sample["elapsed_seconds"],
                            active_users=sample["active_users"],
                            total_requests=sample["total_requests"],
                            successful_requests=sample["successful_requests"],
                            failed_requests=sample["failed_requests"],
                            rps=sample["rps"],
                            avg_response_ms=sample["avg_response_ms"],
                            error_rate=sample["error_rate"],
                            cpu_percent=sample["cpu_percent"],
                            memory_percent=sample["memory_percent"],
                            memory_mb=sample["memory_mb"],
                        )
                    )
                db.session.commit()
                paths = generate_reports(run, self.samples, score)
                run.html_report = paths["html"]
                run.json_report = paths["json"]
                run.csv_report = paths["csv"]
                run.pdf_report = paths["pdf"]
                db.session.commit()
                public_id = run.public_id
                html_path, json_path, csv_path, pdf_path = (
                    paths["html"],
                    paths["json"],
                    paths["csv"],
                    paths["pdf"],
                )

        logger.info(
            "Test completed id=%s total=%s success=%s fail=%s perf=%.1f rel=%.2f status=%s",
            public_id,
            total,
            totals["ok"],
            totals["fail"],
            score.performance_score,
            score.reliability_score,
            score.overall_status,
        )

        with self._lock:
            self.metrics.update(
                {
                    "state": "completed",
                    "data_mode": "LIVE TEST DATA",
                    "test_id": public_id,
                    "total_requests": total,
                    "successful_requests": totals["ok"],
                    "failed_requests": totals["fail"],
                    "avg_response_ms": round(avg, 2),
                    "min_response_ms": round(min_rt, 2),
                    "max_response_ms": round(max_rt, 2),
                    "requests_per_second": round(rps, 2),
                    "error_rate": round(err, 3),
                    "success_rate": round(ok_rate, 3),
                    "performance_score": score.performance_score,
                    "performance_label": score.performance_label,
                    "reliability_score": round(score.reliability_score, 3),
                    "overall_status": score.overall_status,
                    "breaking_point_users": breaking_point,
                    "html_report": html_path,
                    "json_report": json_path,
                    "csv_report": csv_path,
                    "pdf_report": pdf_path,
                    "message": "Test completed. Scores calculated from collected metrics.",
                    "active_users": 0,
                }
            )


engine = TestingEngine()
