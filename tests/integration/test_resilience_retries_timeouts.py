# ==============================
# Resilience: Retries & Timeouts
# ==============================
from __future__ import annotations

from typing import Dict, List, Type

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.run_schema import RunStatus
from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry, ToolRegistration
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products():
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return settings


def _override_echo_tool(factory_cls: Type[BaseTool]) -> ToolRegistration | None:
    reg = ToolRegistry._tools.get("echo_tool")
    ToolRegistry.register("echo_tool", lambda: factory_cls(), overwrite=True)
    return reg


def _restore_echo_tool(registration: ToolRegistration | None) -> None:
    if registration:
        ToolRegistry._tools["echo_tool"] = registration
    else:
        ToolRegistry._tools.pop("echo_tool", None)


class BackendBehaviorTool(BaseTool):
    """Tool wrapper that delegates to a backend function defined by tests."""

    name: str = "echo_tool"

    def __init__(self, *, behavior: str, state: Dict[str, int]) -> None:
        self.behavior = behavior
        self.state = state
        super().__init__()

    def run(self, params, ctx):
        key = (ctx.run_id, ctx.step_id)
        self.state[key] = self.state.get(key, 0) + 1
        meta = ToolMeta(tool_name=self.name, backend="test")
        if self.behavior == "fail_once_then_success" and self.state[key] == 1:
            err = ToolError(
                code=ToolErrorCode.TEMPORARY,
                message="simulated failure",
                details={"phase": "first"},
            )
            return ToolResult(ok=False, data=None, error=err, meta=meta)
        if self.behavior == "always_timeout":
            err = ToolError(
                code=ToolErrorCode.TIMEOUT,
                message="simulated timeout",
                details={"phase": "timeout"},
            )
            return ToolResult(ok=False, data=None, error=err, meta=meta)
        return ToolResult(ok=True, data={"result": "ok"}, error=None, meta=meta)


def test_retry_success(orchestrator, trace_sink: List[Dict[str, Any]]) -> None:
    _register_products()
    state: Dict = {}
    original = _override_echo_tool(lambda: BackendBehaviorTool(behavior="fail_once_then_success", state=state))
    try:
        result = orchestrator.run_flow(product="sandbox", flow="hello_world", payload={})
        assert result.ok, result.error
        assert state, "Tool attempts recorded"
        tool_event_kinds = [e["kind"] for e in trace_sink if e["kind"].startswith("tool_call")]
        assert tool_event_kinds == [
            "tool_call_attempt_started",
            "tool_call_attempt_failed",
            "tool_call_retry_scheduled",
            "tool_call_attempt_started",
            "tool_call_succeeded",
        ]
        resumed = orchestrator.resume_run(run_id=result.data["run_id"], approval_payload={"approved": True})
        assert resumed.ok
        run = orchestrator.get_run(run_id=result.data["run_id"])
        assert run.ok
        assert run.data["run"]["status"] == RunStatus.COMPLETED.value
    finally:
        _restore_echo_tool(original)


def test_timeout_exhaustion(orchestrator, trace_sink: List[Dict[str, Any]]) -> None:
    _register_products()
    state: Dict = {}
    original = _override_echo_tool(lambda: BackendBehaviorTool(behavior="always_timeout", state=state))
    try:
        result = orchestrator.run_flow(product="sandbox", flow="hello_world", payload={})
        assert result.ok
        assert state, "Timeout attempts recorded"
        tool_event_kinds = [e["kind"] for e in trace_sink if e["kind"].startswith("tool_call")]
        assert tool_event_kinds == [
            "tool_call_attempt_started",
            "tool_call_attempt_failed",
            "tool_call_retry_scheduled",
            "tool_call_attempt_started",
            "tool_call_attempt_failed",
        ]
        run = orchestrator.get_run(run_id=result.data["run_id"])
        assert run.ok
        assert run.data["run"]["status"] == RunStatus.FAILED.value
    finally:
        _restore_echo_tool(original)
