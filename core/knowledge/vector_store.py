# ==============================
# Minimal Local Vector Store (SQLite)
# ==============================
"""
A minimal SQLite-backed store for text chunks + metadata.

v1 choices:
- Store chunks in SQLite at a configurable path (default under storage/vectors/).
- Support lexical retrieval (token overlap / Jaccard) by default.
- Optional embeddings support: store embedding JSON if provided by caller (future).
  Retrieval can still be lexical unless embeddings are wired in.

No LLM calls here. No external vector DB dependencies.
"""

from __future__ import annotations



import json
import os
import sqlite3
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
    SQLite-backed chunk store.

    Table schema (v1):
      knowledge_chunks(
        collection TEXT NOT NULL,
        doc_id TEXT NOT NULL,
        chunk_id TEXT NOT NULL,
        text TEXT NOT NULL,
        source TEXT NOT NULL,
        metadata_json TEXT NOT NULL,
        embedding_json TEXT NULL,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        PRIMARY KEY (collection, doc_id, chunk_id)
      )
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_dir()
        self._ensure_schema()

    def _ensure_dir(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    collection TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    embedding_json TEXT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    PRIMARY KEY (collection, doc_id, chunk_id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_collection ON knowledge_chunks(collection)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_doc ON knowledge_chunks(collection, doc_id)"
            )
            conn.commit()

    def upsert(self, items: List[IngestChunk]) -> IngestResult:
        if not items:
            return IngestResult(ok=True, inserted=0, updated=0)

        errors: List[str] = []
        inserted = 0
        updated = 0
        now = _now_ts()

        with self._connect() as conn:
            for it in items:
                try:
                    meta = dict(it.metadata or {})
                    meta.setdefault("doc_id", it.doc_id)
                    meta.setdefault("chunk_id", it.chunk_id)
                    meta.setdefault("source", it.source)
                    meta.setdefault("collection", it.collection)
                    payload = (
                        it.collection,
                        it.doc_id,
                        it.chunk_id,
                        it.text,
                        it.source,
                        json.dumps(meta, ensure_ascii=False),
                        None,
                        now,
                        now,
                    )
                    exists = conn.execute(
                        """
                        SELECT 1 FROM knowledge_chunks
                        WHERE collection=? AND doc_id=? AND chunk_id=?
                        """,
                        (it.collection, it.doc_id, it.chunk_id),
                    ).fetchone()
                    conn.execute(
                        """
                        INSERT INTO knowledge_chunks(
                            collection, doc_id, chunk_id, text, source,
                            metadata_json, embedding_json, created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(collection, doc_id, chunk_id)
                        DO UPDATE SET
                            text=excluded.text,
                            source=excluded.source,
                            metadata_json=excluded.metadata_json,
                            updated_at=excluded.updated_at
                        """,
                        payload,
                    )
                    if exists:
                        updated += 1
                    else:
                        inserted += 1
                except Exception as e:  # pragma: no cover - error path
                    errors.append(str(e))
            conn.commit()
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

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT doc_id, chunk_id, text, source, metadata_json
                FROM knowledge_chunks
                WHERE collection=?
                """,
                (q.collection,),
            ).fetchall()

        scored: List[Chunk] = []
        for row in rows:
            try:
                meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
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
        with self._connect() as conn:
            if doc_ids:
                placeholders = ",".join("?" for _ in doc_ids)
                cur = conn.execute(
                    f"DELETE FROM knowledge_chunks WHERE collection=? AND doc_id IN ({placeholders})",
                    (collection, *doc_ids),
                )
                removed += cur.rowcount
            elif filters:
                rows = conn.execute(
                    """
                    SELECT doc_id, chunk_id, metadata_json
                    FROM knowledge_chunks
                    WHERE collection=?
                    """,
                    (collection,),
                ).fetchall()
                targets: List[Tuple[str, str]] = []
                for row in rows:
                    try:
                        meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                    except Exception:
                        meta = {}
                    if self._passes_filters(row, meta, filters):
                        targets.append((row["doc_id"], row["chunk_id"]))
                for doc_id, chunk_id in targets:
                    cur = conn.execute(
                        """
                        DELETE FROM knowledge_chunks
                        WHERE collection=? AND doc_id=? AND chunk_id=?
                        """,
                        (collection, doc_id, chunk_id),
                    )
                    removed += cur.rowcount
            else:
                cur = conn.execute(
                    "DELETE FROM knowledge_chunks WHERE collection=?",
                    (collection,),
                )
                removed += cur.rowcount
            conn.commit()
        return removed

    def stats(self, collection: Optional[str] = None) -> VectorStoreStats:
        collections: Dict[str, int] = {}
        total = 0
        with self._connect() as conn:
            if collection:
                cur = conn.execute(
                    "SELECT COUNT(1) FROM knowledge_chunks WHERE collection=?",
                    (collection,),
                )
                total = int(cur.fetchone()[0])
                collections[collection] = total
            else:
                cur = conn.execute(
                    "SELECT collection, COUNT(1) FROM knowledge_chunks GROUP BY collection"
                )
                rows = cur.fetchall()
                for coll, cnt in rows:
                    collections[coll] = int(cnt)
                    total += int(cnt)
        return VectorStoreStats(total_chunks=total, store_path=self.db_path, collections=collections)

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM knowledge_chunks")
            conn.commit()

    def _passes_filters(self, row: sqlite3.Row, meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if key == "doc_id":
                if row["doc_id"] != expected:
                    return False
                continue
            if key == "source":
                if row["source"] != expected:
                    return False
                continue
            if meta.get(key) != expected:
                return False
        return True
