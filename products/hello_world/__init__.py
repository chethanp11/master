# ==============================
# Hello World Product
# ==============================
"""
Hello World product package.

This product demonstrates core MASTER capabilities with a simple
greeting-based flow. It serves as a reference implementation and
testing ground for framework features.
"""

from __future__ import annotations

from products.hello_world.semantic import (
    HelloWorldSemanticAdapter,
    create_semantic_adapter,
)


# ==============================
# Module Exports
# ==============================
__all__ = [
    "HelloWorldSemanticAdapter",
    "create_semantic_adapter",
]
