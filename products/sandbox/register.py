# ==============================
# Product Registration Entrypoint (Sandbox)
# ==============================
"""
Importable entrypoint referenced by manifest.yaml to register sandbox assets.
"""

from products.sandbox import registry as sandbox_registry  # noqa: F401  (module does registration on import)
