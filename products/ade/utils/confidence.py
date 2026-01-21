"""Confidence configuration loading for ADE.

TS-AGENT-CONF-003: Confidence thresholds configurable via YAML.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field

_DEFAULT_THRESHOLDS = {"high": 0.7, "medium": 0.4}

# Default sufficiency thresholds
_DEFAULT_SUFFICIENCY = {
    "min_rows": 30,
    "critical_rows": 15,
    "min_time_points": 12,
    "max_cv": 0.6,
    "min_non_null_rate": 0.7,
}


class SufficiencyThresholds(BaseModel):
    """Sufficiency thresholds for data quality assessment."""

    min_rows: int = 30
    critical_rows: int = 15
    min_time_points: int = 12
    max_cv: float = 0.6
    min_non_null_rate: float = 0.7


class ConfidenceConfig(BaseModel):
    """Confidence configuration schema per TS-AGENT-CONF-003."""

    low_threshold: float = 0.4
    high_threshold: float = 0.7
    sufficiency_thresholds: SufficiencyThresholds = Field(default_factory=SufficiencyThresholds)


def _coerce_thresholds(raw: Dict[str, object]) -> Dict[str, float]:
    thresholds: Dict[str, float] = dict(_DEFAULT_THRESHOLDS)
    for key in ("high", "medium"):
        value = raw.get(key)
        if isinstance(value, (int, float)):
            thresholds[key] = float(value)
    return thresholds


def _get_confidence_yaml_path() -> Path:
    """Get path to config/confidence.yaml."""
    return Path(__file__).resolve().parent / "confidence.yaml"


@lru_cache(maxsize=1)
def load_confidence_config() -> ConfidenceConfig:
    """Load confidence configuration from YAML.

    TS-AGENT-CONF-003: Returns ConfidenceConfig with thresholds from
    products/ade/config/confidence.yaml.

    Returns:
        ConfidenceConfig with loaded or default values.
    """
    path = _get_confidence_yaml_path()
    if not path.exists():
        return ConfidenceConfig()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ConfidenceConfig()

    if not isinstance(data, dict):
        return ConfidenceConfig()

    # Parse sufficiency thresholds
    suff_data = data.get("sufficiency_thresholds", {})
    sufficiency = SufficiencyThresholds(
        min_rows=suff_data.get("min_rows", 30),
        critical_rows=suff_data.get("critical_rows", 15),
        min_time_points=suff_data.get("min_time_points", 12),
        max_cv=suff_data.get("max_cv", 0.6),
        min_non_null_rate=suff_data.get("min_non_null_rate", 0.7),
    )

    return ConfidenceConfig(
        low_threshold=data.get("low_threshold", 0.4),
        high_threshold=data.get("high_threshold", 0.7),
        sufficiency_thresholds=sufficiency,
    )


@lru_cache(maxsize=1)
def load_confidence_thresholds() -> Dict[str, float]:
    """Load confidence thresholds from product.yaml (legacy function)."""
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
