"""Context Pack schema for ADE.

TS-SCHEMA-CTX-004: Context Pack includes evidence items with dataset_id/columns.
TS-SCHEMA-CTX-005: Reasoning references Context Pack as sole grounding source.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ContextPackEvidenceItem(BaseModel):
    """Evidence item reference in context pack.

    TS-SCHEMA-CTX-004: Evidence items reference dataset_id and columns.
    """

    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    columns: List[str] = Field(default_factory=list)
    source: str = ""
    description: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ContextPack(BaseModel):
    """Context pack for grounding reasoning.

    TS-SCHEMA-CTX-005: Reasoning outputs cite context pack artifacts.
    """

    model_config = ConfigDict(extra="forbid")

    dataset_profile: Dict[str, Any]
    coverage: Dict[str, Any]
    missingness: Dict[str, Any]
    data_quality_flags: List[str] = Field(default_factory=list)
    metric_availability: List[str] = Field(default_factory=list)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
    # TS-SCHEMA-CTX-004: Evidence items with dataset_id/columns
    evidence_items: List[ContextPackEvidenceItem] = Field(default_factory=list)
    # Context pack ID for traceability
    context_pack_id: Optional[str] = None
