# ==============================
# Platform UI (Streamlit) - v2 Modular Entry Point
# ==============================
"""
Streamlit-based Platform Control Center for master/.

This is a slim entry point that delegates to modular page components.
All page rendering logic has been extracted to:
- gateway/ui/pages/home.py
- gateway/ui/pages/execution.py (Run, Approvals, User Inputs)
- gateway/ui/pages/history.py

All HTTP client logic is in:
- gateway/ui/api_client.py
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import streamlit as st

# Ensure repo root is on path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.config.loader import load_settings

from gateway.ui.api_client import ApiClient, get_api_base_url
from gateway.ui.pages import (
    render_home_page,
    render_execution_page,
    render_history_page,
)


def _observability_root(settings: Optional[Any] = None) -> Path:
    """Resolve the observability root directory."""
    resolved = settings or load_settings(repo_root=str(REPO_ROOT))
    path = Path(resolved.app.paths.observability_dir)
    return path if path.is_absolute() else (resolved.repo_root_path() / path)


def main() -> None:
    """Main entry point for the Platform UI."""
    st.set_page_config(page_title="master platform", layout="wide")
    
    # Load settings and initialize client
    settings = load_settings(repo_root=str(REPO_ROOT))
    observability_root = _observability_root(settings)
    api_base = get_api_base_url(settings)
    client = ApiClient(api_base)

    # Navigation sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Section", ["Home", "Execution", "History"])
    st.sidebar.caption(f"API base: {api_base}")

    # Initialize session state
    st.session_state.setdefault("run_history", [])

    # Load products
    products_resp = client.list_products()
    if not products_resp.ok or not products_resp.body:
        st.error(f"Cannot load products: {products_resp.error or 'Unknown error'}")
        return

    products: List[Dict[str, Any]] = sorted(
        products_resp.body["data"]["products"], 
        key=lambda p: p["name"]
    )

    # Route to appropriate page
    if page == "Home":
        render_home_page(products)
    elif page == "Execution":
        render_execution_page(client, products, observability_root, REPO_ROOT)
    elif page == "History":
        render_history_page(client)


if __name__ == "__main__":
    main()
