# ==============================
# IMP-017: SufficiencyState Lifecycle Tests
# ==============================
"""
Tests for SufficiencyManager and lifecycle operations.

Tech Spec IDs: INT-SUFF-LC-001, INT-SUFF-LC-002, INT-SUFF-LC-003, INT-SUFF-LC-004, INT-SUFF-LC-005
BRD ID: BRD-AUTO-029
"""

import pytest

from core.contracts.sufficiency_schema import (
    Fact,
    Gap,
    Importance,
    Priority,
    SufficiencyState,
    Unknown,
)
from core.knowledge.sufficiency_manager import (
    EvidenceItem,
    SufficiencyManager,
    SufficiencyStateDiff,
    check_sufficiency_for_proceed,
    create_sufficiency_manager_from_context,
)


# ==============================
# EvidenceItem Tests
# ==============================
class TestEvidenceItem:
    """Tests for EvidenceItem dataclass."""

    def test_evidence_item_construction(self):
        """EvidenceItem stores all fields."""
        item = EvidenceItem(
            source="tool_call",
            description="User verified",
            confidence=0.9,
            evidence_ref="ref-123",
            metadata={"tool": "verify_user"},
        )
        assert item.source == "tool_call"
        assert item.description == "User verified"
        assert item.confidence == 0.9
        assert item.evidence_ref == "ref-123"
        assert item.metadata["tool"] == "verify_user"

    def test_evidence_item_defaults(self):
        """EvidenceItem has sensible defaults."""
        item = EvidenceItem(source="test", description="desc")
        assert item.confidence == 1.0
        assert item.evidence_ref is None
        assert item.metadata == {}

    def test_evidence_item_to_fact(self):
        """to_fact converts EvidenceItem to Fact."""
        item = EvidenceItem(
            source="api",
            description="Data retrieved",
            confidence=0.85,
            evidence_ref="ref-456",
        )
        fact = item.to_fact()
        assert fact.description == "Data retrieved"
        assert fact.confidence == 0.85
        assert fact.evidence_ref == "ref-456"


# ==============================
# SufficiencyStateDiff Tests
# ==============================
class TestSufficiencyStateDiff:
    """Tests for SufficiencyStateDiff dataclass."""

    def test_diff_defaults(self):
        """SufficiencyStateDiff has zero defaults."""
        diff = SufficiencyStateDiff()
        assert diff.facts_added == 0
        assert diff.unknowns_resolved == 0
        assert diff.gaps_resolved == 0
        assert not diff.has_changes()

    def test_diff_has_changes(self):
        """has_changes returns True when changes exist."""
        diff = SufficiencyStateDiff(facts_added=1)
        assert diff.has_changes()

    def test_diff_to_trace_payload(self):
        """to_trace_payload converts diff to dict."""
        diff = SufficiencyStateDiff(
            facts_added=2,
            unknowns_resolved=1,
            is_now_sufficient=True,
        )
        payload = diff.to_trace_payload()
        assert payload["facts_added"] == 2
        assert payload["unknowns_resolved"] == 1
        assert payload["is_now_sufficient"] is True
        assert payload["changed"] is True


# ==============================
# SufficiencyManager Tests
# ==============================
class TestSufficiencyManager:
    """Tests for SufficiencyManager class."""

    def test_manager_init_empty(self):
        """Manager initializes with empty state."""
        manager = SufficiencyManager()
        assert manager.state is not None
        assert len(manager.state.facts) == 0
        assert manager.update_count == 0

    def test_manager_init_with_state(self):
        """Manager initializes with provided state."""
        fact = Fact(description="test")
        state = SufficiencyState(run_id="test-run", facts=[fact])
        manager = SufficiencyManager(initial_state=state)
        assert len(manager.state.facts) == 1

    def test_update_with_evidence(self):
        """update_with_evidence adds facts."""
        manager = SufficiencyManager()
        evidence = [
            EvidenceItem(source="tool", description="Fact 1"),
            EvidenceItem(source="tool", description="Fact 2"),
        ]
        diff = manager.update_with_evidence(evidence)

        assert diff.facts_added == 2
        assert len(manager.state.facts) == 2
        assert manager.update_count == 1

    def test_resolve_unknown(self):
        """resolve_unknown resolves unknown and adds fact."""
        manager = SufficiencyManager()
        unknown = manager.add_unknown("What is X?")

        evidence = EvidenceItem(source="tool", description="X is 42")
        diff = manager.resolve_unknown(unknown.id, evidence)

        assert diff.unknowns_resolved == 1
        assert diff.facts_added == 1
        assert len(manager.state.unknowns) == 0
        assert len(manager.state.facts) == 1

    def test_resolve_gap(self):
        """resolve_gap resolves gap and adds fact."""
        manager = SufficiencyManager()
        gap = manager.add_gap("Missing user data")

        evidence = EvidenceItem(source="api", description="User data retrieved")
        diff = manager.resolve_gap(gap.id, evidence)

        assert diff.gaps_resolved == 1
        assert diff.facts_added == 1
        assert len(manager.state.gaps) == 0
        assert len(manager.state.facts) == 1

    def test_add_unknown(self):
        """add_unknown adds unknown to state."""
        manager = SufficiencyManager()
        unknown = manager.add_unknown(
            "What is the user's name?",
            importance=Importance.HIGH,
            blocking=True,
        )

        assert unknown.question == "What is the user's name?"
        assert unknown.importance == Importance.HIGH
        assert unknown.blocking is True
        assert len(manager.state.unknowns) == 1

    def test_add_gap(self):
        """add_gap adds gap to state."""
        manager = SufficiencyManager()
        gap = manager.add_gap(
            "Missing API credentials",
            priority=Priority.HIGH,
            blocking=True,
        )

        assert gap.description == "Missing API credentials"
        assert gap.priority == Priority.HIGH
        assert len(manager.state.gaps) == 1

    def test_add_assumption(self):
        """add_assumption adds assumption to state."""
        manager = SufficiencyManager()
        assumption = manager.add_assumption(
            "User has valid credentials",
            confidence=0.7,
            evidence_ref="session-ref-123",
        )

        assert assumption.description == "User has valid credentials"
        assert assumption.confidence == 0.7
        assert len(manager.state.assumptions) == 1

    def test_is_sufficient_empty(self):
        """Empty state is sufficient."""
        manager = SufficiencyManager()
        assert manager.is_sufficient() is True

    def test_is_sufficient_with_blocking_unknown(self):
        """State with blocking unknown is not sufficient."""
        manager = SufficiencyManager()
        manager.add_unknown("Blocking?", blocking=True)
        assert manager.is_sufficient() is False

    def test_is_sufficient_with_non_blocking_unknown(self):
        """State with non-blocking unknown is sufficient."""
        manager = SufficiencyManager()
        manager.add_unknown("Not blocking", blocking=False)
        assert manager.is_sufficient() is True

    def test_is_sufficient_with_blocking_gap(self):
        """State with blocking gap is not sufficient."""
        manager = SufficiencyManager()
        manager.add_gap("Blocking gap", blocking=True)
        assert manager.is_sufficient() is False

    def test_has_blocking_issues(self):
        """has_blocking_issues returns True when blocking issues exist."""
        manager = SufficiencyManager()
        assert manager.has_blocking_issues() is False

        manager.add_unknown("Q?", blocking=True)
        assert manager.has_blocking_issues() is True

    def test_get_blocking_issues_summary(self):
        """get_blocking_issues_summary returns summary dict."""
        manager = SufficiencyManager()
        manager.add_unknown("Q1?", blocking=True)
        manager.add_gap("G1", blocking=True)
        manager.add_unknown("Q2?", blocking=False)

        summary = manager.get_blocking_issues_summary()

        assert len(summary["blocking_unknowns"]) == 1
        assert len(summary["blocking_gaps"]) == 1
        assert summary["total_blocking"] == 2


# ==============================
# Serialization Tests (INT-SUFF-LC-003, 004)
# ==============================
class TestSufficiencyManagerSerialization:
    """Tests for manager serialization/deserialization."""

    def test_to_serializable(self):
        """to_serializable produces dict."""
        manager = SufficiencyManager()
        manager.add_unknown("Q?")
        manager.add_gap("G")

        data = manager.to_serializable()

        assert isinstance(data, dict)
        assert "unknowns" in data
        assert "gaps" in data
        assert len(data["unknowns"]) == 1
        assert len(data["gaps"]) == 1

    def test_from_serializable(self):
        """from_serializable restores manager."""
        original = SufficiencyManager(run_id="test-run")
        original.add_unknown("Q?", importance=Importance.HIGH)
        original.add_gap("G", priority=Priority.HIGH)

        data = original.to_serializable()
        restored = SufficiencyManager.from_serializable(data)

        assert len(restored.state.unknowns) == 1
        assert len(restored.state.gaps) == 1
        assert restored.state.unknowns[0].question == "Q?"
        assert restored.state.gaps[0].description == "G"

    def test_roundtrip_serialization(self):
        """Full roundtrip serialization preserves state."""
        manager = SufficiencyManager(run_id="test-run")
        
        # Add various items
        manager.add_unknown("What is X?", importance=Importance.HIGH, blocking=True)
        manager.add_gap("Missing data", priority=Priority.HIGH)
        manager.add_assumption("User is valid", confidence=0.8)
        evidence = EvidenceItem(source="test", description="Fact 1")
        manager.update_with_evidence([evidence])

        # Serialize and restore
        data = manager.to_serializable()
        restored = SufficiencyManager.from_serializable(data)

        # Verify
        assert len(restored.state.facts) == 1
        assert len(restored.state.unknowns) == 1
        assert len(restored.state.gaps) == 1
        assert len(restored.state.assumptions) == 1

    def test_get_summary(self):
        """get_summary returns comprehensive summary."""
        manager = SufficiencyManager()
        manager.add_unknown("Q?")
        manager.update_with_evidence([
            EvidenceItem(source="t", description="F")
        ])

        summary = manager.get_summary()

        assert summary["fact_count"] == 1
        assert summary["unknown_count"] == 1
        assert "is_sufficient" in summary
        assert summary["update_count"] == 1


# ==============================
# Utility Function Tests
# ==============================
class TestSufficiencyUtilities:
    """Tests for utility functions."""

    def test_create_manager_from_empty_context(self):
        """create_sufficiency_manager_from_context with no data."""
        manager = create_sufficiency_manager_from_context(None)
        assert manager.is_sufficient() is True

    def test_create_manager_from_context_with_state(self):
        """create_sufficiency_manager_from_context restores state."""
        original = SufficiencyManager()
        original.add_unknown("Q?")
        context = {"sufficiency_state": original.to_serializable()}

        restored = create_sufficiency_manager_from_context(context)
        assert len(restored.state.unknowns) == 1

    def test_check_sufficiency_passes(self):
        """check_sufficiency_for_proceed returns True when sufficient."""
        manager = SufficiencyManager()
        can_proceed, reason = check_sufficiency_for_proceed(manager)

        assert can_proceed is True
        assert "passed" in reason.lower()

    def test_check_sufficiency_fails_with_unknowns(self):
        """check_sufficiency_for_proceed fails with blocking unknowns."""
        manager = SufficiencyManager()
        manager.add_unknown("Q?", blocking=True)

        can_proceed, reason = check_sufficiency_for_proceed(manager)

        assert can_proceed is False
        assert "blocking unknowns" in reason

    def test_check_sufficiency_fails_with_gaps(self):
        """check_sufficiency_for_proceed fails with blocking gaps."""
        manager = SufficiencyManager()
        manager.add_gap("G", blocking=True)

        can_proceed, reason = check_sufficiency_for_proceed(manager)

        assert can_proceed is False
        assert "blocking gaps" in reason

    def test_check_sufficiency_fails_with_both(self):
        """check_sufficiency_for_proceed reports both issues."""
        manager = SufficiencyManager()
        manager.add_unknown("Q?", blocking=True)
        manager.add_gap("G", blocking=True)

        can_proceed, reason = check_sufficiency_for_proceed(manager)

        assert can_proceed is False
        assert "blocking unknowns" in reason
        assert "blocking gaps" in reason


# ==============================
# Trace Event Type Tests
# ==============================
class TestTraceEventTypes:
    """Tests for sufficiency trace event types."""

    def test_sufficiency_state_updated_event_exists(self):
        """SUFFICIENCY_STATE_UPDATED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "SUFFICIENCY_STATE_UPDATED")
        assert TraceEventType.SUFFICIENCY_STATE_UPDATED.value == "sufficiency_state_updated"

    def test_sufficiency_state_restored_event_exists(self):
        """SUFFICIENCY_STATE_RESTORED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "SUFFICIENCY_STATE_RESTORED")
        assert TraceEventType.SUFFICIENCY_STATE_RESTORED.value == "sufficiency_state_restored"


# ==============================
# Integration Tests
# ==============================
class TestSufficiencyManagerIntegration:
    """Integration tests for sufficiency lifecycle."""

    def test_full_lifecycle_unknown_resolution(self):
        """Test full lifecycle: add unknown -> resolve -> sufficient."""
        manager = SufficiencyManager()

        # Start sufficient
        assert manager.is_sufficient()

        # Add blocking unknown
        unknown = manager.add_unknown("What is the API key?", blocking=True)
        assert not manager.is_sufficient()

        # Resolve with evidence
        evidence = EvidenceItem(source="config", description="API key: xxx")
        diff = manager.resolve_unknown(unknown.id, evidence)

        assert diff.unknowns_resolved == 1
        assert diff.facts_added == 1
        assert manager.is_sufficient()

    def test_full_lifecycle_gap_resolution(self):
        """Test full lifecycle: add gap -> resolve -> sufficient."""
        manager = SufficiencyManager()

        # Add blocking gap
        gap = manager.add_gap("Missing user profile", blocking=True)
        assert not manager.is_sufficient()

        # Resolve with evidence
        evidence = EvidenceItem(source="api", description="Profile fetched")
        diff = manager.resolve_gap(gap.id, evidence)

        assert diff.gaps_resolved == 1
        assert manager.is_sufficient()

    def test_diff_tracks_sufficiency_transition(self):
        """SufficiencyStateDiff tracks was_sufficient -> is_now_sufficient."""
        manager = SufficiencyManager()
        manager.add_unknown("Q?", blocking=True)

        assert not manager.is_sufficient()

        evidence = EvidenceItem(source="t", description="Answer")
        unknown_id = manager.state.unknowns[0].id
        diff = manager.resolve_unknown(unknown_id, evidence)

        assert diff.was_sufficient is False
        assert diff.is_now_sufficient is True

    def test_multiple_updates_increment_count(self):
        """Multiple updates increment update_count."""
        manager = SufficiencyManager()

        manager.update_with_evidence([EvidenceItem(source="1", description="F1")])
        manager.update_with_evidence([EvidenceItem(source="2", description="F2")])
        manager.add_unknown("Q?")
        unknown_id = manager.state.unknowns[0].id
        manager.resolve_unknown(
            unknown_id,
            EvidenceItem(source="3", description="A")
        )

        assert manager.update_count == 3
