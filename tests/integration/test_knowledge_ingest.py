# ==============================
# Integration Test: Knowledge Ingestion
# ==============================
from __future__ import annotations

from pathlib import Path

from core.knowledge.base import Query
from core.knowledge.vector_store import SqliteVectorStore
from scripts import ingest_knowledge


def test_ingest_script_round_trip(tmp_path: Path, hello_world_test_env: Path) -> None:
    """
    The hello_world_test_env fixture drives deterministic sqlite overrides so ingestion and flow tests share storage paths.
    """
    data_dir = tmp_path / "docs"
    data_dir.mkdir()
    (data_dir / "note.txt").write_text("Alpha beta", encoding="utf-8")
    (data_dir / "guide.md").write_text("Gamma delta", encoding="utf-8")

    db_path = tmp_path / "knowledge.sqlite"
    args = ingest_knowledge.parse_args(
        [
            "--db",
            str(db_path),
            "--collection",
            "hello_world",
            "--path",
            str(data_dir),
        ]
    )

    exit_code = ingest_knowledge.run_ingest(args)
    assert exit_code == 0

    store = SqliteVectorStore(str(db_path))
    stats = store.stats(collection="hello_world")
    assert stats.total_chunks > 0

    results = store.query(Query(collection="hello_world", text="alpha"))
    assert results

    # Re-ingesting the same folder should be idempotent.
    exit_code_repeat = ingest_knowledge.run_ingest(args)
    assert exit_code_repeat == 0
    stats_after = store.stats(collection="hello_world")
    assert stats_after.total_chunks == stats.total_chunks
