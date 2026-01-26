"""
Enhanced PII Detection (IMP-044)

GOV-SEC-PII-001...005: Named Entity Recognition based PII detection.

This module provides:
- PIIDetector: Pattern and NER-based PII detection
- PIIEntity: Structured entity representation
- PIIMatch: Pattern match representation
- Integration with SecurityRedactor
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple


# ============================================================================
# Enums
# ============================================================================


class PIIEntityType(str, Enum):
    """
    Types of PII entities detected.
    
    GOV-SEC-PII-002: Entity type classification.
    """
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SSN = "SSN"
    CREDIT_CARD = "CREDIT_CARD"
    ADDRESS = "ADDRESS"
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"
    MEDICAL_ID = "MEDICAL_ID"
    PASSPORT = "PASSPORT"
    DRIVER_LICENSE = "DRIVER_LICENSE"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    CUSTOM = "CUSTOM"


class PIISensitivity(str, Enum):
    """
    Sensitivity level of PII.
    
    GOV-SEC-PII-003: Sensitivity classification.
    """
    LOW = "LOW"           # Names, locations
    MEDIUM = "MEDIUM"     # Email, phone
    HIGH = "HIGH"         # SSN, credit cards
    CRITICAL = "CRITICAL" # Medical, financial


# ============================================================================
# PII Entity and Match
# ============================================================================


@dataclass(frozen=True)
class PIIEntity:
    """
    A detected PII entity.
    
    GOV-SEC-PII-001: Structured entity representation.
    
    Attributes:
        entity_type: Type of PII entity
        value: The detected value (will be redacted in output)
        span: Start and end positions in original text
        confidence: Detection confidence (0.0 to 1.0)
        sensitivity: Sensitivity level
        context: Optional surrounding context
    """
    entity_type: PIIEntityType
    value: str
    span: Tuple[int, int]
    confidence: float
    sensitivity: PIISensitivity = PIISensitivity.MEDIUM
    context: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (value redacted)."""
        return {
            "entity_type": self.entity_type.value,
            "span": self.span,
            "confidence": self.confidence,
            "sensitivity": self.sensitivity.value,
            "length": len(self.value),  # Length only, not actual value
        }


@dataclass(frozen=True)
class PIIMatch:
    """
    A pattern-based PII match.
    
    Attributes:
        pattern_name: Name of the pattern that matched
        value: The matched value
        span: Start and end positions
        entity_type: The derived entity type
    """
    pattern_name: str
    value: str
    span: Tuple[int, int]
    entity_type: PIIEntityType
    
    def to_entity(self, confidence: float = 0.9) -> PIIEntity:
        """Convert to PIIEntity."""
        sensitivity = ENTITY_SENSITIVITY.get(
            self.entity_type, PIISensitivity.MEDIUM
        )
        return PIIEntity(
            entity_type=self.entity_type,
            value=self.value,
            span=self.span,
            confidence=confidence,
            sensitivity=sensitivity,
        )


# ============================================================================
# Sensitivity Mapping
# ============================================================================


ENTITY_SENSITIVITY: Dict[PIIEntityType, PIISensitivity] = {
    PIIEntityType.PERSON: PIISensitivity.LOW,
    PIIEntityType.ORGANIZATION: PIISensitivity.LOW,
    PIIEntityType.LOCATION: PIISensitivity.LOW,
    PIIEntityType.DATE: PIISensitivity.LOW,
    PIIEntityType.EMAIL: PIISensitivity.MEDIUM,
    PIIEntityType.PHONE: PIISensitivity.MEDIUM,
    PIIEntityType.IP_ADDRESS: PIISensitivity.MEDIUM,
    PIIEntityType.URL: PIISensitivity.LOW,
    PIIEntityType.SSN: PIISensitivity.HIGH,
    PIIEntityType.CREDIT_CARD: PIISensitivity.HIGH,
    PIIEntityType.BANK_ACCOUNT: PIISensitivity.HIGH,
    PIIEntityType.MEDICAL_ID: PIISensitivity.CRITICAL,
    PIIEntityType.PASSPORT: PIISensitivity.HIGH,
    PIIEntityType.DRIVER_LICENSE: PIISensitivity.HIGH,
    PIIEntityType.ADDRESS: PIISensitivity.MEDIUM,
}


# ============================================================================
# Detection Patterns
# ============================================================================


# Pattern definitions: (pattern_name, regex, entity_type, confidence)
DEFAULT_PII_PATTERNS: List[Tuple[str, str, PIIEntityType, float]] = [
    # Credit card patterns should be checked first (more digits)
    # Credit card (Visa starting with 4)
    (
        "credit_card_visa",
        r"\b4[0-9]{15}\b",
        PIIEntityType.CREDIT_CARD,
        0.92,
    ),
    # Credit card (Visa 13 digit)
    (
        "credit_card_visa_13",
        r"\b4[0-9]{12}\b",
        PIIEntityType.CREDIT_CARD,
        0.90,
    ),
    # Credit card (MasterCard)
    (
        "credit_card_mc",
        r"\b5[1-5][0-9]{14}\b",
        PIIEntityType.CREDIT_CARD,
        0.92,
    ),
    # Credit card (Amex)
    (
        "credit_card_amex",
        r"\b3[47][0-9]{13}\b",
        PIIEntityType.CREDIT_CARD,
        0.92,
    ),
    # Credit card with separators
    (
        "credit_card_sep",
        r"\b(?:4[0-9]{3}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}|5[1-5][0-9]{2}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4})\b",
        PIIEntityType.CREDIT_CARD,
        0.90,
    ),
    # Email
    (
        "email",
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        PIIEntityType.EMAIL,
        0.95,
    ),
    # Phone (US format) - require separator or parentheses to avoid matching card numbers
    (
        "phone_us",
        r"(?:\+1[-.\s]?)?\(?[0-9]{3}\)[-.\s][0-9]{3}[-.\s]?[0-9]{4}|\(?[0-9]{3}\)?[-.\s][0-9]{3}[-.\s][0-9]{4}",
        PIIEntityType.PHONE,
        0.85,
    ),
    # Phone (international)
    (
        "phone_intl",
        r"\+[1-9][0-9]{7,14}",
        PIIEntityType.PHONE,
        0.85,
    ),
    # SSN
    (
        "ssn",
        r"\b[0-9]{3}[-\s][0-9]{2}[-\s][0-9]{4}\b",
        PIIEntityType.SSN,
        0.90,
    ),
    # IP Address (IPv4)
    (
        "ipv4",
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        PIIEntityType.IP_ADDRESS,
        0.95,
    ),
    # Passport (US)
    (
        "passport_us",
        r"\b[A-Z][0-9]{8}\b",
        PIIEntityType.PASSPORT,
        0.70,
    ),
    # Driver's license (generic pattern)
    (
        "driver_license",
        r"\b[A-Z][0-9]{7,8}\b",
        PIIEntityType.DRIVER_LICENSE,
        0.60,
    ),
]


# NER keyword patterns for simple name detection
NAME_PREFIXES = {"mr", "mrs", "ms", "dr", "prof", "sir", "lady", "lord"}
NAME_SUFFIXES = {"jr", "sr", "iii", "iv", "phd", "md", "esq"}


# ============================================================================
# PII Detector
# ============================================================================


@dataclass
class PIIDetectionResult:
    """
    Result of PII detection.
    
    GOV-SEC-PII-004: Detection result with counts and entities.
    
    Attributes:
        entities: List of detected PII entities
        entity_counts: Counts by entity type
        sensitivity_counts: Counts by sensitivity level
        total_detected: Total number of PII items detected
    """
    entities: List[PIIEntity] = field(default_factory=list)
    
    @property
    def entity_counts(self) -> Dict[str, int]:
        """Count of entities by type."""
        counts: Dict[str, int] = {}
        for entity in self.entities:
            key = entity.entity_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    @property
    def sensitivity_counts(self) -> Dict[str, int]:
        """Count of entities by sensitivity."""
        counts: Dict[str, int] = {}
        for entity in self.entities:
            key = entity.sensitivity.value
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    @property
    def total_detected(self) -> int:
        """Total number of detected entities."""
        return len(self.entities)
    
    def has_high_sensitivity(self) -> bool:
        """Check if any high/critical sensitivity PII detected."""
        return any(
            e.sensitivity in (PIISensitivity.HIGH, PIISensitivity.CRITICAL)
            for e in self.entities
        )
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """
        Convert to trace event payload.
        
        GOV-SEC-PII-005: Only counts, not actual values.
        """
        return {
            "total_detected": self.total_detected,
            "entity_counts": self.entity_counts,
            "sensitivity_counts": self.sensitivity_counts,
            "has_high_sensitivity": self.has_high_sensitivity(),
        }


class PIIDetector:
    """
    PII detector with pattern and NER-based detection.
    
    GOV-SEC-PII-001...005: Enhanced PII detection.
    
    Attributes:
        patterns: Compiled regex patterns
        sensitivity_level: Detection sensitivity (affects confidence thresholds)
        emit_event_fn: Optional callback for trace event emission
    """
    
    def __init__(
        self,
        *,
        patterns: Optional[List[Tuple[str, str, PIIEntityType, float]]] = None,
        sensitivity_level: str = "normal",
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        min_confidence: float = 0.5,
    ):
        self._patterns = patterns or DEFAULT_PII_PATTERNS
        self._compiled: List[Tuple[str, Pattern, PIIEntityType, float]] = []
        self._sensitivity_level = sensitivity_level
        self._emit_event = emit_event_fn
        self._min_confidence = min_confidence
        
        # Compile patterns
        for name, pattern, entity_type, confidence in self._patterns:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._compiled.append((name, compiled, entity_type, confidence))
            except re.error:
                pass  # Skip invalid patterns
    
    def detect_patterns(self, text: str) -> List[PIIMatch]:
        """
        Detect PII using pattern matching.
        
        GOV-SEC-PII-002: Pattern-based detection.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            List of PIIMatch objects
        """
        matches: List[PIIMatch] = []
        seen_spans: Set[Tuple[int, int]] = set()
        
        for name, pattern, entity_type, confidence in self._compiled:
            if confidence < self._min_confidence:
                continue
                
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                
                # Avoid duplicate overlapping matches
                if any(
                    self._spans_overlap(span, existing)
                    for existing in seen_spans
                ):
                    continue
                
                seen_spans.add(span)
                matches.append(PIIMatch(
                    pattern_name=name,
                    value=match.group(),
                    span=span,
                    entity_type=entity_type,
                ))
        
        return matches
    
    def detect_named_entities(self, text: str) -> List[PIIEntity]:
        """
        Detect named entities using keyword-based NER.
        
        GOV-SEC-PII-001: NER-based detection (simple implementation).
        
        Note: This is a lightweight keyword-based implementation.
        For production, consider integrating with spaCy or similar.
        
        Args:
            text: Text to scan for named entities
            
        Returns:
            List of PIIEntity objects
        """
        entities: List[PIIEntity] = []
        
        # Simple name detection: look for capitalized word sequences
        # following common prefixes
        words = text.split()
        i = 0
        
        while i < len(words):
            word_lower = words[i].lower().rstrip(".,!?")
            
            # Check for name prefixes
            if word_lower in NAME_PREFIXES:
                # Collect subsequent capitalized words
                name_parts = []
                j = i + 1
                while j < len(words):
                    next_word = words[j].strip(".,!?")
                    if next_word and next_word[0].isupper():
                        name_parts.append(next_word)
                        j += 1
                    else:
                        break
                
                if name_parts:
                    name = " ".join(name_parts)
                    # Find position in original text
                    try:
                        start = text.find(name)
                        if start >= 0:
                            entities.append(PIIEntity(
                                entity_type=PIIEntityType.PERSON,
                                value=name,
                                span=(start, start + len(name)),
                                confidence=0.7,
                                sensitivity=PIISensitivity.LOW,
                            ))
                    except ValueError:
                        pass
                    i = j
                    continue
            
            i += 1
        
        # Detect potential organization names (simple heuristic)
        org_patterns = [
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Co)\b",
            r"\b[A-Z]{2,}\s+(?:Inc|Corp|LLC|Ltd)\b",
        ]
        
        for pattern in org_patterns:
            for match in re.finditer(pattern, text):
                entities.append(PIIEntity(
                    entity_type=PIIEntityType.ORGANIZATION,
                    value=match.group(),
                    span=(match.start(), match.end()),
                    confidence=0.75,
                    sensitivity=PIISensitivity.LOW,
                ))
        
        return entities
    
    def detect(self, text: str) -> PIIDetectionResult:
        """
        Perform full PII detection.
        
        GOV-SEC-PII-001...005: Combined pattern and NER detection.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            PIIDetectionResult with all detected entities
        """
        if not text:
            return PIIDetectionResult()
        
        # Pattern-based detection
        pattern_matches = self.detect_patterns(text)
        entities = [m.to_entity() for m in pattern_matches]
        
        # NER-based detection
        ner_entities = self.detect_named_entities(text)
        
        # Merge, avoiding overlaps
        existing_spans = {e.span for e in entities}
        for ner_entity in ner_entities:
            if not any(
                self._spans_overlap(ner_entity.span, existing)
                for existing in existing_spans
            ):
                entities.append(ner_entity)
                existing_spans.add(ner_entity.span)
        
        result = PIIDetectionResult(entities=entities)
        
        # Emit trace event
        if self._emit_event and result.total_detected > 0:
            self._emit_event("pii_detected", result.to_trace_payload())
        
        return result
    
    def redact(self, text: str) -> str:
        """
        Detect and redact PII from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Text with PII replaced by [REDACTED] markers
        """
        result = self.detect(text)
        if not result.entities:
            return text
        
        # Sort by span start, descending (to preserve positions)
        sorted_entities = sorted(
            result.entities,
            key=lambda e: e.span[0],
            reverse=True,
        )
        
        redacted = text
        for entity in sorted_entities:
            start, end = entity.span
            redacted = (
                redacted[:start] +
                f"[REDACTED:{entity.entity_type.value}]" +
                redacted[end:]
            )
        
        return redacted
    
    @staticmethod
    def _spans_overlap(span1: Tuple[int, int], span2: Tuple[int, int]) -> bool:
        """Check if two spans overlap."""
        return not (span1[1] <= span2[0] or span2[1] <= span1[0])
    
    def add_pattern(
        self,
        name: str,
        pattern: str,
        entity_type: PIIEntityType,
        confidence: float = 0.8,
    ) -> None:
        """
        Add a custom pattern.
        
        Args:
            name: Pattern name
            pattern: Regex pattern
            entity_type: Entity type to assign
            confidence: Detection confidence
        """
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            self._compiled.append((name, compiled, entity_type, confidence))
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
    
    def get_pattern_names(self) -> List[str]:
        """Get list of registered pattern names."""
        return [name for name, _, _, _ in self._compiled]


# ============================================================================
# Factory Functions
# ============================================================================


def create_pii_detector(
    *,
    sensitivity_level: str = "normal",
    emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    min_confidence: float = 0.5,
) -> PIIDetector:
    """
    Create a PII detector with default patterns.
    
    Args:
        sensitivity_level: Detection sensitivity ("low", "normal", "high")
        emit_event_fn: Optional callback for trace events
        min_confidence: Minimum confidence threshold
        
    Returns:
        Configured PIIDetector
    """
    return PIIDetector(
        sensitivity_level=sensitivity_level,
        emit_event_fn=emit_event_fn,
        min_confidence=min_confidence,
    )
