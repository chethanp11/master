from __future__ import annotations

from typing import Any, Dict, List

from products.visual_insights.contracts.card import InsightCard, KeyMetric
from products.visual_insights.contracts.citations import CitationRef, CsvCitation
from products.visual_insights.tools.export_pdf import _build_stub_payload


def _make_card(rows: List[List[Any]]) -> InsightCard:
    columns = ["Expense", "H22024", "H2025", "H2026", "H2027", "H2028", "H2029"]
    chart_spec: Dict[str, Any] = {
        "type": "bar",
        "title": "Visualization for visual_insights_input.csv",
        "data": {"columns": columns, "rows": rows},
        "encoding": {"x": {"field": "Expense"}, "y": {"field": "H22024"}},
    }
    citations = [
        CitationRef(
            type="csv",
            csv=CsvCitation(dataset_id="visual_insights_input.csv", columns=columns, filters=[]),
        )
    ]
    return InsightCard(
        card_id="card_1",
        title="Visualization for visual_insights_input.csv",
        chart_type="bar",
        chart_spec=chart_spec,
        key_metrics=[KeyMetric(name="row_count", value=len(rows))],
        narrative="free-form narrative",
        data_slice=None,
        citations=citations,
        assumptions=["Chart generated from uploaded dataset."],
        anomaly_summary="series too short",
        anomalies=[],
    )


def test_stub_payload_grounding_and_guard_small() -> None:
    rows = [
        ["A", 20, 320, 352, 387, 426, 469],
        ["B", 10, 550, 100, 110, 121, 133],
        ["C", 30, 204, 224, 247, 272, 299],
        ["D", 120, 120, 120, 120, 120, 120],
        ["E", 11, 150, 165, 182, 200, 220],
        ["F", 15, 100, 110, 121, 140, 1500],
        ["G", 30, 300, 330, 363, 250, 275],
        ["H", 20, 400, 440, 484, 532, 586],
        ["I", 20, 100, 110, 121, 133, 146],
    ]
    stub = _build_stub_payload([_make_card(rows)])
    card = stub["cards"][0]

    anomaly_status = card["insights"]["data_quality"]["anomaly_detection"]["status"]
    assert anomaly_status == "INCONCLUSIVE"
    assert "no anomalies" not in card["narrative"].lower()

    highlights = card["insights"]["highlights"]
    assert any(
        item.get("type") == "outlier_candidate"
        and item.get("row_id") == "F"
        and item.get("column") == "H2029"
        and item.get("value") == 1500
        for item in highlights
    )

    assert "rows" in card["chart_spec"]["data"]
    assert "data_ref" not in card


def test_stub_payload_guard_large_dataset() -> None:
    rows = []
    for idx in range(60):
        rows.append([f"row_{idx}", idx, idx + 1, idx + 2, idx + 3, idx + 4, idx + 5])
    stub = _build_stub_payload([_make_card(rows)])
    card = stub["cards"][0]

    assert "data_ref" in card
    assert "rows" not in card["chart_spec"]["data"]
