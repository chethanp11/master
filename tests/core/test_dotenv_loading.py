# ==============================
# .env Loading Tests
# ==============================
from __future__ import annotations

import textwrap

from core.config.loader import load_settings


def _write_yaml(path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


def _base_configs(root) -> None:
    _write_yaml(root / "configs" / "app.yaml", """\
    app:
      env: local
      paths:
        storage_dir: storage
    """)
    _write_yaml(root / "configs" / "models.yaml", "models: {}\n")
    _write_yaml(root / "configs" / "policies.yaml", "policies: {}\n")
    _write_yaml(root / "configs" / "logging.yaml", "logging: {}\n")
    _write_yaml(root / "configs" / "products.yaml", "products: {}\n")


def test_loads_dotenv_and_resolves_secrets(monkeypatch, tmp_path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _base_configs(repo_root)

    secrets_dir = repo_root / "secrets"
    secrets_dir.mkdir()
    _write_yaml(secrets_dir / "secrets.yaml", """\
    secrets:
      openai:
        api_key: test-openai-key
    """)

    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "APP_BASE_PATH=repo\nOPENAI_API_KEY_REF=openai.api_key\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    settings = load_settings(env={})

    assert settings.models.openai.api_key == "test-openai-key"
