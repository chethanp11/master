# ==============================
# IMP-018: Confidence Propagation Tests
# ==============================
"""
Tests for confidence propagation and threshold management.

Tech Spec IDs: INT-CONF-001, INT-CONF-002, INT-CONF-003, INT-CONF-004, INT-CONF-005
Tech Spec IDs (IMP-019): INT-CONF-THR-001, INT-CONF-THR-002, INT-CONF-THR-003, INT-CONF-THR-004, INT-CONF-THR-005
BRD ID: BRD-AUTO-049
"""

import pytest

from core.contracts.reasoning_schema import (
    CritiqueOutput,
    InterpretOutput,
    ProposeOutput,
    RecommendOutput,
)
from core.knowledge.confidence import (
    ConfidenceResult,
    ConfidenceThresholdAction,
    aggregate_confidence,
    aggregate_phase_confidences,
    check_confidence_threshold,
    get_confidence_below_threshold_payload,
    get_phase_confidence,
)


# ==============================
# ConfidenceThresholdAction Tests
# ==============================
class TestConfidenceThresholdAction:
    """Tests for ConfidenceThresholdAction enum."""

    def test_action_enum_values(self):
        """ConfidenceThresholdAction has correct values."""
        assert ConfidenceThresholdAction.CONTINUE.value == "continue"
        assert ConfidenceThresholdAction.ASK_USER.value == "ask_user"
        assert ConfidenceThresholdAction.HITL.value == "hitl"
        assert ConfidenceThresholdAction.ABORT.value == "abort"


# ==============================
# ConfidenceResult Tests
# ==============================
class TestConfidenceResult:
    """Tests for ConfidenceResult dataclass."""

    def test_result_creation(self):
        """ConfidenceResult can be created with basic fields."""
        result = ConfidenceResult(confidence=0.85, component_count=3)
        
        assert result.confidence == 0.85
        assert result.component_count == 3
        assert result.threshold == 0.7  # Default
        assert result.is_below_threshold is False

    def test_result_to_trace_payload(self):
        """ConfidenceResult converts to trace payload."""
        result = ConfidenceResult(
            confidence=0.6,
            component_count=2,
            weights_used=[0.5, 0.5],
            is_below_threshold=True,
            threshold=0.7,
            recommended_action=ConfidenceThresholdAction.ASK_USER,
        )
        
        payload = result.to_trace_payload()
        
        assert payload["confidence"] == 0.6
        assert payload["component_count"] == 2
        assert payload["is_below_threshold"] is True
        assert payload["recommended_action"] == "ask_user"
        assert "timestamp" in payload


# ==============================
# aggregate_confidence Tests
# ==============================
class TestAggregateConfidence:
    """Tests for aggregate_confidence function."""

    def test_empty_confidences_returns_one_int_conf_003(self):
        """INT-CONF-003: Empty list returns confidence 1.0."""
        result = aggregate_confidence([])
        
        assert result.confidence == 1.0
        assert result.component_count == 0

    def test_single_confidence_returns_same(self):
        """Single confidence returns the same value."""
        result = aggregate_confidence([0.8])
        
        assert result.confidence == 0.8
        assert result.component_count == 1

    def test_equal_confidences_geometric_mean(self):
        """Equal confidences return geometric mean."""
        # For [0.9, 0.9, 0.9] with equal weights [1/3, 1/3, 1/3]:
        # prod(0.9 ^ (1/3)) = 0.9
        result = aggregate_confidence([0.9, 0.9, 0.9])
        
        assert abs(result.confidence - 0.9) < 0.001

    def test_weighted_product_int_conf_003(self):
        """INT-CONF-003: Aggregated confidence uses weighted product."""
        # [0.9, 0.8] with weights [0.6, 0.4]:
        # 0.9^0.6 * 0.8^0.4 = 0.934 * 0.909 = 0.849
        result = aggregate_confidence([0.9, 0.8], weights=[0.6, 0.4])
        
        assert 0.84 < result.confidence < 0.86
        assert result.component_count == 2

    def test_zero_confidence_returns_zero(self):
        """Zero confidence makes result zero."""
        result = aggregate_confidence([0.9, 0.0, 0.8])
        
        assert result.confidence == 0.0

    def test_weights_normalized(self):
        """Weights are normalized to sum to 1.0."""
        result = aggregate_confidence([0.9, 0.8], weights=[6, 4])
        
        # Weights normalized to [0.6, 0.4]
        assert abs(result.weights_used[0] - 0.6) < 0.001
        assert abs(result.weights_used[1] - 0.4) < 0.001

    def test_confidences_clamped(self):
        """Confidences are clamped to valid range."""
        result = aggregate_confidence([1.5, 0.8])  # 1.5 clamped to 1.0
        
        # Should be same as [1.0, 0.8]
        expected = aggregate_confidence([1.0, 0.8])
        assert abs(result.confidence - expected.confidence) < 0.001


# ==============================
# get_phase_confidence Tests
# ==============================
class TestGetPhaseConfidence:
    """Tests for get_phase_confidence function."""

    def test_extract_from_interpret_output_int_conf_002(self):
        """INT-CONF-002: Extract confidence from InterpretOutput."""
        output = InterpretOutput(user_intent="Test", confidence=0.92)
        
        assert get_phase_confidence(output) == 0.92

    def test_extract_from_propose_output(self):
        """Extract confidence from ProposeOutput."""
        output = ProposeOutput(confidence=0.85)
        
        assert get_phase_confidence(output) == 0.85

    def test_extract_from_critique_output(self):
        """Extract confidence from CritiqueOutput."""
        output = CritiqueOutput(confidence=0.78)
        
        assert get_phase_confidence(output) == 0.78

    def test_extract_from_recommend_output(self):
        """Extract confidence from RecommendOutput."""
        output = RecommendOutput(recommendation="Do X", confidence=0.95)
        
        assert get_phase_confidence(output) == 0.95

    def test_default_confidence_from_dict(self):
        """Extract confidence from dict, default to 1.0."""
        data = {"confidence": 0.7}
        assert get_phase_confidence(data) == 0.7
        
        empty_data = {}
        assert get_phase_confidence(empty_data) == 1.0

    def test_default_confidence_from_unknown(self):
        """Unknown type returns default 1.0."""
        assert get_phase_confidence("not an output") == 1.0


# ==============================
# check_confidence_threshold Tests
# ==============================
class TestCheckConfidenceThreshold:
    """Tests for check_confidence_threshold function."""

    def test_above_threshold_continues_int_conf_004(self):
        """INT-CONF-004: Above threshold returns CONTINUE."""
        result = check_confidence_threshold(0.8, threshold=0.7)
        
        assert not result.is_below_threshold
        assert result.recommended_action == ConfidenceThresholdAction.CONTINUE

    def test_at_threshold_continues(self):
        """At threshold returns CONTINUE."""
        result = check_confidence_threshold(0.7, threshold=0.7)
        
        assert not result.is_below_threshold
        assert result.recommended_action == ConfidenceThresholdAction.CONTINUE

    def test_below_threshold_within_20_asks_user(self):
        """Within 20% of threshold recommends ASK_USER."""
        result = check_confidence_threshold(0.6, threshold=0.7)  # 0.6 >= 0.56
        
        assert result.is_below_threshold
        assert result.recommended_action == ConfidenceThresholdAction.ASK_USER

    def test_below_threshold_within_50_hitl(self):
        """Within 50% of threshold recommends HITL."""
        result = check_confidence_threshold(0.4, threshold=0.7)  # 0.4 >= 0.35
        
        assert result.is_below_threshold
        assert result.recommended_action == ConfidenceThresholdAction.HITL

    def test_far_below_threshold_aborts(self):
        """Far below threshold recommends ABORT."""
        result = check_confidence_threshold(0.2, threshold=0.7)  # 0.2 < 0.35
        
        assert result.is_below_threshold
        assert result.recommended_action == ConfidenceThresholdAction.ABORT


# ==============================
# aggregate_phase_confidences Tests
# ==============================
class TestAggregatePhaseConfidences:
    """Tests for aggregate_phase_confidences function."""

    def test_single_phase_int_conf_001(self):
        """INT-CONF-001: Confidence flows through single phase."""
        interpret = InterpretOutput(user_intent="Test", confidence=0.9)
        
        result = aggregate_phase_confidences(interpret=interpret)
        
        assert result.confidence == 0.9
        assert result.component_count == 1

    def test_multiple_phases_int_conf_001(self):
        """INT-CONF-001: Confidence flows through all phases."""
        interpret = InterpretOutput(user_intent="Test", confidence=0.9)
        propose = ProposeOutput(confidence=0.85)
        critique = CritiqueOutput(confidence=0.8)
        
        result = aggregate_phase_confidences(
            interpret=interpret,
            propose=propose,
            critique=critique,
        )
        
        assert result.component_count == 3
        # Should be weighted product
        assert 0.8 < result.confidence < 0.9

    def test_weighted_phases(self):
        """Phase weights can be specified."""
        interpret = InterpretOutput(user_intent="Test", confidence=0.9)
        propose = ProposeOutput(confidence=0.6)
        
        result = aggregate_phase_confidences(
            interpret=interpret,
            propose=propose,
            weights={"interpret": 0.3, "propose": 0.7},
        )
        
        # propose (lower) has higher weight, so result should be closer to 0.6
        assert result.confidence < 0.8

    def test_skipped_phases_ignored(self):
        """Phases with None values are skipped."""
        result = aggregate_phase_confidences(
            interpret=None,
            propose=ProposeOutput(confidence=0.8),
            critique=None,
        )
        
        assert result.component_count == 1
        assert result.confidence == 0.8


# ==============================
# Event Payload Tests
# ==============================
class TestConfidenceEventPayloads:
    """Tests for confidence trace event payloads."""

    def test_threshold_payload_int_conf_005(self):
        """INT-CONF-005: Confidence below threshold event has correct payload."""
        payload = get_confidence_below_threshold_payload(
            run_id="test-run",
            actual_confidence=0.5,
            threshold=0.7,
            action=ConfidenceThresholdAction.HITL,
            phase="propose",
        )
        
        assert payload["run_id"] == "test-run"
        assert payload["actual"] == 0.5
        assert payload["threshold"] == 0.7
        assert payload["action"] == "hitl"
        assert payload["phase"] == "propose"
        assert "timestamp" in payload


# ==============================
# Trace Event Type Tests
# ==============================
class TestConfidenceTraceEventTypes:
    """Tests for confidence trace event types."""

    def test_confidence_below_threshold_event_exists(self):
        """CONFIDENCE_BELOW_THRESHOLD trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "CONFIDENCE_BELOW_THRESHOLD")
        assert TraceEventType.CONFIDENCE_BELOW_THRESHOLD.value == "confidence_below_threshold"

    def test_confidence_aggregated_event_exists(self):
        """CONFIDENCE_AGGREGATED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "CONFIDENCE_AGGREGATED")
        assert TraceEventType.CONFIDENCE_AGGREGATED.value == "confidence_aggregated"


# ==============================
# IMP-019: Confidence Threshold Tests
# ==============================
class TestConfidenceThresholdFloor:
    """Tests for confidence threshold governance floor."""

    def test_floor_constant_is_point_five_int_conf_thr_005(self):
        """INT-CONF-THR-005: Governance floor is 0.5."""
        from core.knowledge.confidence import CONFIDENCE_THRESHOLD_FLOOR

        assert CONFIDENCE_THRESHOLD_FLOOR == 0.5


class TestResolveConfidenceThreshold:
    """Tests for resolve_confidence_threshold function."""

    def test_default_threshold_int_conf_thr_001(self):
        """INT-CONF-THR-001: Global threshold default is 0.7."""
        from core.knowledge.confidence import resolve_confidence_threshold

        threshold = resolve_confidence_threshold()
        
        assert threshold == 0.7

    def test_custom_global_threshold(self):
        """Custom global threshold is used when provided."""
        from core.knowledge.confidence import resolve_confidence_threshold

        threshold = resolve_confidence_threshold(global_threshold=0.8)
        
        assert threshold == 0.8

    def test_per_product_override_int_conf_thr_002(self):
        """INT-CONF-THR-002: Per-product threshold overrides global."""
        from core.knowledge.confidence import resolve_confidence_threshold

        by_product = {
            "test_product": {"reasoning_confidence_threshold": 0.85},
        }
        
        threshold = resolve_confidence_threshold(
            product_id="test_product",
            global_threshold=0.7,
            by_product=by_product,
        )
        
        assert threshold == 0.85

    def test_unknown_product_uses_global(self):
        """Unknown product falls back to global threshold."""
        from core.knowledge.confidence import resolve_confidence_threshold

        by_product = {
            "other_product": {"reasoning_confidence_threshold": 0.9},
        }
        
        threshold = resolve_confidence_threshold(
            product_id="test_product",
            global_threshold=0.7,
            by_product=by_product,
        )
        
        assert threshold == 0.7

    def test_floor_enforced_int_conf_thr_005(self):
        """INT-CONF-THR-005: Products cannot lower threshold below 0.5."""
        from core.knowledge.confidence import resolve_confidence_threshold

        by_product = {
            "low_product": {"reasoning_confidence_threshold": 0.3},
        }
        
        threshold = resolve_confidence_threshold(
            product_id="low_product",
            global_threshold=0.7,
            by_product=by_product,
        )
        
        # Clamped to floor
        assert threshold == 0.5


class TestThresholdViolatedPayload:
    """Tests for threshold violated event payload."""

    def test_payload_has_required_fields_int_conf_thr_004(self):
        """INT-CONF-THR-004: confidence_threshold_violated event logged."""
        from core.knowledge.confidence import (
            get_threshold_violated_payload,
            ConfidenceThresholdAction,
        )

        payload = get_threshold_violated_payload(
            run_id="test-run",
            actual_confidence=0.6,
            threshold=0.7,
            action=ConfidenceThresholdAction.ASK_USER,
            product_id="test_product",
        )
        
        assert payload["run_id"] == "test-run"
        assert payload["actual"] == 0.6
        assert payload["threshold"] == 0.7
        assert payload["action"] == "ask_user"
        assert payload["product_id"] == "test_product"
        assert "timestamp" in payload


class TestEvaluateConfidenceWithThreshold:
    """Tests for evaluate_confidence_with_threshold function."""

    def test_uses_resolved_threshold_int_conf_thr_003(self):
        """INT-CONF-THR-003: Threshold comparison deterministic."""
        from core.knowledge.confidence import evaluate_confidence_with_threshold

        # At exactly the threshold should pass
        result = evaluate_confidence_with_threshold(
            confidence=0.7,
            global_threshold=0.7,
        )
        
        assert not result.is_below_threshold
        
        # Just below should fail
        result = evaluate_confidence_with_threshold(
            confidence=0.69,
            global_threshold=0.7,
        )
        
        assert result.is_below_threshold

    def test_uses_product_threshold(self):
        """Product-specific threshold is used when available."""
        from core.knowledge.confidence import evaluate_confidence_with_threshold

        by_product = {
            "strict_product": {"reasoning_confidence_threshold": 0.9},
        }
        
        result = evaluate_confidence_with_threshold(
            confidence=0.8,
            product_id="strict_product",
            global_threshold=0.7,
            by_product=by_product,
        )
        
        # 0.8 is below 0.9, so should fail
        assert result.is_below_threshold
        assert result.threshold == 0.9


class TestConfidenceThresholdViolatedEventType:
    """Tests for CONFIDENCE_THRESHOLD_VIOLATED trace event type."""

    def test_event_exists(self):
        """CONFIDENCE_THRESHOLD_VIOLATED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "CONFIDENCE_THRESHOLD_VIOLATED")
        assert TraceEventType.CONFIDENCE_THRESHOLD_VIOLATED.value == "confidence_threshold_violated"


class TestReasoningConfidenceThresholdConfig:
    """Tests for reasoning_confidence_threshold in PoliciesConfig."""

    def test_config_default_is_point_seven(self):
        """reasoning_confidence_threshold defaults to 0.7."""
        from core.config.schema import PoliciesConfig

        config = PoliciesConfig()
        
        assert config.reasoning_confidence_threshold == 0.7

    def test_config_floor_enforced(self):
        """reasoning_confidence_threshold cannot be below 0.5."""
        from pydantic import ValidationError
        from core.config.schema import PoliciesConfig

        # Should raise validation error when below 0.5
        with pytest.raises(ValidationError):
            PoliciesConfig(reasoning_confidence_threshold=0.3)

    def test_config_accepts_valid_values(self):
        """reasoning_confidence_threshold accepts valid values."""
        from core.config.schema import PoliciesConfig

        config = PoliciesConfig(reasoning_confidence_threshold=0.8)
        assert config.reasoning_confidence_threshold == 0.8
        
        config = PoliciesConfig(reasoning_confidence_threshold=0.5)  # Floor
        assert config.reasoning_confidence_threshold == 0.5