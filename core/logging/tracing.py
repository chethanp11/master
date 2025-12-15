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
from core.governance.security import SecurityRedactor
from core.memory.base import MemoryBackend


class Tracer:
    def __init__(
        self,
        *,
        memory: MemoryBackend,
        logger: Optional[logging.Logger] = None,
        redactor: Optional[SecurityRedactor] = None,
        mirror_to_log: bool = True,
    ) -> None:
        self.memory = memory
        self.logger = logger or logging.getLogger("master.trace")
        self.redactor = redactor or SecurityRedactor()
        self.mirror_to_log = mirror_to_log

    def emit(self, event: TraceEvent) -> None:
        safe = event.model_copy(update={"payload": self.redactor.redact_dict(event.payload)})
        # Persist through backend interface only
        self.memory.append_trace_event(safe)

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