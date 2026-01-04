# ==============================
# Tests: Flow schema user_input steps
# ==============================
from __future__ import annotations

import pytest

from core.contracts.flow_schema import FlowDef


def test_flow_with_user_input_parses() -> None:
    flow = FlowDef.model_validate(
        {
            "id": "demo",
            "version": "1.0.0",
            "steps": [
                {
                    "id": "input",
                    "type": "user_input",
                    "params": {
                        "schema_version": "1.0",
                        "form_id": "demo_input",
                        "prompt": "Choose an option",
                        "input_type": "select",
                        "choices": [{"label": "A", "value": "a"}],
                        "defaults": {"choice": "a"},
                        "schema": {"type": "object", "properties": {"choice": {"type": "string"}}},
                    },
                }
            ],
        }
    )
    assert flow.id == "demo"
    assert flow.steps[0].type.value == "user_input"


def test_flow_user_input_missing_prompt_fails() -> None:
    with pytest.raises(Exception):
        FlowDef.model_validate(
            {
                "id": "demo",
                "version": "1.0.0",
                "steps": [
                    {
                        "id": "input",
                        "type": "user_input",
                        "params": {
                            "schema_version": "1.0",
                            "form_id": "demo_input",
                            "input_type": "text",
                        },
                    }
                ],
            }
        )
