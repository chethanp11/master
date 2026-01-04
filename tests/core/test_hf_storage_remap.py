# ==============================
# Hugging Face Storage Remap Tests
# ==============================
from __future__ import annotations

import textwrap

from core.config.loader import load_settings


def _write_yaml(path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


def _base_configs(root) -> None:
    _write_yaml(root / "configs" / "app.yaml", "app: {}\n")
    _write_yaml(root / "configs" / "models.yaml", "models: {}\n")
    _write_yaml(root / "configs" / "policies.yaml", "policies: {}\n")
    _write_yaml(root / "configs" / "logging.yaml", "logging: {}\n")
    _write_yaml(root / "configs" / "products.yaml", "products: {}\n")


def test_hf_env_applies_persistent_paths_when_unset(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _base_configs(repo_root)

    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir="configs",
        env={"HF_HOME": "/data"},
    )

    assert settings.app.paths.storage_dir == "/data/storage"
    assert settings.app.paths.observability_dir == "/data/observability"


def test_hf_env_respects_env_overrides(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _base_configs(repo_root)

    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir="configs",
        env={
            "HF_HOME": "/data",
            "MASTER__APP__PATHS__STORAGE_DIR": "/custom/storage",
            "MASTER__APP__PATHS__OBSERVABILITY_DIR": "/custom/observability",
        },
    )

    assert settings.app.paths.storage_dir == "/custom/storage"
    assert settings.app.paths.observability_dir == "/custom/observability"
