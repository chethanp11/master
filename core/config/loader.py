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

# High-level load flow:
# 1. Determine paths and environment variables (env, .env).
# 2. Load base YAML configs from configs/ directory.
# 3. Load secrets from secrets.yaml if present.
# 4. Load .env file and merge into environment variables without overriding real env.
# 5. Apply env var overrides with MASTER__ prefix to merged config.
# 6. Inject repo_root path into config to ensure deterministic path.
# 7. Validate merged config against pydantic Settings schema.
# 8. Hydrate provider secrets into models config respecting precedence.
# 9. Return validated Settings object (and optionally raw merged dict).


from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic import ValidationError

from core.config.schema import Settings


# ==============================
# YAML Helpers
# ==============================


def _read_yaml(path: Path) -> Dict[str, Any]:
    # Return empty dict if file does not exist
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    # Return empty dict if file is empty or whitespace only
    if not raw:
        return {}
    data = yaml.safe_load(raw)
    # Guard against non-dict YAML content, return empty dict if not a dict
    return data if isinstance(data, dict) else {}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep-merge dictionaries: override wins.

    Recursively merges nested dicts, with values from 'override' taking precedence.
    """
    out: Dict[str, Any] = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            # Recursively merge nested dictionaries
            out[k] = _deep_merge(out[k], v)
        else:
            # Override scalar or non-dict values
            out[k] = v
    return out


def _section(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    Config files may either namespace their contents (app: {...}) or provide the
    raw fields directly. Normalize to the inner dict for merging.

    This supports legacy configs that either wrap all settings under a top-level key
    or flatten them at the root level.
    """
    value = data.get(key)
    if isinstance(value, dict):
        return value
    # If no top-level key or not a dict, assume data is already the inner dict
    return data


def _normalize_app_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy configs used `name/environment/default_timeout_seconds`. Map/strip them.

    This function normalizes old config keys to current expected keys and removes deprecated ones.
    """
    out = dict(data)
    if "environment" in out and "env" not in out:
        out["env"] = out["environment"]
    # Remove deprecated keys
    out.pop("environment", None)
    out.pop("name", None)
    out.pop("default_timeout_seconds", None)
    return out


# ==============================
# .env Loader
# ==============================


def _read_dotenv(dotenv_path: Path) -> Dict[str, str]:
    """
    Minimal .env parser (KEY=VALUE).
    - Ignores comments and blank lines.
    - Strips surrounding quotes.

    Prefer python-dotenv if available; fallback to a minimal parser.
    """
    if not dotenv_path.exists():
        return {}
    try:
        from dotenv import dotenv_values  # type: ignore

        values = dotenv_values(dotenv_path)
        return {k: v for k, v in values.items() if isinstance(k, str) and isinstance(v, str)}
    except Exception:
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

The MASTER__ prefix is chosen to clearly namespace overrides for this application,
avoiding collisions with other env vars.

Lowercasing keys ensures consistent dict keys regardless of env var casing.

Coercion attempts to convert strings to bool/int/float for convenience.
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


def _is_hf_space_env(env: Dict[str, str]) -> bool:
    if "HF_HOME" in env:
        return True
    return any(key.startswith("HF_") for key in env.keys())


# ==============================
# Public Loader API
# ==============================


def load_settings(
    *,
    repo_root: Optional[str] = None,
    configs_dir: Optional[str] = None,
    secrets_file: Optional[str] = None,
    secrets_path: Optional[str] = None,
    dotenv_file: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    include_raw: bool = False,
) -> Settings | Tuple[Settings, Dict[str, Any]]:
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
    if secrets_file is not None and secrets_path is not None:
        raise ValueError("Provide only one of secrets_file or secrets_path.")

    def _resolve_base_path(base_path: Optional[str], fallback: Path) -> Path:
        if not base_path:
            return fallback
        base = Path(base_path).expanduser()
        if not base.is_absolute():
            base = (fallback / base).resolve()
        return base.resolve()

    # --- Environment variable resolution ---
    env_vars = dict(env) if env is not None else dict(os.environ)

    root = Path(repo_root or os.getcwd()).expanduser().resolve()
    root = _resolve_base_path(env_vars.get("APP_BASE_PATH"), root)

    # --- Load .env file and merge with env vars ---
    dotenv_path = Path(dotenv_file) if dotenv_file else (root / ".env")
    dotenv_vars = _read_dotenv(dotenv_path)
    effective_env = dict(env_vars)
    # .env should not override real env by default; real env wins
    for k, v in dotenv_vars.items():
        effective_env.setdefault(k, v)
    if "APP_BASE_PATH" not in env_vars and "APP_BASE_PATH" in dotenv_vars:
        root = _resolve_base_path(dotenv_vars.get("APP_BASE_PATH"), root)
        if dotenv_file is None:
            repo_dotenv_vars = _read_dotenv(root / ".env")
            for k, v in repo_dotenv_vars.items():
                effective_env.setdefault(k, v)

    cfg_dir = root / (configs_dir or "configs")

    # --- Load base config YAML files ---
    app_cfg = _read_yaml(cfg_dir / "app.yaml")
    models_cfg = _read_yaml(cfg_dir / "models.yaml")
    policies_cfg = _read_yaml(cfg_dir / "policies.yaml")
    logging_cfg = _read_yaml(cfg_dir / "logging.yaml")
    products_cfg = _read_yaml(cfg_dir / "products.yaml")

    merged: Dict[str, Any] = {}
    merged = _deep_merge(merged, {"app": _normalize_app_config(_section(app_cfg, "app"))})
    merged = _deep_merge(merged, {"models": _section(models_cfg, "models")})
    merged = _deep_merge(merged, {"policies": _section(policies_cfg, "policies")})
    merged = _deep_merge(merged, {"logging": _section(logging_cfg, "logging")})
    merged = _deep_merge(merged, {"products": _section(products_cfg, "products")})

    # --- Load secrets.yaml (optional) ---
    sec_path = Path(secrets_file or secrets_path) if (secrets_file or secrets_path) else (root / "secrets" / "secrets.yaml")
    secrets_cfg = _read_yaml(sec_path)
    merged = _deep_merge(merged, {"secrets": _section(secrets_cfg, "secrets")})

    if _is_hf_space_env(effective_env):
        # Hugging Face Spaces has an ephemeral filesystem; default to /data/storage when unset.
        paths_cfg = (merged.get("app") or {}).get("paths") if isinstance(merged.get("app"), dict) else None
        storage_dir = paths_cfg.get("storage_dir") if isinstance(paths_cfg, dict) else None
        if not storage_dir:
            merged = _deep_merge(merged, {"app": {"paths": {"storage_dir": "/data/storage"}}})

    # --- Apply MASTER__ env var overrides ---
    merged = _apply_env_overrides(merged, effective_env)

    # --- Resolve provider secret refs (non-MASTER env vars) ---
    merged = _hydrate_provider_refs(merged, effective_env)

    # --- Inject repo_root path to ensure deterministic path ---
    merged = _deep_merge(merged, {"app": {"paths": {"repo_root": str(root)}}})

    # --- Validate merged config against pydantic schema ---
    try:
        settings = Settings.model_validate(merged)
    except ValidationError as e:
        # raise with helpful context for debugging
        raise ValueError(f"Invalid configuration: {e}") from e

    # --- Hydrate provider secrets after validation ---
    # This happens after validation to avoid breaking precedence rules
    # and to ensure the final Settings object has secrets injected appropriately.
    settings = _hydrate_provider_secrets(settings)

    logger = logging.getLogger(__name__)
    logger.info("OpenAI API key resolved: %s", bool(settings.models.openai.api_key))

    if include_raw:
        return settings, merged
    return settings


def _hydrate_provider_refs(merged: Dict[str, Any], env: Dict[str, str]) -> Dict[str, Any]:
    def _get_dot(data: Dict[str, Any], path: str) -> Any:
        cur: Any = data
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur

    def _resolve_secret(direct_key: str, ref_key: str) -> Optional[str]:
        direct = env.get(direct_key)
        if direct:
            return direct
        ref = env.get(ref_key)
        if not ref:
            return None
        secrets = merged.get("secrets", {}) or {}
        value = _get_dot(secrets, ref)
        return value

    openai_api_key = _resolve_secret("OPENAI_API_KEY", "OPENAI_API_KEY_REF")
    openai_org_id = _resolve_secret("OPENAI_ORG_ID", "OPENAI_ORG_ID_REF")

    models = merged.get("models", {}) or {}
    openai_cfg = models.get("openai", {}) or {}
    if openai_api_key is not None:
        openai_cfg.setdefault("api_key", openai_api_key)
    if openai_org_id is not None:
        openai_cfg.setdefault("org_id", openai_org_id)
    models["openai"] = openai_cfg
    merged["models"] = models
    return merged


def _hydrate_provider_secrets(settings: Settings) -> Settings:
    """
    Map secrets into provider configs without breaking precedence.

    This function injects secrets (like API keys) into the models config if they
    are not already set by higher-precedence sources (env vars or configs).

    It runs after validation to preserve the precedence and avoid validation errors.
    """
    data = settings.model_dump()
    secrets = data.get("secrets", {}) or {}
    models = data.get("models", {}) or {}
    openai = (models.get("openai", {}) or {}).copy()

    # Prefer explicit models.openai.api_key if already set
    if not openai.get("api_key"):
        if secrets.get("openai_api_key"):
            openai["api_key"] = secrets["openai_api_key"]
        elif isinstance(secrets.get("openai"), dict) and secrets["openai"].get("api_key"):
            openai["api_key"] = secrets["openai"]["api_key"]
    if not openai.get("org_id"):
        if isinstance(secrets.get("openai"), dict) and secrets["openai"].get("org_id"):
            openai["org_id"] = secrets["openai"]["org_id"]

    models["openai"] = openai
    data["models"] = models
    return Settings.model_validate(data)
