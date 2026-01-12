# ==============================
# Product Registration (Hello World)
# ==============================
"""
Registers hello_world agents/tools into core registries.

This module uses auto-discovery to register all @agent and @tool
decorated classes from the agents/ and tools/ directories.

This module must remain side-effect safe:
- No persistence
- No network calls
- Only registry registration
"""

from __future__ import annotations

from pathlib import Path

from core.utils.product_loader import ProductRegistries, auto_register


def register(registries: ProductRegistries) -> None:
    """
    Auto-register all agents and tools in this product.

    Agents and tools are discovered by scanning for classes decorated
    with @agent and @tool in the agents/ and tools/ directories.
    """
    auto_register(registries, Path(__file__).parent)
