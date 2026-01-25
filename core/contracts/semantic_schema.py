# ==============================
# Semantic Interpretation Contracts
# ==============================
"""
Semantic interpretation contracts for master/.

These models define the structured output of the semantic interpretation phase,
which extracts intent, entities, constraints, and determines whether execution
should proceed, pause for clarification, or abort.

Intended usage:
- Semantic phase produces SemanticEnvelope before step execution
- Engine checks NextAction to determine run flow
- Memory persists envelope for auditability

References:
- ORC-SEM-010...019: SemanticEnvelope requirements
- ORC-SEM-020...022: NextAction enum requirements
"""

from __future__ import annotations


# ==============================
# Imports
# ==============================

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==============================
# Enums
# ==============================
class NextAction(str, Enum):
    """
    Semantic interpretation outcome directing orchestrator behavior.
    
    ORC-SEM-020: MUST define CONTINUE, ASK_USER, ABORT
    ORC-SEM-021: MAY define NEEDS_APPROVAL for HITL gate integration
    """

    CONTINUE = "CONTINUE"
    """Proceed with step execution."""

    ASK_USER = "ASK_USER"
    """Pause and request clarification from user."""

    ABORT = "ABORT"
    """Abort the run due to unrecoverable semantic issues."""

    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    """Pause for human-in-the-loop approval (optional HITL integration)."""


# ==============================
# Semantic Envelope Enforcement Errors (ORC-SEM-ENV-001...005)
# ==============================
class SemanticEnvelopeRequiredError(Exception):
    """
    Raised when planning or execution is attempted without a valid semantic envelope.
    
    ORC-SEM-ENV-001: Planning phase MUST require valid SemanticEnvelope.
    ORC-SEM-ENV-002: Engine MUST reject calls without envelope.
    """

    def __init__(self, message: str = "SemanticEnvelope required for planning phase"):
        self.message = message
        super().__init__(self.message)


class SemanticEnvelopeNotValidatedError(Exception):
    """
    Raised when planning is attempted with an envelope that hasn't been validated.
    
    ORC-SEM-ENV-003: Engine MUST verify envelope_validated == True before planning.
    """

    def __init__(self, message: str = "SemanticEnvelope must be validated before planning"):
        self.message = message
        super().__init__(self.message)


# ==============================
# Entity Model
# ==============================
class Entity(BaseModel):
    """
    Extracted entity from user input.
    
    ORC-SEM-015: entities with type, value, confidence
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(
        ...,
        description="Entity name/identifier",
        min_length=1,
        max_length=100,
    )
    type: str = Field(
        ...,
        description="Entity type (e.g., 'date', 'amount', 'product_name')",
        min_length=1,
        max_length=50,
    )
    value: Any = Field(
        ...,
        description="Extracted value (type depends on entity type)",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this entity extraction (0.0-1.0)",
    )


# ==============================
# Ambiguity Model (ORC-SEM-AMB-001...006)
# ==============================
class Ambiguity(BaseModel):
    """
    Structured ambiguity detected during semantic interpretation.
    
    ORC-SEM-AMB-001: Ambiguities must be structured, not just string lists.
    ORC-SEM-AMB-002: Each ambiguity must track resolution method and selected option.
    """

    model_config = ConfigDict(frozen=True)

    # ORC-SEM-AMB-001: Unique identifier
    ambiguity_id: str = Field(
        ...,
        description="Unique identifier for this ambiguity",
        min_length=1,
        max_length=64,
    )
    
    # ORC-SEM-AMB-002: Description of the ambiguity
    description: str = Field(
        ...,
        description="Human-readable description of the ambiguity",
        max_length=500,
    )
    
    # ORC-SEM-AMB-003: Possible resolution options
    options: List[str] = Field(
        default_factory=list,
        description="Possible options to resolve this ambiguity",
        max_length=10,
    )
    
    # ORC-SEM-AMB-004: Source span in input text
    source_span: Optional[tuple] = Field(
        default=None,
        description="(start, end) character positions in original input",
    )
    
    # ORC-SEM-AMB-005: Resolution tracking
    resolution_method: Optional[str] = Field(
        default=None,
        description="Method used to resolve (e.g., 'user_clarification', 'default_selection', 'context_inference')",
    )
    selected_option: Optional[str] = Field(
        default=None,
        description="The option selected to resolve this ambiguity",
    )
    
    # ORC-SEM-AMB-006: Blocking flag
    is_blocking: bool = Field(
        default=True,
        description="True if this ambiguity blocks execution until resolved",
    )

    @property
    def is_resolved(self) -> bool:
        """Check if ambiguity has been resolved."""
        return self.resolution_method is not None and self.selected_option is not None


# ==============================
# SemanticEnvelope Model
# ==============================
class SemanticEnvelope(BaseModel):
    """
    Structured output of semantic interpretation phase.
    
    ORC-SEM-010: MUST be a Pydantic model in core/contracts/semantic_schema.py
    ORC-SEM-011...019: Required fields specification
    """

    model_config = ConfigDict(frozen=True)

    # ORC-SEM-011: raw_input (original user input)
    raw_input: str = Field(
        ...,
        description="Original user input before any processing",
    )

    # ORC-SEM-012: normalized_input (cleaned/standardized input)
    normalized_input: str = Field(
        ...,
        description="Cleaned and standardized input after normalization",
    )

    # ORC-SEM-013: product_id (resolved product identifier)
    product_id: str = Field(
        ...,
        description="Resolved product identifier for routing",
        min_length=1,
    )

    # ORC-SEM-014: intent_type (classified intent category)
    intent_type: str = Field(
        ...,
        description="Classified intent category (e.g., 'query', 'action', 'greeting')",
        min_length=1,
    )

    # ORC-SEM-015: entities (list of extracted entities)
    entities: List[Entity] = Field(
        default_factory=list,
        description="List of extracted entities with type, value, confidence",
        max_length=20,
    )

    # ORC-SEM-016: constraints (dict of extracted constraints/filters)
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted constraints and filters from user input",
    )

    # ORC-SEM-017: confidence (float 0.0-1.0)
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for this interpretation (0.0-1.0)",
    )

    # ORC-SEM-018: ambiguities (list of structured ambiguities)
    # ORC-SEM-AMB-001...006: Structured ambiguity tracking
    ambiguities: List[Ambiguity] = Field(
        default_factory=list,
        description="List of structured ambiguities requiring clarification",
        max_length=20,
    )
    
    # Legacy: string ambiguities for backward compatibility
    ambiguity_strings: List[str] = Field(
        default_factory=list,
        description="Legacy string-based ambiguities (deprecated)",
    )

    # ORC-SEM-019: proposed_next_action (NextAction enum value)
    proposed_next_action: NextAction = Field(
        default=NextAction.CONTINUE,
        description="Recommended next action based on interpretation",
    )

    # Additional fields per implementation plan
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters extracted from input",
    )

    interpretation_method: Optional[str] = Field(
        default=None,
        description="Method used for interpretation (e.g., 'llm', 'rule-based', 'hybrid')",
    )

    # ORC-SEM-ENV-001...005: Envelope enforcement fields
    all_constraints_satisfiable: bool = Field(
        default=True,
        description="True if all constraints can be satisfied",
    )
    envelope_validated: bool = Field(
        default=False,
        description="True if envelope has passed validation",
    )
    bypass_attempt_blocked: bool = Field(
        default=False,
        description="True if a bypass attempt was blocked (audit trail)",
    )

    # ==============================
    # Computed Properties
    # ==============================
    @property
    def ambiguity_count(self) -> int:
        """ORC-SEM-AMB: Total count of ambiguities."""
        return len(self.ambiguities)
    
    @property
    def blocking_ambiguity_count(self) -> int:
        """ORC-SEM-AMB: Count of blocking ambiguities."""
        return sum(1 for a in self.ambiguities if a.is_blocking and not a.is_resolved)
    
    @property
    def unresolved_ambiguity_count(self) -> int:
        """ORC-SEM-AMB: Count of unresolved ambiguities."""
        return sum(1 for a in self.ambiguities if not a.is_resolved)

    # ==============================
    # Validators
    # ==============================
    @field_validator("entities", mode="before")
    @classmethod
    def validate_entities_length(cls, v: List[Entity]) -> List[Entity]:
        """Enforce max 20 entities (ORC-SEM-015 implied limit)."""
        if v is not None and len(v) > 20:
            raise ValueError("entities list cannot exceed 20 items")
        return v

    @field_validator("ambiguities", mode="before")
    @classmethod
    def validate_ambiguities_length(cls, v: List[Ambiguity]) -> List[Ambiguity]:
        """Enforce max 20 ambiguities (ORC-SEM-AMB)."""
        if v is not None and len(v) > 20:
            raise ValueError("ambiguities list cannot exceed 20 items")
        return v


# ==============================
# Clarification Response
# ==============================
class ClarificationResponse(BaseModel):
    """
    Structured response when NextAction=ASK_USER.
    
    ORC-SEM-STOP-003: structured response with clarifying_question and ambiguities
    """

    model_config = ConfigDict(frozen=True)

    clarifying_question: str = Field(
        ...,
        description="Question to ask the user for clarification",
    )
    ambiguities: List[str] = Field(
        default_factory=list,
        description="List of specific ambiguities to resolve",
    )
    partial_envelope: Optional[SemanticEnvelope] = Field(
        default=None,
        description="Partial envelope with what was successfully interpreted",
    )


# ==============================
# Abort Response
# ==============================
class AbortResponse(BaseModel):
    """
    Structured error when NextAction=ABORT.
    
    ORC-SEM-STOP-005: structured error with reason and ambiguities
    """

    model_config = ConfigDict(frozen=True)

    reason: str = Field(
        ...,
        description="Reason for aborting the run",
    )
    ambiguities: List[str] = Field(
        default_factory=list,
        description="Unresolved ambiguities that led to abort",
    )
    error_code: str = Field(
        default="semantic_abort",
        description="Error code for categorization",
    )
