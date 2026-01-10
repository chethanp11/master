from __future__ import annotations

# ==============================
# Retrieval Policy Resolver
# ==============================
"""
Policy resolver for approved retrieval sources.
"""

from typing import List, Dict, Any

from core.config.schema import Settings


def resolve_allowed_sources(settings: Settings, *, product: str, flow: str) -> List[str]:
    default_allowed: List[str] = []
    overrides: Dict[str, Any] = settings.policies.by_product.get(product, {}) if settings.policies.by_product else {}
    flow_overrides = overrides.get("retrieval_allowed_sources_by_flow", {}) if isinstance(overrides, dict) else {}
    if isinstance(flow_overrides, dict):
        flow_allowed = flow_overrides.get(flow)
        if isinstance(flow_allowed, list):
            return list(flow_allowed)
    product_allowed = overrides.get("retrieval_allowed_sources") if isinstance(overrides, dict) else None
    if isinstance(product_allowed, list):
        return list(product_allowed)
    return default_allowed
