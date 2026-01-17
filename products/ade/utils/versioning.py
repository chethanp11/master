from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import __version__ as pydantic_version

from products.ade.tools.evidence_utils import inputs_hash


@lru_cache(maxsize=1)
def _manifest_version() -> str:
    path = Path(__file__).resolve().parents[1] / "manifest.yaml"
    if not path.exists():
        return "unknown"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return "unknown"
    return str(data.get("version") or "unknown")


@lru_cache(maxsize=16)
def _flow_version(flow_id: str) -> str:
    path = Path(__file__).resolve().parents[1] / "flows" / f"{flow_id}.yaml"
    if not path.exists():
        return "unknown"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return "unknown"
    return str(data.get("version") or "unknown")


def _dataset_hash(dataset_id: str, columns: List[str], rows: List[List[Any]]) -> str:
    payload = {
        "dataset_id": dataset_id,
        "columns": columns,
        "rows": rows,
    }
    return inputs_hash(payload)


def build_version_metadata(
    *,
    flow_id: str,
    dataset_id: str,
    columns: List[str],
    rows: List[List[Any]],
    input_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "product": "ade",
        "product_version": _manifest_version(),
        "flow_id": flow_id,
        "flow_version": _flow_version(flow_id),
        "schema_version": "1.0",
        "dataset_hash": _dataset_hash(dataset_id, columns, rows),
        "input_hash": inputs_hash(input_payload),
        "dependency_versions": {
            "python": sys.version.split()[0],
            "pydantic": pydantic_version,
        },
    }
