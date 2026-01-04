# ==============================
# Config Schemas (Pydantic)
# ==============================
"""
Pydantic settings models for master/.

Notes:
- Keep these schemas stable: many modules will depend on them.
- No env reads here. No file IO here. Pure types + defaults.
- loader.py builds a single Settings object with precedence merging.

Precedence (implemented in loader.py):
env > secrets/secrets.yaml > configs/*.yaml > defaults
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==============================
# App Settings
# ==============================


class PathsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo_root: str = Field(default=".", description="Repo root (relative or absolute)")
    configs_dir: str = Field(default="configs", description="Configs directory")
    secrets_dir: str = Field(default="secrets", description="Secrets directory")
    storage_dir: str = Field(default="storage", description="Runtime storage directory")
    observability_dir: str = Field(default="observability", description="Observability output directory")


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    env: str = Field(default="local", description="Environment name (local/stage/prod)")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    default_product: str = Field(default="hello_world")
    default_flow: str = Field(default="hello_world")
    api_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for Gateway API used by UI clients.",
    )
    paths: PathsConfig = Field(default_factory=PathsConfig)


# ==============================
# Models Settings
# ==============================


class OpenAIConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_base: Optional[str] = Field(default=None)
    api_key: Optional[str] = Field(default=None, description="Resolved via loader from env/secrets only")
    org_id: Optional[str] = Field(default=None, description="Optional OpenAI org id")
    timeout_seconds: float = Field(default=30.0)


class ModelRoutingConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    default_provider: str = Field(default="openai")
    default_model: str = Field(default="gpt-4o-mini")

    # Optional overrides
    by_product: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_purpose: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ModelsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    routing: ModelRoutingConfig = Field(default_factory=ModelRoutingConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)


# ==============================
# Policies / Governance Settings
# ==============================


class PoliciesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # High-level switches
    enforce: bool = Field(default=True)
    allow_full_autonomy: bool = Field(default=False)

    # Allow/deny lists (names resolved by registries)
    allowed_tools: List[str] = Field(default_factory=list)
    blocked_tools: List[str] = Field(default_factory=list)

    allowed_models: List[str] = Field(default_factory=list)
    blocked_models: List[str] = Field(default_factory=list)
    model_max_tokens: Optional[int] = Field(
        default=None,
        description="Optional hard ceiling for model max_tokens requests.",
    )
    max_tokens_per_run: Optional[int] = Field(
        default=None,
        description="Optional hard ceiling for total model tokens consumed per run.",
    )
    max_steps: Optional[int] = Field(
        default=None,
        description="Optional hard ceiling for total steps per run.",
    )
    max_tool_calls: Optional[int] = Field(
        default=None,
        description="Optional hard ceiling for tool calls per run.",
    )
    max_payload_bytes: Optional[int] = Field(
        default=None,
        description="Optional hard ceiling for run payload size in bytes.",
    )

    # Per-product policy overrides
    by_product: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


# ==============================
# Logging / Observability Settings
# ==============================


class LoggingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    level: str = Field(default="INFO")
    redact: bool = Field(default=True)
    redact_patterns: List[str] = Field(default_factory=list)
    trace_to_memory: bool = Field(default=True, description="Persist trace events via memory backend")
    console: bool = Field(default=True)


# ==============================
# Products Settings
# ==============================


class ProductsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Where products live (relative to repo_root)
    products_dir: str = Field(default="products")
    enabled: List[str] = Field(default_factory=list, description="Explicit allowlist of products to enable")
    auto_enable: bool = Field(
        default=True,
        description="If true and enabled list is empty, enable all discovered products automatically.",
    )


# ==============================
# Secrets Settings
# ==============================


class SecretsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Common secret surfaces. Keep optional; loader fills.
    openai_api_key: Optional[str] = Field(default=None)
    memory_db_path: Optional[str] = Field(default=None)


# ==============================
# Top-Level Settings
# ==============================


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: AppConfig = Field(default_factory=AppConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    policies: PoliciesConfig = Field(default_factory=PoliciesConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    products: ProductsConfig = Field(default_factory=ProductsConfig)
    secrets: SecretsConfig = Field(default_factory=SecretsConfig)

    def repo_root_path(self) -> Path:
        return Path(self.app.paths.repo_root).expanduser().resolve()
