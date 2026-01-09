from __future__ import annotations

# ==============================
# Context Pack Builder
# ==============================
"""
Deterministic builder for ContextPack artifacts.
"""

import json
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Tuple

from core.contracts.context_pack_schema import (
    ContextPack,
    ContextPackConfig,
    DocumentsSummary,
    EvidenceIndexEntry,
    TablesSummary,
    TableRowSample,
    DocumentExcerpt,
    DocumentMetadata,
)
from core.contracts.evidence_schema import EvidenceItem
from core.contracts.run_schema import ArtifactRef


class ContextPackBuildResult(ContextPack):
    content_ref: ArtifactRef


def build_context_pack(
    evidence: List[EvidenceItem],
    question: str,
    config: ContextPackConfig,
) -> ContextPackBuildResult:
    ordered = _order_evidence(evidence)
    evidence_index = [
        EvidenceIndexEntry(
            evidence_id=item.id,
            source_tool=item.source.tool,
            source_ref=item.source.ref,
            source_uri=item.source.uri,
            type=item.type,
        )
        for item in ordered
    ]

    table_rows = _collect_table_rows(ordered, config)
    column_profiles, stats = _summarize_table_rows(table_rows)
    tables_summary = TablesSummary(
        stats=stats,
        key_rows=table_rows,
        column_profiles=column_profiles,
    )

    excerpts, metadata = _summarize_documents(ordered, config)
    documents_summary = DocumentsSummary(excerpts=excerpts, metadata=metadata)

    assumptions = [
        "Evidence items are sorted deterministically by id, type, source tool, source ref, and source uri.",
        "Table key rows are sampled by stable JSON canonicalization and truncated to configured limits.",
        "Document excerpts use the leading characters of the content up to the configured limit.",
    ]
    limits = {"table_row_limit": config.table_row_limit, "excerpt_char_limit": config.excerpt_char_limit}

    pack = ContextPack(
        question=question,
        evidence_index=evidence_index,
        tables_summary=tables_summary,
        documents_summary=documents_summary,
        assumptions=assumptions,
        limits=limits,
    )
    pack_hash = compute_context_pack_hash(pack)
    stored = pack.model_copy(update={"pack_hash": pack_hash})
    content_ref = _store_context_pack(stored, config)
    return ContextPackBuildResult(**stored.model_dump(mode="json"), content_ref=content_ref)


def compute_context_pack_hash(pack: ContextPack) -> str:
    payload = pack.model_dump(mode="json")
    payload.pop("pack_hash", None)
    payload.pop("content_ref", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return sha256(encoded).hexdigest()


def _order_evidence(items: Iterable[EvidenceItem]) -> List[EvidenceItem]:
    def _key(item: EvidenceItem) -> Tuple[str, str, str, str, str]:
        source = item.source
        return (
            item.id,
            item.type,
            source.tool or "",
            source.ref or "",
            source.uri or "",
        )

    return sorted(items, key=_key)


def _collect_table_rows(items: List[EvidenceItem], config: ContextPackConfig) -> List[TableRowSample]:
    rows: List[TableRowSample] = []
    for item in items:
        if item.type != "table":
            continue
        payload = _resolve_artifact(item.content_ref, config)
        table_rows = _extract_rows(payload)
        if not table_rows:
            continue
        ordered_rows = sorted(table_rows, key=_canonical_json)
        for row in ordered_rows[: config.table_row_limit]:
            rows.append(TableRowSample(evidence_id=item.id, row=row))
    return rows


def _summarize_table_rows(rows: List[TableRowSample]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not rows:
        return {}, {"row_count": 0}
    flat_rows = [entry.row for entry in rows]
    columns = sorted({key for row in flat_rows for key in row.keys()})
    profiles: Dict[str, Any] = {}
    numeric_stats: Dict[str, Any] = {}
    row_count = len(flat_rows)

    for col in columns:
        values = [row.get(col) for row in flat_rows]
        null_count = sum(1 for v in values if v is None)
        inferred = _infer_type(values)
        unique_count = len({_canonical_json(v) for v in values})
        profile = {
            "type": inferred,
            "null_pct": (null_count / row_count) if row_count else 0.0,
            "unique_count": unique_count,
        }
        profiles[col] = profile
        if inferred in {"int", "float"}:
            nums = [float(v) for v in values if isinstance(v, (int, float))]
            if nums:
                numeric_stats[col] = {
                    "min": min(nums),
                    "max": max(nums),
                    "mean": sum(nums) / len(nums),
                }

    stats = {"row_count": row_count, "numeric": numeric_stats}
    return profiles, stats


def _summarize_documents(
    items: List[EvidenceItem],
    config: ContextPackConfig,
) -> Tuple[List[DocumentExcerpt], List[DocumentMetadata]]:
    excerpts: List[DocumentExcerpt] = []
    metadata: List[DocumentMetadata] = []
    for item in items:
        if item.type not in {"doc", "text"}:
            continue
        payload = _resolve_artifact(item.content_ref, config)
        text = _extract_text(payload)
        if text:
            snippet = text[: config.excerpt_char_limit]
            excerpts.append(
                DocumentExcerpt(
                    evidence_id=item.id,
                    excerpt_text=snippet,
                    start_offset=0,
                    end_offset=len(snippet),
                    metadata={"tool": item.source.tool, "ref": item.source.ref, "uri": item.source.uri},
                )
            )
        metadata.append(DocumentMetadata(evidence_id=item.id))
    return excerpts, metadata


def _resolve_artifact(content_ref: ArtifactRef, config: ContextPackConfig) -> Any:
    return config.artifacts.get(content_ref.key)


def _extract_rows(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return payload
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list) and all(isinstance(item, dict) for item in rows):
            return rows
    return []


def _extract_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        text = payload.get("text")
        if isinstance(text, str):
            return text
    return ""


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except Exception:
        return str(value)


def _infer_type(values: List[Any]) -> str:
    has_float = False
    has_int = False
    has_bool = False
    has_str = False
    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):
            has_bool = True
        elif isinstance(v, int):
            has_int = True
        elif isinstance(v, float):
            has_float = True
        else:
            has_str = True
    if has_str:
        return "str"
    if has_float:
        return "float"
    if has_int:
        return "int"
    if has_bool:
        return "bool"
    return "null"


def _store_context_pack(pack: ContextPack, config: ContextPackConfig) -> ArtifactRef:
    key = f"context_pack.{pack.pack_hash}"
    uri = f"memory://{key}"
    config.artifacts[key] = pack.model_dump(mode="json")
    return ArtifactRef(key=key, kind="json", uri=uri, meta={"context_pack": True})
