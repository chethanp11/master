# ==============================
# Approval Form Component
# ==============================
"""
Reusable approval form component.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

import streamlit as st

from gateway.ui.api_client import pretty_json


def render_approval_form(
    approval: Dict[str, Any],
    *,
    on_approve: Optional[Callable[[str], None]] = None,
    on_deny: Optional[Callable[[str], None]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Render an approval form with approve/deny buttons.
    
    Args:
        approval: Approval data dictionary.
        on_approve: Optional callback for approve action.
        on_deny: Optional callback for deny action.
    
    Returns:
        Tuple of (action_taken, action_type) where action_type is 'approve', 'deny', or None.
    """
    if not isinstance(approval, dict):
        st.warning("Invalid approval data.")
        return False, None
    
    approval_id = approval.get("approval_id", "")
    approval_type = approval.get("type", "UNKNOWN")
    description = approval.get("description", "")
    run_id = approval.get("run_id", "")
    step = approval.get("step", "")
    agent = approval.get("agent", "")
    payload = approval.get("payload", {})
    
    st.markdown(f"**Type:** {approval_type}")
    if description:
        st.markdown(f"**Description:** {description}")
    if run_id:
        st.markdown(f"**Run:** `{run_id[:12]}...`")
    if step:
        st.markdown(f"**Step:** {step}")
    if agent:
        st.markdown(f"**Agent:** {agent}")
    
    if payload:
        with st.expander("Payload details"):
            st.code(pretty_json(payload), language="json")
    
    # Comments input
    comments = st.text_area(
        "Comments (optional)",
        key=f"approval_comments_{approval_id}",
        help="Add any notes or reasons for your decision.",
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    action_taken = False
    action_type: Optional[str] = None
    
    with col1:
        if st.button("✅ Approve", key=f"btn_approve_{approval_id}", type="primary"):
            action_taken = True
            action_type = "approve"
            if on_approve:
                on_approve(approval_id)
    
    with col2:
        if st.button("🚫 Deny", key=f"btn_deny_{approval_id}"):
            action_taken = True
            action_type = "deny"
            if on_deny:
                on_deny(approval_id)
    
    return action_taken, action_type
