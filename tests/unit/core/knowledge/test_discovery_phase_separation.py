# ==============================
# IMP-039: Discovery Phase Separation Tests
# ==============================
"""
Tests for Discovery Phase Separation.

Tech Specs: INT-DISC-055..073
- INT-DISC-055: Discovery phase started event emitted
- INT-DISC-056: Domain filter from product + explicit tags
- INT-DISC-057: Discovery based on candidate type
- INT-DISC-058: Deterministic discovery hash
- INT-DISC-059: Discovery phase completed event emitted
- INT-DISC-065: Selection phase started event emitted
- INT-DISC-066: Filter by confidence threshold
- INT-DISC-067: Handle no eligible candidates
- INT-DISC-068: Select top candidate
- INT-DISC-069: Selection phase completed event emitted
- INT-DISC-070: Combined discover_and_select
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List

from core.knowledge.discovery_engine import (
    DiscoveryEngine,
    DiscoveryResult,
    SelectionResult,
    ToolCandidate,
    AgentCandidate,
    _compute_discovery_hash,
)
from core.memory.tracing import TraceEventType


# ==============================
# Fixtures
# ==============================
@pytest.fixture
def captured_events():
    """Capture emitted events for testing."""
    events: List[Dict[str, Any]] = []
    
    def emit_event(kind: str, payload: Dict[str, Any]) -> None:
        events.append({"kind": kind, "payload": payload})
    
    return events, emit_event


@pytest.fixture
def discovery_engine(captured_events):
    """Create a discovery engine with event capture."""
    events, emit_fn = captured_events
    return DiscoveryEngine(emit_event_fn=emit_fn, min_confidence=0.0)


# ==============================
# Discovery Hash Tests
# ==============================
class TestDiscoveryHash:
    """Tests for deterministic discovery hash computation."""
    
    def test_hash_deterministic_same_inputs(self):
        """Same inputs produce same hash."""
        candidates = [
            ToolCandidate(name="tool-a", confidence=0.9, match_reason="test"),
            ToolCandidate(name="tool-b", confidence=0.8, match_reason="test"),
        ]
        
        hash1 = _compute_discovery_hash("find data", candidates, ["domain-a"])
        hash2 = _compute_discovery_hash("find data", candidates, ["domain-a"])
        
        assert hash1 == hash2
    
    def test_hash_different_for_different_intent(self):
        """Different intent produces different hash."""
        candidates = [
            ToolCandidate(name="tool-a", confidence=0.9, match_reason="test"),
        ]
        
        hash1 = _compute_discovery_hash("find data", candidates, None)
        hash2 = _compute_discovery_hash("search files", candidates, None)
        
        assert hash1 != hash2
    
    def test_hash_different_for_different_candidates(self):
        """Different candidates produce different hash."""
        candidates1 = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        candidates2 = [ToolCandidate(name="tool-b", confidence=0.9, match_reason="test")]
        
        hash1 = _compute_discovery_hash("find data", candidates1, None)
        hash2 = _compute_discovery_hash("find data", candidates2, None)
        
        assert hash1 != hash2
    
    def test_hash_different_for_different_domains(self):
        """Different domain tags produce different hash."""
        candidates = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        
        hash1 = _compute_discovery_hash("find data", candidates, ["domain-a"])
        hash2 = _compute_discovery_hash("find data", candidates, ["domain-b"])
        
        assert hash1 != hash2
    
    def test_hash_is_16_chars(self):
        """Hash is exactly 16 characters (truncated SHA-256)."""
        candidates = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        hash_val = _compute_discovery_hash("find data", candidates, None)
        
        assert len(hash_val) == 16
        assert all(c in "0123456789abcdef" for c in hash_val)


# ==============================
# DiscoveryResult Tests
# ==============================
class TestDiscoveryResult:
    """Tests for DiscoveryResult dataclass."""
    
    def test_discovery_result_immutable(self):
        """DiscoveryResult is immutable."""
        candidates = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        result = DiscoveryResult(
            intent="find data",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        with pytest.raises(Exception):
            result.intent = "changed"  # type: ignore
    
    def test_discovery_result_candidate_count(self):
        """candidate_count property works correctly."""
        candidates = [
            ToolCandidate(name="tool-a", confidence=0.9, match_reason="test"),
            ToolCandidate(name="tool-b", confidence=0.8, match_reason="test"),
        ]
        result = DiscoveryResult(
            intent="find data",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        assert result.candidate_count == 2
    
    def test_discovery_result_trace_payload(self):
        """to_trace_payload includes all required fields."""
        candidates = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        result = DiscoveryResult(
            intent="find data",
            candidates=candidates,
            discovery_hash="abc123",
            product_domain="ade",
            domain_tags_used=["ade", "finance"],
        )
        
        payload = result.to_trace_payload()
        
        assert payload["intent"] == "find data"
        assert payload["candidate_count"] == 1
        assert payload["discovery_hash"] == "abc123"
        assert payload["product_domain"] == "ade"
        assert "ade" in payload["domain_tags_used"]
        assert "tool-a" in payload["candidates"]


# ==============================
# SelectionResult Tests
# ==============================
class TestSelectionResult:
    """Tests for SelectionResult dataclass."""
    
    def test_selection_result_immutable(self):
        """SelectionResult is immutable."""
        candidate = ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")
        result = SelectionResult(
            selected_candidate=candidate,
            discovery_hash="abc123",
            selection_reason="Best match",
            confidence=0.9,
        )
        
        with pytest.raises(Exception):
            result.confidence = 0.5  # type: ignore
    
    def test_selection_result_has_selection(self):
        """has_selection property works correctly."""
        candidate = ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")
        result_with = SelectionResult(
            selected_candidate=candidate,
            discovery_hash="abc123",
            selection_reason="Best match",
        )
        result_without = SelectionResult(
            selected_candidate=None,
            discovery_hash="abc123",
            selection_reason="No match",
        )
        
        assert result_with.has_selection is True
        assert result_without.has_selection is False
    
    def test_selection_result_selected_name(self):
        """selected_name property works correctly."""
        candidate = ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")
        result = SelectionResult(
            selected_candidate=candidate,
            discovery_hash="abc123",
            selection_reason="Best match",
        )
        
        assert result.selected_name == "tool-a"
    
    def test_selection_result_selected_name_none(self):
        """selected_name is None when no selection."""
        result = SelectionResult(
            selected_candidate=None,
            discovery_hash="abc123",
            selection_reason="No match",
        )
        
        assert result.selected_name is None
    
    def test_selection_result_trace_payload(self):
        """to_trace_payload includes all required fields."""
        candidate = ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")
        result = SelectionResult(
            selected_candidate=candidate,
            discovery_hash="abc123",
            selection_reason="Best match",
            alternatives_considered=["tool-b", "tool-c"],
            confidence=0.9,
        )
        
        payload = result.to_trace_payload()
        
        assert payload["selected_name"] == "tool-a"
        assert payload["discovery_hash"] == "abc123"
        assert payload["selection_reason"] == "Best match"
        assert payload["alternatives_count"] == 2
        assert payload["confidence"] == 0.9


# ==============================
# DiscoveryEngine.discover() Tests
# ==============================
class TestDiscoveryEngineDiscover:
    """Tests for the discover() method (discovery phase)."""
    
    def test_discover_returns_discovery_result(self, captured_events):
        """discover() returns a DiscoveryResult."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover("find something", candidate_type="tool")
        
        assert isinstance(result, DiscoveryResult)
        assert result.intent == "find something"
        assert isinstance(result.discovery_hash, str)
        assert len(result.discovery_hash) == 16
    
    def test_discover_with_product_domain(self, captured_events):
        """discover() includes product domain in domain tags."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover(
            "find something",
            product_domain="ade",
            candidate_type="tool",
        )
        
        assert result.product_domain == "ade"
        assert "ade" in result.domain_tags_used
    
    def test_discover_with_explicit_domain_tags(self, captured_events):
        """discover() includes explicit domain tags."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover(
            "find something",
            domain_tags=["finance", "data"],
            candidate_type="tool",
        )
        
        assert "finance" in result.domain_tags_used
        assert "data" in result.domain_tags_used
    
    def test_discover_emits_started_event(self, captured_events):
        """discover() emits discovery_phase_started event."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        engine.discover("find something", candidate_type="tool")
        
        started_events = [e for e in events if e["kind"] == "discovery_phase_started"]
        assert len(started_events) >= 1
        assert started_events[0]["payload"]["intent"] == "find something"
    
    def test_discover_emits_completed_event(self, captured_events):
        """discover() emits discovery_phase_completed event."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        engine.discover("find something", candidate_type="tool")
        
        completed_events = [e for e in events if e["kind"] == "discovery_phase_completed"]
        assert len(completed_events) >= 1
        assert "discovery_hash" in completed_events[0]["payload"]
    
    def test_discover_hash_deterministic(self, captured_events):
        """discover() produces deterministic hash for same inputs."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result1 = engine.discover("find something", candidate_type="tool")
        result2 = engine.discover("find something", candidate_type="tool")
        
        assert result1.discovery_hash == result2.discovery_hash


# ==============================
# DiscoveryEngine.select() Tests
# ==============================
class TestDiscoveryEngineSelect:
    """Tests for the select() method (selection phase)."""
    
    def test_select_returns_selection_result(self, captured_events):
        """select() returns a SelectionResult."""
        events, emit_fn = captured_events
        
        # Create a discovery result manually
        candidates = [
            ToolCandidate(name="tool-a", confidence=0.9, match_reason="test"),
            ToolCandidate(name="tool-b", confidence=0.8, match_reason="test"),
        ]
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn, min_confidence=0.0)
        result = engine.select(discovery)
        
        assert isinstance(result, SelectionResult)
        assert result.discovery_hash == "abc123"
    
    def test_select_picks_highest_confidence(self, captured_events):
        """select() picks candidate with highest confidence."""
        events, emit_fn = captured_events
        
        candidates = [
            ToolCandidate(name="tool-low", confidence=0.5, match_reason="test"),
            ToolCandidate(name="tool-high", confidence=0.9, match_reason="test"),
            ToolCandidate(name="tool-mid", confidence=0.7, match_reason="test"),
        ]
        # Note: candidates should already be sorted, but let's sort for safety
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn, min_confidence=0.0)
        result = engine.select(discovery)
        
        assert result.selected_name == "tool-high"
        assert result.confidence == 0.9
    
    def test_select_respects_min_confidence(self, captured_events):
        """select() filters by minimum confidence."""
        events, emit_fn = captured_events
        
        candidates = [
            ToolCandidate(name="tool-low", confidence=0.3, match_reason="test"),
            ToolCandidate(name="tool-mid", confidence=0.5, match_reason="test"),
        ]
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn, min_confidence=0.6)
        result = engine.select(discovery)
        
        assert result.has_selection is False
        assert "threshold" in result.selection_reason.lower()
    
    def test_select_override_min_confidence(self, captured_events):
        """select() can override minimum confidence threshold."""
        events, emit_fn = captured_events
        
        candidates = [
            ToolCandidate(name="tool-mid", confidence=0.5, match_reason="test"),
        ]
        
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn, min_confidence=0.8)
        result = engine.select(discovery, min_confidence=0.3)
        
        assert result.has_selection is True
        assert result.selected_name == "tool-mid"
    
    def test_select_records_alternatives(self, captured_events):
        """select() records alternative candidates."""
        events, emit_fn = captured_events
        
        candidates = [
            ToolCandidate(name="tool-a", confidence=0.9, match_reason="test"),
            ToolCandidate(name="tool-b", confidence=0.8, match_reason="test"),
            ToolCandidate(name="tool-c", confidence=0.7, match_reason="test"),
        ]
        
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn, min_confidence=0.0)
        result = engine.select(discovery)
        
        assert "tool-b" in result.alternatives_considered
        assert "tool-c" in result.alternatives_considered
    
    def test_select_emits_started_event(self, captured_events):
        """select() emits selection_phase_started event."""
        events, emit_fn = captured_events
        
        candidates = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        engine.select(discovery)
        
        started_events = [e for e in events if e["kind"] == "selection_phase_started"]
        assert len(started_events) >= 1
        assert started_events[0]["payload"]["discovery_hash"] == "abc123"
    
    def test_select_emits_completed_event(self, captured_events):
        """select() emits selection_phase_completed event."""
        events, emit_fn = captured_events
        
        candidates = [ToolCandidate(name="tool-a", confidence=0.9, match_reason="test")]
        discovery = DiscoveryResult(
            intent="find something",
            candidates=candidates,
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        engine.select(discovery)
        
        completed_events = [e for e in events if e["kind"] == "selection_phase_completed"]
        assert len(completed_events) >= 1
        assert "selected_name" in completed_events[0]["payload"]


# ==============================
# Combined discover_and_select Tests
# ==============================
class TestDiscoverAndSelect:
    """Tests for the combined discover_and_select() method."""
    
    def test_discover_and_select_returns_selection_result(self, captured_events):
        """discover_and_select() returns SelectionResult."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover_and_select("find something", candidate_type="tool")
        
        assert isinstance(result, SelectionResult)
    
    def test_discover_and_select_emits_all_events(self, captured_events):
        """discover_and_select() emits both phase events."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        engine.discover_and_select("find something", candidate_type="tool")
        
        event_kinds = [e["kind"] for e in events]
        assert "discovery_phase_started" in event_kinds
        assert "discovery_phase_completed" in event_kinds
        assert "selection_phase_started" in event_kinds
        assert "selection_phase_completed" in event_kinds
    
    def test_discover_and_select_with_product_domain(self, captured_events):
        """discover_and_select() passes product domain through."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        engine.discover_and_select(
            "find something",
            product_domain="ade",
            candidate_type="tool",
        )
        
        started = [e for e in events if e["kind"] == "discovery_phase_started"][0]
        assert started["payload"]["product_domain"] == "ade"


# ==============================
# Agent Discovery Tests
# ==============================
class TestAgentDiscovery:
    """Tests for agent discovery using separated phases."""
    
    def test_discover_agents(self, captured_events):
        """discover() works for agents."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover("find advisor", candidate_type="agent")
        
        assert isinstance(result, DiscoveryResult)
        assert result.intent == "find advisor"
    
    def test_discover_and_select_agents(self, captured_events):
        """discover_and_select() works for agents."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover_and_select("find advisor", candidate_type="agent")
        
        assert isinstance(result, SelectionResult)


# ==============================
# Edge Cases
# ==============================
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_intent(self, captured_events):
        """Empty intent still produces a result."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        result = engine.discover("", candidate_type="tool")
        
        assert isinstance(result, DiscoveryResult)
        assert result.intent == ""
    
    def test_empty_candidates_selection(self, captured_events):
        """Selection with no candidates returns None selection."""
        events, emit_fn = captured_events
        
        discovery = DiscoveryResult(
            intent="find something",
            candidates=[],
            discovery_hash="abc123",
        )
        
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        result = engine.select(discovery)
        
        assert result.has_selection is False
        assert result.selected_candidate is None
    
    def test_no_event_function(self):
        """Engine works without emit_event_fn."""
        engine = DiscoveryEngine(emit_event_fn=None)
        
        result = engine.discover("find something", candidate_type="tool")
        
        assert isinstance(result, DiscoveryResult)
    
    def test_very_long_intent(self, captured_events):
        """Very long intent is handled correctly."""
        events, emit_fn = captured_events
        engine = DiscoveryEngine(emit_event_fn=emit_fn)
        
        long_intent = "find " + "something " * 100
        result = engine.discover(long_intent, candidate_type="tool")
        
        assert isinstance(result, DiscoveryResult)
        assert long_intent in result.intent


# ==============================
# Trace Event Type Tests
# ==============================
class TestTraceEventTypes:
    """Tests for trace event type registration."""
    
    def test_discovery_phase_started_event_exists(self):
        """DISCOVERY_PHASE_STARTED trace event type exists."""
        assert hasattr(TraceEventType, "DISCOVERY_PHASE_STARTED")
        assert TraceEventType.DISCOVERY_PHASE_STARTED.value == "discovery_phase_started"
    
    def test_discovery_phase_completed_event_exists(self):
        """DISCOVERY_PHASE_COMPLETED trace event type exists."""
        assert hasattr(TraceEventType, "DISCOVERY_PHASE_COMPLETED")
        assert TraceEventType.DISCOVERY_PHASE_COMPLETED.value == "discovery_phase_completed"
    
    def test_selection_phase_started_event_exists(self):
        """SELECTION_PHASE_STARTED trace event type exists."""
        assert hasattr(TraceEventType, "SELECTION_PHASE_STARTED")
        assert TraceEventType.SELECTION_PHASE_STARTED.value == "selection_phase_started"
    
    def test_selection_phase_completed_event_exists(self):
        """SELECTION_PHASE_COMPLETED trace event type exists."""
        assert hasattr(TraceEventType, "SELECTION_PHASE_COMPLETED")
        assert TraceEventType.SELECTION_PHASE_COMPLETED.value == "selection_phase_completed"
