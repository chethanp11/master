# ==============================
# Retriever
# ==============================
"""
High-level retrieval orchestration.

v1:
- Thin wrapper over VectorStore.
- Adds minor conveniences (defaults, safe handling).
"""

from __future__ import annotations



from typing import Any, Dict, List, Optional

from core.knowledge.base import Chunk, Query, VectorStore


class Retriever:
    def __init__(self, store: VectorStore) -> None:
        self.store = store

    def retrieve(
        self,
        *,
        query: str,
        collection: str = "default",
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_embeddings: bool = False,
    ) -> List[Chunk]:
        q = Query(
            collection=collection,
            text=query,
            top_k=top_k,
            filters=filters or {},
            use_embeddings=use_embeddings,
        )
        return self.store.query(q)
