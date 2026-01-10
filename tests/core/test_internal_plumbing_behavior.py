from __future__ import annotations

from typing import List, Dict

from core.config.loader import load_settings
from core.tools.registry import ToolRegistry
from core.agents.registry import AgentRegistry
from core.utils.product_loader import discover_products, register_enabled_products
from core.contracts.run_schema import RunStatus


def _register_products() -> None:
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)


def test_hello_world_golden_path(orchestrator, trace_sink: List[Dict]) -> None:
    _register_products()
    started = orchestrator.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "ok"})
    assert started.ok, started.error
    run_id = started.data["run_id"]
    resumed = orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True})
    assert resumed.ok, resumed.error
    assert resumed.data["status"] == RunStatus.COMPLETED.value

    kinds = [event["kind"] for event in trace_sink]
    assert "run_started" in kinds
    assert "step_started" in kinds
    assert "step_completed" in kinds
    assert "run_completed" in kinds
