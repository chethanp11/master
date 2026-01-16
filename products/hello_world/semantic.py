# ==============================
# Semantic Adapter (Hello World)
# ==============================
"""
Semantic interpreter for hello_world product.

This adapter implements product-specific semantic interpretation logic,
extracting intent, entities, and constraints from user input for the
hello_world domain.

References:
- ORC-SEM-001: Semantic interpretation phase before planning
- ORC-SEM-010...019: SemanticEnvelope requirements
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from core.contracts.semantic_schema import Entity, NextAction, SemanticEnvelope
from core.orchestrator.normalization import normalize_whitespace


# ==============================
# Constants
# ==============================

# Greeting patterns for intent detection
GREETING_PATTERNS: Dict[str, List[str]] = {
    "hello": ["hello", "hallo", "hola"],
    "hi": ["hi", "hey", "heya"],
    "good_morning": ["good morning", "morning"],
    "good_afternoon": ["good afternoon", "afternoon"],
    "good_evening": ["good evening", "evening"],
    "howdy": ["howdy", "howdy-do"],
}

# Language detection patterns
LANGUAGE_PATTERNS: Dict[str, List[str]] = {
    "english": ["in english", "english please", "speak english"],
    "spanish": ["in spanish", "en español", "spanish please", "habla español"],
    "french": ["in french", "en français", "french please", "parle français"],
    "german": ["in german", "auf deutsch", "german please", "sprich deutsch"],
}

# Name extraction pattern: "I'm X", "my name is X", "call me X", etc.
NAME_PATTERNS: List[str] = [
    r"(?:i'm|i am|my name is|call me|this is)\s+([A-Z][a-zA-Z]+)",
    r"(?:hello|hi|hey),?\s+(?:i'm|i am)\s+([A-Z][a-zA-Z]+)",
]


# ==============================
# HelloWorldSemanticAdapter
# ==============================
class HelloWorldSemanticAdapter:
    """
    Semantic interpreter for hello_world product.
    
    Extracts greeting intent, name entities, and language constraints
    from user input to produce a SemanticEnvelope.
    """

    def __init__(self) -> None:
        """Initialize the semantic adapter."""
        self._name_patterns = [re.compile(p, re.IGNORECASE) for p in NAME_PATTERNS]

    def interpret(self, user_input: str, context: Dict[str, Any]) -> SemanticEnvelope:
        """
        Interpret user input into semantic envelope.
        
        For hello_world, extract:
        - Greeting intent (hello, hi, hey, good morning, etc.)
        - Name entity if present
        - Language constraint if detected
        
        Args:
            user_input: Raw user input string.
            context: Additional context (product settings, session info, etc.).
            
        Returns:
            SemanticEnvelope with extracted semantic information.
        """
        # Normalize input
        normalized = normalize_whitespace(user_input)
        lower_input = normalized.lower()
        
        # Extract greeting intent
        intent_type, intent_confidence = self._detect_greeting_intent(lower_input)
        
        # Extract entities
        entities: List[Entity] = []
        
        # Extract name if present
        name_entity = self._extract_name(user_input)
        if name_entity:
            entities.append(name_entity)
        
        # Extract constraints
        constraints: Dict[str, Any] = {}
        
        # Detect language preference
        language = self._detect_language(lower_input)
        if language:
            constraints["language"] = language
        
        # Determine ambiguities and next action
        ambiguities: List[str] = []
        next_action = NextAction.CONTINUE
        
        # If no greeting intent detected, mark as ambiguous
        if intent_type == "unknown":
            ambiguities.append("Could not determine greeting intent from input")
            # Still continue, hello_world is forgiving
            intent_confidence = 0.5
        
        # Build and return envelope
        return SemanticEnvelope(
            raw_input=user_input,
            normalized_input=normalized,
            product_id=context.get("product_id", "hello_world"),
            intent_type=intent_type,
            entities=entities,
            constraints=constraints,
            confidence=intent_confidence,
            ambiguities=ambiguities,
            proposed_next_action=next_action,
            parameters={
                "greeting_detected": intent_type != "unknown",
                "has_name": len(entities) > 0,
                "has_language_preference": "language" in constraints,
            },
            interpretation_method="rule-based",
        )

    def validate(self, envelope: SemanticEnvelope) -> Tuple[bool, List[str]]:
        """
        Validate envelope for hello_world domain.
        
        Checks:
        - Product ID matches hello_world
        - Intent type is valid for domain
        - Confidence is reasonable
        
        Args:
            envelope: SemanticEnvelope to validate.
            
        Returns:
            Tuple of (is_valid, list_of_validation_errors).
        """
        errors: List[str] = []
        
        # Check product ID
        if envelope.product_id != "hello_world":
            errors.append(
                f"Invalid product_id: expected 'hello_world', got '{envelope.product_id}'"
            )
        
        # Check intent type is known
        valid_intents = {"hello", "hi", "good_morning", "good_afternoon", 
                        "good_evening", "howdy", "unknown"}
        if envelope.intent_type not in valid_intents:
            errors.append(
                f"Invalid intent_type for hello_world: '{envelope.intent_type}'"
            )
        
        # Check confidence threshold for continuation
        if envelope.proposed_next_action == NextAction.CONTINUE and envelope.confidence < 0.3:
            errors.append(
                f"Confidence {envelope.confidence} too low for CONTINUE action"
            )
        
        # Validate entity types
        valid_entity_types = {"name", "greeting_variant"}
        for entity in envelope.entities:
            if entity.type not in valid_entity_types:
                errors.append(
                    f"Unknown entity type for hello_world: '{entity.type}'"
                )
        
        return (len(errors) == 0, errors)

    def _detect_greeting_intent(self, lower_input: str) -> Tuple[str, float]:
        """
        Detect greeting intent from lowercased input.
        
        Returns:
            Tuple of (intent_type, confidence).
        """
        for intent_type, patterns in GREETING_PATTERNS.items():
            for pattern in patterns:
                if pattern in lower_input:
                    # Higher confidence for exact match at start
                    if lower_input.startswith(pattern):
                        return (intent_type, 0.95)
                    return (intent_type, 0.85)
        
        return ("unknown", 0.0)

    def _extract_name(self, user_input: str) -> Entity | None:
        """
        Extract name entity from user input.
        
        Returns:
            Entity with type='name' if found, None otherwise.
        """
        for pattern in self._name_patterns:
            match = pattern.search(user_input)
            if match:
                name = match.group(1)
                return Entity(
                    name="user_name",
                    type="name",
                    value=name,
                    confidence=0.9,
                )
        return None

    def _detect_language(self, lower_input: str) -> str | None:
        """
        Detect language preference from input.
        
        Returns:
            Language code if detected, None otherwise.
        """
        for language, patterns in LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if pattern in lower_input:
                    return language
        return None


# ==============================
# Factory Function
# ==============================
def create_semantic_adapter() -> HelloWorldSemanticAdapter:
    """
    Factory function to create HelloWorldSemanticAdapter.
    
    Used by product registry for dependency injection.
    """
    return HelloWorldSemanticAdapter()


# ==============================
# Module Exports
# ==============================
__all__ = [
    "HelloWorldSemanticAdapter",
    "create_semantic_adapter",
]
