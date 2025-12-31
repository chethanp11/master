# ==============================
# Tracing Pipeline
# ==============================
"""
Tracing pipeline.

Responsibilities:
- Accept TraceEvent (contract)
- Scrub payload via SecurityRedactor
- Persist via MemoryBackend interface only
- Optionally mirror to logs

No direct sqlite calls here.
"""

from __future__ import annotations

import logging
from typing import Optional

from core.contracts.run_schema import TraceEvent
from core.config.schema import Settings
from core.governance.security import SecurityRedactor
from core.logging.observability import ObservabilityWriter
from core.memory.base import MemoryBackend


class Tracer:
    def __init__(
        self,
        *,
        memory: MemoryBackend,
        logger: Optional[logging.Logger] = None,
        redactor: Optional[SecurityRedactor] = None,
        mirror_to_log: bool = True,
        writer: Optional[ObservabilityWriter] = None,
    ) -> None:
        self.memory = memory
        self.logger = logger or logging.getLogger("master.trace")
        self.redactor = redactor or SecurityRedactor()
        self.mirror_to_log = mirror_to_log
        self.writer = writer

    def emit(self, event: TraceEvent) -> None:
        sanitized_payload = self.redactor.sanitize(event.payload)
        safe = event.model_copy(
            update={
                "payload": sanitized_payload,
                "redacted": sanitized_payload != event.payload,
            }
        )
        # Persist through backend interface only
        self.memory.append_trace_event(safe)
        if self.writer is not None:
            self.writer.append_event(
                product=safe.product,
                run_id=safe.run_id,
                payload=safe.model_dump(mode="json"),
            )

        if self.mirror_to_log:
            self.logger.info(
                "trace",
                extra={
                    "run_id": safe.run_id,
                    "step_id": safe.step_id,
                    "product": safe.product,
                    "flow": safe.flow,
                    "kind": safe.kind,
                },
            )

    @classmethod
    def from_settings(cls, *, settings: Settings, memory: MemoryBackend) -> "Tracer":
        """
        Convenience constructor for gateway/CLI wiring.
        """
        redactor = SecurityRedactor.from_settings(settings)
        mirror = bool(getattr(settings.logging, "console", True))
        writer = ObservabilityWriter(repo_root=settings.repo_root_path())
        return cls(memory=memory, redactor=redactor, mirror_to_log=mirror, writer=writer)
