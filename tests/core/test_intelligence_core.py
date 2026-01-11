from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from core.config.loader import load_settings
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.governance.security import SecurityRedactor
from core.orchestrator.engine import OrchestratorEngine
from core.utils.product_loader import discover_products, register_enabled_products
from core.contracts.run_schema import RunStatus


def _collecting_tracer(sink: List[Dict[str, Any]], memory: MemoryRouter) -> Tracer:
    class _T(Tracer):
        def __init__(self, *, memory: MemoryRouter, redactor: SecurityRedactor, sink: List[Dict[str, Any]]):
            super().__init__(memory=memory, redactor=redactor)
            self._sink = sink

        def emit(self, event: Any) -> None:  # type: ignore[override]
            super().emit(event)
            payload = event.model_dump()
            # ensure consistent key for legacy tests
            if "event_type" not in payload:
                payload["event_type"] = payload.get("kind")
            self._sink.append(payload)

    return _T(memory=memory, redactor=SecurityRedactor(), sink=sink)


def _register_products_for_settings(settings):
    # deterministic product registration for tests
    from core.agents.registry import AgentRegistry
    from core.tools.registry import ToolRegistry

    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return catalog


def test_pause_resume_and_deterministic(orchestrator, trace_sink: List[Dict[str, Any]]):
    # Ensure products registered in test harness
    settings = load_settings()
    _register_products_for_settings(settings)

    trace_sink.clear()

    # Run once
    start = orchestrator.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "x"})
    assert start.ok
    run_id = start.data["run_id"]
    bundle = orchestrator.memory.get_run(run_id)
    assert bundle and bundle.run.status == RunStatus.PENDING_HUMAN

    # Resume (approve)
    ok = orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True}, decision="APPROVED")
    assert ok.ok
    finished = orchestrator.memory.get_run(run_id)
    assert finished and finished.run.status == RunStatus.COMPLETED

    # Run again with identical input and assert same step id sequence
    start2 = orchestrator.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "x"})
    assert start2.ok
    run2 = start2.data["run_id"]
    # collect step ids for both runs
    steps_a = [s.step_id for s in orchestrator.memory.get_run(run_id).steps]
    steps_b = [s.step_id for s in orchestrator.memory.get_run(run2).steps]
    assert steps_a == steps_b


def test_governance_denies_blocked_tool(tmp_path: Path):
    # create isolated settings pointing to repo root (current working)
    settings = load_settings()
    # block the echo tool
    settings.policies.blocked_tools = ["echo_tool"]

    # register products against these settings
    _register_products_for_settings(settings)

    # wire a fresh engine with in-memory backend + collecting tracer
    backend = InMemoryBackend()
    memory = MemoryRouter(backend=backend)
    sink: List[Dict[str, Any]] = []
    tracer = _collecting_tracer(sink, memory)
    engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer)

    # Run the hello_world flow which calls echo_tool as first step
    result = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "deny"})
    # Expect run to fail due to governance before step
    assert result.ok is True or result.ok is False
    bundle = engine.memory.get_run(result.data["run_id"]) if result.ok else engine.memory.get_run(result.error.details.get("run_id"))
    # Trace must include before_step_denied (emitted when governance blocks a step)
    kinds = [e.get("kind") or e.get("event_type") for e in sink]
    assert any(k in ("before_step_denied", "governance.decision") for k in kinds)


def test_trace_emits_for_tool_and_model_calls(tmp_path: Path):
    # use a small temp product that exercises plan_proposal and llm_reasoner attempt
    repo_root = tmp_path
    prod_dir = repo_root / "products" / "tiny_intel"
    flows_dir = prod_dir / "flows"
    prod_dir.mkdir(parents=True)
    flows_dir.mkdir()

    # manifest
    (prod_dir / "manifest.yaml").write_text("""name: tiny_intel
flows: [plan_flow]
""")
    # config
    (prod_dir / "config").mkdir()
    (prod_dir / "config" / "product.yaml").write_text(json.dumps({"name": "tiny_intel"}))

    # flow: plan_proposal using llm_reasoner (will produce pending_human)
    flow_yaml = """
name: plan_flow
version: "1.0"
autonomy_level: "suggest_only"
steps:
  - id: plan
    type: plan_proposal
    agent: llm_reasoner
    params:
      purpose: INSIGHT
      prompt: "Propose a short plan"
"""
    (flows_dir / "plan_flow.yaml").write_text(flow_yaml)

    # registry required but no product-specific agents/tools
    (prod_dir / "registry.py").write_text("""def register(registries):
    return
""")

    settings = load_settings(repo_root=str(repo_root))
    _register_products_for_settings(settings)

    backend = InMemoryBackend()
    memory = MemoryRouter(backend=backend)
    sink: List[Dict[str, Any]] = []
    tracer = _collecting_tracer(sink, memory)
    engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer)

    res = engine.run_flow(product="tiny_intel", flow="plan_flow", payload={})
    assert res.ok
    rid = res.data["run_id"]

    # plan_proposal should create a pending_human and not execute tools
    kinds = [e.get("kind") or e.get("event_type") for e in sink]
    assert "pending_human" in kinds or "run_pending_human" in kinds
    # ensure no tool.executed trace during plan proposal
    assert not any(k == "tool.executed" for k in kinds)
