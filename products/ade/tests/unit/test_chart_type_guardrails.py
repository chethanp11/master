import pytest

from products.ade.contracts.card import KeyMetric
from products.ade.contracts.citations import CitationRef, CsvCitation
from products.ade.contracts.slices import FilterSpec
from products.ade.tools.assemble_insight_card import (
    AssembleInsightCardInput,
    assemble_insight_card,
)
from products.ade.tools.build_chart_spec import (
    BuildChartSpecInput,
    ChartData,
    build_chart_spec,
)
from products.ade.tools.recommend_chart import (
    RecommendChartInput,
    recommend_chart,
)


def test_recommend_chart_returns_allowed_type():
    payload = RecommendChartInput(
        intent="overview",
        has_time=True,
        has_y_numeric=True,
        has_x_numeric=False,
        wants_composition=False,
    )
    result = recommend_chart(payload)
    assert result.chart_type in {"line", "bar", "stacked_bar", "scatter", "table"}
    assert "time series" in result.rationale


def test_build_chart_spec_rejects_missing_fields():
    data = ChartData(columns=["time", "value"], rows=[[1, 10], [2, 20]])
    spec_input = BuildChartSpecInput(
        chart_type="line",
        title="Missing X",
        data=data,
        x="time",
        y="value2",
    )
    with pytest.raises(ValueError):
        build_chart_spec(spec_input)


def test_assemble_insight_card_requires_citations():
    data = ChartData(columns=["time", "value"], rows=[[1, 10]])
    chart_spec = build_chart_spec(
        BuildChartSpecInput(
            chart_type="line",
            title="Simple",
            data=data,
            x="time",
            y="value",
        )
    ).chart_spec
    metric = KeyMetric(name="sum", value=10)
    citation = CitationRef(
        type="csv",
        csv=CsvCitation(dataset_id="d1", columns=["value"], filters=[]),
        pdf=None,
    )
    assemble_insight_card(
        AssembleInsightCardInput(
            card_id="card1",
            title="Insight",
            chart_type="line",
            chart_spec=chart_spec,
            narrative="narrative",
            key_metrics=[metric],
            citations=[citation],
        )
    )
    with pytest.raises(ValueError):
        assemble_insight_card(
            AssembleInsightCardInput(
                card_id="card2",
                title="Insight",
                chart_type="table",
                chart_spec=chart_spec,
                narrative="narrative",
                key_metrics=[metric],
                citations=[],
            )
        )
