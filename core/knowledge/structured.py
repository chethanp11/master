# ==============================
# Structured Data Access (v1)
# ==============================
"""
Structured access is intentionally minimal in v1.

Supported (v1):
- Load CSV into Pandas DataFrame (optional dependency).
- Basic filtering and column selection.

Not supported (v1):
- Live SQL connectors (planned later).
- Text-to-SQL (planned later).

Keep this module side-effect free (no persistence).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union


@dataclass(frozen=True)
class StructuredQuery:
    path: str
    where: Dict[str, Any] = None  # exact match filters
    select: Optional[List[str]] = None
    limit: int = 100


class StructuredAccessor:
    def __init__(self) -> None:
        pass

    def query_csv(self, q: StructuredQuery) -> List[Dict[str, Any]]:
        try:
            import pandas as pd  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "pandas is required for structured CSV access in v1. Install pandas to use this module."
            ) from e

        df = pd.read_csv(q.path)
        where = q.where or {}
        for col, val in where.items():
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in CSV: {q.path}")
            df = df[df[col] == val]

        if q.select:
            missing = [c for c in q.select if c not in df.columns]
            if missing:
                raise ValueError(f"Select columns not found: {missing}")
            df = df[q.select]

        if q.limit and q.limit > 0:
            df = df.head(int(q.limit))

        # Convert to list[dict]
        return df.to_dict(orient="records")