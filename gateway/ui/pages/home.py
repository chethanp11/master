# ==============================
# Home Page
# ==============================
"""
Product catalog view for the Platform UI.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st


def render_home_page(products: List[Dict[str, Any]]) -> None:
    """Render the home page with product catalog."""
    render_product_summary(products)


def render_product_summary(products: List[Dict[str, Any]]) -> None:
    """Render a summary of all enabled products."""
    st.subheader("Products")
    
    if not products:
        st.info("No enabled products were discovered.")
        return

    for product in sorted(products, key=lambda p: p["name"]):
        header = f"{product['display_name']} ({product['name']})"
        with st.expander(header, expanded=False):
            st.write(product.get("description") or "No description provided.")
            st.markdown("**Flows**")
            flows = sorted(product.get("flows", []))
            st.write(", ".join(flows) if flows else "_No flows defined yet_")
