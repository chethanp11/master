# ==============================
# Integration: Minimal Smoke Test
# ==============================
from __future__ import annotations

from pathlib import Path

from core.config.loader import load_settings
from core.orchestrator.engine import OrchestratorEngine
from core.utils.product_loader import discover_products, register_enabled_products


def test_smoke_engine_init(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sqlite_path = tmp_path / "smoke.sqlite"
    storage_dir = tmp_path / "storage"

    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir=str(repo_root / "configs"),
        env={
            "MASTER__APP__PATHS__STORAGE_DIR": storage_dir.as_posix(),
            "MASTER__SECRETS__MEMORY_DB_PATH": sqlite_path.as_posix(),
        },
    )
    catalog = discover_products(settings, repo_root=repo_root)
    register_enabled_products(catalog, settings=settings)
    engine = OrchestratorEngine.from_settings(settings)
    assert engine is not None
