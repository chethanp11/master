from typing import Any

# ==============================
# UI Smoke Test
# ==============================
import json
from types import SimpleNamespace


class _FakeResponse:
    def __init__(self, body: dict, ok: bool = True) -> None:
        self._body = body
        self.ok = ok

    def json(self) -> dict:
        return self._body


class _FakeStreamlit:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.session_state: dict[str, Any] = {}

    def subheader(self, value: str) -> None:
        self.calls.append(("subheader", value))

    def info(self, message: str) -> None:
        self.calls.append(("info", message))

    def write(self, value: Any) -> None:
        self.calls.append(("write", str(value)))

    def markdown(self, value: str) -> None:
        self.calls.append(("markdown", value))

    def expander(self, label: str, *, expanded: bool = False):
        self.calls.append(("expander_open", label))
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.calls.append(("expander_close", ""))

    def table(self, value: Any) -> None:
        self.calls.append(("table", json.dumps(value)))

    def columns(self, count: int):
        return (self, self)


def test_ui_imports_without_errors(monkeypatch):
    import importlib
    import sys

    evt = SimpleNamespace()
    monkeypatch.setitem(sys.modules, "streamlit", evt)
    module = importlib.import_module("gateway.ui.platform_app")
    assert hasattr(module, "main")


def test_api_client_list_products(monkeypatch):
    import gateway.ui.platform_app as platform_app

    stub_body = {"ok": True, "data": {"products": [{"name": "hello_world", "display_name": "Hello World", "flows": ["hello_world"]}]}}
    monkeypatch.setattr(platform_app.requests, "get", lambda *args, **kwargs: _FakeResponse(stub_body))
    client = platform_app.ApiClient("https://api.example.com")
    resp = client.list_products()
    assert resp.ok
    assert resp.body["data"]["products"][0]["name"] == "hello_world"


def test_product_summary_render(monkeypatch):
    import gateway.ui.platform_app as platform_app

    stub_st = _FakeStreamlit()
    monkeypatch.setattr(platform_app, "st", stub_st)
    products = [{"name": "hello_world", "display_name": "Hello World", "description": "Demo", "flows": ["hello_world"]}]
    platform_app._render_product_summary(products)
    assert any(call[0] == "subheader" for call in stub_st.calls)
    assert any("Hello World" in call[1] for call in stub_st.calls if call[0] == "expander_open")
