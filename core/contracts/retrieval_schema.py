from __future__ import annotations

# ==============================
# Retrieval Contracts
# ==============================
"""
Contracts for approved retrieval tool.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.context_pack_schema import EvidenceItem
from core.contracts.run_schema import ArtifactRef


class TimeRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: Optional[datetime] = None
    end: Optional[datetime] = None


class RetrievalQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    sources_requested: List[str] = Field(default_factory=list)
    product: Optional[str] = None
    flow: Optional[str] = None
    time_range: Optional[TimeRange] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    sensitivity: Optional[str] = None


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: str
    source_type: Literal["run_record", "trace_event", "knowledge"]
    run_id: Optional[str] = None
    step_id: Optional[str] = None
    artifact_ref: Optional[ArtifactRef] = None
    timestamp: Optional[datetime] = None
    locator: Dict[str, Any] = Field(default_factory=dict)
    snippet_summary: str


class RetrievalResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence: List[EvidenceItem]
    citations: List[Citation]
