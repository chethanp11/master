# ==============================
# Flow Loader
# ==============================
"""
Load and validate FlowDef from YAML or JSON.

Requirements:
- Supports YAML (.yaml/.yml) and JSON (.json)
- Returns core.contracts.flow_schema.FlowDef
- Does NOT execute anything; pure parsing + validation
- No persistence and no environment reads

Intended usage:
- Orchestrator calls FlowLoader.load_from_path(...) to get a validated FlowDef
- Gateway/UI may call this to list flows and validate configs
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import ValidationError

from core.contracts.flow_schema import FlowDef

# ==============================
# Errors
# ==============================
class FlowLoadError(RuntimeError):
    """Raised when a flow cannot be loaded or validated."""


# ==============================
# Loader
# ==============================
class FlowLoader:
    """
    Flow loader for YAML/JSON flow definitions.

    Public methods:
    - load(product, flow) -> FlowDef (from products/<product>/flows/<flow>.yaml)
    - load_from_path(path) -> FlowDef
    - load_from_obj(obj) -> FlowDef
    """

    def __init__(self, *, products_root: Union[str, Path]) -> None:
        self.products_root = Path(products_root)

    def load(self, *, product: str, flow: str) -> FlowDef:
        path = self.products_root / product / "flows" / f"{flow}.yaml"
        return self.load_from_path(path)

    # ==============================
    # Public API
    # ==============================
    @staticmethod
    def load_from_path(path: Union[str, Path]) -> FlowDef:
        p = Path(path)
        if not p.exists():
            raise FlowLoadError(f"Flow file not found: {p}")

        suffix = p.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            data = FlowLoader._read_yaml(p)
        elif suffix == ".json":
            data = FlowLoader._read_json(p)
        else:
            raise FlowLoadError(f"Unsupported flow format '{suffix}'. Use .yaml/.yml or .json")

        return FlowLoader.load_from_obj(data)

    @staticmethod
    def load_from_obj(obj: Dict[str, Any]) -> FlowDef:
        """
        Validate a raw dict into FlowDef.

        Raises FlowLoadError with readable validation messages.
        """
        try:
            normalized = FlowLoader._normalize(obj)
            return FlowDef.model_validate(normalized)
        except ValidationError as e:
            raise FlowLoadError(f"Flow validation error: {e}") from e

    # ==============================
    # File Readers
    # ==============================
    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise FlowLoadError("Top-level JSON must be an object/dict.")
            return data
        except json.JSONDecodeError as e:
            raise FlowLoadError(f"Invalid JSON in {path}: {e}") from e

    @staticmethod
    def _read_yaml(path: Path) -> Dict[str, Any]:
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise FlowLoadError(
                "PyYAML is required to load .yaml flows. Add 'pyyaml' to dependencies."
            ) from e

        try:
            raw = path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            if not isinstance(data, dict):
                raise FlowLoadError("Top-level YAML must be a mapping/dict.")
            return data
        except Exception as e:
            raise FlowLoadError(f"Invalid YAML in {path}: {e}") from e

    # ==============================
    # Normalization helpers
    # ==============================
    @staticmethod
    def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(data)
        flow_name = normalized.pop("name", None)
        flow_id = normalized.get("id") or flow_name
        if not flow_id:
            raise FlowLoadError("Flow missing required 'id'.")
        normalized["id"] = flow_id

        steps = normalized.get("steps")
        if not isinstance(steps, list):
            raise FlowLoadError("Flow missing 'steps' list.")
        normalized["steps"] = FlowLoader._normalize_steps(steps)

        if flow_name:
            metadata = dict(normalized.get("metadata") or {})
            metadata.setdefault("display_name", flow_name)
            normalized["metadata"] = metadata

        return normalized

    @staticmethod
    def _normalize_steps(steps: List[Any]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for idx, raw in enumerate(steps):
            if not isinstance(raw, dict):
                raise FlowLoadError(f"Step {idx} is not a mapping/dict.")
            step = dict(raw)
            step_name = step.get("name")
            step_id = step.get("id") or step_name or f"step_{idx}"
            step["id"] = step_id
            normalized.append(step)
        return normalized
