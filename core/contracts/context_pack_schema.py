from __future__ import annotations

# ==============================
# Context Pack Contracts
# ==============================
"""
Deterministic context pack schemas for evidence-backed summaries.

This module consolidates:
- context_pack_schema.py (ContextPack, TablesSummary, DocumentsSummary, etc.)
- evidence_schema.py (EvidenceType, EvidenceSource, EvidenceItem)

IMP-020: Added freeze requirements (frozen, frozen_at, frozen_hash).
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.contracts.run_schema import ArtifactRef

if TYPE_CHECKING:
    from core.contracts.hypothesis_schema import HypothesisSet
    from core.contracts.sufficiency_schema import SufficiencyState


# ==============================
# ContextPack Freeze Exception (IMP-020)
# ==============================
class ContextPackFrozenError(Exception):
    """
    Raised when attempting to modify a frozen ContextPack.
    
    INT-CP-FREEZE-003: Modification attempts raise ContextPackFrozenError.
    """
    
    def __init__(self, message: str = "Cannot modify frozen ContextPack"):
        super().__init__(message)


# ==============================
# ContextPack Not Frozen Exception (IMP-021)
# ==============================
class ContextPackNotFrozenError(Exception):
    """
    Raised when attempting to execute with an unfrozen ContextPack.
    
    INT-CP-FREEZE-LC-003: Execution blocked if ContextPack not frozen.
    """
    
    def __init__(self, message: str = "ContextPack must be frozen before execution"):
        super().__init__(message)


# ==============================
# Evidence Models (from evidence_schema)
# ==============================

EvidenceType = Literal["table", "doc", "text", "metric", "chart", "document"]


class EvidenceSource(BaseModel):
    """Source information for an evidence item."""
    model_config = ConfigDict(extra="forbid")

    tool: str
    uri: Optional[str] = None
    ref: Optional[str] = None


class EvidenceItem(BaseModel):
    """
    Evidence items capture tool outputs with provenance for downstream reasoning.
    """
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EvidenceType
    source: EvidenceSource
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    content_ref: ArtifactRef
    summary: str
    provenance: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("summary")
    @classmethod
    def _summary_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("summary is required")
        return value


# ==============================
# Context Pack Models (original context_pack_schema)
# ==============================

class EvidenceIndexEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    source_tool: str
    source_ref: Optional[str] = None
    source_uri: Optional[str] = None
    type: str


class TableRowSample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    row: Dict[str, Any]


class TablesSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stats: Dict[str, Any] = Field(default_factory=dict)
    key_rows: List[TableRowSample] = Field(default_factory=list)
    column_profiles: Dict[str, Any] = Field(default_factory=dict)


class DocumentExcerpt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    excerpt_text: str
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    page_count: Optional[int] = None


class DocumentsSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    excerpts: List[DocumentExcerpt] = Field(default_factory=list)
    metadata: List[DocumentMetadata] = Field(default_factory=list)


class UserProvidedInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_set_id: str
    created_from: str
    evidence_refs: List[str] = Field(default_factory=list)
    answers: Dict[str, Any] = Field(default_factory=dict)


class ContextPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    evidence_index: List[EvidenceIndexEntry]
    tables_summary: TablesSummary
    documents_summary: DocumentsSummary
    user_provided: Optional[UserProvidedInfo] = None
    assumptions: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    pack_hash: Optional[str] = None
    # IMP-014 (INT-HYP-005): All hypotheses retained in audit trail
    all_hypotheses: List["HypothesisSet"] = Field(
        default_factory=list,
        description="Audit trail of all hypothesis sets generated during reasoning.",
    )
    # IMP-016 (INT-SUFF-001): SufficiencyState maintained per run
    sufficiency_state: Optional["SufficiencyState"] = Field(
        default=None,
        description="Current sufficiency state tracking facts, unknowns, assumptions, and gaps.",
    )
    # IMP-020 (INT-CP-FREEZE-001..003): Freeze fields
    frozen: bool = Field(
        default=False,
        description="Whether the ContextPack is frozen (immutable).",
    )
    frozen_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when ContextPack was frozen.",
    )
    frozen_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of serialized content at freeze time.",
    )
    # IMP-028 (MEM-REPRO-012): Content hash for reproducibility
    content_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of canonical content for reproducibility verification.",
    )
    
    def _check_not_frozen(self) -> None:
        """Check if frozen and raise if so."""
        if self.frozen:
            raise ContextPackFrozenError("Cannot modify frozen ContextPack")
    
    def freeze(self) -> str:
        """
        Freeze the ContextPack, making it immutable.
        
        INT-CP-FREEZE-001: ContextPack frozen (immutable) before plan generation.
        INT-CP-FREEZE-002: Frozen ContextPack has frozen_at timestamp and frozen_hash.
        MEM-REPRO-012: content_hash computed before freeze.
        
        Returns:
            The frozen_hash (SHA-256 of serialized content).
        
        Raises:
            ContextPackFrozenError: If already frozen.
        """
        if self.frozen:
            raise ContextPackFrozenError("ContextPack is already frozen")
        
        # Compute hash of serializable content (excluding freeze fields)
        content = self.model_dump(exclude={"frozen", "frozen_at", "frozen_hash", "content_hash"})
        content_json = json.dumps(content, sort_keys=True, default=str)
        computed_hash = hashlib.sha256(content_json.encode("utf-8")).hexdigest()
        
        # Set freeze state - using object.__setattr__ to bypass frozen validation
        # IMP-028: Set content_hash before freeze
        object.__setattr__(self, "content_hash", computed_hash)
        object.__setattr__(self, "frozen", True)
        object.__setattr__(self, "frozen_at", datetime.now(timezone.utc))
        object.__setattr__(self, "frozen_hash", computed_hash)
        
        return computed_hash
    
    def add_evidence(self, entry: EvidenceIndexEntry) -> None:
        """
        Add evidence to the index.
        
        Raises:
            ContextPackFrozenError: If frozen.
        """
        self._check_not_frozen()
        self.evidence_index.append(entry)
    
    def add_assumption(self, assumption: str) -> None:
        """
        Add an assumption.
        
        Raises:
            ContextPackFrozenError: If frozen.
        """
        self._check_not_frozen()
        self.assumptions.append(assumption)
    
    def add_hypothesis_set(self, hypothesis_set: "HypothesisSet") -> None:
        """
        Add a hypothesis set to the audit trail.
        
        Raises:
            ContextPackFrozenError: If frozen.
        """
        self._check_not_frozen()
        self.all_hypotheses.append(hypothesis_set)
    
    def set_limit(self, key: str, value: Any) -> None:
        """
        Set a limit value.
        
        Raises:
            ContextPackFrozenError: If frozen.
        """
        self._check_not_frozen()
        self.limits[key] = value
    
    def get_evidence_count(self) -> int:
        """Get the number of evidence entries."""
        return len(self.evidence_index)
    
    def get_freeze_payload(self, run_id: str) -> Dict[str, Any]:
        """
        Get payload for context_pack_frozen trace event.
        
        Args:
            run_id: Associated run ID.
        
        Returns:
            Dict with event payload.
        """
        return {
            "run_id": run_id,
            "frozen_hash": self.frozen_hash,
            "evidence_count": self.get_evidence_count(),
            "frozen_at": self.frozen_at.isoformat() if self.frozen_at else None,
        }


class ContextPackConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_row_limit: int = 5
    excerpt_char_limit: int = 800
    artifacts: Dict[str, Any] = Field(default_factory=dict)


# ==============================
# Exports
# ==============================

__all__ = [
    # Evidence (from evidence_schema)
    "EvidenceType",
    "EvidenceSource",
    "EvidenceItem",
    # Context Pack
    "EvidenceIndexEntry",
    "TableRowSample",
    "TablesSummary",
    "DocumentExcerpt",
    "DocumentMetadata",
    "DocumentsSummary",
    "UserProvidedInfo",
    "ContextPack",
    "ContextPackConfig",
    # IMP-020: Freeze exception
    "ContextPackFrozenError",
    # IMP-021: Not frozen exception
    "ContextPackNotFrozenError",
]
