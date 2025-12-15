# ==============================
# Config Loader (only env reader)
# ==============================
"""
Config loader for master/.

Rules:
- This is the ONLY place allowed to read os.environ and .env.
- This is the ONLY place allowed to read secrets/secrets.yaml.
- Everything else receives a validated Settings object.

Precedence:
env > secrets/secrets.yaml > configs/*.yaml > defaults

Testability:
- All functions accept injected paths and env dict.
- No hardcoded absolute paths.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic import ValidationError

from core.config.schema import Settings


# ==============================
# YAML Helpers
# ==============================


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    data = yaml.safe_load(raw)
    return data if isinstance(data, dict) else {}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep-merge dictionaries: override wins.
    """
    out: Dict[str, Any] = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


# ==============================
# .env Loader
# ==============================


def _read_dotenv(dotenv_path: Path) -> Dict[str, str]:
    """
    Minimal .env parser (KEY=VALUE).
    - Ignores comments and blank lines.
    - Strips surrounding quotes.
    """
    if not dotenv_path.exists():
        return {}
    envs: Dict[str, str] = {}
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, val = s.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            envs[key] = val
    return envs


def _apply_env_overrides(cfg: Dict[str, Any], env: Dict[str, str]) -> Dict[str, Any]:
    """
    Apply environment overrides with MASTER__ style nesting.

Example:
  MASTER__APP__DEBUG=true
  MASTER__APP__PORT=8001
  MASTER__MODELS__OPENAI__API_KEY=...
  MASTER__SECRETS__OPENAI_API_KEY=...

Rules:
- Split by '__' after prefix MASTER__
- Lowercase keys for dict insertion
- Coerce booleans/ints/floats when obvious
    """
    out = dict(cfg)
    prefix = "MASTER__"

    def coerce(v: str) -> Any:
        vs = v.strip()
        if vs.lower() in {"true", "false"}:
            return vs.lower() == "true"
        # int
        try:
            if vs.isdigit() or (vs.startswith("-") and vs[1:].isdigit()):
                return int(vs)
        except Exception:
            pass
        # float
        try:
            if "." in vs:
                return float(vs)
        except Exception:
            pass
        return vs

    for k, v in env.items():
        if not k.startswith(prefix):
            continue
        path = k[len(prefix) :].split("__")
        if not path or any(not p for p in path):
            continue
        cur: Dict[str, Any] = out
        for i, seg in enumerate(path):
            key = seg.lower()
            if i == len(path) - 1:
                cur[key] = coerce(v)
            else:
                nxt = cur.get(key)
                if not isinstance(nxt, dict):
                    nxt = {}
                    cur[key] = nxt
                cur = nxt
    return out


# ==============================
# Public Loader API
# ==============================


def load_settings(
    *,
    repo_root: Optional[str] = None,
    configs_dir: Optional[str] = None,
    secrets_file: Optional[str] = None,
    dotenv_file: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> Tuple[Settings, Dict[str, Any]]:
    """
    Load and validate Settings.

Returns:
- (Settings, merged_raw_dict)

Inputs:
- repo_root: defaults to current working directory
- configs_dir: defaults to <repo_root>/configs
- secrets_file: defaults to <repo_root>/secrets/secrets.yaml
- dotenv_file: defaults to <repo_root>/.env
- env: injected env vars (defaults to os.environ)
    """
    env_vars = dict(env) if env is not None else dict(os.environ)

    root = Path(repo_root or os.getcwd()).expanduser().resolve()
    cfg_dir = root / (configs_dir or "configs")

    # base configs
    app_cfg = _read_yaml(cfg_dir / "app.yaml")
    models_cfg = _read_yaml(cfg_dir / "models.yaml")
    policies_cfg = _read_yaml(cfg_dir / "policies.yaml")
    logging_cfg = _read_yaml(cfg_dir / "logging.yaml")
    products_cfg = _read_yaml(cfg_dir / "products.yaml")

    merged: Dict[str, Any] = {}
    merged = _deep_merge(merged, {"app": app_cfg})
    merged = _deep_merge(merged, {"models": models_cfg})
    merged = _deep_merge(merged, {"policies": policies_cfg})
    merged = _deep_merge(merged, {"logging": logging_cfg})
    merged = _deep_merge(merged, {"products": products_cfg})

    # secrets.yaml (optional)
    sec_path = Path(secrets_file) if secrets_file else (root / "secrets" / "secrets.yaml")
    secrets_cfg = _read_yaml(sec_path)
    merged = _deep_merge(merged, {"secrets": secrets_cfg})

    # .env (optional) -> treated as env overrides (highest)
    dotenv_path = Path(dotenv_file) if dotenv_file else (root / ".env")
    dotenv_vars = _read_dotenv(dotenv_path)
    effective_env = dict(env_vars)
    # .env should not override real env by default; real env wins
    for k, v in dotenv_vars.items():
        effective_env.setdefault(k, v)

    merged = _apply_env_overrides(merged, effective_env)

    # ensure repo_root is set deterministically (override configs)
    merged = _deep_merge(merged, {"app": {"paths": {"repo_root": str(root)}}})

    try:
        settings = Settings.model_validate(merged)
    except ValidationError as e:
        # raise with helpful context for debugging
        raise ValueError(f"Invalid configuration: {e}") from e

    # convenience wiring: populate common secret fields into provider configs
    # (still respecting precedence: if models.openai.api_key already set by env override, keep it)
    settings = _hydrate_provider_secrets(settings)

    return settings, merged


def _hydrate_provider_secrets(settings: Settings) -> Settings:
    """
    Map secrets into provider configs without breaking precedence.
    """
    data = settings.model_dump()
    secrets = data.get("secrets", {}) or {}
    models = data.get("models", {}) or {}
    openai = (models.get("openai", {}) or {}).copy()

    # Prefer explicit models.openai.api_key if already set
    if not openai.get("api_key"):
        # Prefer secrets.openai_api_key
        if secrets.get("openai_api_key"):
            openai["api_key"] = secrets["openai_api_key"]

    models["openai"] = openai
    data["models"] = models
    return Settings.model_validate(data)