# ==============================
# Logging Bootstrap
# ==============================
"""
Logging bootstrap.

Goals:
- Centralize logger configuration using Settings.logging.
- Provide structured context fields (run_id, step_id, product, flow).
- Keep v1 simple: stdlib logging + JSON-ish formatter.

No persistence here.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.config.schema import Settings


@dataclass(frozen=True)
class LogContext:
    run_id: Optional[str] = None
    step_id: Optional[str] = None
    product: Optional[str] = None
    flow: Optional[str] = None


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Optional structured extras
        for k in ("run_id", "step_id", "product", "flow"):
            if hasattr(record, k):
                payload[k] = getattr(record, k)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def bootstrap_logger(settings: Settings) -> logging.Logger:
    """
    Configure root logger based on settings.
    Returns a named logger ("master").
    """
    level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    # clear existing handlers to avoid duplicates in reload
    root.handlers = []

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(JsonLineFormatter())
    root.addHandler(handler)

    return logging.getLogger("master")


def with_context(logger: logging.Logger, ctx: LogContext) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(
        logger,
        {
            "run_id": ctx.run_id,
            "step_id": ctx.step_id,
            "product": ctx.product,
            "flow": ctx.flow,
        },
    )