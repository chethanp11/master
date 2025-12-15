# ==============================
# Platform UI (Streamlit) - v1 Single File
# ==============================
"""
Streamlit control-center UI for master/.

Features (v1):
- Home: list products + flows
- Run: JSON payload input, trigger run via API
- Runs: list runs + run detail view
- Approvals: list pending approvals + approve/reject -> resume API

Notes:
- UI calls the Gateway API over HTTP (same host by default).
- API base URL is read from Settings (configs/app.yaml via core/config/loader.py).
- Keep templates/static folders in repo for future non-Streamlit UI.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

from core.config.loader import load_settings
from core.utils.product_loader import discover_products


# ==============================
# Helpers
# ==============================
def _safe_json_loads(s: str) -> Tuple[bool, Dict[str, Any], str]:
    try:
        v = json.loads(s or "{}")
        if not isinstance(v, dict):
            return False, {}, "JSON must be an object (e.g., {\"k\":\"v\"})"
        return True, v, ""
    except Exception as e:
        return False, {}, str(e)


def _pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def _api_base_url(settings) -> str:
    # Settings schema should provide gateway.api_base_url (or fall back).
    # Keep defensive to avoid hard dependency on exact field names.
    val = getattr(getattr(settings, "app", None), "api_base_url", None)
    if isinstance(val, str) and val.strip():
        return val.strip().rstrip("/")
    # fallback: assume same host:8000
    return "http://localhost:8000"


def _http_post(url: str, json_body: Dict[str, Any], timeout_s: int = 30) -> Dict[str, Any]:
    r = requests.post(url, json=json_body, timeout=timeout_s)
    try:
        return {"status": r.status_code, "json": r.json()}
    except Exception:
        return {"status": r.status_code, "text": r.text}


def _http_get(url: str, timeout_s: int = 30) -> Dict[str, Any]:
    r = requests.get(url, timeout=timeout_s)
    try:
        return {"status": r.status_code, "json": r.json()}
    except Exception:
        return {"status": r.status_code, "text": r.text}


# ==============================
# Data access via API
# ==============================
def api_run_flow(api_base: str, product: str, flow: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _http_post(f"{api_base}/api/run/{product}/{flow}", {"payload": payload})


def api_get_run(api_base: str, run_id: str) -> Dict[str, Any]:
    return _http_get(f"{api_base}/api/run/{run_id}")


def api_resume_run(api_base: str, run_id: str, approval_payload: Dict[str, Any]) -> Dict[str, Any]:
    return _http_post(f"{api_base}/api/resume_run/{run_id}", {"approval_payload": approval_payload})


def api_list_runs_v1(api_base: str) -> Dict[str, Any]:
    # Optional endpoint (not in your strict list). Fallback to memory list via a future endpoint.
    # For v1, we use Memory list via a lightweight backend route IF you add it later.
    return {"status": 501, "text": "List runs endpoint not implemented. Use run_id lookup."}


def api_list_pending_approvals_v1(api_base: str) -> Dict[str, Any]:
    # Optional endpoint (not in your strict list). We'll display a placeholder unless you expose it.
    return {"status": 501, "text": "Pending approvals endpoint not implemented. Add /api/approvals/pending later."}


# ==============================
# UI
# ==============================
def main() -> None:
    st.set_page_config(page_title="master platform", layout="wide")
    st.title("master platform")

    settings = load_settings()
    api_base = _api_base_url(settings)

    products_dir = settings.products.products_dir
    registry = discover_products(products_dir)
    products = registry.list()

    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Page", ["Home", "Run", "Runs", "Approvals"], index=0)
    st.sidebar.markdown("---")
    st.sidebar.caption(f"API base: {api_base}")

    if page == "Home":
        st.subheader("Products")
        if not products:
            st.warning("No products discovered. Check products/*/manifest.yaml")
            return

        for p in products:
            with st.expander(f"{p.manifest.display_name or p.name}  —  /{p.name}", expanded=False):
                st.write(p.manifest.description or "")
                st.code(_pretty(p.manifest.model_dump()), language="json")

        st.subheader("Flows")
        st.write("Flows are discovered per-product by scanning `products/<product>/flows/*.(yaml|yml|json)` locally.")
        cols = st.columns(2)
        with cols[0]:
            prod_name = st.selectbox("Select product", [p.name for p in products])
        with cols[1]:
            st.write("")
        st.markdown("")

        # Local flow discovery (UI can show flows without needing list endpoint)
        flow_names = _discover_flows_local(products_dir, prod_name)
        st.write(f"Found {len(flow_names)} flows under products/{prod_name}/flows/")
        st.code("\n".join(flow_names) if flow_names else "(none)", language="text")

    elif page == "Run":
        st.subheader("Run a flow")
        if not products:
            st.warning("No products discovered.")
            return

        col1, col2 = st.columns([1, 2])

        with col1:
            prod_name = st.selectbox("Product", [p.name for p in products])
            flow_names = _discover_flows_local(products_dir, prod_name)
            flow = st.selectbox("Flow", flow_names if flow_names else ["(none)"])
            st.caption(f"UI URL: /{prod_name}")

        with col2:
            st.write("Payload (JSON object)")
            payload_text = st.text_area("payload", value="{}", height=220)
            ok, payload, err = _safe_json_loads(payload_text)
            if not ok:
                st.error(f"Invalid JSON: {err}")

            if st.button("Run", type="primary", disabled=(not ok or flow == "(none)")):
                res = api_run_flow(api_base, prod_name, flow, payload)
                st.markdown("**Response**")
                st.code(_pretty(res), language="json")

                run_id = None
                if isinstance(res.get("json"), dict):
                    run_id = res["json"].get("data", {}).get("run_id") or res["json"].get("run_id")
                if run_id:
                    st.success(f"Run started: {run_id}")
                    st.session_state["last_run_id"] = run_id

        if st.session_state.get("last_run_id"):
            st.info(f"Last run: {st.session_state['last_run_id']}")

    elif page == "Runs":
        st.subheader("Run lookup + details")
        st.write("v1 supports run lookup by run_id. Add list endpoints later if needed.")

        run_id = st.text_input("Run ID", value=st.session_state.get("last_run_id", ""))
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Get run"):
                if not run_id.strip():
                    st.error("Provide a run_id")
                else:
                    res = api_get_run(api_base, run_id.strip())
                    st.markdown("**Run response**")
                    st.code(_pretty(res), language="json")

        with col2:
            st.caption("Tip: copy run_id from Run page response.")

    elif page == "Approvals":
        st.subheader("Approvals queue")
        st.write("v1 needs a pending approvals endpoint for a real queue view.")
        st.caption("Recommended endpoint (future): GET /api/approvals/pending")

        # Placeholder: allow resume if user knows run_id
        st.markdown("### Resume by run_id")
        run_id = st.text_input("Run ID to resume", value="")
        approval_text = st.text_area("Approval payload (JSON object)", value='{"approved": true, "notes": ""}', height=140)
        ok, approval_payload, err = _safe_json_loads(approval_text)
        if not ok:
            st.error(f"Invalid JSON: {err}")

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("Approve (resume)", type="primary", disabled=(not ok or not run_id.strip())):
                res = api_resume_run(api_base, run_id.strip(), approval_payload)
                st.code(_pretty(res), language="json")

        with colB:
            if st.button("Reject (resume)", disabled=(not ok or not run_id.strip())):
                payload = dict(approval_payload)
                payload.setdefault("approved", False)
                res = api_resume_run(api_base, run_id.strip(), payload)
                st.code(_pretty(res), language="json")

        st.markdown("---")
        st.markdown("### Pending approvals (when endpoint exists)")
        res = api_list_pending_approvals_v1(api_base)
        st.code(_pretty(res), language="json")


def _discover_flows_local(products_dir: str, product: str) -> List[str]:
    import glob
    import os

    flow_dir = os.path.join(products_dir, product, "flows")
    names: List[str] = []
    for ext in ("*.yaml", "*.yml", "*.json"):
        for p in glob.glob(os.path.join(flow_dir, ext)):
            base = os.path.basename(p)
            # flow name is file stem
            stem = os.path.splitext(base)[0]
            names.append(stem)
    return sorted(set(names))


if __name__ == "__main__":
    main()