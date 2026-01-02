# ==============================
# Prompt Renderer Tests
# ==============================
from __future__ import annotations

import pytest

from core.agents.renderer import render_messages, render_template


def test_render_template_resolves_artifacts() -> None:
    context = {
        "artifacts": {
            "tool.data_reader.output": {"summary": "read 2 rows"},
        },
        "payload": {},
    }
    rendered = render_template(
        "Dataset: {{artifacts.tool.data_reader.output.summary}}",
        context,
    )
    assert rendered == "Dataset: read 2 rows"


def test_render_template_missing_placeholder_raises() -> None:
    context = {"artifacts": {}, "payload": {}}
    with pytest.raises(KeyError):
        render_template("Value: {{artifacts.tool.unknown.output}}", context)


def test_render_messages_handles_list() -> None:
    context = {
        "artifacts": {
            "tool.data_reader.output": {"summary": "ok"},
        },
        "payload": {"prompt": "hi"},
    }
    messages = [
        {"role": "system", "content": "System {{payload.prompt}}"},
        {"role": "user", "content": "Dataset {{artifacts.tool.data_reader.output.summary}}"},
    ]
    rendered = render_messages(messages, context)
    assert rendered[0]["content"] == "System hi"
    assert rendered[1]["content"] == "Dataset ok"
