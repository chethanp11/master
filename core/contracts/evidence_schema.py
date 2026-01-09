from __future__ import annotations

# ==============================
# Evidence Contracts
# ==============================
"""
Evidence items capture tool outputs with provenance for downstream reasoning.
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.contracts.run_schema import ArtifactRef


EvidenceType = Literal["table", "doc", "text"]


class EvidenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    uri: Optional[str] = None
    ref: Optional[str] = None


class EvidenceItem(BaseModel):
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
