# ==============================
# Tests: Knowledge Core
# ==============================
from __future__ import annotations

from pathlib import Path

from core.knowledge.base import IngestChunk, Query
from core.knowledge.vector_store import SqliteVectorStore


def _chunk(collection: str, doc: str, idx: int, text: str, **metadata) -> IngestChunk:
    return IngestChunk(
        collection=collection,
        doc_id=doc,
        chunk_id=f"{doc}:::{idx}",
        text=text,
        source=f"file://{doc}",
        metadata=metadata,
    )


def test_vector_store_upsert_query_delete(tmp_path: Path) -> None:
    store = SqliteVectorStore(str(tmp_path / "knowledge.sqlite"))
    items = [
        _chunk("sandbox", "doc_a", 0, "Alpha beta gamma", topic="guide", product="sandbox"),
        _chunk("sandbox", "doc_a", 1, "Beta delta epsilon"),
        _chunk("sandbox", "doc_b", 0, "Gamma only text", topic="notes"),
    ]

    res = store.upsert(items)
    assert res.ok
    assert res.inserted == len(items)

    q = Query(collection="sandbox", text="beta", top_k=5)
    matches = store.query(q)
    assert matches
    assert matches[0].source.endswith("doc_a")

    filtered = store.query(Query(collection="sandbox", text="gamma", filters={"topic": "notes"}))
    assert len(filtered) == 1
    assert filtered[0].metadata["topic"] == "notes"

    # Upsert same chunk with new text -> counts as update
    updated_chunk = items[0].model_copy(update={"text": "Alpha refreshed"})
    res2 = store.upsert([updated_chunk])
    assert res2.updated == 1
    stats = store.stats(collection="sandbox")
    assert stats.total_chunks == len(items)

    # Delete by doc_id
    removed = store.delete(collection="sandbox", doc_ids=["doc_b"])
    assert removed == 1
    stats2 = store.stats(collection="sandbox")
    assert stats2.total_chunks == len(items) - 1

    store.clear()
    assert store.stats().total_chunks == 0
