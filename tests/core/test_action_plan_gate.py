from __future__ import annotations

from core.contracts.action_plan_schema import ActionPlan, PlanAgentCall, PlanToolCall
from core.contracts.budget_schema import Budget
from core.governance.gates import gate_action_plan
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry
from core.contracts.descriptors_schema import ToolDescriptor


def test_plan_gate_rejects_disallowed_tool() -> None:
    plan = ActionPlan(
        id="plan1",
        goal="test",
        steps=[
            PlanToolCall(kind="tool", tool_name="forbidden_tool", inputs={}, expected_evidence_types=[]),
        ],
        required_inputs=[],
        expected_evidence=[],
        assumptions=[],
        confidence=0.6,
    )
    result = gate_action_plan(plan, allow_tools=["allowed_tool"], allow_agents=None, budget=None, sensitivity="LOW")
    assert result.status == "REJECTED"
    assert result.rejected_steps


class _NoopTool(BaseTool):
    name = "noop"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        return {"ok": True, "data": params}


def test_plan_gate_truncates_on_budget() -> None:
    ToolRegistry.clear()
    try:
        ToolRegistry.register("t1", lambda: _NoopTool())
        ToolRegistry.register("t2", lambda: _NoopTool())
        ToolRegistry.register("t3", lambda: _NoopTool())
        plan = ActionPlan(
            id="plan2",
            goal="budget",
            steps=[
                PlanToolCall(kind="tool", tool_name="t1", inputs={}, expected_evidence_types=[]),
                PlanToolCall(kind="tool", tool_name="t2", inputs={}, expected_evidence_types=[]),
                PlanToolCall(kind="tool", tool_name="t3", inputs={}, expected_evidence_types=[]),
            ],
            required_inputs=[],
            expected_evidence=[],
            assumptions=[],
            confidence=0.6,
        )
        budget = Budget(
            max_passes=3,
            max_tool_calls=1,
            max_parallel_calls=1,
            max_total_cost_units=5,
            max_latency_bucket="HIGH",
            on_exceed="DEGRADE",
        )
        result = gate_action_plan(plan, allow_tools=["t1", "t2", "t3"], allow_agents=None, budget=budget, sensitivity="LOW")
        assert result.status == "TRUNCATED"
        assert len(result.approved_steps) == 1
    finally:
        ToolRegistry.clear()


def test_plan_gate_requires_hitl_for_side_effect_tool() -> None:
    ToolRegistry.clear()
    try:
        ToolRegistry.register(
            "side_effect_tool",
            lambda: None,
            descriptor=ToolDescriptor(
                name="side_effect_tool",
                description="side effect",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=False,
                side_effect=True,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        plan = ActionPlan(
            id="plan3",
            goal="side effect",
            steps=[
                PlanToolCall(kind="tool", tool_name="side_effect_tool", inputs={}, expected_evidence_types=[]),
            ],
            required_inputs=[],
            expected_evidence=[],
            assumptions=[],
            confidence=0.6,
        )
        result = gate_action_plan(plan, allow_tools=["side_effect_tool"], allow_agents=None, budget=None, sensitivity="LOW")
        assert result.status == "REQUIRES_HITL"
        assert result.requires_hitl_for_steps == [0]
    finally:
        ToolRegistry.clear()
