# ==============================
# Self-Modification Guard
# ==============================
"""
Runtime self-modification prevention for agent safety.

IMP-022: GOV-POL-SELFMOD-001, GOV-POL-SELFMOD-002, GOV-POL-SELFMOD-003
IMP-023: GOV-POL-SELFMOD-010, GOV-POL-SELFMOD-011, GOV-POL-SELFMOD-012, GOV-POL-SELFMOD-013

Agents are strictly prohibited from modifying:
- Their own configuration
- Their own prompts/system messages
- Policies that govern their behavior
- Learning/weight updates during execution

All self-modification attempts are blocked and traced.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, FrozenSet, List, Optional, Tuple


# ==============================
# Exceptions
# ==============================

class SelfModificationBlockedError(Exception):
    """
    Raised when an agent attempts to modify its own configuration, 
    prompts, policies, or perform learning updates.
    
    INT-GOV-SELFMOD-001: All self-modification attempts blocked.
    """
    
    def __init__(
        self,
        message: str = "Self-modification is not permitted",
        *,
        agent_id: Optional[str] = None,
        target: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        self.agent_id = agent_id
        self.target = target
        self.reason = reason
        super().__init__(message)


class ConfigMutationBlockedError(Exception):
    """
    Raised when configuration mutation is detected during run execution.
    
    IMP-023 (GOV-POL-SELFMOD-010..013): Frozen configuration enforcement.
    """
    
    def __init__(
        self,
        message: str = "Configuration mutation blocked",
        *,
        field: Optional[str] = None,
        expected_hash: Optional[str] = None,
        actual_hash: Optional[str] = None,
    ) -> None:
        self.field = field
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        super().__init__(message)


# ==============================
# Guard Payload
# ==============================

@dataclass
class SelfModificationAttempt:
    """
    Record of a self-modification attempt for tracing.
    
    GOV-POL-SELFMOD-003: Trace event payload structure.
    """
    agent_id: str
    target: str  # "config", "prompt", "policy", "learning"
    reason: str
    blocked: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for trace event payload."""
        return {
            "agent_id": self.agent_id,
            "target": self.target,
            "reason": self.reason,
            "blocked": self.blocked,
        }


# ==============================
# Self-Modification Guard
# ==============================

class SelfModificationGuard:
    """
    Guard that prevents agents from modifying their own configuration,
    prompts, policies, or performing learning updates.
    
    GOV-POL-SELFMOD-001: No self-modification of config
    GOV-POL-SELFMOD-002: No learning/weight updates during execution
    GOV-POL-SELFMOD-003: All attempts traced
    
    Usage:
        guard = SelfModificationGuard()
        guard.check_config_modification("agent-1", {"key": "value"})  # raises if blocked
    """
    
    def __init__(
        self,
        *,
        enabled: bool = True,
        exempt_agents: Optional[set] = None,
    ) -> None:
        """
        Initialize the guard.
        
        Args:
            enabled: Whether the guard is active (default True)
            exempt_agents: Set of agent IDs exempt from guard (for special system agents)
        """
        self._enabled = enabled
        self._exempt_agents = exempt_agents or set()
    
    @property
    def enabled(self) -> bool:
        """Whether the guard is enabled."""
        return self._enabled
    
    def is_exempt(self, agent_id: str) -> bool:
        """Check if an agent is exempt from self-modification blocking."""
        return agent_id in self._exempt_agents
    
    def check_config_modification(
        self,
        agent_id: str,
        target_config: Dict[str, Any],
    ) -> SelfModificationAttempt:
        """
        Check if an agent is attempting to modify its own configuration.
        
        GOV-POL-SELFMOD-001: Agents cannot modify their own config.
        
        Args:
            agent_id: The agent attempting modification
            target_config: The configuration being modified
            
        Returns:
            SelfModificationAttempt record
            
        Raises:
            SelfModificationBlockedError: If modification is blocked
        """
        if not self._enabled:
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="config",
                reason="Guard disabled",
                blocked=False,
            )
        
        if self.is_exempt(agent_id):
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="config",
                reason="Agent exempt",
                blocked=False,
            )
        
        attempt = SelfModificationAttempt(
            agent_id=agent_id,
            target="config",
            reason="Agents cannot modify their own configuration",
            blocked=True,
        )
        
        raise SelfModificationBlockedError(
            f"Agent {agent_id} cannot modify its own configuration",
            agent_id=agent_id,
            target="config",
            reason=attempt.reason,
        )
    
    def check_prompt_modification(
        self,
        agent_id: str,
        target_prompt: str,
    ) -> SelfModificationAttempt:
        """
        Check if an agent is attempting to modify its own prompts.
        
        GOV-POL-SELFMOD-001: Agents cannot modify their own prompts.
        
        Args:
            agent_id: The agent attempting modification
            target_prompt: The prompt being modified
            
        Returns:
            SelfModificationAttempt record
            
        Raises:
            SelfModificationBlockedError: If modification is blocked
        """
        if not self._enabled:
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="prompt",
                reason="Guard disabled",
                blocked=False,
            )
        
        if self.is_exempt(agent_id):
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="prompt",
                reason="Agent exempt",
                blocked=False,
            )
        
        attempt = SelfModificationAttempt(
            agent_id=agent_id,
            target="prompt",
            reason="Agents cannot modify their own prompts",
            blocked=True,
        )
        
        raise SelfModificationBlockedError(
            f"Agent {agent_id} cannot modify its own prompts",
            agent_id=agent_id,
            target="prompt",
            reason=attempt.reason,
        )
    
    def check_policy_modification(
        self,
        agent_id: str,
        target_policy: str,
    ) -> SelfModificationAttempt:
        """
        Check if an agent is attempting to modify its governing policies.
        
        GOV-POL-SELFMOD-001: Agents cannot modify policies governing them.
        
        Args:
            agent_id: The agent attempting modification
            target_policy: The policy being modified
            
        Returns:
            SelfModificationAttempt record
            
        Raises:
            SelfModificationBlockedError: If modification is blocked
        """
        if not self._enabled:
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="policy",
                reason="Guard disabled",
                blocked=False,
            )
        
        if self.is_exempt(agent_id):
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="policy",
                reason="Agent exempt",
                blocked=False,
            )
        
        attempt = SelfModificationAttempt(
            agent_id=agent_id,
            target="policy",
            reason="Agents cannot modify policies governing their behavior",
            blocked=True,
        )
        
        raise SelfModificationBlockedError(
            f"Agent {agent_id} cannot modify its governing policies",
            agent_id=agent_id,
            target="policy",
            reason=attempt.reason,
        )
    
    def check_learning_update(
        self,
        agent_id: str,
    ) -> SelfModificationAttempt:
        """
        Check if an agent is attempting to perform learning/weight updates.
        
        GOV-POL-SELFMOD-002: No learning during execution.
        
        Args:
            agent_id: The agent attempting learning
            
        Returns:
            SelfModificationAttempt record
            
        Raises:
            SelfModificationBlockedError: If learning is blocked
        """
        if not self._enabled:
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="learning",
                reason="Guard disabled",
                blocked=False,
            )
        
        if self.is_exempt(agent_id):
            return SelfModificationAttempt(
                agent_id=agent_id,
                target="learning",
                reason="Agent exempt",
                blocked=False,
            )
        
        attempt = SelfModificationAttempt(
            agent_id=agent_id,
            target="learning",
            reason="Learning/weight updates not permitted during execution",
            blocked=True,
        )
        
        raise SelfModificationBlockedError(
            f"Agent {agent_id} cannot perform learning during execution",
            agent_id=agent_id,
            target="learning",
            reason=attempt.reason,
        )
    
    def get_blocked_payload(
        self,
        agent_id: str,
        target: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Get payload for self_modification_blocked trace event.
        
        GOV-POL-SELFMOD-003: Trace event emission.
        
        Args:
            agent_id: The agent that was blocked
            target: What was being modified (config, prompt, policy, learning)
            reason: Why it was blocked
            
        Returns:
            Dict payload for trace event
        """
        return {
            "agent_id": agent_id,
            "target": target,
            "reason": reason,
            "blocked": True,
        }


# ==============================
# Frozen Configuration (IMP-023)
# ==============================

@dataclass
class FrozenConfig:
    """
    Immutable snapshot of configuration at run initialization.
    
    IMP-023 (GOV-POL-SELFMOD-010..013):
    - Policy configurations frozen
    - Agent prompts/system messages frozen
    - Budget and resource limits frozen
    - Tool and agent registry state frozen
    
    All fields are computed at creation and cannot be modified.
    """
    
    # Frozen at initialization
    frozen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Hash snapshots for each configuration domain
    policies_hash: str = ""
    agents_hash: str = ""
    tools_hash: str = ""
    budget_hash: str = ""
    
    # Original config snapshots (for validation)
    policies_snapshot: Dict[str, Any] = field(default_factory=dict)
    agents_snapshot: Dict[str, Any] = field(default_factory=dict)
    tools_snapshot: FrozenSet[str] = field(default_factory=frozenset)
    budget_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def _compute_hash(data: Any) -> str:
        """Compute deterministic hash of data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    
    @classmethod
    def create(
        cls,
        *,
        policies: Optional[Dict[str, Any]] = None,
        agents: Optional[Dict[str, Any]] = None,
        tools: Optional[List[str]] = None,
        budget: Optional[Dict[str, Any]] = None,
    ) -> "FrozenConfig":
        """
        Create a FrozenConfig snapshot from current configuration.
        
        Args:
            policies: Policy configuration dict
            agents: Agent configuration dict (prompts, system messages)
            tools: List of registered tool names
            budget: Budget and resource limits
            
        Returns:
            Immutable FrozenConfig snapshot
        """
        policies = policies or {}
        agents = agents or {}
        tools_list = tools or []
        budget = budget or {}
        
        return cls(
            frozen_at=datetime.now(timezone.utc),
            policies_hash=cls._compute_hash(policies),
            agents_hash=cls._compute_hash(agents),
            tools_hash=cls._compute_hash(sorted(tools_list)),
            budget_hash=cls._compute_hash(budget),
            policies_snapshot=policies.copy(),
            agents_snapshot=agents.copy(),
            tools_snapshot=frozenset(tools_list),
            budget_snapshot=budget.copy(),
        )
    
    def validate_policies(self, current: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate current policies against frozen snapshot.
        
        GOV-POL-SELFMOD-010: Policy configurations frozen.
        
        Returns:
            (valid, error_message)
        """
        current_hash = self._compute_hash(current)
        if current_hash != self.policies_hash:
            return False, f"Policy configuration mutated (expected hash {self.policies_hash[:16]}...)"
        return True, None
    
    def validate_agents(self, current: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate current agent config against frozen snapshot.
        
        GOV-POL-SELFMOD-011: Agent prompts/system messages frozen.
        
        Returns:
            (valid, error_message)
        """
        current_hash = self._compute_hash(current)
        if current_hash != self.agents_hash:
            return False, f"Agent configuration mutated (expected hash {self.agents_hash[:16]}...)"
        return True, None
    
    def validate_tools(self, current: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate current tool registry against frozen snapshot.
        
        GOV-POL-SELFMOD-013: Tool registries read-only.
        
        Returns:
            (valid, error_message)
        """
        current_hash = self._compute_hash(sorted(current))
        if current_hash != self.tools_hash:
            return False, f"Tool registry mutated (expected hash {self.tools_hash[:16]}...)"
        return True, None
    
    def validate_budget(self, current: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate current budget against frozen snapshot.
        
        GOV-POL-SELFMOD-012: Budget/resource limits frozen (except consumption).
        
        Note: This validates limits, not consumption counters.
        
        Returns:
            (valid, error_message)
        """
        current_hash = self._compute_hash(current)
        if current_hash != self.budget_hash:
            return False, f"Budget limits mutated (expected hash {self.budget_hash[:16]}...)"
        return True, None
    
    def check_mutation(
        self,
        *,
        policies: Optional[Dict[str, Any]] = None,
        agents: Optional[Dict[str, Any]] = None,
        tools: Optional[List[str]] = None,
        budget: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Check all provided configurations against frozen snapshot.
        
        Raises ConfigMutationBlockedError if any mutation detected.
        """
        if policies is not None:
            valid, msg = self.validate_policies(policies)
            if not valid:
                raise ConfigMutationBlockedError(
                    msg or "Policy mutation blocked",
                    field="policies",
                    expected_hash=self.policies_hash,
                    actual_hash=self._compute_hash(policies),
                )
        
        if agents is not None:
            valid, msg = self.validate_agents(agents)
            if not valid:
                raise ConfigMutationBlockedError(
                    msg or "Agent config mutation blocked",
                    field="agents",
                    expected_hash=self.agents_hash,
                    actual_hash=self._compute_hash(agents),
                )
        
        if tools is not None:
            valid, msg = self.validate_tools(tools)
            if not valid:
                raise ConfigMutationBlockedError(
                    msg or "Tool registry mutation blocked",
                    field="tools",
                    expected_hash=self.tools_hash,
                    actual_hash=self._compute_hash(sorted(tools)),
                )
        
        if budget is not None:
            valid, msg = self.validate_budget(budget)
            if not valid:
                raise ConfigMutationBlockedError(
                    msg or "Budget limits mutation blocked",
                    field="budget",
                    expected_hash=self.budget_hash,
                    actual_hash=self._compute_hash(budget),
                )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "frozen_at": self.frozen_at.isoformat(),
            "policies_hash": self.policies_hash,
            "agents_hash": self.agents_hash,
            "tools_hash": self.tools_hash,
            "budget_hash": self.budget_hash,
        }


# ==============================
# Allowed Runtime Mutations (IMP-024)
# ==============================

class AllowedMutationType:
    """
    Enumeration of allowed runtime mutations.
    
    IMP-024 (GOV-POL-SELFMOD-020..022): Define allowlist of permitted mutations.
    
    These are the ONLY mutations allowed during run execution.
    All other mutations are blocked by the SelfModificationGuard.
    """
    
    # Budget consumption counters (via BudgetEnforcer)
    # Rationale: Budget tracking is essential for governance
    BUDGET_CONSUMPTION = "budget_consumption"
    
    # Run artifacts and evidence accumulation
    # Rationale: Core function of the system is to gather evidence
    RUN_ARTIFACTS = "run_artifacts"
    EVIDENCE_ACCUMULATION = "evidence_accumulation"
    
    # Run status transitions (per state machine)
    # Rationale: Status changes are fundamental to run lifecycle
    RUN_STATUS = "run_status"
    
    # Step status transitions (per state machine)
    # Rationale: Status changes are fundamental to step lifecycle
    STEP_STATUS = "step_status"
    
    # Trace event emission
    # Rationale: Observability is a core requirement
    TRACE_EVENTS = "trace_events"
    
    # All allowed types
    ALL = frozenset({
        BUDGET_CONSUMPTION,
        RUN_ARTIFACTS,
        EVIDENCE_ACCUMULATION,
        RUN_STATUS,
        STEP_STATUS,
        TRACE_EVENTS,
    })


def is_allowed_mutation(mutation_type: str) -> bool:
    """
    Check if a mutation type is allowed during runtime.
    
    IMP-024 (GOV-POL-SELFMOD-020..022):
    - Budget consumption counters MAY be updated
    - Run artifacts/evidence MAY be accumulated
    - Run/step status MAY transition per state machine
    - All other mutations blocked
    
    Args:
        mutation_type: The type of mutation being attempted
        
    Returns:
        True if mutation is allowed, False otherwise
        
    Examples:
        >>> is_allowed_mutation("budget_consumption")
        True
        >>> is_allowed_mutation("config_change")
        False
    """
    return mutation_type in AllowedMutationType.ALL


def get_allowed_mutation_rationale(mutation_type: str) -> Optional[str]:
    """
    Get the rationale for why a mutation type is allowed.
    
    Args:
        mutation_type: The mutation type to look up
        
    Returns:
        Rationale string if allowed, None if not allowed
    """
    rationales = {
        AllowedMutationType.BUDGET_CONSUMPTION: "Budget tracking is essential for governance",
        AllowedMutationType.RUN_ARTIFACTS: "Core function of the system is to gather artifacts",
        AllowedMutationType.EVIDENCE_ACCUMULATION: "Core function of the system is to gather evidence",
        AllowedMutationType.RUN_STATUS: "Status changes are fundamental to run lifecycle",
        AllowedMutationType.STEP_STATUS: "Status changes are fundamental to step lifecycle",
        AllowedMutationType.TRACE_EVENTS: "Observability is a core requirement",
    }
    return rationales.get(mutation_type)


def check_mutation_allowed(mutation_type: str) -> None:
    """
    Check if mutation is allowed, raise if not.
    
    Args:
        mutation_type: The type of mutation being attempted
        
    Raises:
        SelfModificationBlockedError: If mutation type is not allowed
    """
    if not is_allowed_mutation(mutation_type):
        raise SelfModificationBlockedError(
            f"Mutation type '{mutation_type}' is not allowed",
            target=mutation_type,
            reason=f"Only allowed mutations: {', '.join(sorted(AllowedMutationType.ALL))}",
        )


# Module-level guard instance for simple use cases
_default_guard: Optional[SelfModificationGuard] = None


def get_default_guard() -> SelfModificationGuard:
    """Get the default self-modification guard."""
    global _default_guard
    if _default_guard is None:
        _default_guard = SelfModificationGuard()
    return _default_guard


__all__ = [
    "SelfModificationBlockedError",
    "ConfigMutationBlockedError",
    "SelfModificationAttempt",
    "SelfModificationGuard",
    "FrozenConfig",
    "AllowedMutationType",
    "is_allowed_mutation",
    "get_allowed_mutation_rationale",
    "check_mutation_allowed",
    "get_default_guard",
]
