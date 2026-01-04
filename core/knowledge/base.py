# ==============================
# Knowledge Layer Contracts
# ==============================
"""
Core knowledge abstractions (product-agnostic).

Design goals (v1):
- Keep minimal and stable.
- Avoid vendor/LLM calls here.
- Provide a small, typed interface for:
  - Ingestion (text + metadata)
  - Retrieval (query -> ranked chunks with source metadata)

Embedding is optional in v1. If embeddings are absent, retrieval can degrade to lexical scoring.
"""

from __future__ import annotations



from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
    Retrieval result chunk.

    Fields mirror ingestion metadata so callers can trace provenance.
    """

    chunk_id: str
    text: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0


class IngestChunk(BaseModel):
    """
    Input payload for upserting chunks into the store.
    """

    collection: str = Field(default="default", min_length=1)
    doc_id: str = Field(..., min_length=1)
    chunk_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestResult(BaseModel):
    ok: bool
    inserted: int = 0
    updated: int = 0
    errors: List[str] = Field(default_factory=list)

    @property
    def count(self) -> int:
        return self.inserted + self.updated


class Query(BaseModel):
    collection: str = Field(default="default", min_length=1)
    text: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
    filters: Dict[str, Any] = Field(default_factory=dict)
    use_embeddings: bool = False  # placeholder for future hybrid routing


class VectorStoreStats(BaseModel):
    total_chunks: int
    store_path: str
    collections: Dict[str, int] = Field(default_factory=dict)


class VectorStore:
    """
    Interface-like base for vector stores.
    Concrete backends should implement the abstract operations below.
    """

    def upsert(self, items: List[IngestChunk]) -> IngestResult:  # pragma: no cover
        raise NotImplementedError

    def query(self, q: Query) -> List[Chunk]:  # pragma: no cover
        raise NotImplementedError

    def delete(
        self,
        *,
        collection: str,
        doc_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:  # pragma: no cover
        raise NotImplementedError

    def stats(self, collection: Optional[str] = None) -> VectorStoreStats:  # pragma: no cover
        raise NotImplementedError

    def clear(self) -> None:  # pragma: no cover
        raise NotImplementedError
