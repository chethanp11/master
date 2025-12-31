#!/usr/bin/env python3
"""
scripts/create_product.py

Scaffold a new product under products/<name>/.

Usage:
  python scripts/create_product.py --name myproduct
  python scripts/create_product.py myproduct
  python scripts/create_product.py --name myproduct --base visual_insights
  python scripts/create_product.py --name myproduct --minimal

Rules:
- Validates product name (lowercase, starts with letter, [a-z0-9_], max 50)
- Refuses to overwrite if product folder exists
- By default, clones products/<base>/ (defaults to visual_insights), then rewrites product references.
- Optional: use --minimal to create the minimal scaffold instead.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, Tuple


VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,49}$")


MANIFEST_TEMPLATE = """# Product manifest (tracked in git)
name: "{name}"
display_name: "{display_name}"
description: "TODO: describe this product"
version: "0.1.0"

default_flow: "hello_world"

exposed_api:
  enabled: true
  allowed_flows:
    - "hello_world"

ui_enabled: true
ui:
  enabled: true
  nav_label: "{display_name}"
  panels:
    - id: "runner"
      title: "Run a Flow"

flows:
  - "hello_world"
"""

PRODUCT_CONFIG_TEMPLATE = """# Product config (tracked in git)
# Override global defaults for this product only (no secrets here).
name: "{name}"

defaults:
  autonomy_level: "semi_auto"
  model: "default"

limits:
  max_steps: 50
  max_tool_calls: 50

flags:
  enable_tools: true
  enable_knowledge: true

metadata:
  ui:
    inputs:
      enabled: false
      allowed_types: []
      max_files: 5
      files_field: "files"
      upload_id_field: "upload_id"
      dataset_field: "dataset"
    intent:
      enabled: false
      field: "prompt"
      label: "Instructions"
      help: "Optional guidance for the analysis."
      default: ""
    outputs:
      enabled: true
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
  from core.utils.product_loader import ProductRegistries
  from products.{name}.agents.my_agent import build as build_agent
  from products.{name}.tools.my_tool import build as build_tool

  def register(registries: ProductRegistries) -> None:
      registries.agent_registry.register(build_agent().name, build_agent)
      registries.tool_registry.register(build_tool().name, build_tool)
"""

from __future__ import annotations


from core.utils.product_loader import ProductRegistries


def register(registries: ProductRegistries) -> None:
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
        "--base",
        default="visual_insights",
        help="Base product to copy (defaults to visual_insights).",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Create a minimal scaffold instead of copying a base product.",
    )
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


def copy_base_product(*, base_dir: Path, target_dir: Path) -> None:
    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    )
    shutil.copytree(base_dir, target_dir, ignore=ignore)


def iter_text_files(root: Path) -> Iterable[Path]:
    text_exts = {".py", ".md", ".yaml", ".yml", ".json", ".txt", ".ini", ".toml"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in text_exts:
            continue
        yield path


def rewrite_product_references(
    root: Path,
    *,
    base_name: str,
    name: str,
    display_name: str,
) -> None:
    base_display_name = base_name.replace("_", " ").title()
    replacements = [
        (f"products.{base_name}", f"products.{name}"),
        (base_display_name, display_name),
        (base_name, name),
    ]
    for path in iter_text_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = content
        for old, new in replacements:
            updated = updated.replace(old, new)
        if updated != content:
            path.write_text(updated, encoding="utf-8")


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
    base_name = (args.base or "").strip()
    base_dir = products_dir / base_name if base_name else None

    try:
        ensure_not_exists(product_dir)
    except FileExistsError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 3

    display_name = name.replace("_", " ").title()

    if args.minimal:
        # ==============================
        # Create base folders
        # ==============================
        (product_dir / "__init__.py").parent.mkdir(parents=True, exist_ok=True)
        write_file(product_dir / "__init__.py", "")

        (product_dir / "flows").mkdir(parents=True, exist_ok=True)
        (product_dir / "agents").mkdir(parents=True, exist_ok=True)
        (product_dir / "tools").mkdir(parents=True, exist_ok=True)
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

        # ==============================
        # Starter manifest + product config
        # ==============================
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
    else:
        if not base_dir or not base_dir.exists():
            print(f"❌ Base product not found: {base_dir}", file=sys.stderr)
            return 4
        copy_base_product(base_dir=base_dir, target_dir=product_dir)
        rewrite_product_references(
            product_dir,
            base_name=base_name,
            name=name,
            display_name=display_name,
        )

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
    if args.minimal:
        print("Tip: Start with a simple hello_world flow + one tool + one agent + one HITL step.")
    else:
        print(f"Tip: Base copied from products/{base_name}/. Review config, flows, and registry for {name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
