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

import requests
import streamlit as st

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

    def resume_run(self, run_id: str, payload: Dict[str, Any]) -> ApiResponse:
        return self._request("POST", f"/api/resume_run/{run_id}", {"approval_payload": payload})


def _api_base_url(settings: Any) -> str:
    candidate = getattr(getattr(settings, "app", None), "api_base_url", None)
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip().rstrip("/")
    host = getattr(settings.app, "host", "localhost")
    port = getattr(settings.app, "port", 8000)
    scheme = "https" if getattr(settings.app, "debug", False) is False else "http"
    return f"{scheme}://{host}:{port}"


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


def _render_run_history(client: ApiClient) -> None:
    st.subheader("Recent runs")
    history = list(reversed(st.session_state.get("run_history", [])))
    if not history:
        st.info("No runs have been triggered yet.")
        return

    for run_id in history[:10]:
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
            resp = client.resume_run(run_id.strip(), payload)
            if resp.ok:
                st.success(f"Run resumed (approved): {run_id.strip()}")
                _append_history(run_id.strip())
            else:
                st.error(f"Failed to resume run: {resp.error or resp.body}")
    with col2:
        if st.button("Reject", disabled=(not ok or not run_id.strip())):
            reject_payload = dict(payload)
            reject_payload["approved"] = False
            resp = client.resume_run(run_id.strip(), reject_payload)
            if resp.ok:
                st.success(f"Run resumed (rejected): {run_id.strip()}")
                _append_history(run_id.strip())
            else:
                st.error(f"Failed to reject run: {resp.error or resp.body}")


def main() -> None:
    st.set_page_config(page_title="master platform", layout="wide")
    settings = load_settings()
    api_base = _api_base_url(settings)
    client = ApiClient(api_base)

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Section", ["Home", "Run", "Runs", "Approvals"])
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
        payload_text = st.text_area("Payload (JSON)", value="{}", height=220)
        ok, payload, err = _safe_json_loads(payload_text)
        if not ok:
            st.error(f"Invalid JSON: {err}")
        if flow and st.button("Run flow", disabled=(not ok)):
            resp = client.run_flow(prod, flow, payload)
            st.code(_pretty(resp.body or resp.error), language="json")
            if resp.ok and resp.body:
                run_id = resp.body.get("data", {}).get("run_id")
                if run_id:
                    st.success(f"Run started: {run_id}")
                    _append_history(run_id)

    elif page == "Runs":
        _render_run_history(client)

    elif page == "Approvals":
        _render_approvals(client)


if __name__ == "__main__":
    main()
