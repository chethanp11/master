from typing import Optional

import pytest

from products.visual_insights.contracts.io import UploadRequest
from products.visual_insights.contracts.refs import FileRef
from products.visual_insights.contracts.modes import InsightMode
from products.visual_insights.flows.v1_flow import run_visual_insights_v1

ALLOWED_CHART_TYPES = {"line", "bar", "stacked_bar", "scatter", "table"}
TRACE_ORDER = [
    "ingest",
    "profile_index",
    "plan",
    "compute",
    "evidence",
    "render",
    "export",
]


def _upload_request(mode: InsightMode, prompt: Optional[str] = None) -> UploadRequest:
    files = [
        FileRef(file_id="csv_1", file_type="csv", name="data.csv"),
        FileRef(file_id="pdf_1", file_type="pdf", name="context.pdf"),
    ]
    return UploadRequest(files=files, mode=mode, prompt=prompt)


def _check_response(response, *, min_cards: int) -> None:
    assert response.run_id
    assert response.cards
    assert len(response.cards) >= min_cards
    for card in response.cards:
        assert card.card_id
        assert card.chart_type in ALLOWED_CHART_TYPES
        assert card.narrative
        assert isinstance(card.citations, list)
        assert card.citations
        assert isinstance(card.chart_spec, dict)
    expected_trace = []
    for step in TRACE_ORDER:
        expected_trace.extend([f"{step}:start", f"{step}:end"])
    assert getattr(response, "trace_steps", []) == expected_trace


@pytest.mark.parametrize(
    "mode,prompt,min_cards",
    [
        (InsightMode.summarize_dataset, None, 1),
        (InsightMode.answer_question, "What drove the spike?", 1),
        (InsightMode.anomalies_and_drivers, None, 2),
    ],
)
def test_vi_golden_path_modes(mode, prompt, min_cards):
    upload = _upload_request(mode, prompt)
    response = run_visual_insights_v1(upload_request=upload, ctx={"run_id": "run_test", "mode": mode})
    _check_response(response, min_cards=min_cards)
