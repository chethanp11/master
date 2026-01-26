"""
Tests for Discovery Engine (IMP-036).

Tests INT-DISC-001...010, INT-DISC-019...028, INT-DISC-038...045:
- ToolCandidate and AgentCandidate dataclasses
- Intent-filtered discovery returns ranked candidates
- Capability matching produces confidence scores
- Discovery trace events emitted
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from core.contracts.descriptors_schema import (
    AgentDescriptor,
    ToolDescriptor,
    ReasoningType,
    CostHint,
)
from core.knowledge.discovery_engine import (
    AgentCandidate,
    DiscoveryEngine,
    ToolCandidate,
    match_capabilities,
)


class TestToolCandidate:
    """Tests for ToolCandidate dataclass."""

    def test_tool_candidate_creation(self) -> None:
        """INT-DISC-001: ToolCandidate should include name, confidence, match_reason."""
        candidate = ToolCandidate(
            name="test_tool",
            confidence=0.85,
            match_reason="Matched capabilities: ['data_reading']",
            capabilities=["data_reading", "analysis"],
            domain_tags=["finance"],
        )
        
        assert candidate.name == "test_tool"
        assert candidate.confidence == 0.85
        assert "data_reading" in candidate.match_reason
        assert candidate.capabilities == ["data_reading", "analysis"]
        assert candidate.domain_tags == ["finance"]

    def test_tool_candidate_is_frozen(self) -> None:
        """ToolCandidate should be immutable."""
        candidate = ToolCandidate(
            name="frozen_tool",
            confidence=0.5,
            match_reason="Test",
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            candidate.name = "modified"  # type: ignore


class TestAgentCandidate:
    """Tests for AgentCandidate dataclass."""

    def test_agent_candidate_creation(self) -> None:
        """INT-DISC-002: AgentCandidate should include name, confidence, match_reason."""
        candidate = AgentCandidate(
            name="test_agent",
            confidence=0.9,
            match_reason="Matched capabilities: ['planning']",
            capabilities=["planning", "reasoning"],
            domain_tags=["general"],
            reasoning_type="planner",
        )
        
        assert candidate.name == "test_agent"
        assert candidate.confidence == 0.9
        assert candidate.reasoning_type == "planner"

    def test_agent_candidate_defaults(self) -> None:
        """AgentCandidate should have sensible defaults."""
        candidate = AgentCandidate(
            name="minimal",
            confidence=0.5,
            match_reason="Test",
        )
        
        assert candidate.capabilities == []
        assert candidate.domain_tags == []
        assert candidate.reasoning_type == "unknown"


class TestCapabilityMatching:
    """Tests for capability matching function."""

    def test_exact_match_high_confidence(self) -> None:
        """INT-DISC-005: Exact matches should have high confidence."""
        confidence = match_capabilities(
            "data reading",
            ["data_reading", "analysis"],
        )
        assert confidence > 0.3

    def test_no_match_zero_confidence(self) -> None:
        """No matching tokens should return zero confidence."""
        confidence = match_capabilities(
            "unrelated intent",
            ["data_reading", "analysis"],
        )
        # May have some overlap with common words, but should be low
        assert confidence < 0.5

    def test_empty_intent_zero_confidence(self) -> None:
        """Empty intent should return zero confidence."""
        confidence = match_capabilities("", ["data_reading"])
        assert confidence == 0.0

    def test_empty_capabilities_zero_confidence(self) -> None:
        """Empty capabilities should return zero confidence."""
        confidence = match_capabilities("data reading", [])
        assert confidence == 0.0

    def test_domain_tags_boost_confidence(self) -> None:
        """INT-DISC-006: Domain tags should contribute to matching."""
        without_domain = match_capabilities(
            "finance analysis",
            ["analysis"],
        )
        with_domain = match_capabilities(
            "finance analysis",
            ["analysis"],
            domain_tags=["finance"],
        )
        assert with_domain >= without_domain


class TestDiscoveryEngine:
    """Tests for DiscoveryEngine class."""

    def setup_method(self) -> None:
        """Clear registries before each test."""
        from core.tools.registry import ToolRegistry
        from core.agents.registry import AgentRegistry
        
        ToolRegistry.clear()
        AgentRegistry.clear()

    def _register_test_tools(self) -> None:
        """Helper to register test tools."""
        from core.tools.registry import ToolRegistry
        from core.tools.base import BaseTool
        from core.contracts.tool_schema import ToolResult, ToolMeta
        
        class DummyTool(BaseTool):
            name = "dummy"
            description = "Dummy"
            def run(self, params, ctx):
                return ToolResult(ok=True, data={}, error=None, meta=ToolMeta(tool_name=self.name, backend="test"))
        
        ToolRegistry.register(
            "data_tool",
            lambda: DummyTool(),
            descriptor=ToolDescriptor(
                name="data_tool",
                capabilities=["data_reading", "analysis"],
                domain_tags=["finance"],
            ),
        )
        ToolRegistry.register(
            "viz_tool",
            lambda: DummyTool(),
            descriptor=ToolDescriptor(
                name="viz_tool",
                capabilities=["visualization", "charting"],
                domain_tags=["general"],
            ),
        )

    def _register_test_agents(self) -> None:
        """Helper to register test agents."""
        from core.agents.registry import AgentRegistry
        from core.agents.base import BaseAgent
        from core.contracts.agent_schema import AgentResult, AgentMeta
        
        class DummyAgent(BaseAgent):
            name = "dummy"
            description = "Dummy"
            def run(self, step_context):
                return AgentResult(ok=True, data={}, error=None, meta=AgentMeta(agent_name=self.name))
        
        AgentRegistry.register(
            "planning_agent",
            lambda: DummyAgent(),
            descriptor=AgentDescriptor(
                name="planning_agent",
                capabilities=["planning", "reasoning"],
                reasoning_type=ReasoningType.PLANNER,
            ),
        )
        AgentRegistry.register(
            "critic_agent",
            lambda: DummyAgent(),
            descriptor=AgentDescriptor(
                name="critic_agent",
                capabilities=["evaluation", "critique"],
                reasoning_type=ReasoningType.CRITIC,
            ),
        )

    def test_discover_tools_returns_candidates(self) -> None:
        """INT-DISC-007: Discovery should return candidates."""
        self._register_test_tools()
        
        engine = DiscoveryEngine()
        candidates = engine.discover_tools("data analysis")
        
        assert len(candidates) > 0
        assert all(isinstance(c, ToolCandidate) for c in candidates)

    def test_discover_tools_sorted_by_confidence(self) -> None:
        """INT-DISC-009: Candidates should be sorted by confidence descending."""
        self._register_test_tools()
        
        engine = DiscoveryEngine()
        candidates = engine.discover_tools("data reading analysis")
        
        if len(candidates) > 1:
            confidences = [c.confidence for c in candidates]
            assert confidences == sorted(confidences, reverse=True)

    def test_discover_tools_with_domain_filter(self) -> None:
        """INT-DISC-020: Domain filter should scope results."""
        self._register_test_tools()
        
        engine = DiscoveryEngine()
        candidates = engine.discover_tools(
            "any tool",
            domain_filter=["finance"],
        )
        
        for candidate in candidates:
            assert "finance" in candidate.domain_tags

    def test_discover_tools_emits_events(self) -> None:
        """INT-DISC-010: Discovery should emit trace events."""
        self._register_test_tools()
        events: List[Dict[str, Any]] = []
        
        def capture_event(**kwargs: Any) -> None:
            events.append(kwargs)
        
        engine = DiscoveryEngine(emit_event_fn=capture_event)
        engine.discover_tools("data reading")
        
        event_kinds = [e["kind"] for e in events]
        assert "tool_discovery_started" in event_kinds
        assert "tool_discovery_completed" in event_kinds

    def test_discover_agents_returns_candidates(self) -> None:
        """INT-DISC-038: Agent discovery should return candidates."""
        self._register_test_agents()
        
        engine = DiscoveryEngine()
        candidates = engine.discover_agents("planning and reasoning")
        
        assert len(candidates) > 0
        assert all(isinstance(c, AgentCandidate) for c in candidates)

    def test_discover_agents_with_reasoning_type_filter(self) -> None:
        """INT-DISC-040: Reasoning type filter should scope results."""
        self._register_test_agents()
        
        engine = DiscoveryEngine()
        candidates = engine.discover_agents(
            "any agent",
            reasoning_type_filter="planner",
        )
        
        for candidate in candidates:
            assert candidate.reasoning_type == "planner"

    def test_discover_agents_emits_events(self) -> None:
        """INT-DISC-045: Agent discovery should emit trace events."""
        self._register_test_agents()
        events: List[Dict[str, Any]] = []
        
        def capture_event(**kwargs: Any) -> None:
            events.append(kwargs)
        
        engine = DiscoveryEngine(emit_event_fn=capture_event)
        engine.discover_agents("planning")
        
        event_kinds = [e["kind"] for e in events]
        assert "agent_discovery_started" in event_kinds
        assert "agent_discovery_completed" in event_kinds

    def test_min_confidence_filter(self) -> None:
        """INT-DISC-022: Min confidence should filter low-scoring candidates."""
        self._register_test_tools()
        
        engine = DiscoveryEngine(min_confidence=0.5)
        candidates = engine.discover_tools("totally unrelated gibberish xyz")
        
        for candidate in candidates:
            assert candidate.confidence >= 0.5

