"""
Unified Governance Gates Module

This module consolidates all governance gates into a single registry-based system:
- BranchGate: Validates branch conditions in flows
- LoopGate: Validates loop stop conditions in flows
- PlanGate: Gates action plan execution
- CriticGate: Gates critic recommendations
- RetrievalGate: Resolves allowed retrieval sources

The GateRegistry allows pluggable gate implementations while maintaining
backward compatibility with the original gate functions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Set, Type, Union

from pydantic import BaseModel, ConfigDict, Field

from core.config.schema import Settings
from core.contracts.action_plan_schema import (
    ActionPlan,
    PlanAgentCall,
    PlanGateResult,
    PlanRejection,
    PlanStep,
    PlanToolCall,
)
from core.contracts.budget_schema import Budget
from core.contracts.critic_schema import CriticNextAction, CriticOutput
from core.contracts.flow_schema import (
    ConditionExpr,
    ConfidenceThreshold,
    FlowDef,
    NoMissingEvidence,
    StepType,
    StopConditionExpr,
    StopConditionGroup,
)
from core.governance.budgeting import consume_budget, init_budget_state


# ============================================================================
# Gate Protocol and Base Classes
# ============================================================================


@dataclass
class GateContext:
    """Context passed to gates for evaluation."""

    flow_def: Optional[FlowDef] = None
    settings: Optional[Settings] = None
    product: str = ""
    flow: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    """Result of a gate evaluation."""

    gate_name: str
    allowed: bool
    reason: str
    errors: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class Gate(Protocol):
    """Protocol for gate implementations."""

    name: str

    def evaluate(self, context: GateContext) -> GateResult:
        """Evaluate the gate and return a result."""
        ...


class BaseGate(ABC):
    """Abstract base class for gate implementations."""

    name: str = "base"

    @abstractmethod
    def evaluate(self, context: GateContext) -> GateResult:
        """Evaluate the gate and return a result."""
        pass

    def _success(self, details: Optional[Dict[str, Any]] = None) -> GateResult:
        return GateResult(
            gate_name=self.name,
            allowed=True,
            reason="ok",
            errors=[],
            details=details or {},
        )

    def _failure(
        self,
        reason: str,
        errors: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> GateResult:
        return GateResult(
            gate_name=self.name,
            allowed=False,
            reason=reason,
            errors=errors or [],
            details=details or {},
        )


# ============================================================================
# Gate Registry
# ============================================================================


class GateRegistry:
    """Registry for pluggable gate implementations."""

    _gates: Dict[str, Gate] = {}

    @classmethod
    def register(cls, gate: Gate) -> None:
        """Register a gate implementation."""
        cls._gates[gate.name] = gate

    @classmethod
    def get(cls, name: str) -> Optional[Gate]:
        """Get a registered gate by name."""
        return cls._gates.get(name)

    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a gate is registered."""
        return name in cls._gates

    @classmethod
    def list_registered(cls) -> List[str]:
        """List all registered gate names."""
        return list(cls._gates.keys())

    @classmethod
    def evaluate_all(cls, context: GateContext) -> List[GateResult]:
        """Evaluate all registered gates."""
        results = []
        for gate in cls._gates.values():
            results.append(gate.evaluate(context))
        return results

    @classmethod
    def clear(cls) -> None:
        """Clear all registered gates (for testing)."""
        cls._gates.clear()


# ============================================================================
# Branch Gate
# ============================================================================


_BRANCH_DISALLOWED_SEGMENTS = {
    "raw_text",
    "content",
    "prompt",
    "transcript",
    "free_text",
    "user_input",
    "content_ref",
}


class BranchGate(BaseGate):
    """Gate for validating branch conditions in flows."""

    name = "branch"

    def evaluate(self, context: GateContext) -> GateResult:
        if context.flow_def is None:
            return self._failure("no_flow_def", errors=["flow_def is required"])

        errors = self.validate_branch_conditions(context.flow_def)
        if errors:
            return self._failure(
                "branch_condition_disallowed",
                errors=errors,
                details={"flow": context.flow_def.id, "product": context.product},
            )
        return self._success({"flow": context.flow_def.id, "product": context.product})

    def validate_branch_conditions(self, flow_def: FlowDef) -> List[str]:
        """Validate all branch conditions in a flow definition."""
        step_ids = {step.id for step in flow_def.steps}
        errors: List[str] = []

        for step in flow_def.steps:
            if step.type != StepType.BRANCH:
                continue
            if step.when is None:
                errors.append(f"branch.{step.id}.missing_condition")
                continue
            errors.extend(
                self._validate_condition_expr(step.when, step_ids=step_ids, step_id=step.id)
            )
            if step.then and step.then not in step_ids:
                errors.append(f"branch.{step.id}.unknown_then:{step.then}")
            if step.else_step and step.else_step not in step_ids:
                errors.append(f"branch.{step.id}.unknown_else:{step.else_step}")

        return errors

    def validate_condition_path(
        self, path: str, *, step_ids: Set[str], step_id: str
    ) -> List[str]:
        """Validate a condition path."""
        return self._validate_path(path, step_ids=step_ids, step_id=step_id)

    def _validate_condition_expr(
        self, condition: ConditionExpr, *, step_ids: Set[str], step_id: str
    ) -> List[str]:
        errors: List[str] = []
        if condition.path:
            errors.extend(self._validate_path(condition.path, step_ids=step_ids, step_id=step_id))
            return errors
        if condition.all:
            for child in condition.all:
                errors.extend(
                    self._validate_condition_expr(child, step_ids=step_ids, step_id=step_id)
                )
        if condition.any:
            for child in condition.any:
                errors.extend(
                    self._validate_condition_expr(child, step_ids=step_ids, step_id=step_id)
                )
        return errors

    def _validate_path(
        self, path: str, *, step_ids: Set[str], step_id: str
    ) -> List[str]:
        errors: List[str] = []
        parts = [seg for seg in path.split(".") if seg]
        if not parts:
            return [f"branch.{step_id}.empty_path"]
        if parts[0] not in {"steps", "artifacts"}:
            return [f"branch.{step_id}.unsupported_root:{parts[0]}"]
        if self._has_disallowed_segment(parts):
            return [f"branch.{step_id}.disallowed_path:{path}"]
        if parts[0] == "steps":
            if len(parts) < 4 or parts[2] != "output":
                return [f"branch.{step_id}.invalid_steps_path:{path}"]
            if parts[1] not in step_ids:
                return [f"branch.{step_id}.unknown_step:{parts[1]}"]
        if parts[0] == "artifacts":
            if len(parts) < 3:
                return [f"branch.{step_id}.invalid_artifact_path:{path}"]
        return errors

    def _has_disallowed_segment(self, parts: List[str]) -> bool:
        for seg in parts:
            if seg in _BRANCH_DISALLOWED_SEGMENTS:
                return True
        return False


# ============================================================================
# Loop Gate
# ============================================================================


class LoopGate(BaseGate):
    """Gate for validating loop stop conditions in flows."""

    name = "loop"

    def __init__(self, branch_gate: Optional[BranchGate] = None):
        self.branch_gate = branch_gate or BranchGate()

    def evaluate(self, context: GateContext) -> GateResult:
        if context.flow_def is None:
            return self._failure("no_flow_def", errors=["flow_def is required"])

        errors = self.validate_loop_conditions(context.flow_def)
        if errors:
            return self._failure(
                "loop_condition_disallowed",
                errors=errors,
                details={"flow": context.flow_def.id, "product": context.product},
            )
        return self._success({"flow": context.flow_def.id, "product": context.product})

    def validate_loop_conditions(self, flow_def: FlowDef) -> List[str]:
        """Validate all loop conditions in a flow definition."""
        step_ids = {step.id for step in flow_def.steps}
        errors: List[str] = []

        for step in flow_def.steps:
            if step.type != StepType.REPEAT_UNTIL:
                continue
            if step.stop_condition is None:
                errors.append(f"loop.{step.id}.missing_stop_condition")
                continue
            errors.extend(
                self._validate_stop_condition(
                    step.stop_condition, step_ids=step_ids, step_id=step.id
                )
            )
            if step.iteration_step and step.iteration_step not in step_ids:
                errors.append(f"loop.{step.id}.unknown_iteration_step:{step.iteration_step}")
            if step.on_terminate and step.on_terminate not in step_ids:
                errors.append(f"loop.{step.id}.unknown_on_terminate:{step.on_terminate}")

        return errors

    def _validate_stop_condition(
        self, condition: StopConditionExpr, *, step_ids: Set[str], step_id: str
    ) -> List[str]:
        if isinstance(condition, StopConditionGroup):
            errors: List[str] = []
            for child in condition.conditions:
                errors.extend(
                    self._validate_stop_condition(child, step_ids=step_ids, step_id=step_id)
                )
            return errors
        if isinstance(condition, (ConfidenceThreshold, NoMissingEvidence)):
            return self.branch_gate.validate_condition_path(
                condition.path, step_ids=step_ids, step_id=step_id
            )
        return [f"loop.{step_id}.unsupported_stop_condition"]


# ============================================================================
# Plan Gate
# ============================================================================


class PlanGate(BaseGate):
    """Gate for action plan execution."""

    name = "plan"

    def evaluate(self, context: GateContext) -> GateResult:
        # Plan gate evaluation requires specific parameters
        # This is a placeholder - actual plan gating is done via gate_action_plan
        return self._success()

    def gate_action_plan(
        self,
        plan: ActionPlan,
        *,
        allow_tools: Optional[List[str]] = None,
        allow_agents: Optional[List[str]] = None,
        budget: Optional[Budget] = None,
        sensitivity: str = "LOW",
    ) -> PlanGateResult:
        """Gate an action plan for execution."""
        # Import here to avoid circular imports
        from core.agents.registry import AgentRegistry
        from core.tools.registry import ToolRegistry

        allow_tools_set = {name.strip().lower() for name in (allow_tools or [])}
        allow_agents_set = {name.strip().lower() for name in (allow_agents or [])}
        rejected: List[PlanRejection] = []
        approved: List[PlanStep] = []
        requires_hitl: List[int] = []
        reasons: List[str] = []

        if budget is None:
            budget_state = None
        else:
            budget_state = init_budget_state()

        for idx, step in enumerate(plan.steps):
            if isinstance(step, PlanToolCall):
                tool_name = step.tool_name
                if allow_tools_set and tool_name.strip().lower() not in allow_tools_set:
                    rejected.append(
                        PlanRejection(step=step.model_dump(mode="json"), reason="tool_not_allowed")
                    )
                    reasons.append("tool_not_allowed")
                    return self._reject(plan, rejected, reasons, budget, sensitivity)
                if not ToolRegistry.has(tool_name):
                    rejected.append(
                        PlanRejection(
                            step=step.model_dump(mode="json"), reason="tool_not_registered"
                        )
                    )
                    reasons.append("tool_not_registered")
                    return self._reject(plan, rejected, reasons, budget, sensitivity)
                descriptor = ToolRegistry.get_descriptor(tool_name)
                if descriptor.side_effect:
                    requires_hitl.append(idx)
                if budget and budget_state:
                    allowed, action, updated = consume_budget(
                        budget=budget,
                        state=budget_state,
                        kind="tool",
                        amount=1,
                        cost_units=1,
                    )
                    budget_state = updated
                    if not allowed:
                        reasons.append("budget_exceeded")
                        return self._truncate_or_reject(
                            plan,
                            approved,
                            rejected,
                            requires_hitl,
                            reasons,
                            budget,
                            sensitivity,
                            action,
                        )
                approved.append(step)
            elif isinstance(step, PlanAgentCall):
                agent_name = step.agent_name
                if allow_agents_set and agent_name.strip().lower() not in allow_agents_set:
                    rejected.append(
                        PlanRejection(
                            step=step.model_dump(mode="json"), reason="agent_not_allowed"
                        )
                    )
                    reasons.append("agent_not_allowed")
                    return self._reject(plan, rejected, reasons, budget, sensitivity)
                if not AgentRegistry.has(agent_name):
                    rejected.append(
                        PlanRejection(
                            step=step.model_dump(mode="json"), reason="agent_not_registered"
                        )
                    )
                    reasons.append("agent_not_registered")
                    return self._reject(plan, rejected, reasons, budget, sensitivity)
                if budget and budget_state:
                    allowed, action, updated = consume_budget(
                        budget=budget,
                        state=budget_state,
                        kind="pass",
                        amount=1,
                        cost_units=1,
                    )
                    budget_state = updated
                    if not allowed:
                        reasons.append("budget_exceeded")
                        return self._truncate_or_reject(
                            plan,
                            approved,
                            rejected,
                            requires_hitl,
                            reasons,
                            budget,
                            sensitivity,
                            action,
                        )
                approved.append(step)

        status = "REQUIRES_HITL" if requires_hitl else "APPROVED"
        return PlanGateResult(
            plan_id=plan.id,
            status=status,
            approved_steps=approved,
            rejected_steps=rejected,
            requires_hitl_for_steps=requires_hitl,
            reasons=sorted(set(reasons)),
            effective_budget=budget.model_dump(mode="json") if budget else None,
            sensitivity=sensitivity,
        )

    def _truncate_or_reject(
        self,
        plan: ActionPlan,
        approved: List[PlanStep],
        rejected: List[PlanRejection],
        requires_hitl: List[int],
        reasons: List[str],
        budget: Optional[Budget],
        sensitivity: str,
        action: str,
    ) -> PlanGateResult:
        if action == "FAIL":
            return self._reject(plan, rejected, reasons, budget, sensitivity)
        if not approved:
            return self._reject(plan, rejected, reasons, budget, sensitivity)
        return PlanGateResult(
            plan_id=plan.id,
            status="TRUNCATED",
            approved_steps=approved,
            rejected_steps=rejected,
            requires_hitl_for_steps=requires_hitl,
            reasons=sorted(set(reasons)),
            effective_budget=budget.model_dump(mode="json") if budget else None,
            sensitivity=sensitivity,
        )

    def _reject(
        self,
        plan: ActionPlan,
        rejected: List[PlanRejection],
        reasons: List[str],
        budget: Optional[Budget],
        sensitivity: str,
    ) -> PlanGateResult:
        return PlanGateResult(
            plan_id=plan.id,
            status="REJECTED",
            approved_steps=[],
            rejected_steps=rejected,
            requires_hitl_for_steps=[],
            reasons=sorted(set(reasons)) or ["rejected"],
            effective_budget=budget.model_dump(mode="json") if budget else None,
            sensitivity=sensitivity,
        )


# ============================================================================
# Critic Gate
# ============================================================================


class CriticGateContext(BaseModel):
    """Context for critic gate evaluation."""

    model_config = ConfigDict(extra="forbid")

    allow_user_input: bool = False
    allow_hitl: bool = False
    allow_fetch_more_evidence: bool = False
    evidence_budget: int = 0


class GatedCriticDecision(BaseModel):
    """Result of critic gate evaluation."""

    model_config = ConfigDict(extra="forbid")

    action: CriticNextAction
    allowed_actions: List[CriticNextAction] = Field(default_factory=list)
    reason: str
    details: Dict[str, str] = Field(default_factory=dict)


class CriticGate(BaseGate):
    """Gate for critic recommendations."""

    name = "critic"

    def evaluate(self, context: GateContext) -> GateResult:
        # Critic gate evaluation requires specific parameters
        # This is a placeholder - actual critic gating is done via gate_critic_recommendation
        return self._success()

    def gate_critic_recommendation(
        self,
        critic: CriticOutput,
        context: CriticGateContext,
    ) -> GatedCriticDecision:
        """Gate a critic recommendation."""
        allowed: List[str] = ["NONE"]
        if context.allow_user_input:
            allowed.append("USER_INPUT")
        if context.allow_hitl:
            allowed.append("HITL")
        if context.allow_fetch_more_evidence and context.evidence_budget > 0:
            allowed.append("FETCH_MORE_EVIDENCE")

        requested = critic.recommended_next_action
        if requested in allowed:
            return GatedCriticDecision(
                action=requested, allowed_actions=allowed, reason="allowed"
            )

        return GatedCriticDecision(
            action="NONE",
            allowed_actions=allowed,
            reason="recommendation_blocked",
            details={"requested": requested},
        )


# ============================================================================
# Retrieval Gate
# ============================================================================


class RetrievalGate(BaseGate):
    """Gate for retrieval source resolution."""

    name = "retrieval"

    def evaluate(self, context: GateContext) -> GateResult:
        # Retrieval gate evaluation requires specific parameters
        # This is a placeholder - actual source resolution is done via resolve_allowed_sources
        return self._success()

    def resolve_allowed_sources(
        self, settings: Settings, *, product: str, flow: str
    ) -> List[str]:
        """Resolve allowed retrieval sources for a product/flow."""
        default_allowed: List[str] = []
        overrides: Dict[str, Any] = (
            settings.policies.by_product.get(product, {})
            if settings.policies.by_product
            else {}
        )
        flow_overrides = (
            overrides.get("retrieval_allowed_sources_by_flow", {})
            if isinstance(overrides, dict)
            else {}
        )
        if isinstance(flow_overrides, dict):
            flow_allowed = flow_overrides.get(flow)
            if isinstance(flow_allowed, list):
                return list(flow_allowed)
        product_allowed = (
            overrides.get("retrieval_allowed_sources") if isinstance(overrides, dict) else None
        )
        if isinstance(product_allowed, list):
            return list(product_allowed)
        return default_allowed


# ============================================================================
# Gate Instances (Singletons for backward compatibility)
# ============================================================================

# Create singleton instances
_branch_gate = BranchGate()
_loop_gate = LoopGate(_branch_gate)
_plan_gate = PlanGate()
_critic_gate = CriticGate()
_retrieval_gate = RetrievalGate()


# ============================================================================
# Backward-Compatible Functions
# ============================================================================


def validate_branch_conditions(flow_def: FlowDef) -> List[str]:
    """Validate branch conditions in a flow (backward compatible)."""
    return _branch_gate.validate_branch_conditions(flow_def)


def validate_condition_path(path: str, *, step_ids: Set[str], step_id: str) -> List[str]:
    """Validate a condition path (backward compatible)."""
    return _branch_gate.validate_condition_path(path, step_ids=step_ids, step_id=step_id)


def validate_loop_conditions(flow_def: FlowDef) -> List[str]:
    """Validate loop conditions in a flow (backward compatible)."""
    return _loop_gate.validate_loop_conditions(flow_def)


def gate_action_plan(
    plan: ActionPlan,
    *,
    allow_tools: Optional[List[str]] = None,
    allow_agents: Optional[List[str]] = None,
    budget: Optional[Budget] = None,
    sensitivity: str = "LOW",
) -> PlanGateResult:
    """Gate an action plan for execution (backward compatible)."""
    return _plan_gate.gate_action_plan(
        plan,
        allow_tools=allow_tools,
        allow_agents=allow_agents,
        budget=budget,
        sensitivity=sensitivity,
    )


def gate_critic_recommendation(
    critic: CriticOutput,
    context: CriticGateContext,
) -> GatedCriticDecision:
    """Gate a critic recommendation (backward compatible)."""
    return _critic_gate.gate_critic_recommendation(critic, context)


def resolve_allowed_sources(settings: Settings, *, product: str, flow: str) -> List[str]:
    """Resolve allowed retrieval sources (backward compatible)."""
    return _retrieval_gate.resolve_allowed_sources(settings, product=product, flow=flow)


# ============================================================================
# Register Default Gates
# ============================================================================


def _register_default_gates() -> None:
    """Register all default gates with the registry."""
    GateRegistry.register(_branch_gate)
    GateRegistry.register(_loop_gate)
    GateRegistry.register(_plan_gate)
    GateRegistry.register(_critic_gate)
    GateRegistry.register(_retrieval_gate)


# Auto-register on module import
_register_default_gates()
