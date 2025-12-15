# ==============================
# Config Precedence Tests
# ==============================
from __future__ import annotations

import textwrap

import pytest

from core.config.loader import load_settings


def _write_yaml(path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


def _base_configs(root):
    _write_yaml(root / "configs" / "app.yaml", """\
    app:
      host: config-host
      port: 1111
      paths:
        logs_dir: logs
        storage_dir: storage
    """)
    _write_yaml(root / "configs" / "models.yaml", """\
    models:
      openai:
        timeout_seconds: 5.0
    """)
    _write_yaml(root / "configs" / "policies.yaml", "policies: {}\n")
    _write_yaml(root / "configs" / "logging.yaml", "logging: {}\n")
    _write_yaml(root / "configs" / "products.yaml", "products: {}\n")


def test_config_precedence(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _base_configs(repo_root)

    secrets_dir = repo_root / "secrets"
    secrets_dir.mkdir()
    secrets_path = secrets_dir / "secrets.yaml"
    _write_yaml(secrets_path, """\
    secrets:
      openai_api_key: secret-key
    """)

    env = {"MASTER__APP__PORT": "3333"}

    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir="configs",
        secrets_path=str(secrets_path),
        env=env,
    )

    assert settings.app.port == 3333
    assert settings.models.openai.api_key == "secret-key"

    # Negative case: invalid products config should raise early
    _write_yaml(repo_root / "bad_configs" / "app.yaml", """\
    app:
      env: local
      paths:
        repo_root: .
      port: not-a-number
    """)
    with pytest.raises(ValueError) as excinfo:
        load_settings(
            repo_root=str(repo_root),
            configs_dir="bad_configs",
            secrets_path=str(secrets_path),
        )
    assert "Invalid configuration" in str(excinfo.value)
