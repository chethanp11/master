"""
HITL Binding Requirements (IMP-043)

GOV-HITL-BIND-001...007, GOV-HITL-DECL-001...005: Human-in-the-loop binding enforcement.

This module provides:
- HITLBinding: Immutable HITL configuration
- EscalationPath: Trigger conditions and escalation targets
- Enforcement hooks for runtime modification prevention

HITL bindings are immutable once registered - they cannot be modified at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4


# ============================================================================
# Enums
# ============================================================================


class EscalationTrigger(str, Enum):
    """
    Trigger types for HITL escalation.
    
    GOV-HITL-BIND-002: Defined trigger conditions.
    """
    LOW_CONFIDENCE = "low_confidence"
    BLOCKING_AMBIGUITY = "blocking_ambiguity"
    INSUFFICIENT_INTENT = "insufficient_intent"
    BUDGET_THRESHOLD = "budget_threshold"
    SECURITY_VIOLATION = "security_violation"
    POLICY_VIOLATION = "policy_violation"
    EXPLICIT_REQUEST = "explicit_request"
    TOOL_FAILURE = "tool_failure"
    MODEL_ERROR = "model_error"
    CUSTOM = "custom"


class EscalationAction(str, Enum):
    """
    Actions to take on escalation.
    
    GOV-HITL-BIND-003: Defined escalation actions.
    """
    PAUSE_AND_NOTIFY = "pause_and_notify"
    PAUSE_AND_WAIT = "pause_and_wait"
    REJECT_AND_NOTIFY = "reject_and_notify"
    LOG_AND_CONTINUE = "log_and_continue"
    EMERGENCY_STOP = "emergency_stop"


class HITLPriority(str, Enum):
    """
    Priority levels for HITL escalations.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# Escalation Path
# ============================================================================


@dataclass(frozen=True)
class EscalationCondition:
    """
    A condition that triggers HITL escalation.
    
    Attributes:
        trigger: The type of trigger
        threshold: Optional threshold value (e.g., confidence < 0.5)
        description: Human-readable description of condition
        custom_evaluator: Optional name of custom evaluator function
    """
    trigger: EscalationTrigger
    threshold: Optional[float] = None
    description: str = ""
    custom_evaluator: Optional[str] = None
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """
        Check if this condition matches the given context.
        
        Args:
            context: Dictionary with evaluation context
            
        Returns:
            True if condition is met
        """
        trigger_value = context.get("trigger")
        if trigger_value != self.trigger.value and trigger_value != self.trigger:
            return False
        
        if self.threshold is not None:
            context_value = context.get("value", 0.0)
            # For low_confidence, we check if value is below threshold
            if self.trigger == EscalationTrigger.LOW_CONFIDENCE:
                return context_value < self.threshold
            # For budget_threshold, we check if value exceeds threshold
            if self.trigger == EscalationTrigger.BUDGET_THRESHOLD:
                return context_value >= self.threshold
        
        return True


@dataclass(frozen=True)
class EscalationPath:
    """
    A path for escalating to human intervention.
    
    GOV-HITL-BIND-001: EscalationPath defines trigger conditions and actions.
    
    Attributes:
        path_id: Unique identifier for this escalation path
        name: Human-readable name
        conditions: List of conditions that trigger this path
        action: Action to take when triggered
        priority: Priority level of this escalation
        notification_targets: List of notification target identifiers
        timeout_seconds: Optional timeout before auto-resolution
        require_acknowledgment: Whether human must acknowledge
    """
    path_id: str
    name: str
    conditions: tuple  # Tuple[EscalationCondition, ...] for immutability
    action: EscalationAction
    priority: HITLPriority = HITLPriority.MEDIUM
    notification_targets: tuple = ()  # Tuple[str, ...] for immutability
    timeout_seconds: Optional[int] = None
    require_acknowledgment: bool = True
    
    def matches_any_condition(self, context: Dict[str, Any]) -> bool:
        """
        Check if any condition in this path matches the context.
        
        Args:
            context: Dictionary with evaluation context
            
        Returns:
            True if any condition matches
        """
        return any(cond.matches(context) for cond in self.conditions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path_id": self.path_id,
            "name": self.name,
            "conditions": [
                {
                    "trigger": c.trigger.value,
                    "threshold": c.threshold,
                    "description": c.description,
                }
                for c in self.conditions
            ],
            "action": self.action.value,
            "priority": self.priority.value,
            "notification_targets": list(self.notification_targets),
            "timeout_seconds": self.timeout_seconds,
            "require_acknowledgment": self.require_acknowledgment,
        }


# ============================================================================
# HITL Binding
# ============================================================================


@dataclass(frozen=True)
class HITLBinding:
    """
    Immutable HITL binding configuration.
    
    GOV-HITL-BIND-001...007: HITL bindings are immutable once registered.
    
    This class is frozen (immutable) by design. Any attempt to modify
    a binding at runtime will raise an exception.
    
    Attributes:
        binding_id: Unique identifier for this binding
        product_id: The product this binding belongs to
        escalation_paths: Mapping of path names to EscalationPath objects
        enabled: Whether this binding is active
        created_at: When the binding was created
        registered_by: Identifier of who registered the binding
        immutable: Always True - bindings cannot be modified (enforced at runtime)
    """
    binding_id: str
    product_id: str
    escalation_paths: tuple  # Tuple of (name, EscalationPath) for immutability
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    registered_by: str = "system"
    immutable: bool = True  # Always True - enforced at runtime
    
    def __post_init__(self):
        """Validate immutability constraint."""
        if not self.immutable:
            # Force immutable to True - cannot be False
            object.__setattr__(self, "immutable", True)
    
    def is_runtime_modifiable(self) -> bool:
        """
        Check if this binding can be modified at runtime.
        
        GOV-HITL-BIND-004: Always returns False.
        
        Returns:
            Always False - HITL bindings are immutable
        """
        return False
    
    def get_path(self, name: str) -> Optional[EscalationPath]:
        """
        Get an escalation path by name.
        
        Args:
            name: Name of the path to retrieve
            
        Returns:
            The EscalationPath if found, None otherwise
        """
        for path_name, path in self.escalation_paths:
            if path_name == name:
                return path
        return None
    
    def get_all_paths(self) -> Dict[str, EscalationPath]:
        """
        Get all escalation paths as a dictionary.
        
        Returns:
            Dictionary mapping path names to EscalationPath objects
        """
        return dict(self.escalation_paths)
    
    def find_matching_paths(self, context: Dict[str, Any]) -> List[EscalationPath]:
        """
        Find all paths that match the given context.
        
        Args:
            context: Dictionary with evaluation context
            
        Returns:
            List of matching EscalationPath objects
        """
        if not self.enabled:
            return []
        return [
            path for _, path in self.escalation_paths
            if path.matches_any_condition(context)
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "binding_id": self.binding_id,
            "product_id": self.product_id,
            "escalation_paths": {
                name: path.to_dict() 
                for name, path in self.escalation_paths
            },
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "registered_by": self.registered_by,
            "immutable": self.immutable,
        }


# ============================================================================
# HITL Binding Modification Attempt Record
# ============================================================================


@dataclass(frozen=True)
class HITLModificationAttempt:
    """
    Record of an attempted modification to HITL binding.
    
    GOV-HITL-BIND-006: All modification attempts are logged.
    
    Attributes:
        attempt_id: Unique identifier
        binding_id: The binding that was targeted
        attempted_operation: What operation was attempted
        source: Source of the attempt (e.g., API, runtime)
        timestamp: When the attempt occurred
        blocked: Whether the attempt was blocked (always True)
        reason: Why the attempt was blocked
    """
    attempt_id: str
    binding_id: str
    attempted_operation: str
    source: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    blocked: bool = True  # Always True
    reason: str = "HITL bindings are immutable at runtime"
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload format."""
        return {
            "attempt_id": self.attempt_id,
            "binding_id": self.binding_id,
            "attempted_operation": self.attempted_operation,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "blocked": self.blocked,
            "reason": self.reason,
        }


# ============================================================================
# HITL Binding Registry
# ============================================================================


class HITLBindingModificationError(Exception):
    """
    Raised when attempting to modify an immutable HITL binding.
    
    GOV-HITL-BIND-007: Runtime modifications raise exception.
    """
    def __init__(
        self,
        binding_id: str,
        operation: str,
        message: str = "HITL bindings cannot be modified at runtime",
    ):
        self.binding_id = binding_id
        self.operation = operation
        super().__init__(f"{message}: binding_id={binding_id}, operation={operation}")


class HITLBindingRegistry:
    """
    Registry for HITL bindings.
    
    GOV-HITL-BIND-005: Bindings are registered at product registration time.
    
    Bindings are immutable once registered. The only allowed operation
    after registration is enable/disable (which creates a new binding).
    """
    
    def __init__(
        self,
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self._bindings: Dict[str, HITLBinding] = {}
        self._modification_attempts: List[HITLModificationAttempt] = []
        self._emit_event = emit_event_fn
    
    def register(
        self,
        binding: HITLBinding,
        *,
        overwrite: bool = False,
    ) -> str:
        """
        Register a HITL binding.
        
        GOV-HITL-BIND-005: Registration is only allowed at product registration time.
        
        Args:
            binding: The binding to register
            overwrite: If True, replace existing binding (for re-registration only)
            
        Returns:
            The binding_id of the registered binding
            
        Raises:
            HITLBindingModificationError: If binding exists and overwrite=False
        """
        if binding.binding_id in self._bindings and not overwrite:
            self._record_modification_attempt(
                binding.binding_id,
                "register",
                "registration",
            )
            raise HITLBindingModificationError(
                binding.binding_id,
                "register",
                "Binding already exists and overwrite=False",
            )
        
        self._bindings[binding.binding_id] = binding
        return binding.binding_id
    
    def get(self, binding_id: str) -> Optional[HITLBinding]:
        """
        Get a binding by ID.
        
        Args:
            binding_id: The binding ID to look up
            
        Returns:
            The HITLBinding if found, None otherwise
        """
        return self._bindings.get(binding_id)
    
    def get_by_product(self, product_id: str) -> List[HITLBinding]:
        """
        Get all bindings for a product.
        
        Args:
            product_id: The product ID to filter by
            
        Returns:
            List of bindings for the product
        """
        return [
            b for b in self._bindings.values()
            if b.product_id == product_id
        ]
    
    def update(
        self,
        binding_id: str,
        **updates: Any,
    ) -> None:
        """
        Attempt to update a binding (always fails).
        
        GOV-HITL-BIND-007: Updates are blocked and logged.
        
        Args:
            binding_id: The binding to update
            **updates: The updates to apply
            
        Raises:
            HITLBindingModificationError: Always - bindings are immutable
        """
        self._record_modification_attempt(binding_id, "update", "runtime_api")
        raise HITLBindingModificationError(binding_id, "update")
    
    def delete(self, binding_id: str) -> None:
        """
        Attempt to delete a binding (always fails).
        
        GOV-HITL-BIND-007: Deletions are blocked and logged.
        
        Args:
            binding_id: The binding to delete
            
        Raises:
            HITLBindingModificationError: Always - bindings are immutable
        """
        self._record_modification_attempt(binding_id, "delete", "runtime_api")
        raise HITLBindingModificationError(binding_id, "delete")
    
    def check_hitl_binding_immutable(self, binding_id: str) -> bool:
        """
        Check if a binding is immutable (always True).
        
        GOV-HITL-BIND-004: All bindings are immutable.
        
        Args:
            binding_id: The binding to check
            
        Returns:
            Always True
        """
        binding = self._bindings.get(binding_id)
        if binding:
            return not binding.is_runtime_modifiable()
        return True
    
    def find_matching_escalations(
        self,
        product_id: str,
        context: Dict[str, Any],
    ) -> List[EscalationPath]:
        """
        Find all matching escalation paths for a context.
        
        Args:
            product_id: The product to search bindings for
            context: The evaluation context
            
        Returns:
            List of matching EscalationPath objects
        """
        result = []
        for binding in self.get_by_product(product_id):
            result.extend(binding.find_matching_paths(context))
        # Sort by priority (critical first)
        priority_order = {
            HITLPriority.CRITICAL: 0,
            HITLPriority.HIGH: 1,
            HITLPriority.MEDIUM: 2,
            HITLPriority.LOW: 3,
        }
        result.sort(key=lambda p: priority_order.get(p.priority, 4))
        return result
    
    def get_modification_attempts(self) -> List[HITLModificationAttempt]:
        """
        Get all recorded modification attempts.
        
        Returns:
            List of HITLModificationAttempt records
        """
        return list(self._modification_attempts)
    
    def _record_modification_attempt(
        self,
        binding_id: str,
        operation: str,
        source: str,
    ) -> None:
        """Record a modification attempt and emit trace event."""
        attempt = HITLModificationAttempt(
            attempt_id=f"hitl-mod-{uuid4().hex[:12]}",
            binding_id=binding_id,
            attempted_operation=operation,
            source=source,
        )
        self._modification_attempts.append(attempt)
        
        if self._emit_event:
            self._emit_event(
                "hitl_binding_modification_blocked",
                attempt.to_trace_payload(),
            )
    
    def count(self) -> int:
        """Get count of registered bindings."""
        return len(self._bindings)
    
    def clear(self) -> None:
        """Clear all bindings (for testing only)."""
        self._bindings.clear()
        self._modification_attempts.clear()


# ============================================================================
# Factory Functions
# ============================================================================


def create_escalation_condition(
    trigger: EscalationTrigger,
    *,
    threshold: Optional[float] = None,
    description: str = "",
) -> EscalationCondition:
    """
    Create an escalation condition.
    
    Args:
        trigger: The trigger type
        threshold: Optional threshold value
        description: Human-readable description
        
    Returns:
        Configured EscalationCondition
    """
    return EscalationCondition(
        trigger=trigger,
        threshold=threshold,
        description=description,
    )


def create_escalation_path(
    name: str,
    conditions: List[EscalationCondition],
    action: EscalationAction,
    *,
    priority: HITLPriority = HITLPriority.MEDIUM,
    notification_targets: Optional[List[str]] = None,
    timeout_seconds: Optional[int] = None,
    require_acknowledgment: bool = True,
) -> EscalationPath:
    """
    Create an escalation path.
    
    Args:
        name: Path name
        conditions: List of trigger conditions
        action: Action to take on escalation
        priority: Priority level
        notification_targets: List of notification targets
        timeout_seconds: Optional timeout
        require_acknowledgment: Whether acknowledgment is required
        
    Returns:
        Configured EscalationPath
    """
    return EscalationPath(
        path_id=f"path-{uuid4().hex[:12]}",
        name=name,
        conditions=tuple(conditions),
        action=action,
        priority=priority,
        notification_targets=tuple(notification_targets or []),
        timeout_seconds=timeout_seconds,
        require_acknowledgment=require_acknowledgment,
    )


def create_hitl_binding(
    product_id: str,
    escalation_paths: Dict[str, EscalationPath],
    *,
    enabled: bool = True,
    registered_by: str = "system",
) -> HITLBinding:
    """
    Create a HITL binding.
    
    Args:
        product_id: The product this binding belongs to
        escalation_paths: Dictionary of path names to paths
        enabled: Whether the binding is active
        registered_by: Who registered the binding
        
    Returns:
        Configured HITLBinding
    """
    return HITLBinding(
        binding_id=f"hitl-{uuid4().hex[:12]}",
        product_id=product_id,
        escalation_paths=tuple(escalation_paths.items()),
        enabled=enabled,
        registered_by=registered_by,
    )


def create_default_hitl_binding(product_id: str) -> HITLBinding:
    """
    Create a default HITL binding with standard escalation paths.
    
    GOV-HITL-DECL-001...005: Default escalation paths.
    
    Args:
        product_id: The product this binding belongs to
        
    Returns:
        HITLBinding with standard escalation paths
    """
    low_confidence_path = create_escalation_path(
        name="low_confidence",
        conditions=[
            create_escalation_condition(
                EscalationTrigger.LOW_CONFIDENCE,
                threshold=0.5,
                description="Confidence below 50%",
            ),
        ],
        action=EscalationAction.PAUSE_AND_WAIT,
        priority=HITLPriority.MEDIUM,
    )
    
    blocking_ambiguity_path = create_escalation_path(
        name="blocking_ambiguity",
        conditions=[
            create_escalation_condition(
                EscalationTrigger.BLOCKING_AMBIGUITY,
                description="Blocking ambiguity detected",
            ),
        ],
        action=EscalationAction.PAUSE_AND_WAIT,
        priority=HITLPriority.HIGH,
    )
    
    security_violation_path = create_escalation_path(
        name="security_violation",
        conditions=[
            create_escalation_condition(
                EscalationTrigger.SECURITY_VIOLATION,
                description="Security violation detected",
            ),
        ],
        action=EscalationAction.EMERGENCY_STOP,
        priority=HITLPriority.CRITICAL,
    )
    
    return create_hitl_binding(
        product_id=product_id,
        escalation_paths={
            "low_confidence": low_confidence_path,
            "blocking_ambiguity": blocking_ambiguity_path,
            "security_violation": security_violation_path,
        },
    )
