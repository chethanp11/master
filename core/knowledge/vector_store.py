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

from core.knowledge.base import Chunk, IngestItem, IngestResult, Query, VectorStore, VectorStoreStats


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
      chunks(
        chunk_id TEXT PRIMARY KEY,
        text TEXT NOT NULL,
        metadata_json TEXT NOT NULL,
        embedding_json TEXT NULL,
        created_at INTEGER NOT NULL
      )
    """

    db_path: str

    def __init__(self, db_path: str) -> None:
        super().__init__()
        self.db_path = db_path
        self._ensure_dir()
        self._ensure_schema()

    def _ensure_dir(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    embedding_json TEXT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_created ON chunks(created_at)")
            conn.commit()

    def add_chunks(self, items: List[IngestItem]) -> IngestResult:
        errors: List[str] = []
        count = 0
        with self._connect() as conn:
            for it in items:
                try:
                    chunk_id = _new_chunk_id()
                    meta = dict(it.metadata or {})
                    meta.setdefault("ingested_at", _now_ts())
                    conn.execute(
                        """
                        INSERT INTO chunks(chunk_id, text, metadata_json, embedding_json, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            chunk_id,
                            it.text,
                            json.dumps(meta, ensure_ascii=False),
                            None,
                            _now_ts(),
                        ),
                    )
                    count += 1
                except Exception as e:
                    errors.append(str(e))
            conn.commit()
        return IngestResult(ok=(len(errors) == 0), count=count, errors=errors)

    def query(self, q: Query) -> List[Chunk]:
        # v1: lexical scoring. Filters apply to metadata keys (exact match).
        top_k = max(1, int(q.top_k or 5))
        q_tokens = _tokenize(q.text)

        rows: List[Tuple[str, str, str]] = []
        with self._connect() as conn:
            cur = conn.execute("SELECT chunk_id, text, metadata_json FROM chunks")
            rows = list(cur.fetchall())

        scored: List[Chunk] = []
        for chunk_id, text, meta_json in rows:
            try:
                meta = json.loads(meta_json) if meta_json else {}
            except Exception:
                meta = {}

            if q.filters:
                if not self._passes_filters(meta, q.filters):
                    continue

            score = _jaccard(q_tokens, _tokenize(text))
            if score <= 0.0:
                continue

            scored.append(Chunk(chunk_id=chunk_id, text=text, score=score, metadata=meta))

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]

    def _passes_filters(self, meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for k, v in filters.items():
            if k not in meta:
                return False
            if meta.get(k) != v:
                return False
        return True

    def stats(self) -> VectorStoreStats:
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(1) FROM chunks")
            total = int(cur.fetchone()[0])
        return VectorStoreStats(total_chunks=total, store_path=self.db_path)

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM chunks")
            conn.commit()