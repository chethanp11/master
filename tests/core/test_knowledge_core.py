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
        _chunk("hello_world", "doc_a", 0, "Alpha beta gamma", topic="guide", product="hello_world"),
        _chunk("hello_world", "doc_a", 1, "Beta delta epsilon"),
        _chunk("hello_world", "doc_b", 0, "Gamma only text", topic="notes"),
    ]

    res = store.upsert(items)
    assert res.ok
    assert res.inserted == len(items)

    q = Query(collection="hello_world", text="beta", top_k=5)
    matches = store.query(q)
    assert matches
    assert matches[0].source.endswith("doc_a")

    filtered = store.query(Query(collection="hello_world", text="gamma", filters={"topic": "notes"}))
    assert len(filtered) == 1
    assert filtered[0].metadata["topic"] == "notes"

    # Upsert same chunk with new text -> counts as update
    updated_chunk = items[0].model_copy(update={"text": "Alpha refreshed"})
    res2 = store.upsert([updated_chunk])
    assert res2.updated == 1
    stats = store.stats(collection="hello_world")
    assert stats.total_chunks == len(items)

    # Delete by doc_id
    removed = store.delete(collection="hello_world", doc_ids=["doc_b"])
    assert removed == 1
    stats2 = store.stats(collection="hello_world")
    assert stats2.total_chunks == len(items) - 1

    store.clear()
    assert store.stats().total_chunks == 0
