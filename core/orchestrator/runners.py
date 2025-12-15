# ==============================
# Orchestrator Runners
# ==============================
"""
Convenience runners around OrchestratorEngine.

These are thin helpers intended for CLI/API layers:
- run from product folder flow path
- start new run with flow snapshot embedded for resume
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from core.contracts.flow_schema import FlowDef
from core.orchestrator.engine import OrchestratorEngine
from core.orchestrator.flow_loader import FlowLoader

# ==============================
# Public API
# ==============================
def run_flow_from_path(
    *,
    engine: OrchestratorEngine,
    product: str,
    flow_path: str,
    initial_input: Optional[Dict[str, Any]] = None,
    trace_hook: Optional[Any] = None,
) -> Any:
    """
    Load flow from YAML/JSON path and run it.

    Note:
- To enable resume_run in v1, we embed the loaded flow snapshot into run.meta["flow"].
- engine.run_flow will return a RunRecord.
    """
    p = Path(flow_path)
    flow_def: FlowDef = FlowLoader.load_from_path(p)
    run = engine.run_flow(product=product, flow=flow_def, initial_input=initial_input, trace_hook=trace_hook)
    # embed flow snapshot for resume (v1)
    run.meta["flow"] = flow_def.to_dict()
    return run


def load_flow_from_product(
    *,
    product_dir: str,
    flow_name: str,
) -> FlowDef:
    """
    Load a flow from products/<product>/flows/<flow_name>.yaml or .json.
    """
    base = Path(product_dir) / "flows"
    yaml_path = base / f"{flow_name}.yaml"
    yml_path = base / f"{flow_name}.yml"
    json_path = base / f"{flow_name}.json"

    if yaml_path.exists():
        return FlowLoader.load_from_path(yaml_path)
    if yml_path.exists():
        return FlowLoader.load_from_path(yml_path)
    if json_path.exists():
        return FlowLoader.load_from_path(json_path)

    raise FileNotFoundError(f"Flow '{flow_name}' not found under: {base}")