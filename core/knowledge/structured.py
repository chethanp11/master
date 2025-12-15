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
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class StructuredQuery:
    path: str
    where: Optional[Dict[str, Any]] = None  # exact match filters
    select: Optional[List[str]] = None
    limit: int = 100


def _load_with_pandas(path: str) -> List[Dict[str, Any]]:
    import pandas as pd  # type: ignore

    df = pd.read_csv(path)
    return df.to_dict(orient="records")


def _load_with_csv_module(path: str) -> List[Dict[str, Any]]:
    import csv

    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader]


def load_table(path: str) -> List[Dict[str, Any]]:
    """
    Load a CSV file into a list of dict rows.

    Prefers pandas for speed, but falls back to the csv module if unavailable.
    """
    try:
        return _load_with_pandas(path)
    except Exception:
        return _load_with_csv_module(path)


def filter_rows(rows: List[Dict[str, Any]], filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not filters:
        return rows
    filtered: List[Dict[str, Any]] = []
    for row in rows:
        ok = True
        for key, expected in filters.items():
            if key not in row or row[key] != expected:
                ok = False
                break
        if ok:
            filtered.append(row)
    return filtered


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "row_count": len(rows),
        "columns": {},
    }
    if not rows:
        return summary
    columns = rows[0].keys()
    for col in columns:
        values = [row.get(col) for row in rows]
        non_null = [v for v in values if v not in (None, "")]
        summary["columns"][col] = {
            "non_null": len(non_null),
            "unique": len(set(non_null)),
        }
    return summary


class StructuredAccessor:
    def query_csv(self, q: StructuredQuery) -> List[Dict[str, Any]]:
        rows = load_table(q.path)
        rows = filter_rows(rows, q.where)

        if q.select:
            missing = [col for col in q.select if rows and col not in rows[0]]
            if missing:
                raise ValueError(f"Select columns not found: {missing}")
            rows = [{col: row.get(col) for col in q.select} for row in rows]

        if q.limit and q.limit > 0:
            rows = rows[: int(q.limit)]
        return rows

    def summarize(self, path: str) -> Dict[str, Any]:
        rows = load_table(path)
        return summarize_rows(rows)
