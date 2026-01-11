# ==============================
# Execution Page
# ==============================
"""
Combined execution view: Run, Approvals, and User Inputs.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from gateway.ui.api_client import ApiClient, pretty_json


def render_execution_page(
    client: ApiClient,
    products: List[Dict[str, Any]],
    observability_root: Path,
    repo_root: Path,
) -> None:
    """Render the combined execution page with tabs for Run, Approvals, User Inputs."""
    
    tab_run, tab_approvals, tab_inputs = st.tabs(["▶️ Run", "🔒 Approvals", "❓ User Inputs"])
    
    with tab_run:
        _render_run_section(client, products, observability_root, repo_root)
    
    with tab_approvals:
        _render_approvals_section(client)
    
    with tab_inputs:
        _render_user_inputs_section(client)


# ============================================================================
# Run Section
# ============================================================================

def _render_run_section(
    client: ApiClient,
    products: List[Dict[str, Any]],
    observability_root: Path,
    repo_root: Path,
) -> None:
    """Render the run execution section."""
    st.subheader("Trigger a flow")
    
    if not products:
        st.info("No enabled products discovered.")
        return

    prod = st.selectbox("Product", [prod["name"] for prod in products], key="exec_product")
    product_record = _get_product_record(products, prod)
    product_config = _get_product_config(product_record)
    
    flows_resp = client.list_flows(prod)
    if not flows_resp.ok or not flows_resp.body:
        st.warning(f"Unable to get flows for '{prod}': {flows_resp.error or flows_resp.body}")
        flows = []
    else:
        flows = sorted(flows_resp.body["data"]["flows"])

    if not flows:
        st.info(f"No flows defined for {prod}.")
        return

    flow = st.selectbox("Flow", flows, key="exec_flow")
    
    # Handle file uploads
    file_refs: List[Dict[str, Any]] = []
    input_spec = _resolve_input_spec(product_config)
    allowed_types = input_spec.get("allowed_types") or []
    if isinstance(allowed_types, list):
        allowed_types = [
            str(ext).lower().lstrip(".") for ext in allowed_types if str(ext).strip()
        ]
    else:
        allowed_types = []
    
    inputs_enabled = bool(input_spec.get("enabled", bool(allowed_types)))
    max_files = input_spec.get("max_files")
    files_field = input_spec.get("files_field") or "files"
    upload_id_field = input_spec.get("upload_id_field") or "upload_id"
    dataset_field = input_spec.get("dataset_field")
    upload_key = f"{prod}_upload_id"
    items_key = f"{prod}_upload_items"

    if inputs_enabled and allowed_types:
        st.markdown("### Upload files")
        uploaded = st.file_uploader(
            "Attach data files",
            type=allowed_types,
            accept_multiple_files=(max_files is None or max_files != 1),
            key="exec_file_upload",
        )
        include_uploads = st.checkbox("Include uploaded files in payload", value=True, key="exec_include_uploads")
        if uploaded and include_uploads:
            upload_id = st.session_state.get(upload_key)
            if not upload_id:
                upload_id = str(int(time.time()))
                st.session_state[upload_key] = upload_id
            file_refs, items = _save_uploaded_files(uploaded, upload_id=upload_id)
            if items:
                _write_inputs_to_uploads(
                    observability_root,
                    repo_root=repo_root,
                    product=prod,
                    upload_id=upload_id,
                    items=items,
                )
                st.caption(f"Files staged for upload {upload_id}.")
            if file_refs:
                st.code(pretty_json({files_field: file_refs}), language="json")
            st.session_state[items_key] = items

    # Build payload
    payload: Dict[str, Any] = {}
    ok = True
    intent_spec = _resolve_intent_spec(product_config)
    intent_enabled = bool(intent_spec.get("enabled", False))
    
    if intent_enabled:
        intent_field = str(intent_spec.get("field") or "prompt")
        intent_label = intent_spec.get("label") or "Instructions"
        intent_help = intent_spec.get("help") or "Optional guidance for the analysis."
        intent_default = intent_spec.get("default") or ""
        instructions = st.text_area(
            intent_label,
            value=intent_default,
            height=140,
            help=intent_help,
            key="exec_instructions",
        )
        payload[intent_field] = instructions.strip() if instructions else ""
    else:
        payload_key = f"{prod}_payload_json"
        if payload_key not in st.session_state:
            st.session_state[payload_key] = "{}"
        example_key = f"{prod}_example_loaded"
        if st.button("Load Example", type="secondary", key="exec_load_example"):
            st.session_state[example_key] = True
            if prod == "hello_world":
                st.session_state[payload_key] = pretty_json({"keyword": "Hello from the demo"})
            else:
                st.session_state[payload_key] = pretty_json({
                    "dataset": "ade_input.csv",
                    "prompt": "Summarize key trends and highlight anomalies.",
                    "files": [{"name": "ade_input.csv", "file_type": "csv"}],
                    "upload_id": "demo_upload_1",
                })
        payload_text = st.text_area(
            "Payload (JSON)",
            value=st.session_state[payload_key],
            height=220,
            key="exec_payload",
        )
        st.session_state[payload_key] = payload_text
        ok, payload, err = _safe_json_loads(payload_text)
        if not ok:
            st.error(f"Invalid JSON: {err}")

    # Dataset selection
    if dataset_field:
        candidates = _list_dataset_candidates(prod, repo_root=repo_root, allowed_types=allowed_types)
        selected_value: Optional[str] = None
        if candidates:
            selection = st.selectbox(
                "Dataset",
                ["(none)"] + candidates + ["(custom)"],
                help="Select a staged or built-in dataset, or enter a custom dataset name.",
                key="exec_dataset",
            )
            if selection == "(custom)":
                selected_value = st.text_input(
                    "Dataset name", value=str(payload.get(dataset_field, "")), key="exec_dataset_custom"
                )
            elif selection != "(none)":
                selected_value = selection
        else:
            selected_value = st.text_input(
                "Dataset name",
                value=str(payload.get(dataset_field, "")),
                help="Enter a dataset name staged under the product input directory.",
                key="exec_dataset_name",
            )
        if selected_value:
            payload[dataset_field] = selected_value.strip()

    # Add file refs to payload
    if file_refs:
        payload.setdefault(files_field, file_refs)
        payload[upload_id_field] = st.session_state.get(upload_key)
        if dataset_field and dataset_field not in payload:
            csv_name = next(
                (f["name"] for f in file_refs if f["file_type"] == "csv"), None
            )
            if csv_name:
                payload[dataset_field] = csv_name
        st.markdown("### Payload preview")
        st.code(pretty_json(payload), language="json")

    # Run button
    if flow and st.button("Run flow", disabled=(not ok), key="exec_run_btn"):
        resp = client.run_flow(prod, flow, payload)
        st.code(pretty_json(resp.body or resp.error), language="json")
        if resp.ok and resp.body:
            run_id = resp.body.get("data", {}).get("run_id")
            if run_id:
                st.success(f"Run started: {run_id}")
                _append_history(run_id)
                _materialize_run_dirs(observability_root, product=prod, run_id=run_id)
                st.session_state["last_run_id"] = run_id
                st.session_state["last_run_status"] = resp.body.get("data", {}).get("status")
                st.session_state["last_run_product"] = prod
                st.session_state["last_run_flow"] = flow

    # Refresh status button
    last_run_id = st.session_state.get("last_run_id")
    if st.button("Refresh run status", disabled=not last_run_id, key="exec_refresh_btn"):
        refreshed = _refresh_last_run_status(client, last_run_id or "")
        if refreshed:
            st.success(f"Run status refreshed: {refreshed}")
        else:
            st.warning("Unable to refresh run status.")

    # Show current run status
    last_status = st.session_state.get("last_run_status")
    if last_run_id and last_status:
        st.info(f"Last run: `{last_run_id[:12]}...` - Status: **{last_status}**")
        if last_status in {"PAUSED_WAITING_FOR_USER", "PENDING_USER_INPUT", "NEEDS_USER_INPUT"}:
            st.warning("⚠️ This run requires user input. Switch to the **User Inputs** tab.")
        elif last_status in {"PENDING_APPROVAL", "PAUSED_FOR_APPROVAL"}:
            st.warning("⚠️ This run requires approval. Switch to the **Approvals** tab.")


# ============================================================================
# Approvals Section
# ============================================================================

def _render_approvals_section(client: ApiClient) -> None:
    """Render the approvals section."""
    st.subheader("Pending Approvals")
    st.caption("Review execution details and provide approval decisions. Your comments guide reasoning and planning.")
    
    resp = client.get_pending_approvals()
    if not resp.ok or not resp.body:
        st.info("No pending approvals.")
        return
    
    approvals = resp.body.get("data", {}).get("approvals", [])
    if not isinstance(approvals, list) or not approvals:
        st.info("No pending approvals at this time.")
        return
    
    for approval in approvals:
        if not isinstance(approval, dict):
            continue
        _render_approval_item(client, approval)


def _render_approval_item(client: ApiClient, approval: Dict[str, Any]) -> None:
    """Render a single approval item with execution details."""
    approval_id = approval.get("approval_id", "")
    run_id = approval.get("run_id", "")
    step_id = approval.get("step_id", "")
    approval_type = approval.get("type", "UNKNOWN")
    product = approval.get("product", "")
    flow = approval.get("flow", "")
    created_at = approval.get("created_at", "")[:19] if approval.get("created_at") else ""
    
    # Extract payload details
    payload = approval.get("payload") or {}
    summary = payload.get("summary") or ""
    instructions = payload.get("instructions") or ""
    actions = payload.get("actions") or []
    approval_context = payload.get("approval_context") or {}
    intent = payload.get("intent") or ""
    
    # Header
    st.markdown(f"### 🔒 Approval Required")
    st.markdown(f"**Run:** `{run_id[:12]}...` | **Product:** {product} | **Flow:** {flow}")
    st.markdown(f"**Step:** {step_id} | **Type:** {approval_type} | **Created:** {created_at}")
    
    # What needs approval
    st.markdown("---")
    st.markdown("#### What needs approval?")
    
    if intent:
        st.markdown(f"**User Intent:** {intent}")
    
    if summary:
        st.markdown(f"**Summary:** {summary}")
    
    if isinstance(approval_context, dict):
        reason = approval_context.get("reason")
        step_name = approval_context.get("step_name")
        decision_notes = approval_context.get("decision_notes") or []
        recommended = approval_context.get("recommended_action")
        
        if step_name:
            st.markdown(f"**Step Name:** {step_name}")
        if reason:
            st.markdown(f"**Reason for Approval:** {reason}")
        if decision_notes:
            st.markdown("**Decision Notes:**")
            for note in decision_notes:
                st.markdown(f"- {note}")
        if recommended:
            st.success(f"**Recommended Action:** {recommended}")
    
    # Actions taken
    if actions:
        st.markdown("#### Actions Taken")
        if isinstance(actions, list):
            for action in actions:
                st.markdown(f"- {action}")
        else:
            st.write(actions)
    
    # Approval decision
    st.markdown("---")
    st.markdown("#### Your Decision")
    
    comment_key = f"approval_comment_{approval_id}"
    comment = st.text_area(
        "Comments (optional - used for reasoning and planning)",
        key=comment_key,
        height=100,
        help="Provide guidance or notes. These will be used by the system for reasoning and re-planning if needed.",
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve", key=f"approve_{approval_id}", type="primary"):
            resp = client.resume_run(
                run_id,
                decision="APPROVED",
                approval_payload={"approved": True},
                comment=comment or None,
            )
            if resp.ok:
                st.success("Approved! Run will continue.")
                st.rerun()
            else:
                st.error(f"Failed to approve: {resp.error or resp.body}")
    with col2:
        if st.button("🚫 Reject", key=f"deny_{approval_id}"):
            resp = client.resume_run(
                run_id,
                decision="REJECTED",
                approval_payload={"approved": False},
                comment=comment or None,
            )
            if resp.ok:
                st.success("Rejected. Run will be stopped or re-planned.")
                st.rerun()
            else:
                st.error(f"Failed to reject: {resp.error or resp.body}")
    
    with st.expander("Raw Approval Details"):
        st.code(pretty_json(approval), language="json")
    
    st.divider()


# ============================================================================
# User Inputs Section
# ============================================================================

def _render_user_inputs_section(client: ApiClient) -> None:
    """Render the user inputs section for pending input requests."""
    st.subheader("User Inputs")
    st.caption("Provide guidance and context for the system. Your input is used for reasoning and planning.")
    
    history: List[str] = st.session_state.get("run_history", [])
    pending_inputs: List[Tuple[str, Dict[str, Any]]] = []
    
    # Scan recent runs for pending inputs
    for run_id in reversed(history[:20]):
        resp = client.get_run(run_id)
        if not resp.ok or not resp.body:
            continue
        run = resp.body.get("data", {}).get("run", {})
        status = run.get("status", "") if isinstance(run, dict) else ""
        if status in {"PAUSED_WAITING_FOR_USER", "PENDING_USER_INPUT", "NEEDS_USER_INPUT"}:
            pending_resp = client.get_pending_input(run_id)
            if pending_resp.ok and pending_resp.body:
                prompt = pending_resp.body.get("data", {}).get("prompt")
                if isinstance(prompt, dict):
                    pending_inputs.append((run_id, prompt))
    
    if not pending_inputs:
        st.info("No pending user inputs at this time.")
        return
    
    for run_id, prompt in pending_inputs:
        _render_user_input_item(client, run_id, prompt)


def _render_user_input_item(
    client: ApiClient, run_id: str, prompt: Dict[str, Any]
) -> None:
    """Render a single user input request as simple text input."""
    prompt_id = prompt.get("prompt_id", "")
    question = prompt.get("question", "Please provide your input")
    title = prompt.get("title", "")
    
    st.markdown(f"### ❓ Input Required")
    st.markdown(f"**Run:** `{run_id[:12]}...`")
    
    if title:
        st.markdown(f"**{title}**")
    
    # Display the question prominently
    st.markdown("---")
    st.markdown(f"#### {question}")
    
    # Simple text input only
    input_key = f"user_input_{run_id}_{prompt_id}"
    user_response = st.text_area(
        "Your response",
        key=input_key,
        height=150,
        help="Provide your input. This will be used by the system for reasoning and planning.",
        placeholder="Enter your response here...",
    )
    
    if st.button("Submit", key=f"submit_{run_id}_{prompt_id}", type="primary"):
        if not user_response.strip():
            st.warning("Please provide a response before submitting.")
            return
        
        # Submit as free_text which is used for reasoning
        resp = client.submit_user_input(
            run_id,
            prompt_id=prompt_id,
            selected_option_ids=None,
            free_text=user_response.strip(),
            metadata={"source": "ui_inputs_tab"},
            values={"response": user_response.strip()},
        )
        if resp.ok:
            st.success("Input submitted! The system will use this for reasoning and planning.")
            st.rerun()
        else:
            st.error(f"Failed to submit: {resp.error or resp.body}")
    
    st.divider()


# ============================================================================
# Helper Functions
# ============================================================================

def _get_product_record(products: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
    for product in products:
        if product.get("name") == name:
            return product
    return {}


def _get_product_config(product: Dict[str, Any]) -> Dict[str, Any]:
    config = product.get("config") or {}
    return config if isinstance(config, dict) else {}


def _resolve_input_spec(config: Dict[str, Any]) -> Dict[str, Any]:
    metadata = config.get("metadata") if isinstance(config, dict) else None
    if not isinstance(metadata, dict):
        metadata = {}
    ui = metadata.get("ui")
    if isinstance(ui, dict):
        inputs = ui.get("inputs")
        if isinstance(inputs, dict):
            return inputs
    inputs = metadata.get("inputs")
    if isinstance(inputs, dict):
        return inputs
    for value in metadata.values():
        if isinstance(value, dict) and isinstance(value.get("inputs"), dict):
            return value.get("inputs") or {}
    return {}


def _resolve_intent_spec(config: Dict[str, Any]) -> Dict[str, Any]:
    metadata = config.get("metadata") if isinstance(config, dict) else None
    if not isinstance(metadata, dict):
        metadata = {}
    ui = metadata.get("ui")
    if isinstance(ui, dict):
        intent = ui.get("intent")
        if isinstance(intent, dict):
            return intent
    intent = metadata.get("intent")
    if isinstance(intent, dict):
        return intent
    for value in metadata.values():
        if isinstance(value, dict) and isinstance(value.get("intent"), dict):
            return value.get("intent") or {}
    return {}


def _safe_json_loads(value: str) -> Tuple[bool, Dict[str, Any], str]:
    import json
    try:
        parsed = json.loads(value or "{}")
        if not isinstance(parsed, dict):
            return False, {}, "JSON must be an object (e.g., {\"k\": \"v\"})"
        return True, parsed, ""
    except Exception as exc:
        return False, {}, str(exc)


def _append_history(run_id: str) -> None:
    history = st.session_state.setdefault("run_history", [])
    if run_id in history:
        history.remove(run_id)
    history.append(run_id)


def _refresh_last_run_status(client: ApiClient, run_id: str) -> Optional[str]:
    if not run_id:
        return None
    resp = client.get_run(run_id)
    if not resp.ok or not resp.body:
        return None
    run = resp.body.get("data", {}).get("run", {})
    if not isinstance(run, dict):
        return None
    status = run.get("status")
    if isinstance(status, str) and status:
        st.session_state["last_run_status"] = status
        st.session_state["last_run_id"] = run_id
        return status
    return None


def _save_uploaded_files(
    uploaded_files: List[Any],
    *,
    upload_id: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    file_refs: List[Dict[str, Any]] = []
    items: List[Dict[str, Any]] = []
    for item in uploaded_files:
        name = item.name
        suffix = Path(name).suffix.lower().lstrip(".")
        if suffix not in {"csv", "pdf"}:
            continue
        file_type = suffix
        file_id = f"{upload_id}_{name}"
        file_refs.append({"file_id": file_id, "file_type": file_type, "name": name})
        items.append({
            "name": name,
            "file_type": file_type,
            "content": item.getbuffer().tobytes(),
        })
    return file_refs, items


def _write_inputs_to_uploads(
    observability_root: Path,
    *,
    repo_root: Path,
    product: str,
    upload_id: str,
    items: List[Dict[str, Any]],
) -> None:
    if not items:
        return
    staging_dir = repo_root / "products" / product / "staging" / "input"
    staging_dir.mkdir(parents=True, exist_ok=True)
    _clear_dir(staging_dir)
    output_dir = repo_root / "products" / product / "staging" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    _clear_dir(output_dir)
    for item in items:
        target = staging_dir / item["name"]
        if target.exists():
            continue
        target.write_bytes(item["content"])


def _clear_dir(path: Path) -> None:
    import shutil
    if not path.exists():
        return
    for entry in path.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
        else:
            entry.unlink(missing_ok=True)


def _materialize_run_dirs(
    observability_root: Path, *, product: str, run_id: str
) -> Dict[str, Path]:
    base = observability_root / product / run_id
    paths = {
        "base": base,
        "input": base / "input",
        "runtime": base / "runtime",
        "output": base / "output",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def _list_dataset_candidates(
    product: str, *, repo_root: Path, allowed_types: List[str]
) -> List[str]:
    def _scan(dir_path: Path) -> List[str]:
        if not dir_path.exists():
            return []
        names: List[str] = []
        for path in dir_path.iterdir():
            if not path.is_file():
                continue
            if allowed_types:
                suffix = path.suffix.lower().lstrip(".")
                if suffix not in allowed_types:
                    continue
            names.append(path.name)
        return names

    data_dir = repo_root / "products" / product / "data"
    staging_dir = repo_root / "products" / product / "staging" / "input"
    candidates = _scan(data_dir) + _scan(staging_dir)
    return sorted(dict.fromkeys(candidates))
