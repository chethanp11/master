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
    chunk_id: str
    text: str
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestItem(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestResult(BaseModel):
    ok: bool
    count: int
    errors: List[str] = Field(default_factory=list)


class Query(BaseModel):
    text: str
    top_k: int = 5
    filters: Dict[str, Any] = Field(default_factory=dict)
    use_embeddings: bool = False  # v1: defaults to lexical


class VectorStoreStats(BaseModel):
    total_chunks: int
    store_path: str


class VectorStore(BaseModel):
    """
    Interface-like base. Concrete implementations should provide methods below.
    We keep this as a BaseModel for consistent typing/config in v1.
    """

    class Config:
        arbitrary_types_allowed = True

    def add_chunks(self, items: List[IngestItem]) -> IngestResult:  # pragma: no cover
        raise NotImplementedError

    def query(self, q: Query) -> List[Chunk]:  # pragma: no cover
        raise NotImplementedError

    def stats(self) -> VectorStoreStats:  # pragma: no cover
        raise NotImplementedError

    def clear(self) -> None:  # pragma: no cover
        raise NotImplementedError