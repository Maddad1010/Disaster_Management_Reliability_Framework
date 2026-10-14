import asyncio
import httpx
import time
import uuid
import psutil
import threading
from statistics import mean
from typing import Dict, Any, List

class TestingEngine:
    def __init__(self):
        self.is_running = False
        self.test_id = None
        self._last_summary = None   # cached after test ends
        self.stats = {
            "total_requests": 0,
            "success": 0,
            "failed": 0,
            "response_times": [],
            "start_time": 0,
            "current_users": 0,
            "errors": 0,
            "cpu_usage": 0,
            "memory_usage": 0
        }
        self.config = {}
        self._thread = None

    def start_test(self, config: Dict[str, Any]):
        if self.is_running:
            return False
        
        self.test_id = f"T-{str(uuid.uuid4())[:8]}"
        self.config = config
        self.is_running = True
        self.stats = {
            "total_requests": 0,
            "success": 0,
            "failed": 0,
            "response_times": [],
            "start_time": time.time(),
            "current_users": 0,
            "errors": 0,
            "cpu_usage": 0,
            "memory_usage": 0
        }
        
        self._thread = threading.Thread(target=self._run_in_thread, daemon=True)
        self._thread.start()
        return self.test_id

    def _run_in_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self._monitor_system())
        loop.run_until_complete(self._run_test_loop())
        loop.close()

    def stop_test(self):
        self.is_running = False
        if self._thread:
            # Wait briefly for thread to finish
            self._thread.join(timeout=2.0)
        return self.get_summary()

    async def _monitor_system(self):
        while self.is_running:
            self.stats["cpu_usage"] = psutil.cpu_percent(interval=None)
            self.stats["memory_usage"] = psutil.virtual_memory().percent
            await asyncio.sleep(1)

    async def _worker(self, client: httpx.AsyncClient, target_url: str):
        while self.is_running:
            start = time.perf_counter()
            try:
                # Using a short timeout for tests
                resp = await client.get(target_url, timeout=5.0)
                elapsed = (time.perf_counter() - start) * 1000
                self.stats["total_requests"] += 1
                self.stats["response_times"].append(elapsed)
                
                if resp.status_code < 400:
                    self.stats["success"] += 1
                else:
                    self.stats["failed"] += 1
                    self.stats["errors"] += 1
            except Exception:
                self.stats["total_requests"] += 1
                self.stats["failed"] += 1
                self.stats["errors"] += 1
            
            # Keep response_times bounded to avoid memory leak
            if len(self.stats["response_times"]) > 5000:
                self.stats["response_times"] = self.stats["response_times"][-5000:]
            
            # Sleep longer to allow server to breathe under extreme load
            await asyncio.sleep(0.1)

    async def _run_test_loop(self):
        target_url = f"http://127.0.0.1:8000{self.config.get('endpoint', '/api/health')}"
        users = self.config.get("users", 10)
        duration = self.config.get("duration", 60)
        
        # Simple implementation for Load, can be expanded for Stress/Spike
        self.stats["current_users"] = users
        
        # Increase limits to support many concurrent users
        limits = httpx.Limits(max_connections=users + 50, max_keepalive_connections=users + 50)
        
        async with httpx.AsyncClient(limits=limits) as client:
            workers = [asyncio.create_task(self._worker(client, target_url)) for _ in range(users)]
            
            try:
                # Loop to respect the stop signal mid-test
                for _ in range(duration * 10):
                    if not self.is_running:
                        break
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                pass
            finally:
                self.is_running = False
                for w in workers:
                    w.cancel()
                # Cache final summary so the API can return it after test ends
                self._last_summary = self.get_summary()

    def get_live_metrics(self):
        now = time.time()
        elapsed = now - self.stats["start_time"] if self.stats["start_time"] else 0
        rps = self.stats["total_requests"] / elapsed if elapsed > 0 else 0
        avg_resp = mean(self.stats["response_times"]) if self.stats["response_times"] else 0
        error_rate = (self.stats["errors"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        
        return {
            "test_id": self.test_id,
            "running": self.is_running,
            "users": self.stats["current_users"],
            "requests": self.stats["total_requests"],
            "success": self.stats["success"],
            "failed": self.stats["failed"],
            "rps": round(rps, 2),
            "avg_response_ms": round(avg_resp, 2),
            "error_rate": round(error_rate, 2),
            "cpu_usage": self.stats["cpu_usage"],
            "memory_usage": self.stats["memory_usage"],
            "elapsed": round(elapsed, 1)
        }
        
    def get_summary(self):
        metrics = self.get_live_metrics()
        
        # Score calculation
        perf_score = 100
        if metrics["avg_response_ms"] > 500:
            perf_score -= min(50, (metrics["avg_response_ms"] - 500) / 20)
        if metrics["error_rate"] > 0:
            perf_score -= min(30, metrics["error_rate"] * 5)
            
        reliability_score = 100.0
        if metrics["requests"] > 0:
            reliability_score = (metrics["success"] / metrics["requests"]) * 100
            
        return {
            **metrics,
            "performance_score": max(0, round(perf_score, 1)),
            "reliability_score": round(reliability_score, 1)
        }

engine = TestingEngine()
