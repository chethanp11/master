# ==============================
# Tests for IMP-026: Explanation Artifact Structure
# ==============================
"""
Test suite for Explanation Artifact Pydantic models.

IMP-026: MEM-EXPLAIN-ART-001, MEM-EXPLAIN-ART-002, MEM-EXPLAIN-ART-003
BRD: BRD-OPS-060
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from core.contracts.explanation_schema import (
    EvidenceRefModel,
    DecisionPointModel,
    ReasoningStepModel,
    ConfidencePointModel,
    TerminalOutcomeSection,
    ExplanationArtifactModel,
    dataclass_to_pydantic_evidence,
    dataclass_to_pydantic_decision,
    dataclass_to_pydantic_step,
    dataclass_to_pydantic_artifact,
)
from core.contracts.run_schema import OutcomeReason
from core.memory.explainability import (
    EvidenceRef,
    DecisionPoint,
    ReasoningStep,
    ConfidencePoint,
    ExplanationArtifact,
    explain_run,
    to_pydantic_artifact,
    explain_run_pydantic,
)


# ==============================
# MEM-EXPLAIN-ART-001: ExplanationArtifact Structure
# ==============================

class TestExplanationArtifactModel:
    """Tests for ExplanationArtifactModel Pydantic model."""
    
    def test_artifact_has_run_id(self):
        """MEM-EXPLAIN-ART-001: Artifact includes run_id."""
        artifact = ExplanationArtifactModel(run_id="test-run-001")
        assert artifact.run_id == "test-run-001"
    
    def test_artifact_has_created_at(self):
        """MEM-EXPLAIN-ART-001: Artifact includes created_at."""
        now = datetime.now(timezone.utc)
        artifact = ExplanationArtifactModel(run_id="test-run", created_at=now)
        assert artifact.created_at == now
    
    def test_artifact_has_reasoning_steps(self):
        """MEM-EXPLAIN-ART-001: Artifact includes reasoning_steps."""
        step = ReasoningStepModel(step_id="step-1", phase="retrieval")
        artifact = ExplanationArtifactModel(
            run_id="test-run",
            reasoning_steps=[step]
        )
        assert len(artifact.reasoning_steps) == 1
        assert artifact.reasoning_steps[0].step_id == "step-1"
    
    def test_artifact_defaults_to_empty_lists(self):
        """MEM-EXPLAIN-ART-001: Artifact defaults to empty collections."""
        artifact = ExplanationArtifactModel(run_id="test-run")
        assert artifact.reasoning_steps == []
        assert artifact.evidence_used == []
        assert artifact.decisions_made == []
        assert artifact.confidence_evolution == []
    
    def test_artifact_run_id_required(self):
        """MEM-EXPLAIN-ART-001: run_id is required."""
        with pytest.raises(Exception):
            ExplanationArtifactModel()  # type: ignore


# ==============================
# MEM-EXPLAIN-ART-002: ReasoningStep Fields
# ==============================

class TestReasoningStepModel:
    """Tests for ReasoningStepModel Pydantic model."""
    
    def test_step_has_step_id(self):
        """MEM-EXPLAIN-ART-002: Step has step_id."""
        step = ReasoningStepModel(step_id="step-001", phase="reasoning")
        assert step.step_id == "step-001"
    
    def test_step_has_phase(self):
        """MEM-EXPLAIN-ART-002: Step has phase."""
        step = ReasoningStepModel(step_id="step-001", phase="validation")
        assert step.phase == "validation"
    
    def test_step_has_input_summary(self):
        """MEM-EXPLAIN-ART-002: Step has input_summary."""
        step = ReasoningStepModel(
            step_id="step-001", 
            phase="reasoning",
            input_summary="User query about topic X"
        )
        assert step.input_summary == "User query about topic X"
    
    def test_step_has_output_summary(self):
        """MEM-EXPLAIN-ART-002: Step has output_summary."""
        step = ReasoningStepModel(
            step_id="step-001",
            phase="reasoning",
            output_summary="Generated response with 3 hypotheses"
        )
        assert step.output_summary == "Generated response with 3 hypotheses"
    
    def test_step_has_confidence(self):
        """MEM-EXPLAIN-ART-002: Step has confidence."""
        step = ReasoningStepModel(
            step_id="step-001",
            phase="reasoning",
            confidence=0.85
        )
        assert step.confidence == 0.85
    
    def test_step_has_evidence_refs(self):
        """MEM-EXPLAIN-ART-002: Step has evidence_refs list."""
        evidence = EvidenceRefModel(
            evidence_id="ev-001",
            source_tool="retriever"
        )
        step = ReasoningStepModel(
            step_id="step-001",
            phase="retrieval",
            evidence_refs=[evidence]
        )
        assert len(step.evidence_refs) == 1
        assert step.evidence_refs[0].evidence_id == "ev-001"
    
    def test_step_confidence_validation(self):
        """MEM-EXPLAIN-ART-002: Confidence must be between 0 and 1."""
        with pytest.raises(Exception):
            ReasoningStepModel(step_id="step-001", phase="test", confidence=1.5)
        with pytest.raises(Exception):
            ReasoningStepModel(step_id="step-001", phase="test", confidence=-0.1)
    
    def test_step_required_fields(self):
        """MEM-EXPLAIN-ART-002: step_id and phase are required."""
        with pytest.raises(Exception):
            ReasoningStepModel(phase="test")  # type: ignore
        with pytest.raises(Exception):
            ReasoningStepModel(step_id="test")  # type: ignore


# ==============================
# MEM-EXPLAIN-ART-003: Terminal Outcome Section
# ==============================

class TestTerminalOutcomeSection:
    """Tests for TerminalOutcomeSection Pydantic model."""
    
    def test_terminal_outcome_has_outcome(self):
        """MEM-EXPLAIN-ART-003: Terminal outcome has outcome value."""
        section = TerminalOutcomeSection(
            outcome="COMPLETED",
            outcome_reason=OutcomeReason.SUCCESS
        )
        assert section.outcome == "COMPLETED"
    
    def test_terminal_outcome_has_reason(self):
        """MEM-EXPLAIN-ART-003: Terminal outcome has outcome_reason."""
        section = TerminalOutcomeSection(
            outcome="COMPLETED",
            outcome_reason=OutcomeReason.SUCCESS
        )
        assert section.outcome_reason == OutcomeReason.SUCCESS
    
    def test_terminal_outcome_has_explanation(self):
        """MEM-EXPLAIN-ART-003: Terminal outcome has outcome_explanation."""
        section = TerminalOutcomeSection(
            outcome="COMPLETED",
            outcome_reason=OutcomeReason.SUCCESS,
            outcome_explanation="Run completed successfully with high confidence"
        )
        assert section.outcome_explanation == "Run completed successfully with high confidence"
    
    def test_terminal_outcome_all_reasons(self):
        """MEM-EXPLAIN-ART-003: All OutcomeReason values supported."""
        for reason in OutcomeReason:
            section = TerminalOutcomeSection(
                outcome="TEST",
                outcome_reason=reason
            )
            assert section.outcome_reason == reason
    
    def test_terminal_outcome_required_fields(self):
        """MEM-EXPLAIN-ART-003: outcome and outcome_reason required."""
        with pytest.raises(Exception):
            TerminalOutcomeSection(outcome_reason=OutcomeReason.SUCCESS)  # type: ignore
        with pytest.raises(Exception):
            TerminalOutcomeSection(outcome="COMPLETED")  # type: ignore


class TestArtifactWithTerminalOutcome:
    """Tests for artifact with terminal outcome section."""
    
    def test_artifact_includes_terminal_outcome(self):
        """MEM-EXPLAIN-ART-003: Artifact includes terminal_outcome."""
        terminal = TerminalOutcomeSection(
            outcome="COMPLETED",
            outcome_reason=OutcomeReason.SUCCESS,
            outcome_explanation="All done"
        )
        artifact = ExplanationArtifactModel(
            run_id="test-run",
            terminal_outcome=terminal
        )
        assert artifact.terminal_outcome is not None
        assert artifact.terminal_outcome.outcome == "COMPLETED"
        assert artifact.terminal_outcome.outcome_reason == OutcomeReason.SUCCESS
    
    def test_artifact_terminal_outcome_optional(self):
        """MEM-EXPLAIN-ART-003: Terminal outcome is optional."""
        artifact = ExplanationArtifactModel(run_id="test-run")
        assert artifact.terminal_outcome is None


# ==============================
# Evidence and Decision Models
# ==============================

class TestEvidenceRefModel:
    """Tests for EvidenceRefModel."""
    
    def test_evidence_ref_creation(self):
        """Evidence ref has required fields."""
        ref = EvidenceRefModel(
            evidence_id="ev-001",
            source_tool="retriever"
        )
        assert ref.evidence_id == "ev-001"
        assert ref.source_tool == "retriever"
        assert ref.confidence == 0.5  # default
    
    def test_evidence_ref_with_summary(self):
        """Evidence ref can include summary."""
        ref = EvidenceRefModel(
            evidence_id="ev-001",
            source_tool="retriever",
            summary="Found 5 relevant documents"
        )
        assert ref.summary == "Found 5 relevant documents"
    
    def test_evidence_ref_confidence_bounds(self):
        """Evidence confidence must be 0-1."""
        with pytest.raises(Exception):
            EvidenceRefModel(
                evidence_id="ev-001",
                source_tool="test",
                confidence=1.5
            )


class TestDecisionPointModel:
    """Tests for DecisionPointModel."""
    
    def test_decision_point_creation(self):
        """Decision point has required fields."""
        decision = DecisionPointModel(
            decision_id="dec-001",
            phase="reasoning",
            decision_type="hypothesis_selection"
        )
        assert decision.decision_id == "dec-001"
        assert decision.phase == "reasoning"
        assert decision.decision_type == "hypothesis_selection"
    
    def test_decision_point_with_evidence(self):
        """Decision point can reference evidence."""
        evidence = EvidenceRefModel(
            evidence_id="ev-001",
            source_tool="retriever"
        )
        decision = DecisionPointModel(
            decision_id="dec-001",
            evidence_refs=[evidence]
        )
        assert len(decision.evidence_refs) == 1


# ==============================
# Conversion Functions
# ==============================

class TestDataclassToPydanticConversion:
    """Tests for dataclass to Pydantic conversion."""
    
    def test_convert_evidence_ref(self):
        """Convert EvidenceRef dataclass to Pydantic."""
        dc = EvidenceRef(
            evidence_id="ev-001",
            source_tool="retriever",
            confidence=0.8,
            summary="Test summary"
        )
        model = dataclass_to_pydantic_evidence(dc.to_dict())
        assert model.evidence_id == "ev-001"
        assert model.source_tool == "retriever"
        assert model.confidence == 0.8
        assert model.summary == "Test summary"
    
    def test_convert_decision_point(self):
        """Convert DecisionPoint dataclass to Pydantic."""
        dc = DecisionPoint(
            decision_id="dec-001",
            phase="reasoning",
            decision_type="selection",
            confidence=0.75
        )
        model = dataclass_to_pydantic_decision(dc.to_dict())
        assert model.decision_id == "dec-001"
        assert model.phase == "reasoning"
        assert model.confidence == 0.75
    
    def test_convert_reasoning_step(self):
        """Convert ReasoningStep dataclass to Pydantic."""
        dc = ReasoningStep(
            step_id="step-001",
            phase="retrieval",
            input_summary="Query",
            output_summary="Results",
            confidence=0.9
        )
        model = dataclass_to_pydantic_step(dc.to_dict())
        assert model.step_id == "step-001"
        assert model.phase == "retrieval"
        assert model.input_summary == "Query"
        assert model.output_summary == "Results"
        assert model.confidence == 0.9
    
    def test_convert_full_artifact(self):
        """Convert complete ExplanationArtifact to Pydantic."""
        dc = ExplanationArtifact(
            run_id="run-001",
            terminal_outcome="COMPLETED",
            outcome_reason="SUCCESS",
            outcome_explanation="All done"
        )
        model = dataclass_to_pydantic_artifact(dc.to_dict())
        assert model.run_id == "run-001"
        assert model.terminal_outcome is not None
        assert model.terminal_outcome.outcome_reason == OutcomeReason.SUCCESS


class TestToPydanticArtifactFunction:
    """Tests for to_pydantic_artifact convenience function."""
    
    def test_to_pydantic_artifact_basic(self):
        """Convert dataclass artifact to Pydantic via function."""
        dc = ExplanationArtifact(run_id="run-001")
        model = to_pydantic_artifact(dc)
        assert model.run_id == "run-001"
        assert isinstance(model, ExplanationArtifactModel)
    
    def test_to_pydantic_artifact_with_steps(self):
        """Convert artifact with reasoning steps."""
        step = ReasoningStep(
            step_id="step-001",
            phase="reasoning",
            confidence=0.8
        )
        dc = ExplanationArtifact(
            run_id="run-001",
            reasoning_chain=[step]
        )
        model = to_pydantic_artifact(dc)
        assert len(model.reasoning_steps) == 1
        assert model.reasoning_steps[0].step_id == "step-001"


class TestExplainRunPydantic:
    """Tests for explain_run_pydantic function."""
    
    def test_explain_run_pydantic_returns_model(self):
        """explain_run_pydantic returns Pydantic model."""
        model = explain_run_pydantic("run-001")
        assert isinstance(model, ExplanationArtifactModel)
        assert model.run_id == "run-001"
    
    def test_explain_run_pydantic_with_events(self):
        """explain_run_pydantic processes trace events."""
        events = [
            {
                "event_type": "confidence_update",
                "payload": {"phase": "retrieval", "confidence": 0.7}
            }
        ]
        model = explain_run_pydantic("run-001", trace_events=events)
        assert len(model.confidence_evolution) == 1
        assert model.confidence_evolution[0].phase == "retrieval"


# ==============================
# Artifact Methods
# ==============================

class TestArtifactMethods:
    """Tests for ExplanationArtifactModel methods."""
    
    def test_get_decision_chain(self):
        """Get chronological decision chain."""
        now = datetime.now(timezone.utc)
        d1 = DecisionPointModel(
            decision_id="dec-001",
            timestamp=now
        )
        d2 = DecisionPointModel(
            decision_id="dec-002",
            timestamp=now
        )
        artifact = ExplanationArtifactModel(
            run_id="run-001",
            decisions_made=[d2, d1]
        )
        chain = artifact.get_decision_chain()
        assert len(chain) == 2
    
    def test_trace_evidence_to_decisions(self):
        """Trace evidence to decisions that used it."""
        evidence = EvidenceRefModel(
            evidence_id="ev-001",
            source_tool="retriever"
        )
        decision = DecisionPointModel(
            decision_id="dec-001",
            evidence_refs=[evidence]
        )
        artifact = ExplanationArtifactModel(
            run_id="run-001",
            decisions_made=[decision]
        )
        traced = artifact.trace_evidence_to_decisions("ev-001")
        assert len(traced) == 1
        assert traced[0].decision_id == "dec-001"
    
    def test_trace_evidence_not_found(self):
        """Trace returns empty when evidence not used."""
        artifact = ExplanationArtifactModel(
            run_id="run-001",
            decisions_made=[]
        )
        traced = artifact.trace_evidence_to_decisions("ev-999")
        assert traced == []
    
    def test_get_confidence_tuples(self):
        """Get confidence evolution as tuples."""
        c1 = ConfidencePointModel(phase="start", confidence=0.5)
        c2 = ConfidencePointModel(phase="end", confidence=0.9)
        artifact = ExplanationArtifactModel(
            run_id="run-001",
            confidence_evolution=[c1, c2]
        )
        tuples = artifact.get_confidence_tuples()
        assert tuples == [("start", 0.5), ("end", 0.9)]


# ==============================
# Model Validation
# ==============================

class TestModelValidation:
    """Tests for Pydantic model validation."""
    
    def test_extra_fields_forbidden(self):
        """Extra fields are forbidden in models."""
        with pytest.raises(Exception):
            EvidenceRefModel(
                evidence_id="ev-001",
                source_tool="test",
                extra_field="not allowed"  # type: ignore
            )
    
    def test_confidence_point_model(self):
        """ConfidencePointModel has required fields."""
        cp = ConfidencePointModel(phase="test", confidence=0.8)
        assert cp.phase == "test"
        assert cp.confidence == 0.8
    
    def test_confidence_point_bounds(self):
        """Confidence must be 0-1."""
        with pytest.raises(Exception):
            ConfidencePointModel(phase="test", confidence=-0.5)


# ==============================
# Acceptance Checks
# ==============================

class TestAcceptanceChecks:
    """Acceptance criteria from imp_plan.md."""
    
    def test_artifact_includes_run_id_created_at_reasoning_steps(self):
        """AC: ExplanationArtifact includes run_id, created_at, reasoning_steps."""
        artifact = ExplanationArtifactModel(run_id="test")
        assert hasattr(artifact, "run_id")
        assert hasattr(artifact, "created_at")
        assert hasattr(artifact, "reasoning_steps")
    
    def test_reasoning_step_has_required_fields(self):
        """AC: Each reasoning_step has required fields."""
        step = ReasoningStepModel(step_id="s1", phase="p1")
        assert hasattr(step, "step_id")
        assert hasattr(step, "phase")
        assert hasattr(step, "input_summary")
        assert hasattr(step, "output_summary")
        assert hasattr(step, "confidence")
        assert hasattr(step, "evidence_refs")
    
    def test_explanation_includes_terminal_outcome(self):
        """AC: Explanation includes terminal_outcome with reason and explanation."""
        terminal = TerminalOutcomeSection(
            outcome="COMPLETED",
            outcome_reason=OutcomeReason.SUCCESS,
            outcome_explanation="Done"
        )
        artifact = ExplanationArtifactModel(
            run_id="test",
            terminal_outcome=terminal
        )
        assert artifact.terminal_outcome.outcome == "COMPLETED"
        assert artifact.terminal_outcome.outcome_reason == OutcomeReason.SUCCESS
        assert artifact.terminal_outcome.outcome_explanation == "Done"
