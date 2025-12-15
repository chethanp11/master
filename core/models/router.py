# ==============================
# Model Router
# ==============================
"""
Model routing for master/ (v1).

Goals:
- Centralize all model selection decisions behind a single interface.
- Avoid vendor-specific imports outside providers/.
- No env reads here. Configuration is injected by the caller.

v1 keeps this minimal:
- ModelRouter resolves a provider + model name based on simple inputs:
  product, purpose, and optional override fields.

Later upgrades can add:
- per-agent/per-flow overrides
- budget-aware routing
- fallback models
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.models.providers.openai_provider import OpenAIProvider, OpenAIRequest, OpenAIResponse


@dataclass(frozen=True)
class ModelSelection:
    provider: str
    model: str


class ModelRouter:
    """
    Minimal model router.

    Config shape (example):
{
  "default_provider": "openai",
  "default_model": "gpt-4o-mini",
  "by_product": {
     "agentaura": {"model": "gpt-4o"},
  },
  "by_purpose": {
     "reasoning": {"model": "gpt-4o"},
     "cheap": {"model": "gpt-4o-mini"}
  }
}
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None, providers: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.providers = providers or {"openai": OpenAIProvider(config=self.config.get("openai", {}))}

    def select(
        self,
        *,
        product: str,
        purpose: str,
        override_model: Optional[str] = None,
        override_provider: Optional[str] = None,
    ) -> ModelSelection:
        if override_provider and override_model:
            return ModelSelection(provider=override_provider, model=override_model)

        default_provider = str(self.config.get("default_provider", "openai"))
        default_model = str(self.config.get("default_model", "gpt-4o-mini"))

        by_product = self.config.get("by_product", {}) or {}
        by_purpose = self.config.get("by_purpose", {}) or {}

        model = default_model
        if isinstance(by_product, dict) and product in by_product and isinstance(by_product[product], dict):
            model = str(by_product[product].get("model", model))
        if isinstance(by_purpose, dict) and purpose in by_purpose and isinstance(by_purpose[purpose], dict):
            model = str(by_purpose[purpose].get("model", model))

        provider = default_provider
        if override_provider:
            provider = override_provider
        if override_model:
            model = override_model

        return ModelSelection(provider=provider, model=model)

    def completion_openai(
        self,
        *,
        product: str,
        purpose: str,
        request: OpenAIRequest,
        override_model: Optional[str] = None,
    ) -> OpenAIResponse:
        sel = self.select(product=product, purpose=purpose, override_model=override_model, override_provider="openai")
        provider = self._get_provider("openai")
        req = request.model_copy(update={"model": sel.model})
        return provider.complete(req)

    def _get_provider(self, name: str) -> Any:
        p = self.providers.get(name)
        if p is None:
            raise KeyError(f"Unknown model provider: {name}")
        return p