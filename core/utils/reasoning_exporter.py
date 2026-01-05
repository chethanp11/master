from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def build_reasoning_markdown(events_path: Path) -> str:
    if not events_path.exists():
        return ""

    events: List[Dict[str, Any]] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if not events:
        return ""

    steps: List[str] = []
    tools: List[str] = []
    hitl: List[str] = []
    decisions: List[str] = []

    for event in events:
        kind = event.get("kind")
        step_id = event.get("step_id")
        payload = event.get("payload") or {}

        if kind == "step_started":
            step_type = payload.get("type")
            label = f"{step_id} ({step_type})" if step_type else str(step_id)
            steps.append(label)

        if kind == "tool_call_attempt_started":
            tool = payload.get("tool")
            if tool:
                tools.append(f"{step_id}: {tool}")

        if kind == "pending_user_input":
            prompt = payload.get("question") or payload.get("prompt") or payload.get("title")
            hitl.append(f"INPUT requested: {payload.get('prompt_id') or payload.get('form_id')} - {prompt}")
        if kind == "user_input_received":
            hitl.append(f"INPUT provided: {payload.get('values')}")
        if kind == "pending_approval":
            hitl.append(f"APPROVAL requested: {payload.get('approval_id')}")
        if kind == "run_resumed" and "decision" in payload:
            hitl.append(f"APPROVAL decision: {payload.get('decision')} ({payload.get('comment') or ''})")

        if kind == "run_state_transition":
            decisions.append(
                f"{payload.get('from')} -> {payload.get('to')} ({payload.get('reason') or 'state_transition'})"
            )

    def _section(title: str, items: List[str]) -> str:
        if not items:
            return ""
        lines = [f"## {title}"]
        lines.extend(f"- {item}" for item in items)
        return "\n".join(lines)

    sections = [
        "# Reasoning Summary",
        _section("Steps Executed", steps),
        _section("Tool Calls", tools),
        _section("HITL Interactions", hitl),
        _section("Decisions", decisions),
    ]

    return "\n\n".join([section for section in sections if section]) + "\n"
