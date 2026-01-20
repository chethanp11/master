# ==============================
# Tests: IMP-025 Explainability Core
# ==============================
"""
Tests for IMP-025: Explainability Core.

Tech Spec References:
- MEM-EXPLAIN-001: All reasoning traces persisted with sufficient detail
- MEM-EXPLAIN-002: Each decision point traceable through evidence chain
- MEM-EXPLAIN-003: Reasoning chains reconstructable from trace events
- MEM-EXPLAIN-004: explain_run(run_id) API returns structured artifact
- MEM-EXPLAIN-005: Explanation includes required fields

All tests deterministic. No external I/O.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.memory.explainability import (
    ConfidencePoint,
    DecisionPoint,
    EvidenceRef,
    ExplanationArtifact,
    ReasoningStep,
    create_decision_point,
    create_evidence_ref,
    explain_run,
    get_decision_chain,
    trace_evidence_to_decisions,
)


# --------------------------------------------------------------------------- #
#  EvidenceRef Tests
# --------------------------------------------------------------------------- #

class TestEvidenceRef:
    """Tests for EvidenceRef dataclass."""

    def test_creation(self):
        """EvidenceRef can be created."""
        ref = EvidenceRef(
            evidence_id="ev-001",
            source_tool="sql_query",
        )
        assert ref.evidence_id == "ev-001"
        assert ref.source_tool == "sql_query"

    def test_default_confidence(self):
        """EvidenceRef defaults to 0.5 confidence."""
        ref = EvidenceRef(evidence_id="ev-001", source_tool="tool")
        assert ref.confidence == 0.5

    def test_to_dict(self):
        """EvidenceRef.to_dict() returns correct dict."""
        ref = EvidenceRef(
            evidence_id="ev-001",
            source_tool="sql_query",
            confidence=0.9,
            summary="Query result",
        )
        d = ref.to_dict()
        assert d["evidence_id"] == "ev-001"
        assert d["source_tool"] == "sql_query"
        assert d["confidence"] == 0.9
        assert d["summary"] == "Query result"


# --------------------------------------------------------------------------- #
#  DecisionPoint Tests (MEM-EXPLAIN-002)
# --------------------------------------------------------------------------- #

class TestDecisionPoint:
    """Tests for DecisionPoint dataclass."""

    def test_creation(self):
        """DecisionPoint can be created."""
        dp = DecisionPoint(
            phase="analysis",
            decision_type="hypothesis_selection",
            description="Selected hypothesis A",
        )
        assert dp.phase == "analysis"
        assert dp.decision_type == "hypothesis_selection"

    def test_auto_generated_id(self):
        """DecisionPoint gets auto-generated decision_id."""
        dp1 = DecisionPoint()
        dp2 = DecisionPoint()
        assert dp1.decision_id != dp2.decision_id
        assert len(dp1.decision_id) > 0

    def test_evidence_refs_list(self):
        """DecisionPoint can have evidence references."""
        ref = EvidenceRef(evidence_id="ev-001", source_tool="tool")
        dp = DecisionPoint(evidence_refs=[ref])
        assert len(dp.evidence_refs) == 1
        assert dp.evidence_refs[0].evidence_id == "ev-001"

    def test_source_tools_list(self):
        """DecisionPoint can have source tools."""
        dp = DecisionPoint(source_tools=["tool-a", "tool-b"])
        assert "tool-a" in dp.source_tools
        assert "tool-b" in dp.source_tools

    def test_to_dict(self):
        """DecisionPoint.to_dict() returns correct dict."""
        ref = EvidenceRef(evidence_id="ev-001", source_tool="tool")
        dp = DecisionPoint(
            phase="analysis",
            decision_type="selection",
            description="Test",
            evidence_refs=[ref],
            confidence=0.8,
        )
        d = dp.to_dict()
        assert "decision_id" in d
        assert d["phase"] == "analysis"
        assert d["decision_type"] == "selection"
        assert len(d["evidence_refs"]) == 1
        assert d["confidence"] == 0.8


# --------------------------------------------------------------------------- #
#  ReasoningStep Tests (MEM-EXPLAIN-003)
# --------------------------------------------------------------------------- #

class TestReasoningStep:
    """Tests for ReasoningStep dataclass."""

    def test_creation(self):
        """ReasoningStep can be created."""
        step = ReasoningStep(
            step_id="step-001",
            phase="gathering",
        )
        assert step.step_id == "step-001"
        assert step.phase == "gathering"

    def test_input_output_summary(self):
        """ReasoningStep has input/output summaries."""
        step = ReasoningStep(
            step_id="step-001",
            phase="analysis",
            input_summary="User asked about revenue",
            output_summary="Identified 3 data sources",
        )
        assert "revenue" in step.input_summary
        assert "data sources" in step.output_summary

    def test_with_decisions(self):
        """ReasoningStep can contain decisions."""
        dp = DecisionPoint(decision_type="selection")
        step = ReasoningStep(
            step_id="step-001",
            phase="analysis",
            decisions=[dp],
        )
        assert len(step.decisions) == 1

    def test_to_dict(self):
        """ReasoningStep.to_dict() returns correct dict."""
        step = ReasoningStep(
            step_id="step-001",
            phase="gathering",
            confidence=0.75,
            duration_ms=1500,
        )
        d = step.to_dict()
        assert d["step_id"] == "step-001"
        assert d["phase"] == "gathering"
        assert d["confidence"] == 0.75
        assert d["duration_ms"] == 1500


# --------------------------------------------------------------------------- #
#  ConfidencePoint Tests (MEM-EXPLAIN-005)
# --------------------------------------------------------------------------- #

class TestConfidencePoint:
    """Tests for ConfidencePoint dataclass."""

    def test_creation(self):
        """ConfidencePoint can be created."""
        cp = ConfidencePoint(phase="analysis", confidence=0.85)
        assert cp.phase == "analysis"
        assert cp.confidence == 0.85

    def test_to_tuple(self):
        """ConfidencePoint.to_tuple() returns (phase, confidence)."""
        cp = ConfidencePoint(phase="gathering", confidence=0.7)
        t = cp.to_tuple()
        assert t == ("gathering", 0.7)

    def test_to_dict(self):
        """ConfidencePoint.to_dict() returns correct dict."""
        cp = ConfidencePoint(
            phase="analysis",
            confidence=0.8,
            reason="High evidence quality",
        )
        d = cp.to_dict()
        assert d["phase"] == "analysis"
        assert d["confidence"] == 0.8
        assert d["reason"] == "High evidence quality"
        assert "timestamp" in d


# --------------------------------------------------------------------------- #
#  ExplanationArtifact Tests (MEM-EXPLAIN-004, MEM-EXPLAIN-005)
# --------------------------------------------------------------------------- #

class TestExplanationArtifact:
    """Tests for ExplanationArtifact dataclass."""

    def test_creation(self):
        """ExplanationArtifact can be created."""
        artifact = ExplanationArtifact(run_id="run-001")
        assert artifact.run_id == "run-001"
        assert artifact.created_at is not None

    def test_has_reasoning_chain(self):
        """ExplanationArtifact has reasoning_chain field."""
        step = ReasoningStep(step_id="step-001", phase="analysis")
        artifact = ExplanationArtifact(
            run_id="run-001",
            reasoning_chain=[step],
        )
        assert len(artifact.reasoning_chain) == 1

    def test_has_evidence_used(self):
        """ExplanationArtifact has evidence_used field."""
        ref = EvidenceRef(evidence_id="ev-001", source_tool="tool")
        artifact = ExplanationArtifact(
            run_id="run-001",
            evidence_used=[ref],
        )
        assert len(artifact.evidence_used) == 1

    def test_has_decisions_made(self):
        """ExplanationArtifact has decisions_made field."""
        dp = DecisionPoint(decision_type="selection")
        artifact = ExplanationArtifact(
            run_id="run-001",
            decisions_made=[dp],
        )
        assert len(artifact.decisions_made) == 1

    def test_has_confidence_evolution(self):
        """ExplanationArtifact has confidence_evolution field."""
        cp = ConfidencePoint(phase="analysis", confidence=0.8)
        artifact = ExplanationArtifact(
            run_id="run-001",
            confidence_evolution=[cp],
        )
        assert len(artifact.confidence_evolution) == 1

    def test_get_confidence_tuples(self):
        """get_confidence_tuples returns list of tuples."""
        artifact = ExplanationArtifact(
            run_id="run-001",
            confidence_evolution=[
                ConfidencePoint(phase="gathering", confidence=0.6),
                ConfidencePoint(phase="analysis", confidence=0.8),
            ],
        )
        tuples = artifact.get_confidence_tuples()
        assert tuples == [("gathering", 0.6), ("analysis", 0.8)]

    def test_has_terminal_outcome(self):
        """ExplanationArtifact has terminal outcome fields."""
        artifact = ExplanationArtifact(
            run_id="run-001",
            terminal_outcome="COMPLETED",
            outcome_reason="SUCCESS",
            outcome_explanation="Run completed successfully",
        )
        assert artifact.terminal_outcome == "COMPLETED"
        assert artifact.outcome_reason == "SUCCESS"
        assert artifact.outcome_explanation is not None

    def test_to_dict(self):
        """ExplanationArtifact.to_dict() returns correct dict."""
        artifact = ExplanationArtifact(
            run_id="run-001",
            terminal_outcome="COMPLETED",
        )
        d = artifact.to_dict()
        assert d["run_id"] == "run-001"
        assert "created_at" in d
        assert "reasoning_chain" in d
        assert "evidence_used" in d
        assert "decisions_made" in d
        assert "confidence_evolution" in d
        assert d["terminal_outcome"] == "COMPLETED"


# --------------------------------------------------------------------------- #
#  Helper Function Tests
# --------------------------------------------------------------------------- #

class TestCreateDecisionPoint:
    """Tests for create_decision_point function."""

    def test_creates_decision_point(self):
        """create_decision_point returns DecisionPoint."""
        dp = create_decision_point(
            phase="analysis",
            decision_type="selection",
            description="Selected option A",
        )
        assert isinstance(dp, DecisionPoint)
        assert dp.phase == "analysis"

    def test_auto_generates_id(self):
        """create_decision_point generates unique ID."""
        dp = create_decision_point()
        assert dp.decision_id is not None
        assert len(dp.decision_id) > 0


class TestCreateEvidenceRef:
    """Tests for create_evidence_ref function."""

    def test_creates_evidence_ref(self):
        """create_evidence_ref returns EvidenceRef."""
        ref = create_evidence_ref(
            evidence_id="ev-001",
            source_tool="sql_query",
            confidence=0.9,
        )
        assert isinstance(ref, EvidenceRef)
        assert ref.evidence_id == "ev-001"
        assert ref.confidence == 0.9


class TestExplainRun:
    """Tests for explain_run function (MEM-EXPLAIN-004)."""

    def test_returns_explanation_artifact(self):
        """explain_run returns ExplanationArtifact."""
        artifact = explain_run("run-001")
        assert isinstance(artifact, ExplanationArtifact)
        assert artifact.run_id == "run-001"

    def test_with_trace_events(self):
        """explain_run can process trace events."""
        events = [
            {
                "event_type": "confidence_updated",
                "payload": {"phase": "analysis", "confidence": 0.8},
            },
        ]
        artifact = explain_run("run-001", trace_events=events)
        assert len(artifact.confidence_evolution) > 0

    def test_extracts_terminal_outcome(self):
        """explain_run extracts terminal outcome from events."""
        events = [
            {
                "event_type": "run_terminal_outcome",
                "payload": {
                    "terminal_outcome": "COMPLETED",
                    "outcome_reason": "SUCCESS",
                    "outcome_explanation": "Done",
                },
            },
        ]
        artifact = explain_run("run-001", trace_events=events)
        assert artifact.terminal_outcome == "COMPLETED"


class TestGetDecisionChain:
    """Tests for get_decision_chain function."""

    def test_returns_chronological_order(self):
        """get_decision_chain returns IDs in chronological order."""
        t1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2024, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
        t3 = datetime(2024, 1, 1, 10, 10, 0, tzinfo=timezone.utc)
        
        dp1 = DecisionPoint(decision_id="d1", timestamp=t2)
        dp2 = DecisionPoint(decision_id="d2", timestamp=t1)
        dp3 = DecisionPoint(decision_id="d3", timestamp=t3)
        
        chain = get_decision_chain([dp1, dp2, dp3])
        assert chain == ["d2", "d1", "d3"]

    def test_empty_list(self):
        """get_decision_chain handles empty list."""
        chain = get_decision_chain([])
        assert chain == []


class TestTraceEvidenceToDecisions:
    """Tests for trace_evidence_to_decisions function (MEM-EXPLAIN-002)."""

    def test_finds_decisions_using_evidence(self):
        """Finds all decisions that used specific evidence."""
        ref1 = EvidenceRef(evidence_id="ev-001", source_tool="tool")
        ref2 = EvidenceRef(evidence_id="ev-002", source_tool="tool")
        
        dp1 = DecisionPoint(evidence_refs=[ref1])
        dp2 = DecisionPoint(evidence_refs=[ref2])
        dp3 = DecisionPoint(evidence_refs=[ref1, ref2])
        
        found = trace_evidence_to_decisions("ev-001", [dp1, dp2, dp3])
        assert len(found) == 2
        assert dp1 in found
        assert dp3 in found
        assert dp2 not in found

    def test_no_matches(self):
        """Returns empty list when no decisions use evidence."""
        ref = EvidenceRef(evidence_id="ev-001", source_tool="tool")
        dp = DecisionPoint(evidence_refs=[ref])
        
        found = trace_evidence_to_decisions("ev-999", [dp])
        assert found == []

    def test_empty_decisions(self):
        """Handles empty decisions list."""
        found = trace_evidence_to_decisions("ev-001", [])
        assert found == []
