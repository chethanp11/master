# ==============================
# CLI Entrypoint
# ==============================
"""
CLI for master/ to:
- list products and flows
- run flows with JSON payload
- get run details
- resume runs waiting for approval

Examples:
  python -m gateway.cli.main list-products
  python -m gateway.cli.main list-flows --product sandbox
  python -m gateway.cli.main run --product sandbox --flow hello_world --payload '{"text":"hi"}'
  python -m gateway.cli.main get-run --run-id run_...
  python -m gateway.cli.main resume --run-id run_... --approval '{"approved":true}'
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, safe_register_all
from core.orchestrator.engine import OrchestratorEngine


def _json_load(s: str) -> Dict[str, Any]:
    try:
        v = json.loads(s)
        if not isinstance(v, dict):
            raise ValueError("JSON payload must be an object")
        return v
    except Exception as e:
        raise SystemExit(f"Invalid JSON: {e}")


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def cmd_list_products(engine: OrchestratorEngine) -> int:
    products = engine.list_products()
    _print_json({"products": products})
    return 0


def cmd_list_flows(engine: OrchestratorEngine, product: str) -> int:
    flows = engine.list_flows(product)
    _print_json({"product": product, "flows": flows})
    return 0


def cmd_run(engine: OrchestratorEngine, product: str, flow: str, payload: Dict[str, Any]) -> int:
    res = engine.run_flow(product=product, flow=flow, payload=payload)
    _print_json(res.model_dump())
    return 0 if res.ok else 1


def cmd_get_run(engine: OrchestratorEngine, run_id: str) -> int:
    res = engine.get_run(run_id=run_id)
    _print_json(res.model_dump())
    return 0 if res.ok else 1


def cmd_resume(engine: OrchestratorEngine, run_id: str, approval: Dict[str, Any]) -> int:
    res = engine.resume_run(run_id=run_id, approval_payload=approval)
    _print_json(res.model_dump())
    return 0 if res.ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="master-cli")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-products")

    ap_flows = sub.add_parser("list-flows")
    ap_flows.add_argument("--product", required=True)

    ap_run = sub.add_parser("run")
    ap_run.add_argument("--product", required=True)
    ap_run.add_argument("--flow", required=True)
    ap_run.add_argument("--payload", required=True, help='JSON object string')

    ap_get = sub.add_parser("get-run")
    ap_get.add_argument("--run-id", required=True)

    ap_resume = sub.add_parser("resume")
    ap_resume.add_argument("--run-id", required=True)
    ap_resume.add_argument("--approval", required=True, help='JSON object string')

    args = ap.parse_args(argv)

    settings = load_settings()
    # Discover + register products (explicit import only via manifests)
    reg = discover_products(settings.products.products_dir)
    safe_register_all(reg, enabled_products=settings.products.enabled_products)

    engine = OrchestratorEngine.from_settings(settings)

    if args.cmd == "list-products":
        return cmd_list_products(engine)
    if args.cmd == "list-flows":
        return cmd_list_flows(engine, args.product)
    if args.cmd == "run":
        return cmd_run(engine, args.product, args.flow, _json_load(args.payload))
    if args.cmd == "get-run":
        return cmd_get_run(engine, args.run_id)
    if args.cmd == "resume":
        return cmd_resume(engine, args.run_id, _json_load(args.approval))
    raise SystemExit("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())