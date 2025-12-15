# ==============================
# Run Routes
# ==============================
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.orchestrator.engine import OrchestratorEngine
from gateway.api.deps import get_engine


router = APIRouter()


class RunRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


class ResumeRequest(BaseModel):
    approval_payload: Dict[str, Any] = Field(default_factory=dict)


@router.post("/run/{product}/{flow}")
def run_flow(
    product: str,
    flow: str,
    req: RunRequest,
    engine: OrchestratorEngine = Depends(get_engine),
):
    res = engine.run_flow(product=product, flow=flow, payload=req.payload)
    if not res.ok:
        raise HTTPException(status_code=400, detail=res.error.model_dump() if res.error else {"message": "error"})
    return res.model_dump()


@router.get("/run/{run_id}")
def get_run(
    run_id: str,
    engine: OrchestratorEngine = Depends(get_engine),
):
    res = engine.get_run(run_id=run_id)
    if not res.ok:
        raise HTTPException(status_code=404, detail=res.error.model_dump() if res.error else {"message": "not found"})
    return res.model_dump()


@router.post("/resume_run/{run_id}")
def resume_run(
    run_id: str,
    req: ResumeRequest,
    engine: OrchestratorEngine = Depends(get_engine),
):
    res = engine.resume_run(run_id=run_id, approval_payload=req.approval_payload)
    if not res.ok:
        raise HTTPException(status_code=400, detail=res.error.model_dump() if res.error else {"message": "error"})
    return res.model_dump()