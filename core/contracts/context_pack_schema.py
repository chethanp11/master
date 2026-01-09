from __future__ import annotations

# ==============================
# Context Pack Contracts
# ==============================
"""
Deterministic context pack schemas for evidence-backed summaries.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class ContextPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    evidence_index: List[EvidenceIndexEntry]
    tables_summary: TablesSummary
    documents_summary: DocumentsSummary
    assumptions: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    pack_hash: Optional[str] = None


class ContextPackConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_row_limit: int = 5
    excerpt_char_limit: int = 800
    artifacts: Dict[str, Any] = Field(default_factory=dict)
