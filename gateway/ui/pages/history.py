# ==============================
# History Page
# ==============================
"""
Run history and event timeline view for the Platform UI.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from gateway.ui.api_client import ApiClient, pretty_json


def render_history_page(client: ApiClient) -> None:
    """Render the run history page with list of historical runs."""
    st.subheader("Run History")
    st.caption("View all historical runs and their details.")
    
    history: List[str] = st.session_state.get("run_history", [])
    if not history:
        st.info("No runs in session history yet. Start a run from the Execution page.")
        return
    
    # Display run list
    st.markdown("### Historical Runs")
    
    # Collect run info for all history items
    runs_info: List[Dict[str, Any]] = []
    for run_id in reversed(history):
        resp = client.get_run(run_id)
        if resp.ok and resp.body:
            run_data = resp.body.get("data", {}).get("run", {})
            if isinstance(run_data, dict):
                runs_info.append({
                    "run_id": run_id,
                    "status": run_data.get("status", "UNKNOWN"),
                    "product": run_data.get("product", "-"),
                    "flow": run_data.get("flow", "-"),
                    "created_at": run_data.get("created_at", "")[:19] if run_data.get("created_at") else "-",
                })
            else:
                runs_info.append({
                    "run_id": run_id,
                    "status": "UNKNOWN",
                    "product": "-",
                    "flow": "-",
                    "created_at": "-",
                })
        else:
            runs_info.append({
                "run_id": run_id,
                "status": "ERROR",
                "product": "-",
                "flow": "-",
                "created_at": "-",
            })
    
    # Display runs in a table-like format
    for run_info in runs_info:
        status = run_info["status"]
        status_icon = _get_status_icon(status)
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.markdown(f"**{run_info['run_id'][:16]}...**")
        with col2:
            st.markdown(f"{status_icon} {status}")
        with col3:
            st.markdown(f"{run_info['product']}/{run_info['flow']}")
        with col4:
            st.markdown(f"{run_info['created_at']}")
    
    st.markdown("---")
    
    # Select a run to view details
    st.markdown("### Run Details")
    selected_run = st.selectbox("Select a run to view details", [r["run_id"] for r in runs_info])
    if not selected_run:
        return
    
    _render_run_details(client, selected_run)
    _render_run_events(client, selected_run)


def _get_status_icon(status: str) -> str:
    """Return an icon for the status."""
    icons = {
        "COMPLETED": "✅",
        "RUNNING": "🔄",
        "PENDING": "⏳",
        "FAILED": "❌",
        "PAUSED": "⏸️",
        "PAUSED_WAITING_FOR_USER": "❓",
        "PENDING_USER_INPUT": "❓",
        "NEEDS_USER_INPUT": "❓",
        "PENDING_APPROVAL": "🔒",
        "PAUSED_FOR_APPROVAL": "🔒",
        "CANCELLED": "🚫",
        "ERROR": "⚠️",
        "UNKNOWN": "❔",
    }
    return icons.get(status, "📌")


def _render_run_details(client: ApiClient, run_id: str) -> None:
    """Render run details."""
    resp = client.get_run(run_id)
    if not resp.ok or not resp.body:
        st.warning(f"Could not load run {run_id}: {resp.error or resp.body}")
        return
    
    run_data = resp.body.get("data", {}).get("run", {})
    if not isinstance(run_data, dict):
        run_data = {}
    
    status = run_data.get("status", "UNKNOWN")
    product = run_data.get("product", "")
    flow = run_data.get("flow", "")
    created_at = run_data.get("created_at", "")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Status", status)
    with col2:
        st.metric("Product", product)
    with col3:
        st.metric("Flow", flow)
    with col4:
        st.metric("Created", created_at[:19] if created_at else "-")
    
    with st.expander("Raw run data"):
        st.code(pretty_json(run_data), language="json")


def _render_run_events(client: ApiClient, run_id: str) -> None:
    """Render run event timeline."""
    st.markdown("### Event Timeline")
    
    resp = client.get_run_events(run_id)
    if not resp.ok or not resp.body:
        st.info("No events available.")
        return
    
    events = resp.body.get("data", {}).get("events", [])
    if not isinstance(events, list) or not events:
        st.info("No events recorded for this run.")
        return
    
    for event in events:
        if not isinstance(event, dict):
            continue
        
        event_type = event.get("event_type", "UNKNOWN")
        timestamp = event.get("timestamp", "")[:19] if event.get("timestamp") else ""
        data = event.get("data", {})
        
        icon = _get_event_icon(event_type)
        with st.expander(f"{icon} {event_type} - {timestamp}"):
            if isinstance(data, dict):
                st.code(pretty_json(data), language="json")
            else:
                st.write(data)


def _get_event_icon(event_type: str) -> str:
    """Return an icon for the event type."""
    icons = {
        "RUN_STARTED": "🚀",
        "RUN_COMPLETED": "✅",
        "RUN_FAILED": "❌",
        "STEP_STARTED": "▶️",
        "STEP_COMPLETED": "✔️",
        "STEP_FAILED": "⚠️",
        "USER_INPUT_REQUESTED": "❓",
        "USER_INPUT_RECEIVED": "💬",
        "APPROVAL_REQUESTED": "🔒",
        "APPROVAL_GRANTED": "✅",
        "APPROVAL_DENIED": "🚫",
        "TOOL_CALLED": "🔧",
        "TOOL_RESULT": "📤",
        "LLM_CALL": "🤖",
        "LLM_RESPONSE": "💡",
    }
    return icons.get(event_type, "📌")
