"""
Core Governance Module

This module provides governance controls for the orchestration system:
- Policy enforcement (policies.py)
- Security redaction (security.py)
- Budget management (budgeting.py)
- Gate registry for pluggable gates (gates.py)
- Hook layer for orchestrator/tools (hooks.py)

The gates module consolidates all gate implementations:
- BranchGate: Validates branch conditions
- LoopGate: Validates loop stop conditions
- PlanGate: Gates action plan execution
- CriticGate: Gates critic recommendations
- RetrievalGate: Resolves allowed retrieval sources
"""

from core.governance.gates import (
    # Gate base classes
    Gate,
    BaseGate,
    GateContext,
    GateResult,
    GateRegistry,
    # Gate implementations
    BranchGate,
    LoopGate,
    PlanGate,
    CriticGate,
    RetrievalGate,
    # Critic gate types
    CriticGateContext,
    GatedCriticDecision,
    # Backward-compatible functions
    validate_branch_conditions,
    validate_condition_path,
    validate_loop_conditions,
    gate_action_plan,
    gate_critic_recommendation,
    resolve_allowed_sources,
)

__all__ = [
    # Gate base classes
    "Gate",
    "BaseGate",
    "GateContext",
    "GateResult",
    "GateRegistry",
    # Gate implementations
    "BranchGate",
    "LoopGate",
    "PlanGate",
    "CriticGate",
    "RetrievalGate",
    # Critic gate types
    "CriticGateContext",
    "GatedCriticDecision",
    # Backward-compatible functions
    "validate_branch_conditions",
    "validate_condition_path",
    "validate_loop_conditions",
    "gate_action_plan",
    "gate_critic_recommendation",
    "resolve_allowed_sources",
]
