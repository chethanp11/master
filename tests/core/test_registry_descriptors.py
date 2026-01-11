from __future__ import annotations

from typing import Dict, Any

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult, AgentMeta
from core.contracts.descriptors_schema import ToolDescriptor, AgentDescriptor, CostHint, SensitivityClass
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


def test_tool_descriptor_with_capabilities() -> None:
    """Test that tool descriptors support the capabilities field."""
    ToolRegistry.clear()

    descriptor = ToolDescriptor(
        name="capabilities_tool",
        description="Tool with capabilities.",
        capabilities=["data_reading", "computation", "visualization"],
        read_only=True,
        side_effect=False,
        sensitivity_class=SensitivityClass.MED,
        cost_hint=CostHint.LOW,
    )

    ToolRegistry.register(
        "capabilities_tool",
        lambda: _DescriptorTool(),
        descriptor=descriptor,
    )

    retrieved = ToolRegistry.get_descriptor("capabilities_tool")
    assert retrieved.capabilities == ["data_reading", "computation", "visualization"]
    assert retrieved.sensitivity_class == SensitivityClass.MED
    assert retrieved.cost_hint == CostHint.LOW


def test_agent_descriptor_with_capabilities() -> None:
    """Test that agent descriptors support the capabilities and purpose fields."""
    AgentRegistry.clear()

    descriptor = AgentDescriptor(
        name="capabilities_agent",
        purpose="Primary agent purpose",
        purposes=["planning", "analysis"],
        capabilities=["reasoning", "planning", "evaluation"],
        cost_hint=CostHint.MED,
        allowed_step_types=["agent", "plan_proposal"],
    )

    AgentRegistry.register(
        "capabilities_agent",
        lambda: _DescriptorAgent(),
        descriptor=descriptor,
    )

    retrieved = AgentRegistry.get_descriptor("capabilities_agent")
    assert retrieved.purpose == "Primary agent purpose"
    assert retrieved.purposes == ["planning", "analysis"]
    assert retrieved.capabilities == ["reasoning", "planning", "evaluation"]
    assert retrieved.cost_hint == CostHint.MED


def test_descriptor_coercion_from_meta() -> None:
    """Test that descriptors can be coerced from meta dict with capabilities."""
    ToolRegistry.clear()

    meta = {
        "capabilities": ["data_processing", "analysis"],
        "tags": ["internal"],
        "sensitivity_class": "MED",
        "cost_hint": "LOW",
    }

    ToolRegistry.register(
        "coerced_tool",
        lambda: _DescriptorTool(),
        meta=meta,
    )

    retrieved = ToolRegistry.get_descriptor("coerced_tool")
    assert retrieved.capabilities == ["data_processing", "analysis"]
    assert retrieved.tags == ["internal"]


def test_descriptor_capabilities_fallback_to_tags() -> None:
    """Test that capabilities fall back to tags if not specified."""
    ToolRegistry.clear()

    meta = {
        "tags": ["fallback_capability"],
    }

    ToolRegistry.register(
        "fallback_tool",
        lambda: _DescriptorTool(),
        meta=meta,
    )

    retrieved = ToolRegistry.get_descriptor("fallback_tool")
    assert retrieved.capabilities == ["fallback_capability"]
    assert retrieved.tags == ["fallback_capability"]


def test_list_descriptors_returns_all() -> None:
    """Test that list_descriptors returns all registered descriptors."""
    ToolRegistry.clear()
    AgentRegistry.clear()

    ToolRegistry.register("tool_a", lambda: _DescriptorTool())
    ToolRegistry.register("tool_b", lambda: _DescriptorTool())
    AgentRegistry.register("agent_a", lambda: _DescriptorAgent())

    tool_descs = list(ToolRegistry.list_descriptors())
    agent_descs = list(AgentRegistry.list_descriptors())

    assert len(tool_descs) == 2
    assert len(agent_descs) >= 1  # May include core agents
    assert all(isinstance(d, ToolDescriptor) for d in tool_descs)
    assert all(isinstance(d, AgentDescriptor) for d in agent_descs)
