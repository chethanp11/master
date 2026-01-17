from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

import yaml

_DEFAULT_THRESHOLDS = {"high": 0.7, "medium": 0.4}


def _coerce_thresholds(raw: Dict[str, object]) -> Dict[str, float]:
    thresholds: Dict[str, float] = dict(_DEFAULT_THRESHOLDS)
    for key in ("high", "medium"):
        value = raw.get(key)
        if isinstance(value, (int, float)):
            thresholds[key] = float(value)
    return thresholds


@lru_cache(maxsize=1)
def load_confidence_thresholds() -> Dict[str, float]:
    path = Path(__file__).resolve().parent / "product.yaml"
    if not path.exists():
        return dict(_DEFAULT_THRESHOLDS)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return dict(_DEFAULT_THRESHOLDS)
    meta = data.get("metadata") if isinstance(data, dict) else None
    confidence = meta.get("confidence") if isinstance(meta, dict) else None
    raw = confidence.get("thresholds") if isinstance(confidence, dict) else {}
    if not isinstance(raw, dict):
        return dict(_DEFAULT_THRESHOLDS)
    return _coerce_thresholds(raw)
