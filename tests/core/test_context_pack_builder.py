from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from core.contracts.context_pack_schema import ContextPackConfig
from core.contracts.evidence_schema import EvidenceItem, EvidenceSource
from core.contracts.run_schema import ArtifactRef
from core.knowledge.context_pack import build_context_pack, compute_context_pack_hash


def _make_evidence() -> tuple[List[EvidenceItem], Dict[str, Any]]:
    artifacts: Dict[str, Any] = {}
    table_key = "artifact.table"
    text_key = "artifact.text"
    artifacts[table_key] = [
        {"id": 2, "name": "beta", "score": 10.5},
        {"id": 1, "name": "alpha", "score": 8.0},
    ]
    artifacts[text_key] = {"text": "This is a deterministic excerpt for evidence testing."}

    table_ref = ArtifactRef(key=table_key, kind="json", uri=f"memory://{table_key}")
    text_ref = ArtifactRef(key=text_key, kind="text", uri=f"memory://{text_key}")

    now = datetime(2024, 1, 1)
    evidence = [
        EvidenceItem(
            id="evidence-table-1",
            type="table",
            source=EvidenceSource(tool="table_tool", ref="r1"),
            timestamp=now,
            confidence=0.9,
            content_ref=table_ref,
            summary="table summary",
            provenance={"filter": "none"},
        ),
        EvidenceItem(
            id="evidence-text-1",
            type="text",
            source=EvidenceSource(tool="text_tool", ref="r2"),
            timestamp=now,
            confidence=0.8,
            content_ref=text_ref,
            summary="text summary",
            provenance={"filter": "none"},
        ),
    ]
    return evidence, artifacts


def test_context_pack_deterministic_hash() -> None:
    evidence, artifacts = _make_evidence()
    config = ContextPackConfig(table_row_limit=2, excerpt_char_limit=40, artifacts=artifacts)

    pack_a = build_context_pack(evidence, question="What happened?", config=config)
    pack_b = build_context_pack(evidence, question="What happened?", config=config)

    assert pack_a.pack_hash == pack_b.pack_hash
    assert compute_context_pack_hash(pack_a) == pack_a.pack_hash


def test_context_pack_links_to_evidence() -> None:
    evidence, artifacts = _make_evidence()
    config = ContextPackConfig(table_row_limit=1, excerpt_char_limit=20, artifacts=artifacts)

    pack = build_context_pack(evidence, question="Where is the data?", config=config)
    indexed_ids = {entry.evidence_id for entry in pack.evidence_index}
    assert indexed_ids == {"evidence-table-1", "evidence-text-1"}
    assert pack.tables_summary.key_rows
    assert pack.tables_summary.key_rows[0].evidence_id in indexed_ids
    assert pack.documents_summary.excerpts
    assert pack.documents_summary.excerpts[0].evidence_id in indexed_ids
