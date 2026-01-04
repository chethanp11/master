from __future__ import annotations

# ==============================
# Trace Contract Tests
# ==============================

from typing import List

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products() -> None:
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)


def test_trace_contract(orchestrator, trace_sink: List[dict]) -> None:
    _register_products()
    started = orchestrator.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "trace secret"})
    assert started.ok
    run_id = started.data["run_id"]
    resumed = orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True})
    assert resumed.ok

    kinds = [event["kind"] for event in trace_sink]
    assert "run_started" in kinds
    assert "step_started" in kinds
    assert "step_completed" in kinds
    assert "run_completed" in kinds
    assert kinds.index("step_started") < kinds.index("step_completed")

    for event in trace_sink:
        assert event.get("run_id") == run_id
        assert event.get("product") == "hello_world"
        assert event.get("flow") == "hello_world"
        assert event.get("ts") and isinstance(event["ts"], int)
        assert event.get("event_type")
