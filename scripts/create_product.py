#!/usr/bin/env python3
"""
scripts/create_product.py

Scaffold a new product under products/<name>/ with required folders and starter files.

Usage:
  python scripts/create_product.py --name myproduct
  python scripts/create_product.py myproduct

Rules:
- Validates product name (lowercase, starts with letter, [a-z0-9_], max 50)
- Refuses to overwrite if product folder exists
- Creates:
    products/<name>/
      __init__.py
      manifest.yaml
      registry.py                # NEW: product registration entrypoint
      flows/.keep
      agents/__init__.py
      tools/__init__.py
      prompts/.keep
      config/product.yaml
      tests/__init__.py
      tests/test_smoke.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Tuple


VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,49}$")


MANIFEST_TEMPLATE = """# Product manifest (tracked in git)
name: "{name}"
display_name: "{display_name}"
description: "TODO: describe this product"
default_flow: "hello_world"

# Exposure flags (used by gateway/UI to hide/show products)
expose_api: true
ui_enabled: true

# Optional UI hints (platform UI can read these later)
ui:
  icon: "🧩"
  category: "prototype"
  notes: "TODO"

# Optional: which flows should appear in UI by default
flows:
  - "hello_world"

# Registration entrypoint (imported by product loader)
entrypoints:
  register_module: "products.{name}.registry"
"""

PRODUCT_CONFIG_TEMPLATE = """# Product config (tracked in git)
# Override global defaults for this product only (no secrets here).
name: "{name}"

defaults:
  autonomy_level: "semi_auto"   # suggest_only | semi_auto | full_auto
  model: "default"             # logical model name resolved by core/models/router.py

limits:
  max_steps: 50
  max_tool_calls: 50
  max_tokens: 8000

flags:
  enable_tools: true
  enable_knowledge: true
"""

SMOKE_TEST_TEMPLATE = """def test_product_scaffold_smoke():
    # Basic smoke test to ensure scaffold exists and is importable.
    assert True
"""

REGISTRY_TEMPLATE = '''# ==============================
# Product Registry (Registration Entrypoint)
# ==============================
"""
products/{name}/registry.py

This is the canonical registration entrypoint for this product.

Rules:
- Keep this module side-effect safe:
  - No persistence
  - No network calls
  - No model calls
- Only register agents/tools with core registries.
- Product loader will import this module to bind components.

How to use:
1) Implement agents in products/{name}/agents/
2) Implement tools in products/{name}/tools/
3) Register them in register()

Example (after you create a tool/agent):
  from core.agents.registry import AgentRegistry
  from core.tools.registry import ToolRegistry
  from products.{name}.agents.my_agent import build as build_agent
  from products.{name}.tools.my_tool import build as build_tool

  def register() -> None:
      AgentRegistry.register(build_agent().name, build_agent())
      ToolRegistry.register(build_tool().name, build_tool())
"""

from __future__ import annotations


def register() -> None:
    # TODO: register your agents/tools here.
    # Keep this safe: no DB writes, no HTTP, no vendor calls.
    return
'''

KEEP_FILE_NOTE = (
    "# Placeholder file to keep this folder in git.\n"
    "# Remove this once you add real files.\n"
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a new product under products/<name>/")
    parser.add_argument("positional_name", nargs="?", help="Product name (alternative to --name)")
    parser.add_argument("--name", "-n", dest="name", help="Product name (lowercase, [a-z0-9_])")
    parser.add_argument(
        "--root",
        default=".",
        help="Repo root (defaults to current directory). products/ will be created under this.",
    )
    return parser.parse_args(argv)


def validate_name(name: str) -> Tuple[bool, str]:
    if not name:
        return False, "Product name is required."
    if not VALID_NAME_RE.match(name):
        return (
            False,
            "Invalid product name. Use: lowercase, start with letter, only [a-z0-9_], max 50 chars.",
        )
    return True, ""


def ensure_not_exists(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing product at: {path}")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def touch_keep(path: Path) -> None:
    write_file(path, KEEP_FILE_NOTE)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    name = (args.name or args.positional_name or "").strip()

    ok, msg = validate_name(name)
    if not ok:
        print(f"❌ {msg}", file=sys.stderr)
        return 2

    repo_root = Path(args.root).resolve()
    products_dir = repo_root / "products"
    product_dir = products_dir / name

    try:
        ensure_not_exists(product_dir)
    except FileExistsError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 3

    # ==============================
    # Create base folders
    # ==============================
    (product_dir / "__init__.py").parent.mkdir(parents=True, exist_ok=True)
    write_file(product_dir / "__init__.py", "")

    (product_dir / "flows").mkdir(parents=True, exist_ok=True)
    (product_dir / "agents").mkdir(parents=True, exist_ok=True)
    (product_dir / "tools").mkdir(parents=True, exist_ok=True)
    (product_dir / "prompts").mkdir(parents=True, exist_ok=True)
    (product_dir / "config").mkdir(parents=True, exist_ok=True)
    (product_dir / "tests").mkdir(parents=True, exist_ok=True)

    # ==============================
    # Package init files
    # ==============================
    write_file(product_dir / "agents" / "__init__.py", "")
    write_file(product_dir / "tools" / "__init__.py", "")
    write_file(product_dir / "tests" / "__init__.py", "")

    # ==============================
    # Keep placeholders
    # ==============================
    touch_keep(product_dir / "flows" / ".keep")
    touch_keep(product_dir / "prompts" / ".keep")

    # ==============================
    # Starter manifest + product config
    # ==============================
    display_name = name.replace("_", " ").title()
    write_file(product_dir / "manifest.yaml", MANIFEST_TEMPLATE.format(name=name, display_name=display_name))
    write_file(product_dir / "config" / "product.yaml", PRODUCT_CONFIG_TEMPLATE.format(name=name))

    # ==============================
    # NEW: registry.py entrypoint
    # ==============================
    write_file(product_dir / "registry.py", REGISTRY_TEMPLATE.format(name=name))

    # ==============================
    # Starter test
    # ==============================
    write_file(product_dir / "tests" / "test_smoke.py", SMOKE_TEST_TEMPLATE)

    # ==============================
    # Next steps
    # ==============================
    print("✅ Product scaffold created:")
    print(f"   {product_dir.relative_to(repo_root)}")
    print("")
    print("Next steps:")
    print(f"  1) Add flows:        products/{name}/flows/<flow>.yaml")
    print(f"  2) Add agents:       products/{name}/agents/<agent>.py (register in products/{name}/registry.py)")
    print(f"  3) Add tools:        products/{name}/tools/<tool>.py (register in products/{name}/registry.py)")
    print(f"  4) Update manifest:  products/{name}/manifest.yaml (default_flow, exposure flags)")
    print(f"  5) Run tests:        pytest -q")
    print("")
    print("Tip: Start with a simple hello_world flow + one tool + one agent + one HITL step.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))