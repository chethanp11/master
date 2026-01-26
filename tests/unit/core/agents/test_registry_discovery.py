"""
Tests for Discovery Registry Integration (IMP-037).

Tests INT-DISC-011...018, INT-DISC-046...054:
- Registry exposes descriptor access methods
- Discovery engine uses strategy pattern
- Custom strategies can be registered
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult, AgentMeta
from core.contracts.descriptors_schema import (
    AgentDescriptor,
    ToolDescriptor,
    ReasoningType,
)
from core.contracts.tool_schema import ToolResult, ToolMeta
from core.knowledge.discovery_engine import (
    AgentCandidate,
    DefaultDiscoveryStrategy,
    DiscoveryEngine,
    DiscoveryStrategy,
    ToolCandidate,
    get_discovery_strategy,
    register_discovery_strategy,
)
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry


class _TestAgent(BaseAgent):
    name = "test_agent"
    description = "Test agent."

    def run(self, step_context: StepContext) -> AgentResult:
        meta = AgentMeta(agent_name=self.name)
        return AgentResult(ok=True, data={}, error=None, meta=meta)


class _TestTool(BaseTool):
    name = "test_tool"
    description = "Test tool."

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data={}, error=None, meta=meta)


class TestRegistryDescriptorMethods:
    """Tests for registry descriptor access methods."""

    def setup_method(self) -> None:
        """Clear registries before each test."""
        ToolRegistry.clear()
        AgentRegistry.clear()

    def test_tool_registry_get_all_descriptors(self) -> None:
        """INT-DISC-046: ToolRegistry should expose get_all_descriptors()."""
        ToolRegistry.register(
            "tool_a",
            lambda: _TestTool(),
            descriptor=ToolDescriptor(name="tool_a", capabilities=["cap_a"]),
        )
        ToolRegistry.register(
            "tool_b",
            lambda: _TestTool(),
            descriptor=ToolDescriptor(name="tool_b", capabilities=["cap_b"]),
        )
        
        descriptors = ToolRegistry.get_all_descriptors()
        
        assert len(descriptors) == 2
        assert all(isinstance(d, ToolDescriptor) for d in descriptors)

    def test_agent_registry_get_all_descriptors(self) -> None:
        """INT-DISC-011: AgentRegistry should expose get_all_descriptors()."""
        AgentRegistry.register(
            "agent_a",
            lambda: _TestAgent(),
            descriptor=AgentDescriptor(name="agent_a", capabilities=["cap_a"]),
        )
        
        descriptors = AgentRegistry.get_all_descriptors()
        
        assert len(descriptors) >= 1
        assert all(isinstance(d, AgentDescriptor) for d in descriptors)

    def test_tool_registry_filter_by_capability_tags(self) -> None:
        """INT-DISC-047: ToolRegistry should support filter_by_capability_tags()."""
        ToolRegistry.register(
            "data_tool",
            lambda: _TestTool(),
            descriptor=ToolDescriptor(name="data_tool", capabilities=["data", "analysis"]),
        )
        ToolRegistry.register(
            "viz_tool",
            lambda: _TestTool(),
            descriptor=ToolDescriptor(name="viz_tool", capabilities=["visualization"]),
        )
        
        data_tools = ToolRegistry.filter_by_capability_tags(["data"])
        viz_tools = ToolRegistry.filter_by_capability_tags(["visualization"])
        
        assert "data_tool" in data_tools
        assert "viz_tool" not in data_tools
        assert "viz_tool" in viz_tools

    def test_agent_registry_filter_by_capability_tags(self) -> None:
        """INT-DISC-012: AgentRegistry should support filter_by_capability_tags()."""
        AgentRegistry.register(
            "planning_agent",
            lambda: _TestAgent(),
            descriptor=AgentDescriptor(name="planning_agent", capabilities=["planning"]),
        )
        AgentRegistry.register(
            "eval_agent",
            lambda: _TestAgent(),
            descriptor=AgentDescriptor(name="eval_agent", capabilities=["evaluation"]),
        )
        
        planning_agents = AgentRegistry.filter_by_capability_tags(["planning"])
        
        assert "planning_agent" in planning_agents
        assert "eval_agent" not in planning_agents

    def test_filter_by_capability_tags_match_all(self) -> None:
        """Filter with match_all=True should require all tags."""
        ToolRegistry.register(
            "multi_cap_tool",
            lambda: _TestTool(),
            descriptor=ToolDescriptor(name="multi_cap_tool", capabilities=["data", "viz"]),
        )
        ToolRegistry.register(
            "single_cap_tool",
            lambda: _TestTool(),
            descriptor=ToolDescriptor(name="single_cap_tool", capabilities=["data"]),
        )
        
        # Match any (default)
        any_match = ToolRegistry.filter_by_capability_tags(["data", "viz"])
        assert "multi_cap_tool" in any_match
        assert "single_cap_tool" in any_match
        
        # Match all
        all_match = ToolRegistry.filter_by_capability_tags(["data", "viz"], match_all=True)
        assert "multi_cap_tool" in all_match
        assert "single_cap_tool" not in all_match


class TestDiscoveryStrategy:
    """Tests for discovery strategy pattern."""

    def test_default_strategy_exists(self) -> None:
        """INT-DISC-012: Default strategy should exist."""
        strategy = get_discovery_strategy("default")
        assert isinstance(strategy, DefaultDiscoveryStrategy)

    def test_custom_strategy_registration(self) -> None:
        """INT-DISC-013: Custom strategies should be registrable."""
        
        class CustomStrategy(DiscoveryStrategy):
            def discover_tools(self, intent, descriptors, context=None):
                return []
            
            def discover_agents(self, intent, descriptors, context=None):
                return []
        
        custom = CustomStrategy()
        register_discovery_strategy("custom_test", custom)
        
        retrieved = get_discovery_strategy("custom_test")
        assert retrieved is custom

    def test_unknown_strategy_raises(self) -> None:
        """INT-DISC-014: Unknown strategy should raise KeyError."""
        with pytest.raises(KeyError):
            get_discovery_strategy("nonexistent_strategy")

    def test_default_strategy_discover_tools(self) -> None:
        """DefaultDiscoveryStrategy should discover tools from descriptors."""
        strategy = DefaultDiscoveryStrategy()
        
        descriptors = [
            ToolDescriptor(name="data_tool", capabilities=["data", "reading"]),
            ToolDescriptor(name="viz_tool", capabilities=["visualization"]),
        ]
        
        candidates = strategy.discover_tools("data reading", descriptors)
        
        assert len(candidates) == 2
        # Data tool should have higher confidence
        data_candidate = next(c for c in candidates if c.name == "data_tool")
        viz_candidate = next(c for c in candidates if c.name == "viz_tool")
        assert data_candidate.confidence >= viz_candidate.confidence

    def test_default_strategy_discover_agents(self) -> None:
        """DefaultDiscoveryStrategy should discover agents from descriptors."""
        strategy = DefaultDiscoveryStrategy()
        
        descriptors = [
            AgentDescriptor(
                name="planner",
                capabilities=["planning", "reasoning"],
                reasoning_type=ReasoningType.PLANNER,
            ),
        ]
        
        candidates = strategy.discover_agents("planning task", descriptors)
        
        assert len(candidates) == 1
        assert candidates[0].name == "planner"
        assert candidates[0].reasoning_type == "planner"

    def test_strategy_min_confidence_filter(self) -> None:
        """Strategy should filter by min_confidence."""
        strategy = DefaultDiscoveryStrategy(min_confidence=0.5)
        
        descriptors = [
            ToolDescriptor(name="matching_tool", capabilities=["exact", "match"]),
            ToolDescriptor(name="unrelated_tool", capabilities=["xyz", "abc"]),
        ]
        
        candidates = strategy.discover_tools("exact match", descriptors)
        
        for c in candidates:
            assert c.confidence >= 0.5

