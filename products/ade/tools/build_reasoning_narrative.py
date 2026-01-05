from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class BuildReasoningInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = ""
    product: str = ""


class BuildReasoningOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    narrative: str
    steps: List[str] = Field(default_factory=list)


def _load_events(events_path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not events_path.exists():
        return events
    for line in events_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _summarize(events: List[Dict[str, Any]]) -> BuildReasoningOutput:
    inputs: List[str] = []
    plans: List[str] = []
    tools: List[str] = []
    approvals: List[str] = []

    for event in events:
        kind = event.get("kind")
        payload = event.get("payload") or {}
        step_id = event.get("step_id")

        if kind == "user_input_received":
            inputs.append(f"User input captured: {payload.get('values')}")
        if kind == "pending_approval":
            approvals.append(f"Approval requested at step {step_id}")
        if kind == "run_resumed" and payload.get("decision"):
            approvals.append(f"Approval decision: {payload.get('decision')}")
        if kind == "plan_proposed":
            plan = payload.get("plan") or {}
            summary = plan.get("summary") or "Plan proposed"
            plans.append(summary)
        if kind == "tool_call_attempt_started":
            tool = payload.get("tool")
            if tool:
                tools.append(f"Tool executed: {tool}")

    steps = [
        *inputs,
        *plans,
        *approvals,
        *tools,
    ]
    if not steps:
        steps.append("No reasoning events captured.")
    narrative = "\n".join(f"- {item}" for item in steps)
    return BuildReasoningOutput(narrative=narrative, steps=steps)


class BuildReasoningNarrativeTool(BaseTool):
    name = "build_reasoning_narrative"
    description = "Builds a concise reasoning narrative from observability events."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = BuildReasoningInput.model_validate(params or {})
            output_dir = (ctx.run.meta or {}).get("output_dir")
            if not output_dir:
                raise RuntimeError("output_dir_missing")
            runtime_dir = Path(str(output_dir)).parent / "runtime"
            events_path = runtime_dir / "events.jsonl"
            events = _load_events(events_path)
            output = _summarize(events)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> BuildReasoningNarrativeTool:
    return BuildReasoningNarrativeTool()
