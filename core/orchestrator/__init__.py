"""
Orchestrator Package

This package contains the core orchestration engine and supporting modules.

Public API:
- OrchestratorEngine: Main entry point for flow execution
- Normalization functions: Core semantic normalization

Internal modules (not for external use):
- run_lifecycle: Run lifecycle management
- user_input_handler: User input handling
- plan_executor: Plan execution
- loop_executor: Loop execution
- step_executor: Step dispatch
- hitl: Human-in-the-loop service
- context: Run/Step context
- flow_loader: Flow definition loading
- branching: Branch condition evaluation
- looping: Loop condition evaluation
- templating: Parameter templating
- state: Run state helpers
- error_policy: Error handling policies

Usage:
    from core.orchestrator.engine import OrchestratorEngine
    from core.orchestrator.normalization import apply_core_normalization
"""

# Lazy import to avoid circular imports
def __getattr__(name: str):
    if name == "OrchestratorEngine":
        from core.orchestrator.engine import OrchestratorEngine
        return OrchestratorEngine
    
    # Normalization functions
    if name in (
        "normalize_whitespace",
        "deduplicate_entities", 
        "merge_constraints",
        "apply_stable_ordering",
        "coerce_types",
        "apply_core_normalization",
    ):
        from core.orchestrator import normalization
        return getattr(normalization, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "OrchestratorEngine",
    # Normalization (ORC-SEM-030...034)
    "normalize_whitespace",
    "deduplicate_entities",
    "merge_constraints",
    "apply_stable_ordering",
    "coerce_types",
    "apply_core_normalization",
]
