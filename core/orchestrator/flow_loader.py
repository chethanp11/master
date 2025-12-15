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
from typing import Any, Dict, Union

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
    - load_from_path(path) -> FlowDef
    - load_from_obj(obj) -> FlowDef
    """

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
            return FlowDef.model_validate(obj)
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