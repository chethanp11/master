"""
Minimal in-memory vector store for text chunks + metadata.

v1 choices:
- Keep storage local/in-memory to avoid sqlite usage outside persistence modules.
- Support lexical retrieval (token overlap / Jaccard) by default.
- Optional embeddings support: store embedding JSON if provided by caller (future).
  Retrieval can still be lexical unless embeddings are wired in.

No LLM calls here. No external vector DB dependencies.
"""

from __future__ import annotations



import json
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from core.knowledge.base import Chunk, IngestChunk, IngestResult, Query, VectorStore, VectorStoreStats


def _now_ts() -> int:
    return int(time.time())


def _new_chunk_id() -> str:
    return f"chk_{uuid.uuid4().hex}"


def _tokenize(text: str) -> List[str]:
    # Simple tokenizer for v1 lexical scoring.
    # Lowercase, split on whitespace, strip punctuation-ish edges.
    out: List[str] = []
    for raw in text.lower().split():
        tok = raw.strip(".,;:!?()[]{}\"'`")
        if tok:
            out.append(tok)
    return out


def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa.intersection(sb))
    union = len(sa.union(sb))
    return float(inter) / float(union) if union else 0.0


class SqliteVectorStore(VectorStore):
    """
    In-memory chunk store (keeps interface name for compatibility).
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._store: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}

    def upsert(self, items: List[IngestChunk]) -> IngestResult:
        if not items:
            return IngestResult(ok=True, inserted=0, updated=0)

        errors: List[str] = []
        inserted = 0
        updated = 0
        now = _now_ts()

        for it in items:
            try:
                meta = dict(it.metadata or {})
                meta.setdefault("doc_id", it.doc_id)
                meta.setdefault("chunk_id", it.chunk_id)
                meta.setdefault("source", it.source)
                meta.setdefault("collection", it.collection)
                collection = self._store.setdefault(it.collection, {})
                doc_bucket = collection.setdefault(it.doc_id, {})
                exists = it.chunk_id in doc_bucket
                doc_bucket[it.chunk_id] = {
                    "collection": it.collection,
                    "doc_id": it.doc_id,
                    "chunk_id": it.chunk_id,
                    "text": it.text,
                    "source": it.source,
                    "metadata_json": json.dumps(meta, ensure_ascii=False),
                    "created_at": now if not exists else doc_bucket[it.chunk_id].get("created_at", now),
                    "updated_at": now,
                }
                if exists:
                    updated += 1
                else:
                    inserted += 1
            except Exception as e:  # pragma: no cover - error path
                errors.append(str(e))
        # ensure counts sum even if items empty
        remainder = len(items) - (inserted + updated)
        if remainder > 0 and errors:
            # errors already captured; keep counts as-is
            pass
        elif remainder > 0:
            inserted += remainder

        ok = len(errors) == 0
        return IngestResult(ok=ok, inserted=inserted, updated=updated, errors=errors)

    def query(self, q: Query) -> List[Chunk]:
        top_k = max(1, int(q.top_k or 5))
        q_tokens = _tokenize(q.text)

        scored: List[Chunk] = []
        collection = self._store.get(q.collection, {})
        for doc_bucket in collection.values():
            for row in doc_bucket.values():
                try:
                    meta = json.loads(row.get("metadata_json") or "") if row.get("metadata_json") else {}
                except Exception:
                    meta = {}

                if q.filters and not self._passes_filters(row, meta, q.filters):
                    continue

                score = _jaccard(q_tokens, _tokenize(row["text"]))
                if score <= 0.0:
                    continue

                scored.append(
                    Chunk(
                        chunk_id=row["chunk_id"],
                        text=row["text"],
                        source=row["source"],
                        metadata=meta,
                        score=score,
                    )
                )

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]

    def delete(
        self,
        *,
        collection: str,
        doc_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        removed = 0
        collection_bucket = self._store.get(collection, {})
        if doc_ids:
            for doc_id in list(doc_ids):
                doc_bucket = collection_bucket.pop(doc_id, None)
                if doc_bucket:
                    removed += len(doc_bucket)
        elif filters:
            targets: List[Tuple[str, str]] = []
            for doc_id, doc_bucket in collection_bucket.items():
                for chunk_id, row in doc_bucket.items():
                    try:
                        meta = json.loads(row.get("metadata_json") or "") if row.get("metadata_json") else {}
                    except Exception:
                        meta = {}
                    if self._passes_filters(row, meta, filters):
                        targets.append((doc_id, chunk_id))
            for doc_id, chunk_id in targets:
                if chunk_id in collection_bucket.get(doc_id, {}):
                    del collection_bucket[doc_id][chunk_id]
                    removed += 1
                if not collection_bucket.get(doc_id):
                    collection_bucket.pop(doc_id, None)
        else:
            removed = sum(len(doc_bucket) for doc_bucket in collection_bucket.values())
            self._store[collection] = {}
        return removed

    def stats(self, collection: Optional[str] = None) -> VectorStoreStats:
        collections: Dict[str, int] = {}
        total = 0
        if collection:
            total = sum(len(doc_bucket) for doc_bucket in self._store.get(collection, {}).values())
            collections[collection] = total
        else:
            for coll, doc_bucket in self._store.items():
                count = sum(len(bucket) for bucket in doc_bucket.values())
                collections[coll] = count
                total += count
        return VectorStoreStats(total_chunks=total, store_path=self.db_path, collections=collections)

    def clear(self) -> None:
        self._store = {}

    def _passes_filters(self, row: Dict[str, Any], meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if key == "doc_id":
                if row.get("doc_id") != expected:
                    return False
                continue
            if key == "source":
                if row.get("source") != expected:
                    return False
                continue
            if meta.get(key) != expected:
                return False
        return True
