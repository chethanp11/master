# ==============================
# Semantic Normalization
# ==============================
"""
Core normalization functions for semantic interpretation.

These functions apply domain-agnostic, deterministic transformations
to the SemanticEnvelope before step execution.

ORC-SEM-030...035: Deterministic resolution rules
ORC-SEM-035: Core MUST NOT contain domain-specific rules

Usage:
    from core.orchestrator.normalization import apply_core_normalization
    normalized = apply_core_normalization(envelope)
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, List, Type, Union

from core.contracts.semantic_schema import Entity, SemanticEnvelope


# ==============================
# ORC-SEM-030: Whitespace Normalization
# ==============================
def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    ORC-SEM-030: Core MUST apply domain-agnostic normalization:
    whitespace trimming, case normalization.
    
    Rules:
    - Collapse multiple spaces/tabs to single space
    - Strip leading/trailing whitespace
    - Normalize line endings (CRLF/CR -> LF)
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text with consistent whitespace
        
    Examples:
        >>> normalize_whitespace("  hello   world  ")
        'hello world'
        >>> normalize_whitespace("line1\\r\\nline2\\rline3")
        'line1\\nline2\\nline3'
    """
    if not text:
        return ""
    
    # Normalize line endings: CRLF -> LF, CR -> LF
    result = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Collapse multiple whitespace (spaces, tabs) to single space
    # But preserve newlines
    lines = result.split("\n")
    normalized_lines = []
    for line in lines:
        # Collapse spaces/tabs within each line
        collapsed = re.sub(r"[ \t]+", " ", line)
        # Strip leading/trailing whitespace from each line
        normalized_lines.append(collapsed.strip())
    
    # Rejoin with newlines, then strip outer whitespace
    result = "\n".join(normalized_lines).strip()
    
    return result


# ==============================
# ORC-SEM-031: Entity Deduplication
# ==============================
def deduplicate_entities(entities: List[Entity]) -> List[Entity]:
    """
    Deduplicate entities by (name, type) tuple.
    
    ORC-SEM-031: Core MUST apply entity deduplication 
    (same type+value -> single entity).
    
    Rules:
    - Key entities by (name, type) tuple
    - Keep the instance with highest confidence
    - Preserve order of first occurrence
    
    Args:
        entities: List of entities to deduplicate
        
    Returns:
        Deduplicated list with highest-confidence instances
        
    Examples:
        >>> e1 = Entity(name="date", type="datetime", value="2026-01-16", confidence=0.8)
        >>> e2 = Entity(name="date", type="datetime", value="2026-01-16", confidence=0.95)
        >>> result = deduplicate_entities([e1, e2])
        >>> result[0].confidence
        0.95
    """
    if not entities:
        return []
    
    # Track best entity per (name, type) key
    best_by_key: Dict[tuple, Entity] = {}
    order: List[tuple] = []
    
    for entity in entities:
        key = (entity.name, entity.type)
        
        if key not in best_by_key:
            # First occurrence - track order
            order.append(key)
            best_by_key[key] = entity
        elif entity.confidence > best_by_key[key].confidence:
            # Higher confidence - replace
            best_by_key[key] = entity
    
    # Return in original order of first occurrence
    return [best_by_key[key] for key in order]


# ==============================
# ORC-SEM-032: Constraint Merging
# ==============================
def merge_constraints(constraints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge overlapping constraints deterministically.
    
    ORC-SEM-032: Core MUST merge overlapping constraints deterministically.
    
    Rules:
    - Later values override earlier values
    - Deep merge nested dicts
    - Lists are replaced, not concatenated
    
    Args:
        constraints: List of constraint dicts to merge
        
    Returns:
        Single merged constraint dict
        
    Examples:
        >>> merge_constraints([{"a": 1}, {"b": 2}, {"a": 3}])
        {'a': 3, 'b': 2}
    """
    if not constraints:
        return {}
    
    result: Dict[str, Any] = {}
    
    for constraint_dict in constraints:
        if not isinstance(constraint_dict, dict):
            continue
        result = _deep_merge(result, constraint_dict)
    
    return result


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dicts, with override taking precedence.
    
    Args:
        base: Base dictionary
        override: Override dictionary (values take precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict(base)
    
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            # Recursively merge nested dicts
            result[key] = _deep_merge(result[key], value)
        else:
            # Override (including lists - no concatenation)
            result[key] = value
    
    return result


# ==============================
# ORC-SEM-033: Stable Ordering
# ==============================
def apply_stable_ordering(envelope: SemanticEnvelope) -> SemanticEnvelope:
    """
    Apply stable ordering to envelope collections.
    
    ORC-SEM-033: Core MUST apply stable ordering to entities and constraints.
    
    Rules:
    - Sort entities by name (alphabetically)
    - Sort ambiguities alphabetically
    - Constraints dict keys are sorted
    
    Args:
        envelope: SemanticEnvelope to reorder
        
    Returns:
        New SemanticEnvelope with stable ordering
        
    Note:
        SemanticEnvelope is frozen, so this returns a new instance.
    """
    # Sort entities by name
    sorted_entities = sorted(envelope.entities, key=lambda e: e.name)
    
    # Sort ambiguities alphabetically
    sorted_ambiguities = sorted(envelope.ambiguities)
    
    # Sort constraint keys (create new ordered dict)
    sorted_constraints = dict(sorted(envelope.constraints.items()))
    
    # Sort parameters keys
    sorted_parameters = dict(sorted(envelope.parameters.items()))
    
    # Create new envelope with sorted collections
    return SemanticEnvelope(
        raw_input=envelope.raw_input,
        normalized_input=envelope.normalized_input,
        product_id=envelope.product_id,
        intent_type=envelope.intent_type,
        entities=sorted_entities,
        constraints=sorted_constraints,
        confidence=envelope.confidence,
        ambiguities=sorted_ambiguities,
        proposed_next_action=envelope.proposed_next_action,
        parameters=sorted_parameters,
        interpretation_method=envelope.interpretation_method,
    )


# ==============================
# ORC-SEM-034: Type Coercion
# ==============================
def coerce_types(value: Any, target_type: Type) -> Any:
    """
    Coerce value to target type.
    
    ORC-SEM-034: Core MUST apply schema coercions 
    (string->int, string->date where schema declares type).
    
    Supported coercions:
    - str -> int
    - str -> float
    - str -> bool ("true"/"false", "1"/"0", "yes"/"no")
    - str -> date (ISO format YYYY-MM-DD)
    - str -> datetime (ISO format)
    - int -> float
    - float -> int (truncates)
    - Any -> str
    
    Args:
        value: Value to coerce
        target_type: Target type to coerce to
        
    Returns:
        Coerced value
        
    Raises:
        TypeError: If coercion is not possible
        
    Examples:
        >>> coerce_types("42", int)
        42
        >>> coerce_types("3.14", float)
        3.14
        >>> coerce_types("true", bool)
        True
    """
    # Already correct type
    if isinstance(value, target_type):
        return value
    
    # None handling
    if value is None:
        if target_type in (str, int, float, bool):
            raise TypeError(f"Cannot coerce None to {target_type.__name__}")
        return None
    
    try:
        # String -> int
        if target_type is int and isinstance(value, str):
            return int(value.strip())
        
        # String -> float
        if target_type is float and isinstance(value, str):
            return float(value.strip())
        
        # String -> bool
        if target_type is bool and isinstance(value, str):
            lower = value.strip().lower()
            if lower in ("true", "1", "yes", "on"):
                return True
            if lower in ("false", "0", "no", "off"):
                return False
            raise ValueError(f"Cannot interpret '{value}' as bool")
        
        # String -> date
        if target_type is date and isinstance(value, str):
            return date.fromisoformat(value.strip())
        
        # String -> datetime
        if target_type is datetime and isinstance(value, str):
            return datetime.fromisoformat(value.strip())
        
        # Int -> float
        if target_type is float and isinstance(value, int):
            return float(value)
        
        # Float -> int (truncates)
        if target_type is int and isinstance(value, float):
            return int(value)
        
        # Any -> str
        if target_type is str:
            return str(value)
        
        # Unsupported coercion
        raise TypeError(
            f"Unsupported coercion: {type(value).__name__} -> {target_type.__name__}"
        )
        
    except (ValueError, TypeError) as exc:
        raise TypeError(
            f"Failed to coerce {type(value).__name__} '{value}' to {target_type.__name__}: {exc}"
        ) from exc


# ==============================
# Combined Normalization
# ==============================
def apply_core_normalization(envelope: SemanticEnvelope) -> SemanticEnvelope:
    """
    Apply all core normalizations to a SemanticEnvelope.
    
    ORC-SEM-030...034: Applies all deterministic resolution rules in order:
    1. Whitespace normalization on raw_input -> normalized_input
    2. Entity deduplication
    3. Stable ordering (entities by name, ambiguities alphabetically)
    
    Note: Constraint merging and type coercion are applied at envelope
    creation time, not here (they operate on inputs, not the envelope).
    
    Args:
        envelope: SemanticEnvelope to normalize
        
    Returns:
        New normalized SemanticEnvelope
        
    Examples:
        >>> env = SemanticEnvelope(
        ...     raw_input="  hello   world  ",
        ...     normalized_input="",
        ...     product_id="test",
        ...     intent_type="greeting",
        ... )
        >>> normalized = apply_core_normalization(env)
        >>> normalized.normalized_input
        'hello world'
    """
    # 1. Normalize whitespace: raw_input -> normalized_input
    normalized_input = normalize_whitespace(envelope.raw_input)
    
    # If envelope already has normalized_input set, use whitespace-normalized version of it
    if envelope.normalized_input:
        normalized_input = normalize_whitespace(envelope.normalized_input)
    
    # 2. Deduplicate entities
    deduped_entities = deduplicate_entities(list(envelope.entities))
    
    # 3. Create intermediate envelope with normalizations
    intermediate = SemanticEnvelope(
        raw_input=envelope.raw_input,
        normalized_input=normalized_input,
        product_id=envelope.product_id,
        intent_type=envelope.intent_type,
        entities=deduped_entities,
        constraints=envelope.constraints,
        confidence=envelope.confidence,
        ambiguities=list(envelope.ambiguities),
        proposed_next_action=envelope.proposed_next_action,
        parameters=envelope.parameters,
        interpretation_method=envelope.interpretation_method,
    )
    
    # 4. Apply stable ordering
    result = apply_stable_ordering(intermediate)
    
    return result


# ==============================
# Exports
# ==============================
__all__ = [
    "normalize_whitespace",
    "deduplicate_entities",
    "merge_constraints",
    "apply_stable_ordering",
    "coerce_types",
    "apply_core_normalization",
]
