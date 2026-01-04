from __future__ import annotations

# ==============================
# OpenAI Provider Header Tests
# ==============================

from core.models.providers.openai_provider import _should_send_org_header


def test_org_header_skips_placeholder() -> None:
    assert _should_send_org_header("PUT_OPENAI_ORG_ID_HERE") is False
    assert _should_send_org_header("placeholder") is False
    assert _should_send_org_header("YOUR_ORG_ID") is False
    assert _should_send_org_header("  ") is False


def test_org_header_allows_realistic_value() -> None:
    assert _should_send_org_header("org_1234567890") is True
