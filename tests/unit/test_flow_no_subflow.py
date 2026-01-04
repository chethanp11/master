# ==============================
# Tests: Disallow subflow steps in v1
# ==============================
from __future__ import annotations

import pytest

from core.contracts.flow_schema import FlowDef


def test_flow_subflow_is_rejected() -> None:
    with pytest.raises(Exception):
        FlowDef.model_validate(
            {
                "id": "demo",
                "version": "1.0.0",
                "steps": [
                    {
                        "id": "call_flow",
                        "type": "subflow",
                        "subflow": "other_flow",
                    }
                ],
            }
        )
