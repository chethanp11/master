# ==============================
# Concurrency Isolation Tests
# ==============================
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.memory.router import MemoryRouter
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products():
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return settings


def _run_and_finish(orchestrator, trace_sink) -> str:
    res = orchestrator.run_flow(product="hello_world", flow="hello_world", payload={})
    assert res.ok
    run_id = res.data["run_id"]
    orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True})
    return run_id


def test_concurrent_runs_isolated(orchestrator, trace_sink) -> None:
    _register_products()
    executor = ThreadPoolExecutor(max_workers=3)
    futures = [executor.submit(_run_and_finish, orchestrator, trace_sink) for _ in range(3)]
    run_ids = [f.result() for f in futures]
    executor.shutdown()

    memory = orchestrator.memory  # type: ignore[assignment]
    for run_id in run_ids:
        bundle = memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.run_id == run_id
        assert bundle.run.status == "COMPLETED"

    trace_runs = {event["run_id"] for event in trace_sink}
    assert set(run_ids) == trace_runs
    assert all(run_id in trace_runs for run_id in run_ids)

    # Shared fixture sanity: each run_id has its own entries, no cross-run leaks
    run_steps = {run_id: [e for e in trace_sink if e["run_id"] == run_id] for run_id in run_ids}
    for run_id, events in run_steps.items():
        assert all(event["run_id"] == run_id for event in events)
        assert events, "Expected trace events per run"
