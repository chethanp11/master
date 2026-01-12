# ==============================
# Product Registry (Registration Entrypoint)
# ==============================
"""
products/ade/registry.py

This is the canonical registration entrypoint for this product.

Rules:
- Keep this module side-effect safe:
  - No persistence
  - No network calls
  - No model calls
- Only register agents/tools with core registries.
- Product loader will import this module to bind components.

How to use:
1) Implement agents in products/ade/agents/ with @agent decorator
2) Implement tools in products/ade/tools/ with @tool decorator
3) Call auto_register() in register() - no manual registration needed!

The @agent and @tool decorators define the descriptors inline with the class,
and auto_register() discovers and registers all decorated components automatically.
"""

from __future__ import annotations

from pathlib import Path

from core.utils.product_loader import ProductRegistries, auto_register


def register(registries: ProductRegistries) -> None:
    """Auto-discover and register all decorated agents and tools."""
    auto_register(registries, Path(__file__).parent)
