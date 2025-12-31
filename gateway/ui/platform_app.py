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


def _record_runtime_snapshot(
    observability_root: Path,
    *,
    product: str,
    run_id: str,
    payload: Dict[str, Any],
    label: str,
) -> None:
    runtime_dir = _materialize_run_dirs(observability_root, product=product, run_id=run_id)["runtime"]
    ts = int(time.time())
    snapshot_path = runtime_dir / f"{label}_{ts}.json"
    snapshot_path.write_text(_pretty(payload), encoding="utf-8")
    latest_path = runtime_dir / "run.json"
    latest_path.write_text(_pretty(payload), encoding="utf-8")


def _list_observed_runs(observability_root: Path) -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    if not observability_root.exists():
        return runs
    for product_dir in sorted(observability_root.glob("*")):
        if not product_dir.is_dir():
            continue
        for run_dir in sorted(product_dir.glob("*")):
            runtime_path = run_dir / "runtime" / "run.json"
            if not runtime_path.exists():
                continue
            try:
                data = json.loads(runtime_path.read_text(encoding="utf-8"))
                run = data.get("data", {}).get("run", {})
                runs.append(
                    {
                        "run_id": run.get("run_id", run_dir.name),
                        "started_at": run.get("started_at", 0),
                        "product": run.get("product", product_dir.name),
                        "flow": run.get("flow", "unknown"),
                    }
                )
            except Exception:
                continue
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


def _render_run_history(client: ApiClient, *, observability_root: Path) -> None:
    st.subheader("Run history")
    runs_resp = client.list_runs()
    if not runs_resp.ok or not runs_resp.body:
        st.warning(f"Unable to list runs: {runs_resp.error or runs_resp.body}")
        return
    runs = runs_resp.body["data"].get("runs", [])
    if not runs:
        st.info("No runs have been recorded yet.")
        return
    runs = sorted(runs, key=lambda r: r.get("started_at", 0), reverse=True)

    for run in runs:
        run_id = run.get("run_id")
        resp = client.get_run(run_id)
        if not resp.ok or not resp.body:
            st.warning(f"Unable to fetch run {run_id}: {resp.error or 'unknown error'}")
            continue

        run = resp.body["data"]["run"]
        steps = resp.body["data"].get("steps", [])
        status = run["status"]
        title = f"{run_id} — {run['product']}/{run['flow']} ({status})"
        with st.expander(title, expanded=False):
            st.write(f"Started: {run.get('started_at')}")
            st.write(f"Summary: {json.dumps(run.get('summary', {}), indent=2)}")
            if run.get("status") == "COMPLETED":
                output_dir = _materialize_run_dirs(observability_root, product=run["product"], run_id=run_id)["output"]
                response_path = output_dir / "response.json"
                if not response_path.exists():
                    response_path.write_text(_pretty(resp.body), encoding="utf-8")
                pdf_path = output_dir / "visualization.pdf"
                base_url = _api_base_url(load_settings())
                if response_path.exists():
                    st.markdown(
                        f"[Download response.json]({base_url}/api/output/{run['product']}/{run_id}/response.json)"
                    )
                if pdf_path.exists():
                    st.markdown(
                        f"[Download visualization.pdf]({base_url}/api/output/{run['product']}/{run_id}/visualization.pdf)"
                    )
            if run.get("error"):
                st.error(f"Error: {run['error']}")
            if steps:
                st.table(
                    [
                        {
                            "step_id": step["step_id"],
                            "name": step["name"],
                            "type": step["type"],
                            "status": step["status"],
                        }
                        for step in steps
                    ]
                )
            else:
                st.write("No steps recorded yet.")


def _render_approvals(client: ApiClient) -> None:
    st.subheader("Pending approvals")
    pending_runs: List[str] = []
    history = st.session_state.get("run_history", [])
    for run_id in history:
        resp = client.get_run(run_id)
        if resp.ok and resp.body:
            status = resp.body["data"]["run"]["status"]
            if status == "PENDING_HUMAN":
                pending_runs.append(run_id)

    if not pending_runs:
        st.info("No pending approvals in recent runs.")
    else:
        st.write("Pending run approvals:")
        for run_id in pending_runs:
            st.write(f"- {run_id}")

    st.markdown("### Resume a run")
    run_id = st.text_input("Run ID", value=st.session_state.get("approval_run_id", ""))
    st.session_state["approval_run_id"] = run_id
    payload_input = st.text_area("Approval payload (JSON)", value='{"approved": true}', height=140)
    ok, payload, err = _safe_json_loads(payload_input)
    if not ok:
        st.error(f"Invalid approval JSON: {err}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve", type="primary", disabled=(not ok or not run_id.strip())):
            resp = client.resume_run(
                run_id.strip(),
                decision="APPROVED",
                approval_payload=payload,
            )
            if resp.ok:
                st.success(f"Run resumed (approved): {run_id.strip()}")
                _append_history(run_id.strip())
                run_resp = client.get_run(run_id.strip())
                if run_resp.ok and run_resp.body:
                    run = run_resp.body["data"]["run"]
                    _record_runtime_snapshot(
                        _observability_root(),
                        product=run["product"],
                        run_id=run_id.strip(),
                        payload=run_resp.body,
                        label="run_resumed",
                    )
            else:
                st.error(f"Failed to resume run: {resp.error or resp.body}")
    with col2:
        if st.button("Reject", disabled=(not ok or not run_id.strip())):
            reject_payload = dict(payload)
            reject_payload["approved"] = False
            resp = client.resume_run(
                run_id.strip(),
                decision="REJECTED",
                approval_payload=reject_payload,
            )
            if resp.ok:
                st.success(f"Run resumed (rejected): {run_id.strip()}")
                _append_history(run_id.strip())
                run_resp = client.get_run(run_id.strip())
                if run_resp.ok and run_resp.body:
                    run = run_resp.body["data"]["run"]
                    _record_runtime_snapshot(
                        _observability_root(),
                        product=run["product"],
                        run_id=run_id.strip(),
                        payload=run_resp.body,
                        label="run_rejected",
                    )
            else:
                st.error(f"Failed to reject run: {resp.error or resp.body}")


def main() -> None:
    st.set_page_config(page_title="master platform", layout="wide")
    settings = load_settings()
    observability_root = _observability_root()
    api_base = _api_base_url(settings)
    client = ApiClient(api_base)

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Section", ["Home", "Run", "Run history", "Approvals"])
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
                    st.caption("Files will be saved under the run id once the flow starts.")
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
                        items = st.session_state.get("vi_upload_items", [])
                        _write_inputs_to_run(observability_root, product=prod, run_id=run_id, items=items)
                        output_path = observability_root / prod / run_id / "output" / "response.json"
                        output_path.write_text(_pretty(resp.body), encoding="utf-8")
                        st.caption(f"Saved response to {output_path}")
                        _record_runtime_snapshot(
                            observability_root,
                            product=prod,
                            run_id=run_id,
                            payload=resp.body,
                            label="run_started",
                        )

    elif page == "Run history":
        _render_run_history(client, observability_root=observability_root)

    elif page == "Approvals":
        _render_approvals(client)


if __name__ == "__main__":
    main()
