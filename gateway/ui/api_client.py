# ==============================
# API Client for UI
# ==============================
"""
HTTP client for UI interactions with the Gateway API.

All UI pages should use this client instead of direct core/ imports.
Handles errors gracefully with user-friendly messages.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


@dataclass(frozen=True)
class ApiResponse:
    """Response wrapper for API calls."""
    
    ok: bool
    body: Optional[Dict[str, Any]]
    error: Optional[str]


class ApiClient:
    """HTTP client for Gateway API calls."""
    
    def __init__(self, base_url: str, timeout: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self, method: str, path: str, payload: Optional[Dict[str, Any]] = None
    ) -> ApiResponse:
        """Make an HTTP request and return a standardized response."""
        url = f"{self.base_url}{path}"
        try:
            resp = getattr(requests, method.lower())(
                url, json=payload, timeout=self.timeout
            )
        except requests.RequestException as exc:
            return ApiResponse(ok=False, body=None, error=str(exc))

        try:
            body = resp.json()
        except ValueError:
            body = None

        if not resp.ok:
            error_msg = (
                body.get("error", {}).get("message")
                if body
                else resp.text
            )
            return ApiResponse(ok=False, body=body, error=error_msg)

        if isinstance(body, dict) and not body.get("ok", True):
            return ApiResponse(
                ok=False,
                body=body,
                error=body.get("error", {}).get("message", "API error"),
            )

        return ApiResponse(ok=True, body=body, error=None)

    # Product endpoints
    def list_products(self) -> ApiResponse:
        """List all enabled products."""
        return self._request("GET", "/api/products")

    def list_flows(self, product: str) -> ApiResponse:
        """List flows for a product."""
        return self._request("GET", f"/api/products/{product}/flows")

    # Run endpoints
    def run_flow(
        self, product: str, flow: str, payload: Dict[str, Any]
    ) -> ApiResponse:
        """Start a new flow run."""
        return self._request("POST", f"/api/run/{product}/{flow}", {"payload": payload})

    def get_run(self, run_id: str) -> ApiResponse:
        """Get run details."""
        return self._request("GET", f"/api/run/{run_id}")

    def list_runs(self) -> ApiResponse:
        """List all runs."""
        return self._request("GET", "/api/runs")

    # User input endpoints
    def get_pending_input(self, run_id: str) -> ApiResponse:
        """Get pending user input prompt for a run."""
        return self._request("GET", f"/api/runs/{run_id}/pending_input")

    def submit_user_input(
        self,
        run_id: str,
        *,
        prompt_id: str,
        selected_option_ids: Optional[List[str]] = None,
        free_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        values: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None,
    ) -> ApiResponse:
        """Submit user input for a pending prompt."""
        payload = {
            "prompt_id": prompt_id,
            "selected_option_ids": selected_option_ids,
            "free_text": free_text,
            "metadata": metadata or {},
            "values": values,
            "comment": comment or "",
        }
        return self._request("POST", f"/api/runs/{run_id}/user_input", payload)

    # Approval endpoints
    def list_approvals(self) -> ApiResponse:
        """List pending approvals."""
        return self._request("GET", "/api/approvals")

    def get_pending_approvals(self) -> ApiResponse:
        """Get all pending approvals (alias for list_approvals)."""
        return self.list_approvals()

    def approve(self, approval_id: str) -> ApiResponse:
        """Approve a pending approval."""
        return self._request("POST", f"/api/approvals/{approval_id}/approve", {})

    def deny(self, approval_id: str) -> ApiResponse:
        """Deny a pending approval."""
        return self._request("POST", f"/api/approvals/{approval_id}/deny", {})

    def resume_run(
        self,
        run_id: str,
        *,
        decision: str,
        approval_payload: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None,
        user_input_response: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        """Resume a paused run with an approval decision."""
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

    # Event endpoints
    def get_run_events(self, run_id: str) -> ApiResponse:
        """Get events for a run."""
        return self._request("GET", f"/api/runs/{run_id}/events")


def get_api_base_url(settings: Any) -> str:
    """Determine the API base URL from settings."""
    candidate = getattr(getattr(settings, "app", None), "api_base_url", None)
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip().rstrip("/")
    host = getattr(settings.app, "host", "localhost")
    port = getattr(settings.app, "port", 8000)
    scheme = "https" if getattr(settings.app, "debug", False) is False else "http"
    return f"{scheme}://{host}:{port}"


def pretty_json(obj: Any) -> str:
    """Format an object as pretty JSON."""
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
