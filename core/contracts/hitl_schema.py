from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

HitlRequestType = Literal["APPROVAL", "INPUT"]
HitlResolutionStatus = Literal["ACCEPTED", "REJECTED", "PROVIDED", "ABORTED"]


class HitlInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    defaults: Dict[str, Any] = Field(default_factory=dict)
    prompt: Dict[str, Any] = Field(default_factory=dict)


class HitlRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    request_type: HitlRequestType
    run_id: str
    step_id: str
    product: str
    flow: str
    status: str = Field(default="PENDING")
    created_at: int
    schema: Optional[HitlInputSchema] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class HitlResolution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    request_type: HitlRequestType
    status: HitlResolutionStatus
    resolved_at: int
    decision: Optional[str] = None
    values: Dict[str, Any] = Field(default_factory=dict)
    comment: Optional[str] = None
    resolved_by: Optional[str] = None
