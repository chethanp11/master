# ==============================
# Confidence Propagation Module
# ==============================
"""
Confidence propagation and threshold management.

IMP-018 (INT-CONF-001..005): Confidence as runtime signal.

This module provides:
- `aggregate_confidence`: Weighted product of component confidences
- `ConfidenceResult`: Result of confidence evaluation
- `ConfidenceThresholdAction`: Actions when confidence is below threshold
- Event payload generators for confidence-related trace events
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from core.contracts.reasoning_schema import (
    CritiqueOutput,
    InterpretOutput,
    ProposeOutput,
    RecommendOutput,
)


# ==============================
# Confidence Threshold Action (IMP-018)
# ==============================
class ConfidenceThresholdAction(str, Enum):
    """
    Actions to take when confidence falls below threshold.
    
    INT-CONF-004: Confidence below threshold triggers governance actions.
    """
    CONTINUE = "continue"  # Proceed despite low confidence
    ASK_USER = "ask_user"  # Request user input
    HITL = "hitl"  # Human-in-the-loop escalation
    ABORT = "abort"  # Abort the operation


# ==============================
# Confidence Result
# ==============================
@dataclass
class ConfidenceResult:
    """
    Result of confidence evaluation.
    
    INT-CONF-001: Confidence flows through all reasoning phases.
    """
    confidence: float
    component_count: int
    weights_used: List[float] = field(default_factory=list)
    is_below_threshold: bool = False
    threshold: float = 0.7
    recommended_action: ConfidenceThresholdAction = ConfidenceThresholdAction.CONTINUE
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "confidence": self.confidence,
            "component_count": self.component_count,
            "weights_used": self.weights_used,
            "is_below_threshold": self.is_below_threshold,
            "threshold": self.threshold,
            "recommended_action": self.recommended_action.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ==============================
# Aggregation Functions (IMP-018)
# ==============================
def aggregate_confidence(
    confidences: List[float],
    weights: Optional[List[float]] = None,
) -> ConfidenceResult:
    """
    Aggregate multiple confidence values into a single score.
    
    INT-CONF-003: Aggregated confidence uses weighted product formula.
    
    The weighted product formula:
        C_agg = prod(c_i ^ w_i) where sum(w_i) = 1
    
    Args:
        confidences: List of confidence values (0.0 to 1.0).
        weights: Optional weights (must sum to 1.0 if provided).
    
    Returns:
        ConfidenceResult with aggregated confidence.
    
    Example:
        >>> result = aggregate_confidence([0.9, 0.8, 0.7])
        >>> result.confidence  # ~0.495 (geometric mean)
    """
    if not confidences:
        return ConfidenceResult(
            confidence=1.0,
            component_count=0,
            weights_used=[],
        )
    
    # Clamp all confidences to valid range
    clamped = [max(0.0, min(1.0, c)) for c in confidences]
    n = len(clamped)
    
    # Default to equal weights if not provided
    if weights is None:
        weights = [1.0 / n] * n
    else:
        # Normalize weights to sum to 1.0
        weight_sum = sum(weights)
        if weight_sum > 0:
            weights = [w / weight_sum for w in weights]
        else:
            weights = [1.0 / n] * n
    
    # Ensure weights list matches confidences
    if len(weights) < n:
        # Pad with equal distribution of remaining weight
        remaining = 1.0 - sum(weights)
        extra_count = n - len(weights)
        extra_weight = remaining / extra_count if extra_count > 0 else 0
        weights = list(weights) + [extra_weight] * extra_count
    elif len(weights) > n:
        weights = weights[:n]
        # Re-normalize
        weight_sum = sum(weights)
        if weight_sum > 0:
            weights = [w / weight_sum for w in weights]
    
    # Weighted product: prod(c_i ^ w_i)
    result = 1.0
    for c, w in zip(clamped, weights):
        if c > 0:
            result *= c ** w
        else:
            # Any zero confidence makes result zero
            result = 0.0
            break
    
    return ConfidenceResult(
        confidence=round(result, 6),  # Avoid floating point artifacts
        component_count=n,
        weights_used=weights,
    )


def get_phase_confidence(
    phase_output: Any,
) -> float:
    """
    Extract confidence from a phase output.
    
    INT-CONF-002: Each reasoning output includes confidence field.
    
    Args:
        phase_output: A phase output (InterpretOutput, ProposeOutput, etc.)
    
    Returns:
        Confidence value (0.0 to 1.0), default 1.0 if not found.
    """
    if isinstance(phase_output, (InterpretOutput, ProposeOutput, CritiqueOutput, RecommendOutput)):
        return phase_output.confidence
    
    # Try to extract from dict or object
    if hasattr(phase_output, "confidence"):
        return getattr(phase_output, "confidence", 1.0)
    
    if isinstance(phase_output, dict):
        return phase_output.get("confidence", 1.0)
    
    return 1.0


def check_confidence_threshold(
    confidence: float,
    threshold: float = 0.7,
) -> ConfidenceResult:
    """
    Check if confidence meets threshold.
    
    INT-CONF-004: Confidence below threshold triggers governance actions.
    
    Args:
        confidence: Confidence value to check.
        threshold: Minimum acceptable confidence (default 0.7).
    
    Returns:
        ConfidenceResult with threshold evaluation.
    """
    is_below = confidence < threshold
    
    # Determine recommended action based on how far below threshold
    if not is_below:
        action = ConfidenceThresholdAction.CONTINUE
    elif confidence >= threshold * 0.8:  # Within 20% of threshold
        action = ConfidenceThresholdAction.ASK_USER
    elif confidence >= threshold * 0.5:  # Within 50% of threshold
        action = ConfidenceThresholdAction.HITL
    else:
        action = ConfidenceThresholdAction.ABORT
    
    return ConfidenceResult(
        confidence=confidence,
        component_count=1,
        weights_used=[1.0],
        is_below_threshold=is_below,
        threshold=threshold,
        recommended_action=action,
    )


def aggregate_phase_confidences(
    interpret: Optional[InterpretOutput] = None,
    propose: Optional[ProposeOutput] = None,
    critique: Optional[CritiqueOutput] = None,
    recommend: Optional[RecommendOutput] = None,
    weights: Optional[Dict[str, float]] = None,
) -> ConfidenceResult:
    """
    Aggregate confidences from all reasoning phases.
    
    INT-CONF-001: Confidence flows through all reasoning phases.
    
    Args:
        interpret: INTERPRET phase output.
        propose: PROPOSE phase output.
        critique: CRITIQUE phase output.
        recommend: RECOMMEND phase output.
        weights: Optional phase weights (interpret, propose, critique, recommend).
    
    Returns:
        ConfidenceResult with aggregated confidence.
    """
    phase_names = ["interpret", "propose", "critique", "recommend"]
    outputs = [interpret, propose, critique, recommend]
    
    # Extract confidences from provided outputs
    confidences = []
    weight_list = []
    
    for name, output in zip(phase_names, outputs):
        if output is not None:
            confidences.append(get_phase_confidence(output))
            if weights is not None:
                weight_list.append(weights.get(name, 1.0))
    
    return aggregate_confidence(
        confidences,
        weight_list if weights else None,
    )


# ==============================
# Event Payloads (IMP-018)
# ==============================
def get_confidence_below_threshold_payload(
    run_id: str,
    actual_confidence: float,
    threshold: float,
    action: ConfidenceThresholdAction,
    phase: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get payload for confidence_below_threshold trace event.
    
    INT-CONF-005: Confidence emitted in all reasoning trace events.
    
    Args:
        run_id: Associated run ID.
        actual_confidence: The actual confidence value.
        threshold: The threshold that was violated.
        action: The action taken in response.
        phase: Optional phase where violation occurred.
    
    Returns:
        Dict with event payload.
    """
    return {
        "run_id": run_id,
        "actual": actual_confidence,
        "threshold": threshold,
        "action": action.value,
        "phase": phase,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==============================
# Threshold Resolution (IMP-019)
# ==============================
# Governance floor: minimum allowed threshold
CONFIDENCE_THRESHOLD_FLOOR = 0.5


def resolve_confidence_threshold(
    product_id: Optional[str] = None,
    global_threshold: float = 0.7,
    by_product: Optional[Dict[str, Dict[str, Any]]] = None,
) -> float:
    """
    Resolve confidence threshold with per-product override.
    
    INT-CONF-THR-002: Per-product thresholds override global.
    INT-CONF-THR-005: Products cannot lower threshold below 0.5.
    
    Args:
        product_id: Product ID for per-product lookup.
        global_threshold: Global default threshold.
        by_product: Per-product configuration dict.
    
    Returns:
        Resolved confidence threshold, clamped to floor.
    """
    threshold = global_threshold
    
    # Check for per-product override
    if product_id and by_product:
        product_config = by_product.get(product_id, {})
        if "reasoning_confidence_threshold" in product_config:
            threshold = product_config["reasoning_confidence_threshold"]
    
    # Apply governance floor (INT-CONF-THR-005)
    return max(threshold, CONFIDENCE_THRESHOLD_FLOOR)


def get_threshold_violated_payload(
    run_id: str,
    actual_confidence: float,
    threshold: float,
    action: ConfidenceThresholdAction,
    product_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get payload for confidence_threshold_violated trace event.
    
    INT-CONF-THR-004: confidence_threshold_violated event logged.
    
    Args:
        run_id: Associated run ID.
        actual_confidence: The actual confidence value.
        threshold: The threshold that was violated.
        action: The action taken in response.
        product_id: Optional product ID.
    
    Returns:
        Dict with event payload.
    """
    return {
        "run_id": run_id,
        "actual": actual_confidence,
        "threshold": threshold,
        "action": action.value,
        "product_id": product_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_confidence_with_threshold(
    confidence: float,
    product_id: Optional[str] = None,
    global_threshold: float = 0.7,
    by_product: Optional[Dict[str, Dict[str, Any]]] = None,
) -> ConfidenceResult:
    """
    Evaluate confidence against resolved threshold.
    
    INT-CONF-THR-003: Threshold comparison deterministic.
    
    Args:
        confidence: Confidence value to evaluate.
        product_id: Product ID for per-product threshold.
        global_threshold: Global default threshold.
        by_product: Per-product configuration dict.
    
    Returns:
        ConfidenceResult with threshold evaluation.
    """
    threshold = resolve_confidence_threshold(
        product_id=product_id,
        global_threshold=global_threshold,
        by_product=by_product,
    )
    
    return check_confidence_threshold(confidence, threshold)
