from __future__ import annotations

from typing import Dict, Any

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult, AgentMeta
from core.contracts.descriptors_schema import ToolDescriptor, AgentDescriptor
from core.contracts.tool_schema import ToolResult, ToolMeta
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry
from core.tools.executor import ToolExecutor


class _DescriptorTool(BaseTool):
    name = "descriptor_tool"
    description = "Descriptor test tool."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data={"ok": True}, error=None, meta=meta)


class _DescriptorAgent(BaseAgent):
    name = "descriptor_agent"
    description = "Descriptor test agent."

    def run(self, step_context: StepContext) -> AgentResult:
        meta = AgentMeta(agent_name=self.name)
        return AgentResult(ok=True, data={"ok": True}, error=None, meta=meta)


def test_registry_descriptors_present() -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()

    ToolRegistry.register("descriptor_tool", lambda: _DescriptorTool())
    AgentRegistry.register("descriptor_agent", lambda: _DescriptorAgent())

    tool_desc = ToolRegistry.get_descriptor("descriptor_tool")
    assert isinstance(tool_desc, ToolDescriptor)
    assert tool_desc.name == "descriptor_tool"
    assert tool_desc.read_only is True
    assert tool_desc.side_effect is False
    assert tool_desc.sensitivity_class
    assert tool_desc.cost_hint

    agent_desc = AgentRegistry.get_descriptor("descriptor_agent")
    assert isinstance(agent_desc, AgentDescriptor)
    assert agent_desc.name == "descriptor_agent"
    assert agent_desc.cost_hint
    assert agent_desc.allowed_step_types


def test_descriptor_queries_do_not_execute_tools(monkeypatch) -> None:
    ToolRegistry.clear()

    ToolRegistry.register("descriptor_tool", lambda: _DescriptorTool())

    def _explode(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("ToolExecutor.execute should not be invoked for descriptor queries.")

    monkeypatch.setattr(ToolExecutor, "execute", _explode)
    ToolRegistry.get_descriptor("descriptor_tool")
