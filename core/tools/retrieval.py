from __future__ import annotations

# ==============================
# Approved Retrieval Tool
# ==============================
"""
Read-only retrieval tool restricted to approved sources.

Supports:
- query_prior_runs: Search previous run records for evidence
- query_approved_sources: Search approved knowledge sources
- Full provenance tracking for all retrieved evidence
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from core.config.schema import Settings
from core.contracts.context_pack_schema import EvidenceItem, EvidenceSource
from core.contracts.retrieval_schema import RetrievalQuery, RetrievalResult, Citation
from core.contracts.run_schema import ArtifactRef
from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.governance.gates import resolve_allowed_sources
from core.memory.router import MemoryRouter
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry
from core.contracts.descriptors_schema import ToolDescriptor


# ============================================================================
# Retrieval Policy Types
# ============================================================================


class RetrievalPolicy:
    """Policy for controlling retrieval source access."""
    
    def __init__(
        self,
        *,
        allowed_sources: Optional[List[str]] = None,
        blocked_sources: Optional[List[str]] = None,
    ) -> None:
        self.allowed_sources = allowed_sources or []
        self.blocked_sources = blocked_sources or []
    
    def is_allowed(self, source: str) -> bool:
        """Check if a source is allowed by this policy."""
        if source in self.blocked_sources:
            return False
        if not self.allowed_sources:
            return True  # Empty allowed = allow all not blocked
        return source in self.allowed_sources
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "RetrievalPolicy":
        """Create policy from config dict."""
        return cls(
            allowed_sources=config.get("allowed_sources"),
            blocked_sources=config.get("blocked_sources"),
        )


# ============================================================================
# Query Functions
# ============================================================================


def query_prior_runs(
    *,
    memory: MemoryRouter,
    product: str,
    flow: str,
    query: str,
    top_k: int = 5,
    time_range: Optional[Any] = None,
    policy: Optional[RetrievalPolicy] = None,
) -> List[EvidenceItem]:
    """
    Query prior run records for evidence.
    
    Searches run input/output/summary for matching content.
    Returns EvidenceItems with full provenance.
    
    Args:
        memory: Memory router for run access
        product: Product name
        flow: Flow name  
        query: Search query
        top_k: Maximum results to return
        time_range: Optional time range filter
        policy: Optional retrieval policy
        
    Returns:
        List of EvidenceItems with provenance
    """
    source_type = "runs:current_product"
    if policy and not policy.is_allowed(source_type):
        return []
    
    retrieval_query = RetrievalQuery(
        query=query,
        top_k=top_k,
        sources_requested=["run_records"],
        product=product,
        flow=flow,
        time_range=time_range,
    )
    
    hits = _search_runs(memory, product, flow, retrieval_query)
    hits.sort(key=lambda hit: (-hit.score, hit.timestamp or 0, hit.id_key))
    hits = hits[:top_k]
    
    return _hits_to_evidence(hits, "query_prior_runs")


def query_approved_sources(
    *,
    memory: MemoryRouter,
    product: str,
    flow: str,
    query: str,
    top_k: int = 5,
    sources: Optional[List[str]] = None,
    policy: Optional[RetrievalPolicy] = None,
) -> List[EvidenceItem]:
    """
    Query approved knowledge sources for evidence.
    
    Searches trace events and approved knowledge bases.
    Returns EvidenceItems with full provenance.
    
    Args:
        memory: Memory router
        product: Product name
        flow: Flow name
        query: Search query
        top_k: Maximum results
        sources: Specific sources to query
        policy: Optional retrieval policy
        
    Returns:
        List of EvidenceItems with provenance
    """
    requested = sources or ["trace_events"]
    
    # Filter by policy
    if policy:
        requested = [s for s in requested if policy.is_allowed(s)]
    
    if not requested:
        return []
    
    retrieval_query = RetrievalQuery(
        query=query,
        top_k=top_k,
        sources_requested=requested,
        product=product,
        flow=flow,
    )
    
    hits: List[_Hit] = []
    if "trace_events" in requested:
        hits.extend(_search_traces(memory, product, flow, retrieval_query))
    
    hits.sort(key=lambda hit: (-hit.score, hit.timestamp or 0, hit.id_key))
    hits = hits[:top_k]
    
    return _hits_to_evidence(hits, "query_approved_sources")


def _hits_to_evidence(hits: List["_Hit"], tool_name: str) -> List[EvidenceItem]:
    """Convert hits to EvidenceItems with full provenance."""
    if not hits:
        return []
    
    max_score = max((hit.score for hit in hits), default=1)
    evidence: List[EvidenceItem] = []
    
    for idx, hit in enumerate(hits):
        evidence_id = _stable_evidence_id(hit, idx)
        snippet = _bounded_snippet(hit.text)
        artifact_ref = ArtifactRef(
            key=f"retrieval.{evidence_id}",
            kind="text",
            uri=f"memory://retrieval/{evidence_id}",
        )
        
        confidence = min(1.0, hit.score / max_score) if max_score else 0.5
        evidence_item = EvidenceItem(
            id=evidence_id,
            type="text",
            source=EvidenceSource(tool=tool_name, uri=artifact_ref.uri, ref=artifact_ref.key),
            timestamp=_timestamp_from_hit(hit),
            confidence=confidence,
            content_ref=artifact_ref,
            summary=snippet,
            provenance={
                "source_type": hit.source_type,
                "run_id": hit.run_id,
                "step_id": hit.step_id,
                "locator": hit.locator,
                "query_tool": tool_name,
            },
        )
        evidence.append(evidence_item)
    
    return evidence


# ============================================================================
# ApprovedRetrievalTool
# ============================================================================


class ApprovedRetrievalTool(BaseTool):
    name = "approved_retrieval"

    def __init__(self, *, memory: MemoryRouter, settings: Settings) -> None:
        super().__init__(config=None)
        self._memory = memory
        self._settings = settings

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        query = RetrievalQuery.model_validate(params)
        product = query.product or ctx.run.product
        flow = query.flow or ctx.run.flow

        allowed_sources = resolve_allowed_sources(self._settings, product=product, flow=flow)
        requested = query.sources_requested or allowed_sources
        denied = _deny_sources(requested, allowed_sources)
        ctx.emit(
            "retrieval_policy_applied",
            {"allowed_sources": allowed_sources, "denied_sources": denied},
        )
        if denied:
            return _deny_result(denied)

        supported = [src for src in requested if _is_supported_source(src)]
        if len(supported) != len(requested):
            unsupported = [src for src in requested if src not in supported]
            return _deny_result(unsupported)

        hits: List[_Hit] = []
        if "run_records" in supported:
            hits.extend(_search_runs(self._memory, product, flow, query))
        if "trace_events" in supported:
            hits.extend(_search_traces(self._memory, product, flow, query))

        hits.sort(key=lambda hit: (-hit.score, hit.timestamp or 0, hit.id_key))
        hits = hits[: query.top_k]

        max_score = max((hit.score for hit in hits), default=1)
        evidence: List[EvidenceItem] = []
        citations: List[Citation] = []
        artifacts: Dict[str, ArtifactRef] = {}

        for idx, hit in enumerate(hits):
            evidence_id = _stable_evidence_id(hit, idx)
            snippet = _bounded_snippet(hit.text)
            artifact_key = f"retrieval.snippet.{evidence_id}"
            artifact_ref = ArtifactRef(key=artifact_key, kind="text", uri=f"memory://{artifact_key}")
            ctx.run.artifacts[artifact_key] = {"snippet": snippet, "locator": hit.locator, "source_type": hit.source_type}
            artifacts[artifact_key] = artifact_ref

            confidence = min(1.0, hit.score / max_score) if max_score else 0.5
            evidence_item = EvidenceItem(
                id=evidence_id,
                type="text",
                source=EvidenceSource(tool=self.name, uri=artifact_ref.uri, ref=artifact_ref.key),
                timestamp=_timestamp_from_hit(hit),
                confidence=confidence,
                content_ref=artifact_ref,
                summary=snippet,
                provenance={
                    "source_type": hit.source_type,
                    "run_id": hit.run_id,
                    "step_id": hit.step_id,
                    "locator": hit.locator,
                },
            )
            evidence.append(evidence_item)
            citations.append(
                Citation(
                    citation_id=evidence_id,
                    source_type=hit.source_type,
                    run_id=hit.run_id,
                    step_id=hit.step_id,
                    artifact_ref=artifact_ref,
                    timestamp=_timestamp_from_hit(hit),
                    locator=hit.locator,
                    snippet_summary=snippet,
                )
            )

        result_payload = RetrievalResult(evidence=evidence, citations=citations).model_dump(mode="json")
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data=result_payload, error=None, meta=meta, evidence=evidence, artifacts=artifacts or None)


def register_retrieval_tool(*, memory: MemoryRouter, settings: Settings, overwrite: bool = False) -> None:
    ToolRegistry.register(
        ApprovedRetrievalTool.name,
        lambda: ApprovedRetrievalTool(memory=memory, settings=settings),
        descriptor=ToolDescriptor(
            name=ApprovedRetrievalTool.name,
            description="Approved retrieval from internal evidence sources.",
            tags=["retrieval", "read_only"],
            input_schema_ref="RetrievalQuery",
            output_schema_ref="RetrievalResult",
            read_only=True,
            side_effect=False,
            sensitivity_class="LOW",
            cost_hint="LOW",
        ),
        overwrite=overwrite,
    )


class _Hit:
    def __init__(
        self,
        *,
        source_type: str,
        text: str,
        score: int,
        run_id: Optional[str],
        step_id: Optional[str],
        timestamp: Optional[int],
        locator: Dict[str, Any],
        id_key: str,
    ) -> None:
        self.source_type = source_type
        self.text = text
        self.score = score
        self.run_id = run_id
        self.step_id = step_id
        self.timestamp = timestamp
        self.locator = locator
        self.id_key = id_key


def _deny_sources(requested: List[str], allowed: List[str]) -> List[str]:
    return [src for src in requested if src not in allowed]


def _is_supported_source(source: str) -> bool:
    return source in {"run_records", "trace_events"}


def _deny_result(denied: List[str]) -> ToolResult:
    err = ToolError(
        code=ToolErrorCode.PERMISSION_DENIED,
        message="retrieval sources not allowed",
        details={"denied_sources": denied},
    )
    meta = ToolMeta(tool_name="approved_retrieval", backend="local")
    return ToolResult(ok=False, data=None, error=err, meta=meta)


def _search_runs(memory: MemoryRouter, product: str, flow: str, query: RetrievalQuery) -> List[_Hit]:
    hits: List[_Hit] = []
    for run in memory.list_runs(limit=1000, offset=0):
        if run.product != product or run.flow != flow:
            continue
        if not _within_range(run.started_at, query.time_range):
            continue
        text = _serialize_payload({"input": run.input, "output": run.output, "summary": run.summary})
        score = _score_text(text, query.query)
        if score <= 0:
            continue
        hits.append(
            _Hit(
                source_type="run_record",
                text=text,
                score=score,
                run_id=run.run_id,
                step_id=None,
                timestamp=run.started_at,
                locator={"run_id": run.run_id},
                id_key=f"run:{run.run_id}",
            )
        )
    return hits


def _search_traces(memory: MemoryRouter, product: str, flow: str, query: RetrievalQuery) -> List[_Hit]:
    hits: List[_Hit] = []
    for run in memory.list_runs(limit=1000, offset=0):
        if run.product != product or run.flow != flow:
            continue
        bundle = memory.get_run(run.run_id)
        if bundle is None:
            continue
        for event in bundle.events:
            if event.product != product or event.flow != flow:
                continue
            if not _within_range(event.ts, query.time_range):
                continue
            text = _serialize_payload(event.payload)
            score = _score_text(text, query.query)
            if score <= 0:
                continue
            hits.append(
                _Hit(
                    source_type="trace_event",
                    text=text,
                    score=score,
                    run_id=event.run_id,
                    step_id=event.step_id,
                    timestamp=event.ts,
                    locator={"trace_event_id": event.event_id},
                    id_key=f"trace:{event.event_id}",
                )
            )
    return hits


def _score_text(text: str, query: str) -> int:
    text_lower = text.lower()
    tokens = [tok for tok in query.lower().split() if tok]
    score = 0
    for token in tokens:
        if token in text_lower:
            score += text_lower.count(token)
    return score


def _serialize_payload(payload: Any) -> str:
    try:
        return json.dumps(payload or {}, sort_keys=True, ensure_ascii=True)
    except Exception:
        return str(payload)


def _within_range(timestamp: Optional[int], time_range: Optional[Any]) -> bool:
    if timestamp is None or time_range is None:
        return True
    start = int(time_range.start.timestamp()) if time_range.start else None
    end = int(time_range.end.timestamp()) if time_range.end else None
    if start is not None and timestamp < start:
        return False
    if end is not None and timestamp > end:
        return False
    return True


def _stable_evidence_id(hit: _Hit, index: int) -> str:
    seed = f"{hit.source_type}:{hit.id_key}:{hit.run_id}:{hit.step_id}:{index}"
    return f"retrieval_{hashlib.sha256(seed.encode('utf-8')).hexdigest()}"


def _bounded_snippet(text: str, limit: int = 200) -> str:
    snippet = text.strip()
    if len(snippet) > limit:
        return snippet[: limit - 1] + "…"
    return snippet or "retrieval_result"


def _timestamp_from_hit(hit: _Hit) -> datetime:
    if hit.timestamp is None:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    return datetime.fromtimestamp(hit.timestamp, tz=timezone.utc)
