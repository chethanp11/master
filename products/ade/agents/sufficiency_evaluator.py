
from __future__ import annotations

from math import sqrt
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.agents.base import BaseAgent, agent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult

MIN_ROWS = 30
MIN_TIME_POINTS = 12
MAX_CV = 0.6


class SufficiencyOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str = "critique"
    confidence_level: str
    downgrade_reasons: List[str]
    sufficiency_state: Dict[str, List[str]] = Field(default_factory=dict)


def _extract_series_values(series: List[Dict[str, Any]]) -> List[float]:
    values: List[float] = []
    for item in series:
        raw = item.get("value") if isinstance(item, dict) else None
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return values


def _variance_stable(values: List[float]) -> bool:
    if len(values) < 2:
        return False
    mean = sum(values) / len(values)
    if mean == 0:
        return False
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = sqrt(variance)
    cv = std / abs(mean)
    return cv <= MAX_CV


def evaluate_sufficiency(
    *,
    row_count: int,
    has_time: bool,
    series: List[Dict[str, Any]],
) -> Dict[str, Any]:
    downgrade_reasons: List[str] = []
    known: List[str] = []
    unknown: List[str] = []
    blocked: List[str] = []
    critical = False

    if row_count < MIN_ROWS:
        downgrade_reasons.append("insufficient_rows")
        if row_count < max(1, MIN_ROWS // 2):
            critical = True
            blocked.append("row_count")
        else:
            unknown.append("row_count")
    else:
        known.append("row_count")

    if not has_time or len(series) < MIN_TIME_POINTS:
        downgrade_reasons.append("insufficient_time_window")
        unknown.append("time_window")
    else:
        known.append("time_window")

    values = _extract_series_values(series)
    if not _variance_stable(values):
        downgrade_reasons.append("unstable_variance")
        unknown.append("variance_stability")
    else:
        known.append("variance_stability")

    if not downgrade_reasons:
        confidence_level = "high"
    elif critical or len(downgrade_reasons) >= 2:
        confidence_level = "low"
    else:
        confidence_level = "medium"

    return SufficiencyOutput(
        confidence_level=confidence_level,
        downgrade_reasons=downgrade_reasons,
        sufficiency_state={
            "known": known,
            "unknown": unknown,
            "blocked": blocked,
        },
    ).model_dump(mode="json")


@agent(
    name="sufficiency_evaluator",
    purpose="Evaluates data sufficiency for analysis tasks",
    capabilities=["data_quality", "sufficiency_analysis", "confidence_scoring"],
    cost_hint="LOW",
)
class SufficiencyEvaluatorAgent(BaseAgent):
    name = "sufficiency_evaluator"
    description = "Evaluates data sufficiency for ADE decisions without model calls."

    def run(self, step_context: Any) -> AgentResult:
        try:
            artifacts = step_context.run.artifacts or {}
            tool_output = artifacts.get("tool.data_reader.output", {}) or {}
            row_count = int(tool_output.get("row_count") or 0)
            has_time = bool(tool_output.get("has_time"))
            series = tool_output.get("series") or []

            payload = evaluate_sufficiency(
                row_count=row_count,
                has_time=has_time,
                series=series,
            )
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data=payload, error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> SufficiencyEvaluatorAgent:
    return SufficiencyEvaluatorAgent()
