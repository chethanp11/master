# ==============================
# IMP-053: Enhanced Confidence Governance Tests
# ==============================
"""
Tests for Enhanced Confidence Governance.

Tech Specs: GOV-SEM-CONF-008..018
- GOV-SEM-CONF-008: Multiple aggregation strategies
- GOV-SEM-CONF-009: Multi-source aggregation
- GOV-SEM-CONF-010: MIN strategy takes minimum
- GOV-SEM-CONF-011: MAX strategy takes maximum
- GOV-SEM-CONF-012: WEIGHTED strategy uses weighted average
- GOV-SEM-CONF-013: PRODUCT strategy uses geometric mean
- GOV-SEM-CONF-014: Confidence decay over iterations
- GOV-SEM-CONF-015: Confidence floor enforcement
- GOV-SEM-CONF-016: Floor violation detection
- GOV-SEM-CONF-017: CONFIDENCE_FLOOR = 0.5 constant
- GOV-SEM-CONF-018: confidence_aggregated trace event
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List

from core.knowledge.confidence import (
    ConfidenceAggregationStrategy,
    aggregate_multi_source,
    apply_confidence_decay,
    validate_confidence_floor,
    is_below_confidence_floor,
    get_confidence_aggregated_payload,
    CONFIDENCE_FLOOR,
    CONFIDENCE_THRESHOLD_FLOOR,
)
from core.memory.tracing import TraceEventType


# ==============================
# ConfidenceAggregationStrategy Tests
# ==============================
class TestConfidenceAggregationStrategy:
    """Tests for ConfidenceAggregationStrategy enum."""
    
    def test_all_strategies_exist(self):
        """All required strategies are defined."""
        assert ConfidenceAggregationStrategy.MIN.value == "min"
        assert ConfidenceAggregationStrategy.MAX.value == "max"
        assert ConfidenceAggregationStrategy.WEIGHTED.value == "weighted"
        assert ConfidenceAggregationStrategy.PRODUCT.value == "product"
    
    def test_strategy_is_string_enum(self):
        """Strategy inherits from str."""
        assert isinstance(ConfidenceAggregationStrategy.MIN, str)


# ==============================
# CONFIDENCE_FLOOR Tests
# ==============================
class TestConfidenceFloor:
    """Tests for CONFIDENCE_FLOOR constant."""
    
    def test_confidence_floor_value(self):
        """CONFIDENCE_FLOOR is 0.5."""
        assert CONFIDENCE_FLOOR == 0.5
    
    def test_threshold_floor_uses_confidence_floor(self):
        """CONFIDENCE_THRESHOLD_FLOOR equals CONFIDENCE_FLOOR."""
        assert CONFIDENCE_THRESHOLD_FLOOR == CONFIDENCE_FLOOR


# ==============================
# aggregate_multi_source Tests
# ==============================
class TestAggregateMultiSourceMinStrategy:
    """Tests for MIN aggregation strategy."""
    
    def test_min_returns_minimum(self):
        """MIN strategy returns minimum confidence."""
        result = aggregate_multi_source(
            [0.9, 0.8, 0.7],
            ConfidenceAggregationStrategy.MIN,
        )
        assert result == 0.7
    
    def test_min_single_value(self):
        """MIN with single value returns that value."""
        result = aggregate_multi_source(
            [0.85],
            ConfidenceAggregationStrategy.MIN,
        )
        assert result == 0.85
    
    def test_min_clamps_values(self):
        """MIN clamps values to 0-1 range."""
        result = aggregate_multi_source(
            [0.5, 1.5, -0.2],
            ConfidenceAggregationStrategy.MIN,
        )
        assert result == 0.0  # -0.2 clamped to 0.0


class TestAggregateMultiSourceMaxStrategy:
    """Tests for MAX aggregation strategy."""
    
    def test_max_returns_maximum(self):
        """MAX strategy returns maximum confidence."""
        result = aggregate_multi_source(
            [0.9, 0.8, 0.7],
            ConfidenceAggregationStrategy.MAX,
        )
        assert result == 0.9
    
    def test_max_single_value(self):
        """MAX with single value returns that value."""
        result = aggregate_multi_source(
            [0.65],
            ConfidenceAggregationStrategy.MAX,
        )
        assert result == 0.65
    
    def test_max_clamps_values(self):
        """MAX clamps values to 0-1 range."""
        result = aggregate_multi_source(
            [0.5, 1.5, 0.3],
            ConfidenceAggregationStrategy.MAX,
        )
        assert result == 1.0  # 1.5 clamped to 1.0


class TestAggregateMultiSourceWeightedStrategy:
    """Tests for WEIGHTED aggregation strategy."""
    
    def test_weighted_equal_weights(self):
        """WEIGHTED with equal weights is arithmetic mean."""
        result = aggregate_multi_source(
            [0.6, 0.8, 1.0],
            ConfidenceAggregationStrategy.WEIGHTED,
        )
        assert result == 0.8  # (0.6 + 0.8 + 1.0) / 3
    
    def test_weighted_custom_weights(self):
        """WEIGHTED with custom weights applies correctly."""
        result = aggregate_multi_source(
            [0.6, 0.8],
            ConfidenceAggregationStrategy.WEIGHTED,
            weights=[0.25, 0.75],  # 25% to first, 75% to second
        )
        # 0.6 * 0.25 + 0.8 * 0.75 = 0.15 + 0.6 = 0.75
        assert result == 0.75
    
    def test_weighted_normalizes_weights(self):
        """WEIGHTED normalizes weights that don't sum to 1."""
        result = aggregate_multi_source(
            [0.5, 1.0],
            ConfidenceAggregationStrategy.WEIGHTED,
            weights=[1.0, 1.0],  # Will be normalized to [0.5, 0.5]
        )
        # 0.5 * 0.5 + 1.0 * 0.5 = 0.75
        assert result == 0.75


class TestAggregateMultiSourceProductStrategy:
    """Tests for PRODUCT aggregation strategy."""
    
    def test_product_geometric_mean(self):
        """PRODUCT strategy uses geometric mean."""
        result = aggregate_multi_source(
            [0.81, 0.81],
            ConfidenceAggregationStrategy.PRODUCT,
        )
        # sqrt(0.81 * 0.81) = 0.81
        assert result == 0.81
    
    def test_product_zero_confidence(self):
        """PRODUCT with zero confidence returns zero."""
        result = aggregate_multi_source(
            [0.9, 0.0, 0.8],
            ConfidenceAggregationStrategy.PRODUCT,
        )
        assert result == 0.0


class TestAggregateMultiSourceEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_list_returns_one(self):
        """Empty confidence list returns 1.0."""
        result = aggregate_multi_source([])
        assert result == 1.0
    
    def test_default_strategy_is_weighted(self):
        """Default strategy is WEIGHTED."""
        result = aggregate_multi_source([0.6, 0.8, 1.0])
        assert result == 0.8  # Weighted average


class TestAggregateMultiSourceTraceEvent:
    """Tests for trace event emission."""
    
    def test_emits_confidence_aggregated_event(self):
        """Emits confidence_aggregated trace event."""
        events: List[Dict[str, Any]] = []
        
        def emit(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        aggregate_multi_source(
            [0.9, 0.8],
            ConfidenceAggregationStrategy.MIN,
            emit_event_fn=emit,
        )
        
        assert len(events) == 1
        assert events[0]["type"] == "confidence_aggregated"
        assert events[0]["payload"]["strategy"] == "min"
        assert events[0]["payload"]["source_count"] == 2
        assert events[0]["payload"]["result"] == 0.8


# ==============================
# apply_confidence_decay Tests
# ==============================
class TestApplyConfidenceDecay:
    """Tests for apply_confidence_decay function."""
    
    def test_no_decay_at_zero_iteration(self):
        """No decay at iteration 0."""
        result = apply_confidence_decay(0.9, 0)
        assert result == 0.9
    
    def test_decay_after_one_iteration(self):
        """Decay applied after one iteration."""
        result = apply_confidence_decay(1.0, 1, 0.1)  # 10% decay
        assert result == 0.9  # 1.0 * 0.9
    
    def test_decay_after_multiple_iterations(self):
        """Decay compounds over iterations."""
        result = apply_confidence_decay(1.0, 2, 0.1)  # 10% decay
        # 1.0 * 0.9 * 0.9 = 0.81
        assert result == 0.81
    
    def test_decay_default_rate(self):
        """Default decay rate is 5%."""
        result = apply_confidence_decay(1.0, 1)
        assert result == 0.95  # 1.0 * 0.95
    
    def test_decay_clamps_to_valid_range(self):
        """Decay clamps to 0-1 range."""
        result = apply_confidence_decay(0.1, 100, 0.1)  # Many iterations
        assert result >= 0.0
        assert result <= 1.0
    
    def test_decay_with_zero_rate(self):
        """Zero decay rate causes no change."""
        result = apply_confidence_decay(0.9, 5, 0.0)
        assert result == 0.9
    
    def test_decay_with_negative_iteration(self):
        """Negative iteration returns clamped original."""
        result = apply_confidence_decay(0.9, -1)
        assert result == 0.9


# ==============================
# validate_confidence_floor Tests
# ==============================
class TestValidateConfidenceFloor:
    """Tests for validate_confidence_floor function."""
    
    def test_above_floor_unchanged(self):
        """Value above floor unchanged."""
        result = validate_confidence_floor(0.8)
        assert result == 0.8
    
    def test_below_floor_clamped(self):
        """Value below floor clamped to floor."""
        result = validate_confidence_floor(0.3)
        assert result == 0.5  # CONFIDENCE_FLOOR
    
    def test_above_one_clamped(self):
        """Value above 1.0 clamped to 1.0."""
        result = validate_confidence_floor(1.5)
        assert result == 1.0
    
    def test_custom_floor(self):
        """Custom floor is respected."""
        result = validate_confidence_floor(0.5, floor=0.6)
        assert result == 0.6


# ==============================
# is_below_confidence_floor Tests
# ==============================
class TestIsBelowConfidenceFloor:
    """Tests for is_below_confidence_floor function."""
    
    def test_below_floor_returns_true(self):
        """Returns True when below floor."""
        assert is_below_confidence_floor(0.4) is True
    
    def test_at_floor_returns_false(self):
        """Returns False when at floor."""
        assert is_below_confidence_floor(0.5) is False
    
    def test_above_floor_returns_false(self):
        """Returns False when above floor."""
        assert is_below_confidence_floor(0.7) is False
    
    def test_custom_floor(self):
        """Custom floor is respected."""
        assert is_below_confidence_floor(0.5, floor=0.6) is True


# ==============================
# get_confidence_aggregated_payload Tests
# ==============================
class TestGetConfidenceAggregatedPayload:
    """Tests for get_confidence_aggregated_payload function."""
    
    def test_payload_includes_required_fields(self):
        """Payload includes all required fields."""
        payload = get_confidence_aggregated_payload(
            confidences=[0.9, 0.8],
            strategy=ConfidenceAggregationStrategy.MIN,
            result=0.8,
        )
        
        assert payload["source_count"] == 2
        assert payload["strategy"] == "min"
        assert payload["result"] == 0.8
        assert "sources" in payload
        assert "timestamp" in payload
    
    def test_payload_with_source_labels(self):
        """Payload includes source labels when provided."""
        payload = get_confidence_aggregated_payload(
            confidences=[0.9, 0.8],
            strategy=ConfidenceAggregationStrategy.WEIGHTED,
            result=0.85,
            source_labels=["retrieval", "user_input"],
        )
        
        assert payload["sources"][0]["label"] == "retrieval"
        assert payload["sources"][1]["label"] == "user_input"


# ==============================
# Trace Event Type Tests
# ==============================
class TestTraceEventType:
    """Tests for trace event type registration."""
    
    def test_confidence_aggregated_event_exists(self):
        """CONFIDENCE_AGGREGATED trace event type exists."""
        assert hasattr(TraceEventType, "CONFIDENCE_AGGREGATED")
        assert TraceEventType.CONFIDENCE_AGGREGATED.value == "confidence_aggregated"
