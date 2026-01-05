from __future__ import annotations

from pathlib import Path

from core.config.loader import load_settings


def test_feature_flags_default_off() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    settings = load_settings(repo_root=str(repo_root), configs_dir=str(repo_root / "configs"))

    assert settings.app.features.observability_input_mirroring is False
    assert settings.app.features.enable_sqlite_backend is False
    assert settings.app.features.enable_vector_backend is False
    assert settings.app.features.enable_knowledge_index is False
