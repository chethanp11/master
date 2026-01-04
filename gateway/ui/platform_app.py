# ==============================
# Platform UI (Streamlit) - v1 Control Center
# ==============================
"""
Streamlit-based Platform Control Center for master/.

Capabilities:
- Discover enabled products + flows via /api/products
- Trigger flow runs with JSON payloads
- View run history + details via /api/run/{run_id}
- Inspect and resolve pending approvals via POST /api/resume_run/{run_id}

UI architecture:
- Home: product/flow overview
- Run: product+flow selection + payload editor
- Runs: history + detail view
- Approvals: list pending approvals + actions

All actions go through the Gateway API. No direct core imports besides settings.
"""

from __future__ import annotations



import json
import shutil
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import sys
import time

import requests
import streamlit as st
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.config.loader import load_settings


@dataclass(frozen=True)
class ApiResponse:
    ok: bool
    body: Optional[Dict[str, Any]]
    error: Optional[str]


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> ApiResponse:
        url = f"{self.base_url}{path}"
        try:
            resp = getattr(requests, method.lower())(url, json=payload, timeout=self.timeout)
        except requests.RequestException as exc:
            return ApiResponse(ok=False, body=None, error=str(exc))

        try:
            body = resp.json()
        except ValueError:
            body = None

        if not resp.ok:
            return ApiResponse(ok=False, body=body, error=body.get("error", {}).get("message") if body else resp.text)

        if isinstance(body, dict) and not body.get("ok", True):
            return ApiResponse(ok=False, body=body, error=body.get("error", {}).get("message", "API error"))

        return ApiResponse(ok=True, body=body, error=None)

    def list_products(self) -> ApiResponse:
        return self._request("GET", "/api/products")

    def list_flows(self, product: str) -> ApiResponse:
        return self._request("GET", f"/api/products/{product}/flows")

    def run_flow(self, product: str, flow: str, payload: Dict[str, Any]) -> ApiResponse:
        return self._request("POST", f"/api/run/{product}/{flow}", {"payload": payload})

    def get_run(self, run_id: str) -> ApiResponse:
        return self._request("GET", f"/api/run/{run_id}")

    def get_pending_input(self, run_id: str) -> ApiResponse:
        return self._request("GET", f"/api/runs/{run_id}/pending_input")

    def submit_user_input(
        self,
        run_id: str,
        *,
        prompt_id: str,
        selected_option_ids: Optional[List[str]] = None,
        free_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        payload = {
            "prompt_id": prompt_id,
            "selected_option_ids": selected_option_ids,
            "free_text": free_text,
            "metadata": metadata or {},
        }
        return self._request("POST", f"/api/runs/{run_id}/user_input", payload)

    def resume_run(
        self,
        run_id: str,
        *,
        decision: str,
        approval_payload: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None,
        user_input_response: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        return self._request(
            "POST",
            f"/api/resume_run/{run_id}",
            {
                "decision": decision,
                "approval_payload": approval_payload or {},
                "comment": comment or "",
                "user_input_response": user_input_response or {},
            },
        )

    def list_runs(self) -> ApiResponse:
        return self._request("GET", "/api/runs")

    def list_approvals(self) -> ApiResponse:
        return self._request("GET", "/api/approvals")


def _api_base_url(settings: Any) -> str:
    candidate = getattr(getattr(settings, "app", None), "api_base_url", None)
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip().rstrip("/")
    host = getattr(settings.app, "host", "localhost")
    port = getattr(settings.app, "port", 8000)
    scheme = "https" if getattr(settings.app, "debug", False) is False else "http"
    return f"{scheme}://{host}:{port}"

def _resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else (REPO_ROOT / path)


def _observability_root(settings: Optional[Any] = None) -> Path:
    resolved = settings or load_settings()
    path = Path(resolved.app.paths.observability_dir)
    return path if path.is_absolute() else (resolved.repo_root_path() / path)


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
        items.append({"name": name, "file_type": file_type, "content": item.getbuffer().tobytes()})
    return file_refs, items


def _materialize_run_dirs(observability_root: Path, *, product: str, run_id: str) -> Dict[str, Path]:
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


def _clear_dir(path: Path) -> None:
    if not path.exists():
        return
    for entry in path.iterdir():
        if entry.is_dir():
            for child in entry.iterdir():
                if child.is_dir():
                    for grandchild in child.iterdir():
                        if grandchild.is_dir():
                            shutil.rmtree(grandchild, ignore_errors=True)
                        else:
                            grandchild.unlink(missing_ok=True)
                else:
                    child.unlink(missing_ok=True)
            shutil.rmtree(entry, ignore_errors=True)
        else:
            entry.unlink(missing_ok=True)


def _materialize_upload_dirs(observability_root: Path, *, product: str, upload_id: str) -> Path:
    staging_dir = REPO_ROOT / "products" / product / "staging" / "input"
    staging_dir.mkdir(parents=True, exist_ok=True)
    return staging_dir


def _write_inputs_to_uploads(
    observability_root: Path,
    *,
    product: str,
    upload_id: str,
    items: List[Dict[str, Any]],
) -> None:
    if not items:
        return
    upload_dir = _materialize_upload_dirs(observability_root, product=product, upload_id=upload_id)
    _clear_dir(upload_dir)
    output_dir = REPO_ROOT / "products" / product / "staging" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    _clear_dir(output_dir)
    for item in items:
        target = upload_dir / item["name"]
        if target.exists():
            continue
        target.write_bytes(item["content"])


def _write_inputs_to_run(
    observability_root: Path,
    *,
    product: str,
    run_id: str,
    items: List[Dict[str, Any]],
) -> None:
    if not items:
        return
    run_input_dir = _materialize_run_dirs(observability_root, product=product, run_id=run_id)["input"]
    for item in items:
        target = run_input_dir / item["name"]
        if target.exists():
            continue
        target.write_bytes(item["content"])


def _load_run_events(observability_root: Path, *, product: str, run_id: str) -> List[Dict[str, Any]]:
    runtime_path = observability_root / product / run_id / "runtime" / "events.jsonl"
    events: List[Dict[str, Any]] = []
    if not runtime_path.exists():
        return events
    for line in runtime_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events


def _summarize_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not events:
        return {"status": "UNKNOWN", "started_at": 0}
    events_sorted = sorted(events, key=lambda e: e.get("ts", 0))
    started_at = events_sorted[0].get("ts", 0)
    status = "RUNNING"
    for event in reversed(events_sorted):
        kind = event.get("kind")
        if kind == "run_completed":
            status = "COMPLETED"
            break
        if kind in {"run_failed", "run_rejected"}:
            status = "FAILED"
            break
        if kind == "pending_human":
            status = "PENDING_HUMAN"
            break
        if kind in {"pending_user_input", "user_input_requested", "run_paused"}:
            status = "PAUSED_WAITING_FOR_USER"
            break
    return {"status": status, "started_at": started_at}


def _list_observed_runs(observability_root: Path) -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    if not observability_root.exists():
        return runs
    for product_dir in sorted(observability_root.glob("*")):
        if not product_dir.is_dir():
            continue
        for run_dir in sorted(product_dir.glob("*")):
            if not run_dir.is_dir():
                continue
            events = _load_run_events(observability_root, product=product_dir.name, run_id=run_dir.name)
            if not events:
                continue
            events_sorted = sorted(events, key=lambda e: e.get("ts", 0))
            summary = _summarize_events(events)
            runs.append(
                {
                    "run_id": run_dir.name,
                    "product": product_dir.name,
                    "flow": events_sorted[0].get("flow", "unknown") if events_sorted else "unknown",
                    "started_at": summary["started_at"],
                    "status": summary["status"],
                }
            )
    return runs


def _safe_json_loads(value: str) -> Tuple[bool, Dict[str, Any], str]:
    try:
        parsed = json.loads(value or "{}")
        if not isinstance(parsed, dict):
            return False, {}, "JSON must be an object (e.g., {\"k\": \"v\"})"
        return True, parsed, ""
    except Exception as exc:
        return False, {}, str(exc)


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


def _pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def _append_history(run_id: str) -> None:
    history = st.session_state.setdefault("run_history", [])
    if run_id in history:
        history.remove(run_id)
    history.append(run_id)


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


def _render_product_summary(products: List[Dict[str, Any]]) -> None:
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


def _render_run_history(*, observability_root: Path) -> None:
    st.subheader("Run history")
    runs = _list_observed_runs(observability_root)
    if not runs:
        st.info("No runs have been recorded yet.")
        return
    runs = sorted(runs, key=lambda r: r.get("started_at", 0), reverse=True)

    for run in runs:
        run_id = run.get("run_id")
        product = run.get("product", "unknown")
        flow = run.get("flow", "unknown")
        status = run.get("status", "UNKNOWN")
        title = f"{run_id} — {product}/{flow} ({status})"
        with st.expander(title, expanded=False):
            st.write(f"Started: {run.get('started_at')}")
            events = _load_run_events(observability_root, product=product, run_id=run_id)
            st.write(f"Events: {len(events)}")
            approvals_from_output: List[Dict[str, Any]] = []
            output_dir = observability_root / product / run_id / "output"
            base_url = _api_base_url(load_settings())
            if output_dir.exists() and output_dir.is_dir():
                response_path = output_dir / "response.json"
                if response_path.exists():
                    try:
                        response_payload = json.loads(response_path.read_text(encoding="utf-8"))
                        approvals_from_output = response_payload.get("approvals") or []
                    except Exception:
                        approvals_from_output = []
                output_files = sorted([p for p in output_dir.iterdir() if p.is_file()])
                if output_files:
                    st.markdown("**Outputs**")
                    for output_file in output_files:
                        st.markdown(
                            f"[Download {output_file.name}]({base_url}/api/output/{product}/{run_id}/{output_file.name})"
                        )
            if events:
                step_state: Dict[str, Dict[str, str]] = {}
                approvals: List[Dict[str, Any]] = []
                for event in events:
                    step_id = event.get("step_id")
                    if not step_id:
                        continue
                    kind = event.get("kind")
                    if kind == "step_started":
                        step_state[step_id] = {"step_id": step_id, "status": "RUNNING"}
                    elif kind == "step_completed":
                        step_state[step_id] = {"step_id": step_id, "status": "COMPLETED"}
                    elif kind == "step_failed":
                        step_state[step_id] = {"step_id": step_id, "status": "FAILED"}
                    elif kind == "pending_human":
                        step_state[step_id] = {"step_id": step_id, "status": "PENDING_HUMAN"}
                    elif kind in {"user_input_requested", "pending_user_input", "run_paused"}:
                        step_state[step_id] = {"step_id": step_id, "status": "PAUSED_WAITING_FOR_USER"}
                    elif kind == "user_input_received":
                        step_state[step_id] = {"step_id": step_id, "status": "COMPLETED"}
                    if kind in {"run_resumed", "run_rejected"}:
                        step_state[step_id] = {
                            "step_id": step_id,
                            "status": "APPROVED" if kind == "run_resumed" else "REJECTED",
                        }
                        approvals.append(
                            {
                                "time": event.get("ts"),
                                "decision": (event.get("payload") or {}).get("decision"),
                                "comment": (event.get("payload") or {}).get("comment") or "",
                                "step_id": step_id,
                            }
                        )
                if step_state:
                    st.table(list(step_state.values()))
                if approvals_from_output or approvals:
                    st.markdown("**Approvals**")
                    for approval in approvals_from_output:
                        decision = approval.get("decision")
                        comment = approval.get("comment") or ""
                        step_id = approval.get("step_id")
                        resolved_at = approval.get("resolved_at")
                        line = f"{resolved_at} • {step_id} • {decision}"
                        if comment:
                            line = f"{line} — {comment}"
                        st.write(line)
                    for approval in approvals:
                        decision = approval.get("decision")
                        comment = approval.get("comment")
                        step_id = approval.get("step_id")
                        ts = approval.get("time")
                        line = f"{ts} • {step_id} • {decision}"
                        if comment:
                            line = f"{line} — {comment}"
                        st.write(line)


def _render_approvals(client: ApiClient) -> None:
    st.subheader("Pending approvals")
    st.markdown(
        """
<style>
button[kind="primary"] { background-color: #2e7d32 !important; color: white !important; }
button[kind="secondary"] { background-color: #c62828 !important; color: white !important; }
</style>
""",
        unsafe_allow_html=True,
    )
    approvals_resp = client.list_approvals()
    if not approvals_resp.ok or not approvals_resp.body:
        st.warning(f"Unable to load approvals: {approvals_resp.error or approvals_resp.body}")
        return
    approvals = approvals_resp.body["data"].get("approvals", [])
    if not approvals:
        st.info("No pending approvals.")
        return

    options = []
    for approval in approvals:
        label = f"{approval['run_id']} — {approval['product']}/{approval['flow']} ({approval['step_id']})"
        options.append((label, approval))

    selection = st.selectbox("Select pending run", options, format_func=lambda item: item[0])
    approval = selection[1]
    run_id = approval["run_id"]
    st.write(f"Selected run: {run_id}")
    events = _load_run_events(_observability_root(), product=approval["product"], run_id=run_id)
    decisions: List[Dict[str, Any]] = []
    for event in events:
        kind = event.get("kind")
        if kind in {"run_resumed", "run_rejected"}:
            decisions.append(
                {
                    "time": event.get("ts"),
                    "decision": (event.get("payload") or {}).get("decision"),
                    "comment": (event.get("payload") or {}).get("comment") or "",
                    "step_id": event.get("step_id"),
                }
            )
    if decisions:
        st.markdown("**Decision history**")
        for entry in decisions:
            line = f"{entry.get('time')} • {entry.get('step_id')} • {entry.get('decision')}"
            if entry.get("comment"):
                line = f"{line} — {entry.get('comment')}"
            st.write(line)
    else:
        st.caption("Decision and notes will appear here after approval or rejection.")
    payload = approval.get("payload") or {}
    summary = payload.get("summary") if isinstance(payload, dict) else None
    instructions = payload.get("instructions") if isinstance(payload, dict) else None
    actions = payload.get("actions") if isinstance(payload, dict) else None
    approval_context = payload.get("approval_context") if isinstance(payload, dict) else None
    intent = payload.get("intent") if isinstance(payload, dict) else None
    if intent:
        st.markdown("**User intent**")
        st.write(intent)
    if summary:
        st.markdown("**Approval summary**")
        st.write(summary)
    if approval_context:
        st.markdown("**Approval needed for**")
        reason = approval_context.get("reason") if isinstance(approval_context, dict) else None
        step_name = approval_context.get("step_name") if isinstance(approval_context, dict) else None
        decision_notes = approval_context.get("decision_notes") if isinstance(approval_context, dict) else None
        recommended = approval_context.get("recommended_action") if isinstance(approval_context, dict) else None
        if step_name:
            st.write(f"Step: {step_name}")
        if reason:
            st.write(reason)
        if decision_notes:
            st.markdown("**Decision notes**")
            for note in decision_notes:
                st.write(f"- {note}")
        if recommended:
            st.markdown("**System recommendation**")
            st.write(recommended)
    if actions:
        st.markdown("**Actions taken**")
        if isinstance(actions, list):
            for action in actions:
                st.write(f"- {action}")
        else:
            st.write(actions)
    if payload:
        with st.expander("Approval context (advanced)"):
            st.code(_pretty(payload), language="json")
    comment = st.text_area("Reviewer comments", value="", height=120, help="Optional guidance for re-planning.")
    approval_payload = {"approved": True}

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve", type="primary", disabled=(not run_id.strip())):
            resp = client.resume_run(
                run_id.strip(),
                decision="APPROVED",
                approval_payload=approval_payload,
                comment=comment or None,
            )
            if resp.ok:
                st.success(f"Run resumed (approved): {run_id.strip()}")
                if resp.body:
                    updated_status = resp.body.get("data", {}).get("status")
                    if isinstance(updated_status, str):
                        st.session_state["last_run_status"] = updated_status
                        st.session_state["last_run_id"] = run_id.strip()
                _append_history(run_id.strip())
                st.rerun()
            else:
                st.error(f"Failed to resume run: {resp.error or resp.body}")
    with col2:
        if st.button("Reject", type="secondary", disabled=(not run_id.strip())):
            reject_payload = {"approved": False}
            resp = client.resume_run(
                run_id.strip(),
                decision="REJECTED",
                approval_payload=reject_payload,
                comment=comment or None,
            )
            if resp.ok:
                st.success(f"Run resumed (rejected): {run_id.strip()}")
                if resp.body:
                    updated_status = resp.body.get("data", {}).get("status")
                    if isinstance(updated_status, str):
                        st.session_state["last_run_status"] = updated_status
                        st.session_state["last_run_id"] = run_id.strip()
                _append_history(run_id.strip())
                st.rerun()
            else:
                st.error(f"Failed to reject run: {resp.error or resp.body}")


def _pending_user_inputs_from_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pending: Dict[str, Dict[str, Any]] = {}
    for event in sorted(events, key=lambda e: e.get("ts", 0)):
        kind = event.get("kind")
        step_id = event.get("step_id")
        if kind == "user_input_requested" and step_id:
            payload = event.get("payload") or {}
            form_id = payload.get("form_id")
            if isinstance(form_id, str):
                pending[step_id] = {
                    "step_id": step_id,
                    "form_id": form_id,
                    "payload": payload,
                    "ts": event.get("ts", 0),
                }
        elif kind == "user_input_received" and step_id:
            pending.pop(step_id, None)
        elif kind in {"run_completed", "run_failed", "run_rejected"}:
            pending.clear()
    return list(pending.values())


def _load_flow_definition(product: str, flow: str) -> Optional[Dict[str, Any]]:
    flow_path = REPO_ROOT / "products" / product / "flows" / f"{flow}.yaml"
    if not flow_path.exists():
        return None
    try:
        return yaml.safe_load(flow_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None


def _get_user_input_config(flow_def: Dict[str, Any], form_id: str) -> Optional[Dict[str, Any]]:
    steps = flow_def.get("steps") if isinstance(flow_def, dict) else None
    if not isinstance(steps, list):
        return None
    for step in steps:
        if not isinstance(step, dict):
            continue
        if step.get("type") != "user_input":
            continue
        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        if params.get("form_id") == form_id:
            return params
    return None


def _pending_user_input_runs(client: ApiClient) -> List[Dict[str, Any]]:
    resp = client.list_runs()
    if not resp.ok or not resp.body:
        return []
    runs = resp.body.get("data", {}).get("runs", [])
    pending: List[Dict[str, Any]] = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        status = run.get("status")
        if status in {"PAUSED_WAITING_FOR_USER", "PENDING_USER_INPUT"}:
            pending.append(run)
    return pending


def _render_user_input_prompt(prompt: Dict[str, Any]) -> Tuple[Optional[List[str]], Optional[str]]:
    options = prompt.get("options") if isinstance(prompt.get("options"), list) else []
    defaults = prompt.get("defaults") if isinstance(prompt.get("defaults"), dict) else {}
    allow_free_text = bool(prompt.get("allow_free_text"))
    selected_ids: Optional[List[str]] = None
    free_text: Optional[str] = None

    if options:
        option_ids = [opt.get("option_id") for opt in options if isinstance(opt, dict) and opt.get("option_id")]
        labels = [opt.get("label") or opt.get("option_id") for opt in options if isinstance(opt, dict) and opt.get("option_id")]
        default_candidate = next((v for v in defaults.values() if isinstance(v, str)), None)
        if default_candidate and default_candidate in option_ids:
            default_idx = option_ids.index(default_candidate)
        else:
            default_idx = 0 if option_ids else 0
        if option_ids:
            selection = st.selectbox("Select option", labels, index=default_idx)
            selected_ids = [option_ids[labels.index(selection)]]

    if allow_free_text:
        free_text = st.text_area("Free text", value="", height=120)

    return selected_ids, free_text


def _render_user_inputs(client: ApiClient) -> None:
    st.subheader("Pending user inputs")
    pending_inputs = _pending_user_input_runs(client)
    if not pending_inputs:
        st.info("No pending user inputs.")
        return

    options = []
    for item in pending_inputs:
        run_id = item.get("run_id") or ""
        product = item.get("product") or ""
        flow = item.get("flow") or ""
        label = f"{run_id} — {product}/{flow}"
        options.append((label, item))

    selection = st.selectbox("Select pending input", options, format_func=lambda item: item[0])
    selected = selection[1]
    run_id = selected.get("run_id", "")
    if not run_id:
        st.info("No run selected.")
        return

    pending_resp = client.get_pending_input(run_id)
    if not pending_resp.ok or not pending_resp.body:
        st.error(f"Failed to load pending input: {pending_resp.error or pending_resp.body}")
        return
    prompt = pending_resp.body.get("data", {}).get("prompt")
    if not isinstance(prompt, dict):
        st.info("No pending user input prompt available.")
        return

    st.write(f"Selected run: {run_id}")
    title = prompt.get("title") or prompt.get("prompt_id") or "User input"
    st.markdown(f"**{title}**")
    question = prompt.get("question")
    if question:
        st.write(question)

    selected_ids, free_text = _render_user_input_prompt(prompt)
    if st.button("Submit input", type="primary", disabled=not run_id.strip()):
        prompt_id = str(prompt.get("prompt_id") or "")
        if not prompt_id:
            st.error("Missing prompt_id for pending input.")
            return
        resp = client.submit_user_input(
            run_id.strip(),
            prompt_id=prompt_id,
            selected_option_ids=selected_ids,
            free_text=free_text,
            metadata={"source": "ui"},
        )
        if resp.ok:
            st.success(f"User input submitted for run: {run_id.strip()}")
            if resp.body:
                updated_status = resp.body.get("data", {}).get("status")
                if isinstance(updated_status, str):
                    st.session_state["last_run_status"] = updated_status
                    st.session_state["last_run_id"] = run_id.strip()
            _append_history(run_id.strip())
            st.rerun()
        else:
            st.error(f"Failed to submit user input: {resp.error or resp.body}")


def main() -> None:
    st.set_page_config(page_title="master platform", layout="wide")
    settings = load_settings()
    observability_root = _observability_root()
    api_base = _api_base_url(settings)
    client = ApiClient(api_base)

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Section", ["Home", "Run", "Approvals", "User Inputs"])
    st.sidebar.caption(f"API base: {api_base}")

    st.session_state.setdefault("run_history", [])

    products_resp = client.list_products()
    if not products_resp.ok or not products_resp.body:
        st.error(f"Cannot load products: {products_resp.error or 'Unknown error'}")
        return

    products = sorted(products_resp.body["data"]["products"], key=lambda p: p["name"])

    if page == "Home":
        _render_product_summary(products)

    elif page == "Run":
        st.subheader("Trigger a flow")
        if not products:
            st.info("No enabled products discovered.")
            return
        prod = st.selectbox("Product", [prod["name"] for prod in products])
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

        flow = st.selectbox("Flow", flows)
        file_refs: List[Dict[str, Any]] = []
        input_spec = _resolve_input_spec(product_config)
        allowed_types = input_spec.get("allowed_types") or []
        if isinstance(allowed_types, list):
            allowed_types = [str(ext).lower().lstrip(".") for ext in allowed_types if str(ext).strip()]
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
            )
            include_uploads = st.checkbox("Include uploaded files in payload", value=True)
            if uploaded and include_uploads:
                upload_id = st.session_state.get(upload_key)
                if not upload_id:
                    upload_id = str(int(time.time()))
                    st.session_state[upload_key] = upload_id
                file_refs, items = _save_uploaded_files(
                    uploaded,
                    upload_id=upload_id,
                )
                if items:
                    _write_inputs_to_uploads(
                        observability_root,
                        product=prod,
                        upload_id=upload_id,
                        items=items,
                    )
                    st.caption(f"Files staged for upload {upload_id}.")
                if file_refs:
                    st.code(_pretty({files_field: file_refs}), language="json")
                st.session_state[items_key] = items

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
            )
            payload[intent_field] = instructions.strip() if instructions else ""
        else:
            payload_key = f"{prod}_payload_json"
            if payload_key not in st.session_state:
                st.session_state[payload_key] = "{}"
            example_key = f"{prod}_example_loaded"
            if st.button("Load Example", type="secondary"):
                st.session_state[example_key] = True
                if prod == "hello_world":
                    st.session_state[payload_key] = _pretty({"keyword": "Hello from the demo"})
                else:
                        st.session_state[payload_key] = _pretty(
                            {
                                "dataset": "ade_input.csv",
                                "prompt": "Summarize key trends and highlight anomalies.",
                                "files": [{"name": "ade_input.csv", "file_type": "csv"}],
                                "upload_id": "demo_upload_1",
                            }
                        )
            payload_text = st.text_area("Payload (JSON)", value=st.session_state[payload_key], height=220)
            st.session_state[payload_key] = payload_text
            ok, payload, err = _safe_json_loads(payload_text)
            if not ok:
                st.error(f"Invalid JSON: {err}")

        if file_refs:
            payload.setdefault(files_field, file_refs)
            payload[upload_id_field] = st.session_state.get(upload_key)
            if dataset_field and dataset_field not in payload:
                csv_name = next((f["name"] for f in file_refs if f["file_type"] == "csv"), None)
                if csv_name:
                    payload[dataset_field] = csv_name
            st.markdown("### Payload preview")
            st.code(_pretty(payload), language="json")

        if flow and st.button("Run flow", disabled=(not ok)):
            resp = client.run_flow(prod, flow, payload)
            st.code(_pretty(resp.body or resp.error), language="json")
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

        last_run_id = st.session_state.get("last_run_id")
        if st.button("Refresh run status", disabled=not last_run_id):
            refreshed = _refresh_last_run_status(client, last_run_id or "")
            if refreshed:
                st.success(f"Run status refreshed: {refreshed}")
            else:
                st.warning("Unable to refresh run status.")

        pending_status = st.session_state.get("last_run_status")
        if pending_status in {"PAUSED_WAITING_FOR_USER", "PENDING_USER_INPUT", "NEEDS_USER_INPUT"}:
            run_id = st.session_state.get("last_run_id")
            if run_id:
                pending_resp = client.get_pending_input(run_id)
                if not pending_resp.ok or not pending_resp.body:
                    st.error(f"Failed to load pending input: {pending_resp.error or pending_resp.body}")
                else:
                    prompt = pending_resp.body.get("data", {}).get("prompt")
                    if not isinstance(prompt, dict):
                        st.info("Run is waiting for user input, but no prompt is available.")
                    else:
                        st.markdown("### User input required")
                        st.write(prompt.get("question") or "Provide input")
                        selected_ids, free_text = _render_user_input_prompt(prompt)
                        if st.button("Submit input", type="primary"):
                            prompt_id = str(prompt.get("prompt_id") or "")
                            if not prompt_id:
                                st.error("Missing prompt_id for pending input.")
                            else:
                                resp = client.submit_user_input(
                                    run_id,
                                    prompt_id=prompt_id,
                                    selected_option_ids=selected_ids,
                                    free_text=free_text,
                                    metadata={"source": "ui"},
                                )
                                if resp.ok:
                                    st.success("User input submitted. Refreshing run status...")
                                    if resp.body:
                                        updated_status = resp.body.get("data", {}).get("status")
                                        if isinstance(updated_status, str):
                                            st.session_state["last_run_status"] = updated_status
                                            st.session_state["last_run_id"] = run_id
                                    st.rerun()
                                else:
                                    st.error(f"Failed to submit user input: {resp.error or resp.body}")

    elif page == "Approvals":
        _render_approvals(client)

    elif page == "User Inputs":
        _render_user_inputs(client)
        st.divider()
        _render_run_history(observability_root=observability_root)


if __name__ == "__main__":
    main()
