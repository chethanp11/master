# Visual insights tool: simple data reader
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import csv
import time
from pathlib import Path

from pydantic import BaseModel, Field

from core.contracts.tool_schema import ToolResult, ToolError, ToolErrorCode, ToolMeta
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class ReadParams(BaseModel):
    dataset: str = Field(..., description="Dataset to read")


class DataReaderTool(BaseTool):
    name = "data_reader"
    description = "Returns a stubbed summary for a dataset"
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            validated = ReadParams.model_validate(params or {})
            input_dir = (ctx.run.meta or {}).get("input_dir")
            if not input_dir:
                meta = ToolMeta(tool_name=self.name, backend="local")
                return ToolResult(
                    ok=False,
                    data=None,
                    error=ToolError(
                        code=ToolErrorCode.INVALID_INPUT,
                        message="Input directory not available for this run.",
                    ),
                    meta=meta,
                )
            dataset_path = Path(str(input_dir)) / validated.dataset
            columns: List[str] = []
            rows: List[List[Any]] = []
            row_count = 0
            file_exists = dataset_path.exists()
            if not file_exists:
                meta = ToolMeta(tool_name=self.name, backend="local")
                return ToolResult(
                    ok=False,
                    data=None,
                    error=ToolError(
                        code=ToolErrorCode.INVALID_INPUT,
                        message=f"Dataset not found at {dataset_path}",
                    ),
                    meta=meta,
                )
            columns, rows, row_count = _read_csv(dataset_path)
            if not columns and row_count == 0:
                summary = f"Insights for {validated.dataset}: file empty."
            else:
                summary = f"Insights for {validated.dataset}: read {row_count} rows."

            numeric_columns: List[str] = []
            for col_idx, col in enumerate(columns):
                values = []
                for row in rows:
                    if col_idx >= len(row):
                        continue
                    value = row[col_idx]
                    if value in (None, ""):
                        continue
                    values.append(value)
                if values and all(isinstance(v, (int, float)) or _is_number(v) for v in values):
                    numeric_columns.append(col)

            date_column = next((c for c in columns if "date" in c.lower() or "time" in c.lower()), None)
            x_field = date_column or (columns[0] if columns else None)
            y_field = next((c for c in numeric_columns if c != x_field), None)
            category_field = next((c for c in columns if c not in numeric_columns and c != date_column), None)

            has_time = date_column is not None
            has_category = category_field is not None
            has_x_numeric = x_field in numeric_columns if x_field else False
            has_y_numeric = y_field in numeric_columns if y_field else False

            series = []
            if date_column and y_field and columns:
                date_idx = columns.index(date_column)
                y_idx = columns.index(y_field)
                for row in rows:
                    if date_idx >= len(row) or y_idx >= len(row):
                        continue
                    value = row[y_idx]
                    if value in (None, ""):
                        continue
                    series.append({"ts": str(row[date_idx]), "value": float(value)})

            data = {"columns": columns, "rows": rows}
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(
                ok=True,
                data={
                    "summary": summary,
                    "row_count": row_count,
                    "columns": columns,
                    "rows": rows,
                    "data": data,
                    "series": series,
                    "file_exists": file_exists,
                    "input_path": str(dataset_path),
                    "x_field": x_field,
                    "y_field": y_field,
                    "category_field": category_field,
                    "has_time": has_time,
                    "has_category": has_category,
                    "has_x_numeric": has_x_numeric,
                    "has_y_numeric": has_y_numeric,
                },
                error=None,
                meta=meta,
            )
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            return ToolResult(ok=False, data=None, error=err, meta=ToolMeta(tool_name=self.name, backend="local"))


def build() -> DataReaderTool:
    return DataReaderTool()


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _normalize_cell(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip().strip('"').strip("'")
    if text in {"", "-", "—"}:
        return None
    numeric = text.replace(",", "")
    if _is_number(numeric):
        try:
            if "." in numeric:
                return float(numeric)
            return int(numeric)
        except (ValueError, TypeError):
            return numeric
    return text


def _normalize_row(row: List[Any], column_count: int) -> Optional[List[Any]]:
    if not row:
        return None
    normalized = [_normalize_cell(cell) for cell in row]
    if len(normalized) < column_count:
        normalized.extend([None] * (column_count - len(normalized)))
    elif len(normalized) > column_count and column_count > 0:
        overflow = normalized[column_count - 1 :]
        head = normalized[: column_count - 1]
        overflow_text = ",".join("" if v is None else str(v) for v in overflow)
        head.append(_normalize_cell(overflow_text))
        normalized = head
    return normalized


def _read_csv(path: Path) -> Tuple[List[str], List[List[Any]], int]:
    columns: List[str] = []
    rows: List[List[Any]] = []
    row_count = 0
    attempts = 3
    for attempt in range(attempts):
        if not path.exists():
            time.sleep(0.2)
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, skipinitialspace=True)
            try:
                columns = [str(c).strip() for c in next(reader)]
                if columns and columns[0].startswith("\ufeff"):
                    columns[0] = columns[0].lstrip("\ufeff")
            except StopIteration:
                columns = []
            for raw_row in reader:
                if not columns:
                    continue
                row = _normalize_row(raw_row, len(columns))
                if row is None:
                    continue
                row_count += 1
                if len(rows) < 50:
                    rows.append(row)
        if columns:
            break
        time.sleep(0.2)
    return columns, rows, row_count
