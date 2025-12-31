# ==============================
# CLI Entrypoint
# ==============================
"""
CLI for master/ platform.

Supported commands:
  master list-products
  master list-flows --product hello_world
  master run --product hello_world --flow hello_world --payload '{"keyword":"hi"}'
  master run --product hello_world --flow hello_world --payload-file payload.json
  master status --run-id run_123
  master approvals
  master resume --run-id run_123 --approve --payload '{"approved": true}'
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.memory.router import MemoryRouter
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import (
    ProductCatalog,
    discover_products,
    register_enabled_products,
)


def _json_load(text: str) -> Dict[str, Any]:
    try:
        value = json.loads(text)
    except Exception as exc:  # pragma: no cover - defensive
        raise SystemExit(f"Invalid JSON payload: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("JSON payload must be an object.")
    return value


def _load_payload_arg(payload: Optional[str], payload_file: Optional[str]) -> Dict[str, Any]:
    if payload and payload_file:
        raise SystemExit("Provide only one of --payload or --payload-file.")
    if payload_file:
        text = Path(payload_file).read_text(encoding="utf-8")
        return _json_load(text)
    if payload:
        return _json_load(payload)
    return {}


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def _catalog_product(catalog: ProductCatalog, product: str) -> Tuple[Any, List[str]]:
    meta = catalog.products.get(product)
    if meta is None:
        raise SystemExit(f"Unknown product '{product}'. Run `list-products` to inspect enabled packs.")
    if not meta.enabled:
        raise SystemExit(f"Product '{product}' is not enabled. Update configs/products.yaml to enable it.")
    errors = [err for err in catalog.errors if err.product == product]
    if errors:
        raise SystemExit(f"Product '{product}' is unavailable: {errors[0].message} ({errors[0].path})")
    return meta, catalog.flows.get(product, [])


def cmd_list_products(catalog: ProductCatalog) -> int:
    products = {
        name: {
            "display_name": meta.display_name,
            "description": meta.description,
            "default_flow": meta.default_flow,
            "enabled": meta.enabled,
            "flows": catalog.flows.get(name, []),
            "errors": [
                {"path": err.path, "message": err.message}
                for err in catalog.errors
                if err.product == name
            ],
        }
        for name, meta in sorted(catalog.products.items())
    }
    _print_json({"products": products})
    return 0


def cmd_list_flows(catalog: ProductCatalog, product: str) -> int:
    _, flows = _catalog_product(catalog, product)
    _print_json({"product": product, "flows": flows})
    return 0


def cmd_run(
    engine: OrchestratorEngine,
    catalog: ProductCatalog,
    *,
    product: str,
    flow: str,
    payload: Dict[str, Any],
    requested_by: Optional[str],
) -> int:
    _, flows = _catalog_product(catalog, product)
    if flow not in flows:
        raise SystemExit(f"Unknown flow '{flow}' for product '{product}'. Available: {', '.join(flows)}")
    res = engine.run_flow(product=product, flow=flow, payload=payload, requested_by=requested_by)
    _print_json(res.model_dump())
    return 0 if res.ok else 1


def cmd_status(engine: OrchestratorEngine, *, run_id: str) -> int:
    res = engine.get_run(run_id=run_id)
    _print_json(res.model_dump())
    return 0 if res.ok else 1


def cmd_resume(
    engine: OrchestratorEngine,
    *,
    run_id: str,
    decision: str,
    payload: Dict[str, Any],
    resolved_by: Optional[str],
    comment: Optional[str],
) -> int:
    res = engine.resume_run(
        run_id=run_id,
        decision=decision,
        approval_payload=payload,
        resolved_by=resolved_by,
        comment=comment,
    )
    _print_json(res.model_dump())
    return 0 if res.ok else 1


def cmd_approvals(memory: MemoryRouter) -> int:
    approvals = [
        approval.model_dump()
        for approval in memory.list_pending_approvals(limit=100, offset=0)
    ]
    _print_json({"approvals": approvals})
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="master")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-products")

    ap_flows = sub.add_parser("list-flows")
    ap_flows.add_argument("--product", required=True)

    ap_run = sub.add_parser("run")
    ap_run.add_argument("--product", required=True)
    ap_run.add_argument("--flow", required=True)
    ap_run.add_argument("--payload", help="JSON object string", default=None)
    ap_run.add_argument("--payload-file", help="Path to JSON file with payload", default=None)
    ap_run.add_argument("--requested-by", help="Optional requester identifier", default=None)

    ap_status = sub.add_parser("status")
    ap_status.add_argument("--run-id", required=True)

    ap_get = sub.add_parser("get-run")
    ap_get.add_argument("--run-id", required=True)

    ap_approvals = sub.add_parser("approvals")

    ap_resume = sub.add_parser("resume")
    ap_resume.add_argument("--run-id", required=True)
    decision_group = ap_resume.add_mutually_exclusive_group()
    decision_group.add_argument("--approve", action="store_true", help="Approve the pending run")
    decision_group.add_argument("--reject", action="store_true", help="Reject the pending run")
    ap_resume.add_argument("--payload", help="JSON object string", default=None)
    ap_resume.add_argument("--payload-file", help="Path to JSON file with approval payload", default=None)
    ap_resume.add_argument("--comment", help="Optional approval comment", default=None)
    ap_resume.add_argument("--resolved-by", help="Optional reviewer identifier", default=None)

    args = ap.parse_args(argv)

    settings = load_settings()
    catalog = discover_products(settings)
    AgentRegistry.clear()
    ToolRegistry.clear()
    register_enabled_products(catalog, settings=settings)
    engine = OrchestratorEngine.from_settings(settings)
    memory = engine.memory

    if args.cmd == "list-products":
        return cmd_list_products(catalog)
    if args.cmd == "list-flows":
        return cmd_list_flows(catalog, args.product)
    if args.cmd == "run":
        payload = _load_payload_arg(args.payload, args.payload_file)
        return cmd_run(
            engine,
            catalog,
            product=args.product,
            flow=args.flow,
            payload=payload,
            requested_by=args.requested_by,
        )
    if args.cmd in {"status", "get-run"}:
        return cmd_status(engine, run_id=args.run_id)
    if args.cmd == "approvals":
        return cmd_approvals(memory)
    if args.cmd == "resume":
        decision = "REJECTED" if args.reject else "APPROVED"
        payload = _load_payload_arg(args.payload, args.payload_file)
        return cmd_resume(
            engine,
            run_id=args.run_id,
            decision=decision,
            payload=payload,
            resolved_by=args.resolved_by,
            comment=args.comment,
        )

    raise SystemExit("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
