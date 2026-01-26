"""
Tests for IMP-050: Gate Rejection Artifacts (GOV-GATE-REJ-001..010).

Verifies:
- GateRejectionArtifact model behavior and validation
- Factory functions for different rejection types
- GateRejectionStore operations
- Trace event payload generation
- Persistence dictionary format
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict

from core.contracts.gate_schema import (
    GateRejectionArtifact,
    GateRejectionSeverity,
    GateRejectionStore,
    create_rejection_artifact,
    create_confidence_rejection,
    create_sufficiency_rejection,
    create_semantic_rejection,
)
from core.memory.tracing import TraceEventType


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_run_id() -> str:
    return "run-test-12345"


@pytest.fixture
def sample_step_id() -> str:
    return "step-abc"


@pytest.fixture
def sample_artifact(sample_run_id: str) -> GateRejectionArtifact:
    return GateRejectionArtifact(
        gate_name="test_gate",
        rejection_reason="Test rejection",
        run_id=sample_run_id,
        severity=GateRejectionSeverity.MEDIUM,
    )


@pytest.fixture
def store() -> GateRejectionStore:
    return GateRejectionStore()


# ============================================================================
# GOV-GATE-REJ-001: Artifact Structure Tests
# ============================================================================


class TestGateRejectionArtifactStructure:
    """Test GateRejectionArtifact model structure."""
    
    def test_artifact_has_required_fields(self, sample_run_id: str):
        """GOV-GATE-REJ-001: Artifact has all required fields."""
        artifact = GateRejectionArtifact(
            gate_name="confidence",
            rejection_reason="Low confidence",
            run_id=sample_run_id,
        )
        
        assert artifact.rejection_id.startswith("rej-")
        assert artifact.gate_name == "confidence"
        assert artifact.rejection_reason == "Low confidence"
        assert artifact.run_id == sample_run_id
        assert artifact.severity == GateRejectionSeverity.MEDIUM  # default
        assert isinstance(artifact.timestamp, datetime)
    
    def test_artifact_auto_generates_rejection_id(self, sample_run_id: str):
        """GOV-GATE-REJ-001: Artifact auto-generates unique rejection_id."""
        artifact1 = GateRejectionArtifact(
            gate_name="gate1",
            rejection_reason="reason1",
            run_id=sample_run_id,
        )
        artifact2 = GateRejectionArtifact(
            gate_name="gate1",
            rejection_reason="reason1",
            run_id=sample_run_id,
        )
        
        assert artifact1.rejection_id != artifact2.rejection_id
    
    def test_artifact_is_frozen(self, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-001: Artifact is immutable (frozen)."""
        with pytest.raises(Exception):  # Pydantic ValidationError for frozen model
            sample_artifact.gate_name = "new_name"
    
    def test_artifact_with_optional_fields(self, sample_run_id: str, sample_step_id: str):
        """GOV-GATE-REJ-001: Artifact supports all optional fields."""
        artifact = GateRejectionArtifact(
            gate_name="semantic",
            rejection_reason="Incomplete envelope",
            run_id=sample_run_id,
            step_id=sample_step_id,
            product="test_product",
            flow="test_flow",
            severity=GateRejectionSeverity.HIGH,
            gate_inputs={"threshold": 0.7},
            recommendations=["Gather more context"],
            errors=["Field X is empty"],
            metadata={"version": "1.0"},
        )
        
        assert artifact.step_id == sample_step_id
        assert artifact.product == "test_product"
        assert artifact.flow == "test_flow"
        assert artifact.gate_inputs == {"threshold": 0.7}
        assert artifact.recommendations == ["Gather more context"]
        assert artifact.errors == ["Field X is empty"]
        assert artifact.metadata == {"version": "1.0"}


# ============================================================================
# GOV-GATE-REJ-002: Severity Tests
# ============================================================================


class TestGateRejectionSeverity:
    """Test severity classification."""
    
    def test_all_severity_levels_exist(self):
        """GOV-GATE-REJ-002: All severity levels are defined."""
        assert GateRejectionSeverity.LOW.value == "LOW"
        assert GateRejectionSeverity.MEDIUM.value == "MEDIUM"
        assert GateRejectionSeverity.HIGH.value == "HIGH"
        assert GateRejectionSeverity.CRITICAL.value == "CRITICAL"
    
    def test_default_severity_is_medium(self, sample_run_id: str):
        """GOV-GATE-REJ-002: Default severity is MEDIUM."""
        artifact = GateRejectionArtifact(
            gate_name="test",
            rejection_reason="test",
            run_id=sample_run_id,
        )
        assert artifact.severity == GateRejectionSeverity.MEDIUM
    
    def test_severity_can_be_set(self, sample_run_id: str):
        """GOV-GATE-REJ-002: Severity can be customized."""
        for severity in GateRejectionSeverity:
            artifact = GateRejectionArtifact(
                gate_name="test",
                rejection_reason="test",
                run_id=sample_run_id,
                severity=severity,
            )
            assert artifact.severity == severity


# ============================================================================
# GOV-GATE-REJ-003: Factory Function Tests
# ============================================================================


class TestRejectionArtifactFactory:
    """Test factory functions for artifact creation."""
    
    def test_create_rejection_artifact_basic(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Basic factory creates valid artifact."""
        artifact = create_rejection_artifact(
            gate_name="budget",
            rejection_reason="Budget exceeded",
            run_id=sample_run_id,
        )
        
        assert artifact.gate_name == "budget"
        assert artifact.rejection_reason == "Budget exceeded"
        assert artifact.run_id == sample_run_id
        assert artifact.severity == GateRejectionSeverity.MEDIUM
    
    def test_create_rejection_artifact_with_all_options(
        self, sample_run_id: str, sample_step_id: str
    ):
        """GOV-GATE-REJ-003: Factory supports all optional parameters."""
        artifact = create_rejection_artifact(
            gate_name="security",
            rejection_reason="Permission denied",
            run_id=sample_run_id,
            severity=GateRejectionSeverity.CRITICAL,
            gate_inputs={"resource": "secret.txt"},
            step_id=sample_step_id,
            product="prod",
            flow="flow",
            recommendations=["Check permissions"],
            errors=["Access denied"],
            metadata={"attempt": 1},
        )
        
        assert artifact.severity == GateRejectionSeverity.CRITICAL
        assert artifact.gate_inputs == {"resource": "secret.txt"}
        assert artifact.step_id == sample_step_id
        assert artifact.recommendations == ["Check permissions"]


class TestConfidenceRejectionFactory:
    """Test confidence rejection factory."""
    
    def test_creates_confidence_rejection(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Factory creates confidence rejection artifact."""
        artifact = create_confidence_rejection(
            run_id=sample_run_id,
            actual_confidence=0.45,
            threshold=0.7,
        )
        
        assert artifact.gate_name == "confidence"
        assert "Low confidence" in artifact.rejection_reason
        assert artifact.gate_inputs["actual_confidence"] == 0.45
        assert artifact.gate_inputs["threshold"] == 0.7
        assert len(artifact.recommendations) > 0
    
    def test_confidence_rejection_includes_failing_entities(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Confidence rejection includes entity failures."""
        artifact = create_confidence_rejection(
            run_id=sample_run_id,
            actual_confidence=0.5,
            threshold=0.7,
            failing_entities=["entity_a", "entity_b"],
        )
        
        assert artifact.gate_inputs["failing_entities"] == ["entity_a", "entity_b"]
        assert any("entity_a" in e for e in artifact.errors)
        assert any("entity_b" in e for e in artifact.errors)


class TestSufficiencyRejectionFactory:
    """Test sufficiency rejection factory."""
    
    def test_creates_sufficiency_rejection(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Factory creates sufficiency rejection artifact."""
        artifact = create_sufficiency_rejection(
            run_id=sample_run_id,
            blocking_gaps=["Missing user budget", "Missing date range"],
        )
        
        assert artifact.gate_name == "intent_sufficiency"
        assert "2 blocking gap(s)" in artifact.rejection_reason
        assert artifact.severity == GateRejectionSeverity.HIGH
        assert artifact.gate_inputs["blocking_gap_count"] == 2
    
    def test_sufficiency_rejection_with_unknowns(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Sufficiency rejection includes unknowns."""
        artifact = create_sufficiency_rejection(
            run_id=sample_run_id,
            blocking_gaps=["Gap 1"],
            blocking_unknowns=["Unknown 1", "Unknown 2"],
        )
        
        assert artifact.gate_inputs["blocking_unknowns"] == ["Unknown 1", "Unknown 2"]
        assert any("Unknown 1" in e for e in artifact.errors)


class TestSemanticRejectionFactory:
    """Test semantic rejection factory."""
    
    def test_creates_semantic_rejection_envelope_incomplete(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Semantic rejection for incomplete envelope."""
        artifact = create_semantic_rejection(
            run_id=sample_run_id,
            failures=["intent is empty"],
            envelope_complete=False,
        )
        
        assert artifact.gate_name == "semantic"
        assert "Incomplete semantic envelope" in artifact.rejection_reason
        assert artifact.gate_inputs["envelope_complete"] is False
    
    def test_creates_semantic_rejection_low_confidence(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Semantic rejection for low confidence."""
        artifact = create_semantic_rejection(
            run_id=sample_run_id,
            failures=["confidence too low"],
            confidence_passed=False,
        )
        
        assert "Low confidence" in artifact.rejection_reason
        assert artifact.gate_inputs["confidence_passed"] is False
    
    def test_creates_semantic_rejection_insufficient(self, sample_run_id: str):
        """GOV-GATE-REJ-003: Semantic rejection for insufficient intent."""
        artifact = create_semantic_rejection(
            run_id=sample_run_id,
            failures=["blocking gaps exist"],
            sufficiency_passed=False,
        )
        
        assert "Insufficient intent" in artifact.rejection_reason
        assert artifact.gate_inputs["sufficiency_passed"] is False


# ============================================================================
# GOV-GATE-REJ-004: Trace Payload Tests
# ============================================================================


class TestTracePayloadGeneration:
    """Test trace event payload generation."""
    
    def test_to_trace_payload_includes_required_fields(self, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-004: Trace payload has required fields."""
        payload = sample_artifact.to_trace_payload()
        
        assert "rejection_id" in payload
        assert "gate_name" in payload
        assert "rejection_reason" in payload
        assert "severity" in payload
        assert "run_id" in payload
        assert "timestamp" in payload
    
    def test_trace_payload_severity_is_string(self, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-004: Severity in payload is string value."""
        payload = sample_artifact.to_trace_payload()
        assert payload["severity"] == "MEDIUM"
    
    def test_trace_payload_timestamp_is_iso_format(self, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-004: Timestamp is ISO format string."""
        payload = sample_artifact.to_trace_payload()
        # Should be parseable back to datetime
        parsed = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)
    
    def test_trace_payload_includes_counts(self, sample_run_id: str):
        """GOV-GATE-REJ-004: Trace payload includes recommendation/error counts."""
        artifact = create_rejection_artifact(
            gate_name="test",
            rejection_reason="test",
            run_id=sample_run_id,
            recommendations=["rec1", "rec2"],
            errors=["err1", "err2", "err3"],
        )
        payload = artifact.to_trace_payload()
        
        assert payload["recommendation_count"] == 2
        assert payload["error_count"] == 3


# ============================================================================
# GOV-GATE-REJ-005: Persistence Tests
# ============================================================================


class TestPersistenceDictionary:
    """Test persistence dictionary format."""
    
    def test_to_persistence_dict_is_serializable(self, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-005: Persistence dict is JSON-serializable."""
        import json
        
        data = sample_artifact.to_persistence_dict()
        # Should not raise
        serialized = json.dumps(data)
        assert isinstance(serialized, str)
    
    def test_to_persistence_dict_includes_all_fields(self, sample_run_id: str):
        """GOV-GATE-REJ-005: Persistence dict includes all fields."""
        artifact = GateRejectionArtifact(
            gate_name="test",
            rejection_reason="test",
            run_id=sample_run_id,
            step_id="step-1",
            product="prod",
            flow="flow",
            recommendations=["rec1"],
            errors=["err1"],
            metadata={"key": "value"},
        )
        data = artifact.to_persistence_dict()
        
        assert data["gate_name"] == "test"
        assert data["rejection_reason"] == "test"
        assert data["run_id"] == sample_run_id
        assert data["step_id"] == "step-1"
        assert data["product"] == "prod"
        assert data["flow"] == "flow"
        assert data["recommendations"] == ["rec1"]
        assert data["errors"] == ["err1"]
        assert data["metadata"] == {"key": "value"}


# ============================================================================
# GOV-GATE-REJ-006..008: Store Tests
# ============================================================================


class TestGateRejectionStore:
    """Test GateRejectionStore operations."""
    
    def test_store_artifact(self, store: GateRejectionStore, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-006: Store accepts and returns ID."""
        rejection_id = store.store(sample_artifact)
        assert rejection_id == sample_artifact.rejection_id
    
    def test_get_by_id(self, store: GateRejectionStore, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-008: Retrieve by rejection_id."""
        store.store(sample_artifact)
        retrieved = store.get(sample_artifact.rejection_id)
        assert retrieved == sample_artifact
    
    def test_get_nonexistent_returns_none(self, store: GateRejectionStore):
        """GOV-GATE-REJ-008: Get nonexistent ID returns None."""
        result = store.get("nonexistent-id")
        assert result is None
    
    def test_get_by_run(self, store: GateRejectionStore, sample_run_id: str):
        """GOV-GATE-REJ-007: Filter by run_id."""
        artifact1 = create_rejection_artifact("g1", "r1", sample_run_id)
        artifact2 = create_rejection_artifact("g2", "r2", sample_run_id)
        artifact3 = create_rejection_artifact("g3", "r3", "other-run")
        
        store.store(artifact1)
        store.store(artifact2)
        store.store(artifact3)
        
        results = store.get_by_run(sample_run_id)
        assert len(results) == 2
        assert all(a.run_id == sample_run_id for a in results)
    
    def test_get_by_gate(self, store: GateRejectionStore, sample_run_id: str):
        """GOV-GATE-REJ-007: Filter by gate name."""
        artifact1 = create_rejection_artifact("confidence", "r1", sample_run_id)
        artifact2 = create_rejection_artifact("confidence", "r2", "run2")
        artifact3 = create_rejection_artifact("sufficiency", "r3", sample_run_id)
        
        store.store(artifact1)
        store.store(artifact2)
        store.store(artifact3)
        
        results = store.get_by_gate("confidence")
        assert len(results) == 2
        assert all(a.gate_name == "confidence" for a in results)
    
    def test_clear_store(self, store: GateRejectionStore, sample_artifact: GateRejectionArtifact):
        """GOV-GATE-REJ-009: Clear removes all artifacts."""
        store.store(sample_artifact)
        assert store.count() == 1
        
        store.clear()
        assert store.count() == 0
    
    def test_count(self, store: GateRejectionStore, sample_run_id: str):
        """GOV-GATE-REJ-009: Count returns correct number."""
        assert store.count() == 0
        
        for i in range(5):
            store.store(create_rejection_artifact(f"g{i}", f"r{i}", sample_run_id))
        
        assert store.count() == 5


# ============================================================================
# GOV-GATE-REJ-010: Trace Event Type Tests
# ============================================================================


class TestTraceEventTypeExists:
    """Test trace event type for rejection artifacts."""
    
    def test_gate_rejection_artifact_created_event_exists(self):
        """GOV-GATE-REJ-010: GATE_REJECTION_ARTIFACT_CREATED event type exists."""
        assert hasattr(TraceEventType, "GATE_REJECTION_ARTIFACT_CREATED")
        assert TraceEventType.GATE_REJECTION_ARTIFACT_CREATED.value == "gate_rejection_artifact_created"


# ============================================================================
# Validation Tests
# ============================================================================


class TestArtifactValidation:
    """Test artifact validation rules."""
    
    def test_gate_name_required(self, sample_run_id: str):
        """Gate name is required."""
        with pytest.raises(Exception):
            GateRejectionArtifact(
                rejection_reason="test",
                run_id=sample_run_id,
            )
    
    def test_rejection_reason_required(self, sample_run_id: str):
        """Rejection reason is required."""
        with pytest.raises(Exception):
            GateRejectionArtifact(
                gate_name="test",
                run_id=sample_run_id,
            )
    
    def test_run_id_required(self):
        """Run ID is required."""
        with pytest.raises(Exception):
            GateRejectionArtifact(
                gate_name="test",
                rejection_reason="test",
            )
    
    def test_gate_name_max_length(self, sample_run_id: str):
        """Gate name has max length of 100."""
        with pytest.raises(Exception):
            GateRejectionArtifact(
                gate_name="x" * 101,
                rejection_reason="test",
                run_id=sample_run_id,
            )
    
    def test_rejection_reason_max_length(self, sample_run_id: str):
        """Rejection reason has max length of 500."""
        with pytest.raises(Exception):
            GateRejectionArtifact(
                gate_name="test",
                rejection_reason="x" * 501,
                run_id=sample_run_id,
            )
    
    def test_extra_fields_forbidden(self, sample_run_id: str):
        """Extra fields are not allowed."""
        with pytest.raises(Exception):
            GateRejectionArtifact(
                gate_name="test",
                rejection_reason="test",
                run_id=sample_run_id,
                unknown_field="value",
            )


# ============================================================================
# Integration-style Tests
# ============================================================================


class TestArtifactCreationWorkflow:
    """Test complete artifact creation workflow."""
    
    def test_full_workflow(self, sample_run_id: str):
        """Test complete artifact lifecycle."""
        store = GateRejectionStore()
        
        # Create rejection artifact using factory
        artifact = create_confidence_rejection(
            run_id=sample_run_id,
            actual_confidence=0.5,
            threshold=0.8,
            step_id="step-1",
            product="test_product",
            flow="advisor",
            failing_entities=["entity_x"],
        )
        
        # Store artifact
        rejection_id = store.store(artifact)
        
        # Retrieve and verify
        retrieved = store.get(rejection_id)
        assert retrieved is not None
        assert retrieved.gate_name == "confidence"
        assert retrieved.product == "test_product"
        
        # Generate trace payload
        payload = retrieved.to_trace_payload()
        assert payload["rejection_id"] == rejection_id
        assert payload["gate_name"] == "confidence"
        
        # Generate persistence dict
        persist_data = retrieved.to_persistence_dict()
        assert persist_data["gate_inputs"]["actual_confidence"] == 0.5
        
    def test_multiple_rejections_in_run(self, sample_run_id: str):
        """Test multiple rejections in single run."""
        store = GateRejectionStore()
        
        # Create multiple rejections
        a1 = create_confidence_rejection(sample_run_id, 0.4, 0.7)
        a2 = create_sufficiency_rejection(sample_run_id, ["gap1"])
        a3 = create_semantic_rejection(sample_run_id, ["failure1"], envelope_complete=False)
        
        for a in [a1, a2, a3]:
            store.store(a)
        
        # Retrieve all for run
        run_artifacts = store.get_by_run(sample_run_id)
        assert len(run_artifacts) == 3
        
        gate_names = {a.gate_name for a in run_artifacts}
        assert gate_names == {"confidence", "intent_sufficiency", "semantic"}
