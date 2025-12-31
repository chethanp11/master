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
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import sys
import time

import requests
import streamlit as st

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

    def resume_run(
        self,
        run_id: str,
        *,
        decision: str,
        approval_payload: Dict[str, Any],
        comment: Optional[str] = None,
    ) -> ApiResponse:
        return self._request(
            "POST",
            f"/api/resume_run/{run_id}",
            {"decision": decision, "approval_payload": approval_payload, "comment": comment or ""},
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


def _observability_root() -> Path:
    return REPO_ROOT / "observability"


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


def _materialize_upload_dirs(observability_root: Path, *, product: str, upload_id: str) -> Path:
    upload_dir = observability_root / product / "uploads" / upload_id / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


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


def _pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def _append_history(run_id: str) -> None:
    history = st.session_state.setdefault("run_history", [])
    if run_id in history:
        history.remove(run_id)
    history.append(run_id)


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
            if status == "COMPLETED":
                output_dir = _materialize_run_dirs(observability_root, product=product, run_id=run_id)["output"]
                response_path = output_dir / "response.json"
                pdf_path = output_dir / "visualization.pdf"
                stub_path = output_dir / "visualization_stub.json"
                base_url = _api_base_url(load_settings())
                if response_path.exists():
                    try:
                        response_payload = json.loads(response_path.read_text(encoding="utf-8"))
                        approvals_from_output = response_payload.get("approvals") or []
                    except Exception:
                        approvals_from_output = []
                if response_path.exists():
                    st.markdown(
                        f"[Download response.json]({base_url}/api/output/{product}/{run_id}/response.json)"
                    )
                if pdf_path.exists():
                    st.markdown(
                        f"[Download visualization.pdf]({base_url}/api/output/{product}/{run_id}/visualization.pdf)"
                    )
                if stub_path.exists():
                    st.markdown(
                        f"[Download visualization_stub.json]({base_url}/api/output/{product}/{run_id}/visualization_stub.json)"
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
                    if kind in {"run_resumed", "run_rejected"}:
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
        if step_name:
            st.write(f"Step: {step_name}")
        if reason:
            st.write(reason)
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
                _append_history(run_id.strip())
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
                _append_history(run_id.strip())
            else:
                st.error(f"Failed to reject run: {resp.error or resp.body}")


def main() -> None:
    st.set_page_config(page_title="master platform", layout="wide")
    settings = load_settings()
    observability_root = _observability_root()
    api_base = _api_base_url(settings)
    client = ApiClient(api_base)

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Section", ["Home", "Run", "Approvals"])
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
        if prod == "visual_insights":
            st.markdown("### Upload files (CSV/PDF)")
            uploaded = st.file_uploader(
                "Attach data files",
                type=["csv", "pdf"],
                accept_multiple_files=True,
            )
            include_uploads = st.checkbox("Include uploaded files in payload", value=True)
            if uploaded and include_uploads:
                upload_id = st.session_state.get("vi_upload_id")
                if not upload_id:
                    upload_id = str(int(time.time()))
                    st.session_state["vi_upload_id"] = upload_id
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
                    st.code(_pretty({"files": file_refs}), language="json")
                st.session_state["vi_upload_items"] = items

        payload: Dict[str, Any] = {}
        ok = True
        if prod == "visual_insights":
            instructions = st.text_area(
                "Instructions",
                value="Summarize key trends and highlight anomalies.",
                height=140,
                help="Optional guidance for the analysis (stored in payload as 'prompt').",
            )
            payload["prompt"] = instructions.strip() if instructions else ""
        else:
            payload_text = st.text_area("Payload (JSON)", value="{}", height=220)
            ok, payload, err = _safe_json_loads(payload_text)
            if not ok:
                st.error(f"Invalid JSON: {err}")

        if prod == "visual_insights" and file_refs:
            payload.setdefault("files", file_refs)
            payload["upload_id"] = st.session_state.get("vi_upload_id")
            if "dataset" not in payload:
                csv_name = next((f["name"] for f in file_refs if f["file_type"] == "csv"), None)
                if csv_name:
                    payload["dataset"] = csv_name
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
                    if prod == "visual_insights":
                        _materialize_run_dirs(observability_root, product=prod, run_id=run_id)

    elif page == "Approvals":
        _render_approvals(client)
        st.divider()
        _render_run_history(observability_root=observability_root)


if __name__ == "__main__":
    main()
