from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, ConfigDict

from .card import InsightCard
from .modes import InsightMode
from .refs import FileRef


class UploadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    files: List[FileRef]
    mode: InsightMode
    prompt: Optional[str] = None


class RunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    session_id: str
    cards: List[InsightCard]
    trace_steps: List[str] = []


class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    format: Literal["pdf"]
