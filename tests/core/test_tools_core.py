# ==============================
# Tests: Tools (Registry + Executor + Local Backend)
# ==============================
from __future__ import annotations

from typing import Any, Dict

import pytest

from core.config.schema import Settings
from core.tools.registry import ToolRegistry
from core.tools.executor import ToolExecutor
from core.orchestrator.context import RunContext
from core.orchestrator.state import RunStatus
from core.contracts.tool_schema import ToolResult
from core.contracts.flow_schema import AutonomyLevel

from products.sandbox.tools.echo_tool import build as build_echo


def test_tool_registry_register_and_resolve() -> None:
    ToolRegistry.clear()
    t = build_echo()
    ToolRegistry.register(t.name, t)
    resolved = ToolRegistry.resolve(t.name)
    assert resolved is not None
    assert resolved.name == "echo_tool"


def test_tool_executor_runs_local_tool() -> None:
    ToolRegistry.clear()
    ToolRegistry.register("echo_tool", build_echo())

    settings = Settings()
    executor = ToolExecutor.from_settings(settings)

    run = RunContext(
        run_id="r1",
        product="sandbox",
        flow="hello_world",
        status=RunStatus.RUNNING,
        payload={"message": "hi"},
        artifacts={},
        meta={},
    )
    step = run.new_step(step_id="s1", step_type="tool", backend="local", target="echo_tool")

    res = executor.execute(
        tool_name="echo_tool",
        params={"message": "hello"},
        step_ctx=step,
        autonomy=AutonomyLevel.suggest_only,
    )
    assert isinstance(res, ToolResult)
    assert res.ok is True
    assert res.data and res.data["echo"] == "hello"