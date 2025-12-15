# ==============================
# Metrics (In-Memory)
# ==============================
"""
Thread-safe in-memory counters and timers.

v1 goals:
- Basic counters (increment)
- Basic timing (observe ms)
- Snapshot for debugging / simple UI

No exporters (Prometheus/OpenTelemetry) in v1.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Timer:
    name: str
    started: float


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = {}
        self._timers_ms: Dict[str, list[int]] = {}

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def start_timer(self, name: str) -> Timer:
        return Timer(name=name, started=time.time())

    def stop_timer(self, timer: Timer) -> int:
        elapsed_ms = int((time.time() - timer.started) * 1000)
        with self._lock:
            self._timers_ms.setdefault(timer.name, []).append(elapsed_ms)
        return elapsed_ms

    def observe_ms(self, name: str, value_ms: int) -> None:
        with self._lock:
            self._timers_ms.setdefault(name, []).append(value_ms)

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timers_ms": {k: list(v) for k, v in self._timers_ms.items()},
            }