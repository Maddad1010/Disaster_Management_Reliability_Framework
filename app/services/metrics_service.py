"""System resource monitoring via psutil."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass

import psutil


@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    net_mb_s: float
    status: str


_prev_net: tuple[float, int] | None = None


psutil.cpu_percent(interval=None)


def read_system_health() -> SystemHealth:
    """Return current CPU, memory, disk, and approximate network throughput."""
    global _prev_net

    cpu = float(psutil.cpu_percent(interval=None))
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    now = time.time()
    net_mb_s = 0.0
    if _prev_net is not None:
        prev_t, prev_bytes = _prev_net
        dt = max(0.001, now - prev_t)
        delta = (net.bytes_sent + net.bytes_recv) - prev_bytes
        net_mb_s = (delta / dt) / (1024 * 1024)
    _prev_net = (now, int(net.bytes_sent + net.bytes_recv))

    if cpu > 90 or mem.percent > 90:
        status = "CRITICAL"
    elif cpu > 75 or mem.percent > 80:
        status = "WARNING"
    else:
        status = "HEALTHY"

    return SystemHealth(
        cpu_percent=round(cpu, 1),
        memory_percent=round(mem.percent, 1),
        memory_used_mb=round(mem.used / (1024 * 1024), 1),
        memory_total_mb=round(mem.total / (1024 * 1024), 1),
        disk_percent=round(disk.percent, 1),
        net_mb_s=round(net_mb_s, 2),
        status=status,
    )


def health_to_dict(health: SystemHealth) -> dict:
    return asdict(health)
