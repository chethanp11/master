from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple

from core.config.schema import Settings
from core.contracts.flow_schema import FlowDef, StepDef, StepType
from core.contracts.run_schema import RunRecord, RunStatus
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.orchestrator.context import RunContext, StepContext
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry

from products.sandbox.tools.echo_tool import EchoTool


@dataclass
class RecordingTool(EchoTool):
    calls: int = 0

    def run(self, params, ctx):
        self.calls += 1
        return super().run(params, ctx)


def _build_step_ctx(*, product: str = "sandbox", events: List[Tuple[str, dict]] | None = None) -> StepContext:
    run_record = RunRecord(run_id="run-tools", product=product, flow_id="hello", status=RunStatus.RUNNING)
    flow = FlowDef(id="hello", steps=[StepDef(id="s1", type=StepType.TOOL, tool="echo_tool")])
    trace: Callable[[str, dict], None] | None = None
    if events is not None:
        trace = lambda event_type, payload: events.append((event_type, payload))
    run_ctx = RunContext(run_id=run_record.run_id, product=run_record.product, flow=flow.id, trace=trace)
    return run_ctx.new_step(step_def=flow.steps[0])


def _executor(settings: Settings, registry: ToolRegistry) -> ToolExecutor:
    return ToolExecutor(registry=registry, hooks=GovernanceHooks(settings=settings), redactor=SecurityRedactor())


def test_tool_registry_registers_and_resolves() -> None:
    ToolRegistry.clear()
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register(name="echo_tool", factory=lambda: tool)
    resolved = registry.resolve("echo_tool")
    assert isinstance(resolved, EchoTool)


def test_tool_executor_runs_tool_and_redacts_traces() -> None:
    ToolRegistry.clear()
    settings = Settings()
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register(name="echo_tool", factory=lambda: tool)
    events: List[Tuple[str, dict]] = []
    ctx = _build_step_ctx(events=events)

    executor = _executor(settings, registry)
    result = executor.execute(tool_name="echo_tool", params={"message": "secret sk-abc"}, ctx=ctx)

    assert result.ok is True
    assert tool.calls == 1
    assert result.data and "secret" in result.data["echo"]
    payloads = [payload for event, payload in events if event == "tool.executed"]
    assert payloads
    serialized = str(payloads[0])
    assert "sk-" not in serialized  # redacted
    assert "step_id" in payloads[0]


def test_tool_executor_blocks_denied_tool_without_running_code() -> None:
    ToolRegistry.clear()
    settings = Settings()
    settings.policies.blocked_tools = ["echo_tool"]
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register(name="echo_tool", factory=lambda: tool)
    events: List[Tuple[str, dict]] = []
    ctx = _build_step_ctx(events=events)

    executor = _executor(settings, registry)
    result = executor.execute(tool_name="echo_tool", params={"message": "hi"}, ctx=ctx)

    assert result.ok is False
    assert tool.calls == 0
    assert any(event == "governance.decision" for event, _ in events)
