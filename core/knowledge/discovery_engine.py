"""
Discovery Engine for Tools and Agents.

INT-DISC-001...010: Provides intent-filtered discovery of tools and agents
using capability tags and semantic matching.

IMP-039 (INT-DISC-055...073): Separate discover() and select() phases with
product domain scoping and deterministic selection.

This module provides:
- DiscoveryEngine: Main discovery orchestrator
- ToolCandidate/AgentCandidate: Discovery result dataclasses
- DiscoveryStrategy: Strategy pattern for extensible discovery
- Capability matching via tag-based scoring
- DiscoveryResult/SelectionResult: Phase-separated results (IMP-039)
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from core.orchestrator.context import RunContext
    from core.contracts.descriptors_schema import AgentDescriptor, ToolDescriptor


# ============================================================================
# Candidate Dataclasses (INT-DISC-001...004)
# ============================================================================


@dataclass(frozen=True)
class ToolCandidate:
    """
    A tool discovered as potentially suitable for an intent.
    
    INT-DISC-001: Candidates include name, confidence, and match reason.
    """
    
    name: str
    confidence: float
    match_reason: str
    capabilities: List[str] = field(default_factory=list)
    domain_tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentCandidate:
    """
    An agent discovered as potentially suitable for an intent.
    
    INT-DISC-002: Candidates include name, confidence, and match reason.
    """
    
    name: str
    confidence: float
    match_reason: str
    capabilities: List[str] = field(default_factory=list)
    domain_tags: List[str] = field(default_factory=list)
    reasoning_type: str = "unknown"


# ============================================================================
# IMP-039: Discovery and Selection Result Types
# ============================================================================


def _compute_discovery_hash(
    intent: str,
    candidates: List[ToolCandidate] | List[AgentCandidate],
    domain_tags: Optional[List[str]] = None,
) -> str:
    """
    Compute deterministic hash for discovery results.
    
    INT-DISC-061: Discovery produces deterministic hash.
    
    Args:
        intent: Original intent string
        candidates: List of discovered candidates
        domain_tags: Optional domain filter used
        
    Returns:
        SHA-256 hash of discovery inputs and outputs
    """
    hash_input = f"intent:{intent}|"
    if domain_tags:
        hash_input += f"domains:{','.join(sorted(domain_tags))}|"
    hash_input += "candidates:" + ",".join(c.name for c in candidates)
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class DiscoveryResult:
    """
    Result of discovery phase (IMP-039: INT-DISC-055...060).
    
    Discovery phase identifies all matching candidates without selection.
    """
    
    intent: str
    candidates: List[ToolCandidate] | List[AgentCandidate]
    discovery_hash: str
    product_domain: Optional[str] = None
    domain_tags_used: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def candidate_count(self) -> int:
        """Number of candidates discovered."""
        return len(self.candidates)
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "intent": self.intent,
            "candidate_count": self.candidate_count,
            "discovery_hash": self.discovery_hash,
            "product_domain": self.product_domain,
            "domain_tags_used": self.domain_tags_used,
            "candidates": [c.name for c in self.candidates[:10]],
            "discovered_at": self.discovered_at.isoformat(),
        }


@dataclass(frozen=True)
class SelectionResult:
    """
    Result of selection phase (IMP-039: INT-DISC-065...073).
    
    Selection phase picks the best candidate from discovery results.
    """
    
    selected_candidate: Optional[ToolCandidate] | Optional[AgentCandidate]
    discovery_hash: str
    selection_reason: str
    alternatives_considered: List[str] = field(default_factory=list)
    confidence: float = 0.0
    selected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def has_selection(self) -> bool:
        """Check if a candidate was selected."""
        return self.selected_candidate is not None
    
    @property
    def selected_name(self) -> Optional[str]:
        """Get name of selected candidate."""
        if self.selected_candidate:
            return self.selected_candidate.name
        return None
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "selected_name": self.selected_name,
            "discovery_hash": self.discovery_hash,
            "selection_reason": self.selection_reason,
            "alternatives_count": len(self.alternatives_considered),
            "alternatives": self.alternatives_considered[:5],
            "confidence": self.confidence,
            "selected_at": self.selected_at.isoformat(),
        }


# ============================================================================
# Capability Matching (INT-DISC-005...010)
# ============================================================================


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words for matching."""
    import re
    # Split on non-alphanumeric characters including underscores and hyphens
    words = re.split(r'[^a-zA-Z0-9]+', text.lower())
    return [w for w in words if w]  # Filter out empty strings


def _compute_tag_overlap(intent_tokens: List[str], tags: List[str]) -> float:
    """
    Compute overlap between intent tokens and capability tags.
    
    INT-DISC-005: Capability matching produces confidence scores.
    """
    if not tags:
        return 0.0
    
    tag_tokens = set()
    for tag in tags:
        tag_tokens.update(_tokenize(tag))
    
    if not tag_tokens:
        return 0.0
    
    intent_set = set(intent_tokens)
    overlap = intent_set & tag_tokens
    
    # Jaccard-like score: overlap / union
    union_size = len(intent_set | tag_tokens)
    if union_size == 0:
        return 0.0
    
    return len(overlap) / union_size


def match_capabilities(
    intent: str,
    capabilities: List[str],
    domain_tags: Optional[List[str]] = None,
) -> float:
    """
    Compute capability match score for intent against tags.
    
    INT-DISC-006: Returns confidence score 0.0-1.0.
    
    Args:
        intent: Natural language intent string
        capabilities: List of capability tags
        domain_tags: Optional domain scoping tags
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    intent_tokens = _tokenize(intent)
    if not intent_tokens:
        return 0.0
    
    # Combine capabilities and domain tags for matching
    all_tags = list(capabilities)
    if domain_tags:
        all_tags.extend(domain_tags)
    
    return _compute_tag_overlap(intent_tokens, all_tags)


# ============================================================================
# Discovery Strategy Pattern (INT-DISC-011...018)
# ============================================================================


class DiscoveryStrategy(ABC):
    """
    Abstract base class for discovery strategies.
    
    INT-DISC-011: Extensible discovery via strategy pattern.
    """
    
    @abstractmethod
    def discover_tools(
        self,
        intent: str,
        descriptors: List["ToolDescriptor"],
        context: Optional["RunContext"] = None,
    ) -> List[ToolCandidate]:
        """Discover tools matching intent from given descriptors."""
        ...
    
    @abstractmethod
    def discover_agents(
        self,
        intent: str,
        descriptors: List["AgentDescriptor"],
        context: Optional["RunContext"] = None,
    ) -> List[AgentCandidate]:
        """Discover agents matching intent from given descriptors."""
        ...


class DefaultDiscoveryStrategy(DiscoveryStrategy):
    """
    Default discovery strategy using capability tag matching.
    
    INT-DISC-012: Default implementation using tag-based matching.
    """
    
    def __init__(self, min_confidence: float = 0.0) -> None:
        self._min_confidence = min_confidence
    
    def discover_tools(
        self,
        intent: str,
        descriptors: List["ToolDescriptor"],
        context: Optional["RunContext"] = None,
    ) -> List[ToolCandidate]:
        """Discover tools using capability tag matching."""
        candidates: List[ToolCandidate] = []
        
        for descriptor in descriptors:
            confidence = match_capabilities(
                intent,
                descriptor.capabilities,
                descriptor.domain_tags,
            )
            
            if confidence < self._min_confidence:
                continue
            
            matched_caps = [
                c for c in descriptor.capabilities
                if any(t in c.lower() for t in _tokenize(intent))
            ]
            match_reason = f"Matched capabilities: {matched_caps}" if matched_caps else "Partial match"
            
            candidates.append(ToolCandidate(
                name=descriptor.name,
                confidence=confidence,
                match_reason=match_reason,
                capabilities=list(descriptor.capabilities),
                domain_tags=list(descriptor.domain_tags),
            ))
        
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates
    
    def discover_agents(
        self,
        intent: str,
        descriptors: List["AgentDescriptor"],
        context: Optional["RunContext"] = None,
    ) -> List[AgentCandidate]:
        """Discover agents using capability tag matching."""
        candidates: List[AgentCandidate] = []
        
        for descriptor in descriptors:
            confidence = match_capabilities(
                intent,
                descriptor.capabilities,
                descriptor.domain_tags,
            )
            
            if confidence < self._min_confidence:
                continue
            
            matched_caps = [
                c for c in descriptor.capabilities
                if any(t in c.lower() for t in _tokenize(intent))
            ]
            match_reason = f"Matched capabilities: {matched_caps}" if matched_caps else "Partial match"
            
            candidates.append(AgentCandidate(
                name=descriptor.name,
                confidence=confidence,
                match_reason=match_reason,
                capabilities=list(descriptor.capabilities),
                domain_tags=list(descriptor.domain_tags),
                reasoning_type=descriptor.reasoning_type.value,
            ))
        
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates


# Registry for custom strategies
_strategy_registry: Dict[str, DiscoveryStrategy] = {
    "default": DefaultDiscoveryStrategy(),
}


def register_discovery_strategy(name: str, strategy: DiscoveryStrategy) -> None:
    """
    INT-DISC-013: Register a custom discovery strategy.
    
    Args:
        name: Unique name for the strategy
        strategy: Strategy instance
    """
    _strategy_registry[name] = strategy


def get_discovery_strategy(name: str = "default") -> DiscoveryStrategy:
    """
    INT-DISC-014: Get a registered discovery strategy.
    
    Args:
        name: Strategy name (default: "default")
        
    Returns:
        Registered strategy instance
        
    Raises:
        KeyError: If strategy not found
    """
    if name not in _strategy_registry:
        raise KeyError(f"Unknown discovery strategy: {name}")
    return _strategy_registry[name]


# ============================================================================
# Discovery Engine (INT-DISC-007...010)
# ============================================================================


class DiscoveryEngine:
    """
    Engine for discovering suitable tools and agents based on intent.
    
    INT-DISC-007: Main discovery orchestrator.
    INT-DISC-008: Uses capability tags for discovery.
    INT-DISC-009: Returns ranked candidates.
    INT-DISC-010: Emits discovery trace events.
    """
    
    def __init__(
        self,
        *,
        emit_event_fn: Optional[Callable[..., None]] = None,
        min_confidence: float = 0.0,
    ) -> None:
        """
        Initialize discovery engine.
        
        Args:
            emit_event_fn: Optional function to emit trace events
            min_confidence: Minimum confidence threshold for candidates
        """
        self._emit_event_fn = emit_event_fn
        self._min_confidence = min_confidence
    
    def discover_tools(
        self,
        intent: str,
        context: Optional["RunContext"] = None,
        *,
        domain_filter: Optional[List[str]] = None,
    ) -> List[ToolCandidate]:
        """
        Discover tools matching an intent.
        
        INT-DISC-019...028: Intent-filtered tool discovery.
        
        Args:
            intent: Natural language description of desired capability
            context: Optional run context for scoping
            domain_filter: Optional domain tags to filter by
            
        Returns:
            List of ToolCandidate sorted by confidence descending
        """
        from core.tools.registry import ToolRegistry
        
        # INT-DISC-019: Emit discovery started event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="tool_discovery_started",
                payload={"intent": intent, "domain_filter": domain_filter},
            )
        
        candidates: List[ToolCandidate] = []
        
        for descriptor in ToolRegistry.list_descriptors():
            # INT-DISC-020: Apply domain filter if specified
            if domain_filter:
                if not any(dt in descriptor.domain_tags for dt in domain_filter):
                    continue
            
            # INT-DISC-021: Compute capability match
            confidence = match_capabilities(
                intent,
                descriptor.capabilities,
                descriptor.domain_tags,
            )
            
            # INT-DISC-022: Filter by minimum confidence
            if confidence < self._min_confidence:
                continue
            
            # INT-DISC-023: Build match reason
            matched_caps = [
                c for c in descriptor.capabilities
                if any(t in c.lower() for t in _tokenize(intent))
            ]
            match_reason = f"Matched capabilities: {matched_caps}" if matched_caps else "Partial match"
            
            candidates.append(ToolCandidate(
                name=descriptor.name,
                confidence=confidence,
                match_reason=match_reason,
                capabilities=list(descriptor.capabilities),
                domain_tags=list(descriptor.domain_tags),
            ))
        
        # INT-DISC-024: Sort by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        
        # INT-DISC-025: Emit discovery completed event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="tool_discovery_completed",
                payload={
                    "intent": intent,
                    "candidate_count": len(candidates),
                    "candidates": [c.name for c in candidates[:10]],  # Top 10
                },
            )
        
        return candidates
    
    def discover_agents(
        self,
        intent: str,
        context: Optional["RunContext"] = None,
        *,
        domain_filter: Optional[List[str]] = None,
        reasoning_type_filter: Optional[str] = None,
    ) -> List[AgentCandidate]:
        """
        Discover agents matching an intent.
        
        INT-DISC-038...045: Intent-filtered agent discovery.
        
        Args:
            intent: Natural language description of desired capability
            context: Optional run context for scoping
            domain_filter: Optional domain tags to filter by
            reasoning_type_filter: Optional reasoning type to filter by
            
        Returns:
            List of AgentCandidate sorted by confidence descending
        """
        from core.agents.registry import AgentRegistry
        
        # INT-DISC-038: Emit discovery started event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="agent_discovery_started",
                payload={
                    "intent": intent,
                    "domain_filter": domain_filter,
                    "reasoning_type_filter": reasoning_type_filter,
                },
            )
        
        candidates: List[AgentCandidate] = []
        
        for descriptor in AgentRegistry.list_descriptors():
            # INT-DISC-039: Apply domain filter if specified
            if domain_filter:
                if not any(dt in descriptor.domain_tags for dt in domain_filter):
                    continue
            
            # INT-DISC-040: Apply reasoning type filter if specified
            if reasoning_type_filter:
                if descriptor.reasoning_type.value != reasoning_type_filter:
                    continue
            
            # INT-DISC-041: Compute capability match
            confidence = match_capabilities(
                intent,
                descriptor.capabilities,
                descriptor.domain_tags,
            )
            
            # INT-DISC-042: Filter by minimum confidence
            if confidence < self._min_confidence:
                continue
            
            # INT-DISC-043: Build match reason
            matched_caps = [
                c for c in descriptor.capabilities
                if any(t in c.lower() for t in _tokenize(intent))
            ]
            match_reason = f"Matched capabilities: {matched_caps}" if matched_caps else "Partial match"
            
            candidates.append(AgentCandidate(
                name=descriptor.name,
                confidence=confidence,
                match_reason=match_reason,
                capabilities=list(descriptor.capabilities),
                domain_tags=list(descriptor.domain_tags),
                reasoning_type=descriptor.reasoning_type.value,
            ))
        
        # INT-DISC-044: Sort by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        
        # INT-DISC-045: Emit discovery completed event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="agent_discovery_completed",
                payload={
                    "intent": intent,
                    "candidate_count": len(candidates),
                    "candidates": [c.name for c in candidates[:10]],  # Top 10
                },
            )
        
        return candidates

    # ========================================================================
    # IMP-039: Separated Discovery and Selection Phases
    # ========================================================================
    
    def discover(
        self,
        intent: str,
        *,
        product_domain: Optional[str] = None,
        domain_tags: Optional[List[str]] = None,
        candidate_type: str = "tool",
    ) -> DiscoveryResult:
        """
        Discovery phase: Find all matching candidates (IMP-039: INT-DISC-055...060).
        
        This is the first phase of the two-phase discovery process.
        It identifies all candidates without making a selection.
        
        Args:
            intent: Natural language description of desired capability
            product_domain: Optional product domain for scoping
            domain_tags: Optional domain tags to filter by
            candidate_type: "tool" or "agent"
            
        Returns:
            DiscoveryResult with all matching candidates and hash
        """
        # INT-DISC-055: Emit discovery phase started event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="discovery_phase_started",
                payload={
                    "intent": intent,
                    "product_domain": product_domain,
                    "domain_tags": domain_tags,
                    "candidate_type": candidate_type,
                },
            )
        
        # INT-DISC-056: Compute domain filter from product + explicit tags
        effective_domain_tags = list(domain_tags or [])
        if product_domain and product_domain not in effective_domain_tags:
            effective_domain_tags.append(product_domain)
        
        # INT-DISC-057: Perform discovery based on candidate type
        if candidate_type == "agent":
            candidates = self.discover_agents(
                intent,
                domain_filter=effective_domain_tags if effective_domain_tags else None,
            )
        else:
            candidates = self.discover_tools(
                intent,
                domain_filter=effective_domain_tags if effective_domain_tags else None,
            )
        
        # INT-DISC-058: Compute deterministic discovery hash
        discovery_hash = _compute_discovery_hash(intent, candidates, effective_domain_tags)
        
        result = DiscoveryResult(
            intent=intent,
            candidates=candidates,
            discovery_hash=discovery_hash,
            product_domain=product_domain,
            domain_tags_used=effective_domain_tags,
        )
        
        # INT-DISC-059: Emit discovery phase completed event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="discovery_phase_completed",
                payload=result.to_trace_payload(),
            )
        
        return result
    
    def select(
        self,
        discovery_result: DiscoveryResult,
        *,
        min_confidence: Optional[float] = None,
        max_candidates: int = 1,
    ) -> SelectionResult:
        """
        Selection phase: Pick the best candidate(s) (IMP-039: INT-DISC-065...073).
        
        This is the second phase of the two-phase discovery process.
        It selects the best candidate(s) from discovery results.
        
        Args:
            discovery_result: Result from discover() phase
            min_confidence: Override minimum confidence threshold
            max_candidates: Maximum candidates to select (default: 1)
            
        Returns:
            SelectionResult with selected candidate(s)
        """
        threshold = min_confidence if min_confidence is not None else self._min_confidence
        
        # INT-DISC-065: Emit selection phase started event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="selection_phase_started",
                payload={
                    "discovery_hash": discovery_result.discovery_hash,
                    "candidate_count": discovery_result.candidate_count,
                    "min_confidence": threshold,
                },
            )
        
        # INT-DISC-066: Filter by confidence threshold
        eligible_candidates = [
            c for c in discovery_result.candidates
            if c.confidence >= threshold
        ]
        
        if not eligible_candidates:
            # INT-DISC-067: No eligible candidates
            result = SelectionResult(
                selected_candidate=None,
                discovery_hash=discovery_result.discovery_hash,
                selection_reason=f"No candidates met confidence threshold {threshold}",
                alternatives_considered=[c.name for c in discovery_result.candidates],
                confidence=0.0,
            )
        else:
            # INT-DISC-068: Select top candidate (already sorted by confidence)
            selected = eligible_candidates[0]
            alternatives = [c.name for c in eligible_candidates[1:max_candidates+5]]
            
            result = SelectionResult(
                selected_candidate=selected,
                discovery_hash=discovery_result.discovery_hash,
                selection_reason=f"Highest confidence match: {selected.match_reason}",
                alternatives_considered=alternatives,
                confidence=selected.confidence,
            )
        
        # INT-DISC-069: Emit selection phase completed event
        if self._emit_event_fn:
            self._emit_event_fn(
                kind="selection_phase_completed",
                payload=result.to_trace_payload(),
            )
        
        return result
    
    def discover_and_select(
        self,
        intent: str,
        *,
        product_domain: Optional[str] = None,
        domain_tags: Optional[List[str]] = None,
        candidate_type: str = "tool",
        min_confidence: Optional[float] = None,
    ) -> SelectionResult:
        """
        Combined discover and select for convenience (IMP-039: INT-DISC-070...073).
        
        This is a convenience method that performs both phases.
        
        Args:
            intent: Natural language description of desired capability
            product_domain: Optional product domain for scoping
            domain_tags: Optional domain tags to filter by
            candidate_type: "tool" or "agent"
            min_confidence: Override minimum confidence threshold
            
        Returns:
            SelectionResult with selected candidate
        """
        # INT-DISC-070: Perform discovery phase
        discovery_result = self.discover(
            intent,
            product_domain=product_domain,
            domain_tags=domain_tags,
            candidate_type=candidate_type,
        )
        
        # INT-DISC-071: Perform selection phase
        selection_result = self.select(
            discovery_result,
            min_confidence=min_confidence,
        )
        
        return selection_result


# ============================================================================
# Eligibility Checking (INT-DISC-029...037)
# ============================================================================


@dataclass(frozen=True)
class EligibilityResult:
    """
    Result of eligibility check for a candidate.
    
    INT-DISC-029: Eligibility result with eligible flag and reasons.
    """
    
    eligible: bool
    reasons: List[str] = field(default_factory=list)


class EligibilityChecker:
    """
    Checks eligibility of candidates based on budget, confidence, and context.
    
    INT-DISC-030: Eligibility checker for discovery filtering.
    """
    
    def __init__(
        self,
        *,
        emit_event_fn: Optional[Callable[..., None]] = None,
    ) -> None:
        self._emit_event_fn = emit_event_fn
    
    def check_budget_eligibility(
        self,
        candidate: ToolCandidate,
        budget: Any,
        budget_state: Any,
    ) -> bool:
        """
        INT-DISC-031: Check if candidate is affordable given budget.
        
        Args:
            candidate: Tool candidate to check
            budget: Budget limits
            budget_state: Current budget state
            
        Returns:
            True if candidate can be afforded
        """
        from core.governance.budgeting import can_afford_tool
        
        return can_afford_tool(candidate.name, budget, budget_state)
    
    def check_confidence_eligibility(
        self,
        candidate: ToolCandidate | AgentCandidate,
        min_confidence: float,
    ) -> bool:
        """
        INT-DISC-032: Check if candidate meets confidence threshold.
        
        Args:
            candidate: Candidate to check
            min_confidence: Minimum required confidence
            
        Returns:
            True if candidate meets threshold
        """
        return candidate.confidence >= min_confidence
    
    def check_context_eligibility(
        self,
        candidate: ToolCandidate | AgentCandidate,
        context: Optional["RunContext"] = None,
    ) -> bool:
        """
        INT-DISC-033: Check if candidate is eligible given run context.
        
        Args:
            candidate: Candidate to check
            context: Run context for scoping
            
        Returns:
            True if candidate is eligible in context
        """
        if context is None:
            return True
        
        # Check domain scoping if context has product info
        product = getattr(context, "product", None)
        if product and candidate.domain_tags:
            # If candidate has domain tags, it should match the product
            if product.lower() not in [t.lower() for t in candidate.domain_tags]:
                # Allow if "general" or no domain restriction
                if "general" not in [t.lower() for t in candidate.domain_tags]:
                    return False
        
        return True
    
    def check_eligibility(
        self,
        candidate: ToolCandidate | AgentCandidate,
        context: Optional["RunContext"] = None,
        *,
        budget: Optional[Any] = None,
        budget_state: Optional[Any] = None,
        min_confidence: float = 0.0,
    ) -> EligibilityResult:
        """
        INT-DISC-034: Composite eligibility check.
        
        Args:
            candidate: Candidate to check
            context: Optional run context
            budget: Optional budget limits
            budget_state: Optional budget state
            min_confidence: Minimum confidence threshold
            
        Returns:
            EligibilityResult with eligible flag and reasons
        """
        reasons: List[str] = []
        
        # Confidence check
        if not self.check_confidence_eligibility(candidate, min_confidence):
            reasons.append(f"Confidence {candidate.confidence:.2f} below threshold {min_confidence:.2f}")
        
        # Context check
        if not self.check_context_eligibility(candidate, context):
            reasons.append("Context eligibility failed (domain mismatch)")
        
        # Budget check (only for tools)
        if isinstance(candidate, ToolCandidate) and budget and budget_state:
            if not self.check_budget_eligibility(candidate, budget, budget_state):
                reasons.append("Budget insufficient for tool call")
        
        eligible = len(reasons) == 0
        
        # INT-DISC-035: Emit exclusion event for ineligible candidates
        if not eligible and self._emit_event_fn:
            self._emit_event_fn(
                kind="candidate_excluded",
                payload={
                    "candidate_name": candidate.name,
                    "candidate_type": "tool" if isinstance(candidate, ToolCandidate) else "agent",
                    "exclusion_reasons": reasons,
                },
            )
        
        return EligibilityResult(eligible=eligible, reasons=reasons)
    
    def filter_eligible(
        self,
        candidates: List[ToolCandidate] | List[AgentCandidate],
        context: Optional["RunContext"] = None,
        *,
        budget: Optional[Any] = None,
        budget_state: Optional[Any] = None,
        min_confidence: float = 0.0,
    ) -> List[ToolCandidate] | List[AgentCandidate]:
        """
        INT-DISC-036: Filter candidates by eligibility.
        
        Args:
            candidates: List of candidates to filter
            context: Optional run context
            budget: Optional budget limits
            budget_state: Optional budget state
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered list of eligible candidates
        """
        eligible_candidates = []
        
        for candidate in candidates:
            result = self.check_eligibility(
                candidate,
                context,
                budget=budget,
                budget_state=budget_state,
                min_confidence=min_confidence,
            )
            if result.eligible:
                eligible_candidates.append(candidate)
        
        return eligible_candidates
