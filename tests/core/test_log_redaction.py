from __future__ import annotations

# ==============================
# Log Redaction Tests
# ==============================

import logging

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.governance.security import DEFAULT_MASK
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products() -> None:
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)


def test_log_redaction(orchestrator, trace_sink, caplog) -> None:
    _register_products()
    secret_value = "sk-very-secret TOKEN=pa55word"
    caplog.set_level(logging.INFO, logger="master.trace")

    orchestrator.run_flow(product="hello_world", flow="hello_world", payload={"keyword": secret_value})

    assert secret_value not in caplog.text
    for record in caplog.records:
        message = record.getMessage()
        assert secret_value not in message
        assert secret_value not in str(record.__dict__)

    assert trace_sink, "Expected traces recorded"
    for event in trace_sink:
        payload_repr = str(event.get("payload", {}))
        assert secret_value not in payload_repr
