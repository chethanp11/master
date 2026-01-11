from __future__ import annotations

# ==============================
# Context Pack Contracts
# ==============================
"""
Deterministic context pack schemas for evidence-backed summaries.

This module consolidates:
- context_pack_schema.py (ContextPack, TablesSummary, DocumentsSummary, etc.)
- evidence_schema.py (EvidenceType, EvidenceSource, EvidenceItem)
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.contracts.run_schema import ArtifactRef


# ==============================
# Evidence Models (from evidence_schema)
# ==============================

EvidenceType = Literal["table", "doc", "text"]


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
]
