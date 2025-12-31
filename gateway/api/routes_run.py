# ==============================
# Run & Product Routes
# ==============================
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.contracts.run_schema import RunOperationResult
from core.orchestrator.engine import OrchestratorEngine
from core.utils.product_loader import ProductCatalog, ProductLoadError, ProductMeta
from gateway.api.deps import get_engine, get_product_catalog, get_memory_router, get_settings


router = APIRouter()


class RunRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


class ResumeRequest(BaseModel):
    decision: str = Field(default="APPROVED", description="Decision applied to the pending approval.")
    resolved_by: Optional[str] = Field(default=None, description="Optional reviewer identifier.")
    comment: Optional[str] = Field(default=None, description="Optional reviewer comment.")
    approval_payload: Dict[str, Any] = Field(default_factory=dict)


def _ok(data: Dict[str, Any], *, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"ok": True, "data": data, "error": None, "meta": meta or {}}


def _error(
    *,
    http_status: int,
    code: str,
    message: str,
    details: Dict[str, Any] | None = None,
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "ok": False,
        "data": None,
        "error": {"code": code, "message": message, "details": details or {}},
        "meta": meta or {},
    }
    raise HTTPException(status_code=http_status, detail=payload)


def _serialize_error(err: ProductLoadError) -> Dict[str, Any]:
    return {"product": err.product, "path": err.path, "message": err.message}


def _serialize_product(meta: ProductMeta, errors: List[ProductLoadError]) -> Dict[str, Any]:
    per_product_errors = [_serialize_error(err) for err in errors if err.product == meta.name]
    return {
        "name": meta.name,
        "display_name": meta.display_name,
        "description": meta.description,
        "version": meta.version,
        "default_flow": meta.default_flow,
        "expose_api": meta.expose_api,
        "ui_enabled": meta.ui_enabled,
        "flows": meta.flows,
        "ui": meta.ui.model_dump(),
        "enabled": meta.enabled,
        "errors": per_product_errors,
    }


def _product_errors(catalog: ProductCatalog, product: str) -> List[Dict[str, Any]]:
    return [_serialize_error(err) for err in catalog.errors if err.product == product]


def _ensure_product_ready(catalog: ProductCatalog, product: str) -> Tuple[ProductMeta, List[str]]:
    meta = catalog.products.get(product)
    if meta is None:
        _error(
            http_status=status.HTTP_404_NOT_FOUND,
            code="product_not_found",
            message=f"Unknown product '{product}'.",
        )
    if not meta.enabled:
        _error(
            http_status=status.HTTP_404_NOT_FOUND,
            code="product_disabled",
            message=f"Product '{product}' is not enabled.",
        )
    errs = _product_errors(catalog, product)
    if errs:
        _error(
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="product_unavailable",
            message=f"Product '{product}' failed to load.",
            details={"errors": errs},
        )
    flows = catalog.flows.get(product, [])
    return meta, flows


def _ensure_flow(meta: ProductMeta, flows: List[str], flow: str) -> None:
    if flow not in flows:
        _error(
            http_status=status.HTTP_404_NOT_FOUND,
            code="flow_not_found",
            message=f"Unknown flow '{flow}' for product '{meta.name}'.",
            details={"available_flows": flows},
        )


def _respond(result: RunOperationResult, *, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if result.ok:
        return _ok(result.data or {}, meta=meta)
    error = result.error
    if error is None:
        _error(
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="unknown_error",
            message="Unknown failure.",
            meta=meta,
        )
    http_status = status.HTTP_404_NOT_FOUND if error.code == "not_found" else status.HTTP_400_BAD_REQUEST
    _error(
        http_status=http_status,
        code=error.code,
        message=error.message,
        details=error.details,
        meta=meta,
    )


@router.get("/products")
def list_products(catalog: ProductCatalog = Depends(get_product_catalog)) -> Dict[str, Any]:
    products = [
        _serialize_product(meta, catalog.errors) for meta in sorted(catalog.products.values(), key=lambda m: m.name)
    ]
    orphan_errors = [_serialize_error(err) for err in catalog.errors if err.product not in catalog.products]
    return _ok({"products": products, "errors": orphan_errors})


@router.get("/products/{product}/flows")
def list_flows(
    product: str,
    catalog: ProductCatalog = Depends(get_product_catalog),
) -> Dict[str, Any]:
    meta, flows = _ensure_product_ready(catalog, product)
    return _ok({"product": meta.name, "flows": flows, "default_flow": meta.default_flow})

@router.get("/runs")
def list_runs(
    limit: int = 50,
    offset: int = 0,
    memory=Depends(get_memory_router),
) -> Dict[str, Any]:
    runs = [r.model_dump() for r in memory.list_runs(limit=limit, offset=offset)]
    return _ok({"runs": runs})


@router.get("/approvals")
def list_approvals(
    limit: int = 50,
    offset: int = 0,
    memory=Depends(get_memory_router),
) -> Dict[str, Any]:
    approvals = [a.model_dump() for a in memory.list_pending_approvals(limit=limit, offset=offset)]
    return _ok({"approvals": approvals})


@router.get("/output/{product}/{run_id}/{filename}")
def get_output_file(
    product: str,
    run_id: str,
    filename: str,
    settings=Depends(get_settings),
) -> FileResponse:
    base = settings.repo_root_path() / "observability" / product / run_id / "output"
    target = (base / filename).resolve()
    if not str(target).startswith(str(base.resolve())):
        _error(http_status=status.HTTP_400_BAD_REQUEST, code="invalid_path", message="Invalid output path.")
    if not target.exists():
        _error(http_status=status.HTTP_404_NOT_FOUND, code="not_found", message="Output file not found.")
    return FileResponse(target)

@router.post("/run/{product}/{flow}")
def run_flow(
    product: str,
    flow: str,
    req: RunRequest,
    engine: OrchestratorEngine = Depends(get_engine),
    catalog: ProductCatalog = Depends(get_product_catalog),
) -> Dict[str, Any]:
    meta, flows = _ensure_product_ready(catalog, product)
    _ensure_flow(meta, flows, flow)
    res = engine.run_flow(product=product, flow=flow, payload=req.payload)
    return _respond(res, meta={"product": product, "flow": flow})


@router.get("/run/{run_id}")
def get_run(
    run_id: str,
    engine: OrchestratorEngine = Depends(get_engine),
) -> Dict[str, Any]:
    res = engine.get_run(run_id=run_id)
    return _respond(res, meta={"run_id": run_id})


@router.post("/resume_run/{run_id}")
def resume_run(
    run_id: str,
    req: ResumeRequest,
    engine: OrchestratorEngine = Depends(get_engine),
) -> Dict[str, Any]:
    res = engine.resume_run(
        run_id=run_id,
        approval_payload=req.approval_payload,
        decision=req.decision,
        resolved_by=req.resolved_by,
        comment=req.comment,
    )
    return _respond(res, meta={"run_id": run_id, "decision": req.decision})
