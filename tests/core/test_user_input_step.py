from __future__ import annotations

# ==============================
# Tests: User Input Modes
# ==============================

from core.contracts.user_input_schema import UserInputModes, UserInputRequest
from core.orchestrator.engine import _validate_user_input_values


def test_user_input_free_text_requires_text() -> None:
    request = UserInputRequest(
        schema_version="1.0",
        form_id="notes",
        prompt="Notes",
        input_type="text",
        mode=UserInputModes.FREE_TEXT_INPUT,
    )
    errors = _validate_user_input_values(request, {"text": ""})
    assert "missing_or_empty:text" in errors

    ok_errors = _validate_user_input_values(request, {"text": "hello"})
    assert ok_errors == []


def test_user_input_choice_input_validates_required() -> None:
    request = UserInputRequest(
        schema_version="1.0",
        form_id="choice",
        prompt="Choice",
        input_type="select",
        mode=UserInputModes.CHOICE_INPUT,
        schema={
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "enum": ["bar", "line"]},
            },
        },
        required=["chart_type"],
    )
    errors = _validate_user_input_values(request, {})
    assert "missing_required:chart_type" in errors
