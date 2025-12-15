# ==============================
# UI Smoke Test
# ==============================
def test_ui_imports_without_errors(monkeypatch):
    import importlib
    import sys
    from types import SimpleNamespace

    monkeypatch.setitem(sys.modules, "streamlit", SimpleNamespace())
    module = importlib.import_module("gateway.ui.platform_app")
    assert hasattr(module, "main")
