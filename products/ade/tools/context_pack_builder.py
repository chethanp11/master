from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool, tool
from products.ade.schemas.context_pack import ContextPack


class ContextPackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    columns: List[str] = Field(default_factory=list)
    rows: List[List[Any]] = Field(default_factory=list)


class ContextPackOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context_pack: ContextPack


def _column_missingness(columns: List[str], rows: List[List[Any]]) -> Dict[str, Dict[str, Any]]:
    missingness: Dict[str, Dict[str, Any]] = {}
    for idx, column in enumerate(columns):
        missing = 0
        for row in rows:
            if idx >= len(row) or row[idx] in (None, ""):
                missing += 1
        total = len(rows)
        missing_pct = float(missing) / total if total else 0.0
        missingness[column] = {"missing": missing, "total": total, "missing_pct": missing_pct}
    return missingness


def _numeric_columns(columns: List[str], rows: List[List[Any]]) -> List[str]:
    numeric: List[str] = []
    for idx, column in enumerate(columns):
        values = []
        for row in rows:
            if idx >= len(row):
                continue
            value = row[idx]
            if value in (None, ""):
                continue
            values.append(value)
        if values and all(_is_number(value) for value in values):
            numeric.append(column)
    return numeric


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def build_context_pack(payload: ContextPackInput) -> ContextPackOutput:
    row_count = len(payload.rows)
    column_count = len(payload.columns)
    missingness = _column_missingness(payload.columns, payload.rows)
    numeric_columns = _numeric_columns(payload.columns, payload.rows)

    data_quality_flags: List[str] = []
    if row_count < 30:
        data_quality_flags.append("low_row_count")
    if any(item["missing_pct"] > 0.3 for item in missingness.values()):
        data_quality_flags.append("sparse_columns")
    if any(item["missing"] > 0 for item in missingness.values()):
        data_quality_flags.append("missing_values_present")

    dataset_profile = {
        "dataset_id": payload.dataset_id,
        "row_count": row_count,
        "column_count": column_count,
        "columns": payload.columns,
        "numeric_columns": numeric_columns,
    }
    coverage = {
        "row_count": row_count,
        "column_count": column_count,
        "non_null_rates": {k: 1.0 - v["missing_pct"] for k, v in missingness.items()},
    }
    evidence_refs = [
        {
            "dataset_id": payload.dataset_id,
            "columns": payload.columns,
            "row_count": row_count,
        }
    ]

    pack = ContextPack(
        dataset_profile=dataset_profile,
        coverage=coverage,
        missingness=missingness,
        data_quality_flags=data_quality_flags,
        metric_availability=numeric_columns,
        evidence_refs=evidence_refs,
    )
    return ContextPackOutput(context_pack=pack)


@tool(
    name="context_pack_builder",
    description="Builds a dataset context pack for ADE reasoning.",
    capabilities=["context_pack", "dataset_profile", "coverage"],
    read_only=True,
    side_effect=False,
    sensitivity_class="LOW",
    cost_hint="LOW",
)
class ContextPackBuilderTool(BaseTool):
    name = "context_pack_builder"
    description = "Builds a dataset context pack for ADE reasoning."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: Any) -> ToolResult:
        try:
            payload = ContextPackInput.model_validate(params or {})
            output = build_context_pack(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> ContextPackBuilderTool:
    return ContextPackBuilderTool()
