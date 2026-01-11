# ==============================
# Run Card Component
# ==============================
"""
Reusable run card and step table components.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from gateway.ui.api_client import pretty_json


def render_run_card(run_data: Dict[str, Any]) -> None:
    """
    Render a run summary card.
    
    Args:
        run_data: Run data dictionary with status, product, flow, etc.
    """
    if not isinstance(run_data, dict):
        st.warning("Invalid run data.")
        return
    
    run_id = run_data.get("run_id", "")
    status = run_data.get("status", "UNKNOWN")
    product = run_data.get("product", "")
    flow = run_data.get("flow", "")
    created_at = run_data.get("created_at", "")
    
    status_color = _get_status_color(status)
    
    st.markdown(
        f"""
        <div style="border: 1px solid #ccc; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0;">Run: {run_id[:12]}...</h4>
                <span style="background-color: {status_color}; color: white; padding: 4px 8px; border-radius: 4px;">{status}</span>
            </div>
            <p style="margin: 8px 0 0 0; color: #666;">
                <strong>Product:</strong> {product} | <strong>Flow:</strong> {flow}
            </p>
            <p style="margin: 4px 0 0 0; color: #888; font-size: 0.9em;">
                Created: {created_at[:19] if created_at else '-'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_table(steps: List[Dict[str, Any]]) -> None:
    """
    Render a table of run steps.
    
    Args:
        steps: List of step dictionaries with name, status, duration, etc.
    """
    if not steps:
        st.info("No steps recorded.")
        return
    
    import pandas as pd
    
    rows = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        rows.append({
            "Step": step.get("name", ""),
            "Status": step.get("status", "UNKNOWN"),
            "Duration": f"{step.get('duration_ms', 0)}ms",
            "Agent": step.get("agent", ""),
        })
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No steps to display.")


def _get_status_color(status: str) -> str:
    """Return a color for the given status."""
    colors = {
        "COMPLETED": "#28a745",
        "RUNNING": "#007bff",
        "PENDING": "#6c757d",
        "FAILED": "#dc3545",
        "PAUSED": "#ffc107",
        "PAUSED_WAITING_FOR_USER": "#ffc107",
        "PENDING_USER_INPUT": "#ffc107",
        "NEEDS_USER_INPUT": "#ffc107",
        "CANCELLED": "#6c757d",
    }
    return colors.get(status, "#6c757d")
