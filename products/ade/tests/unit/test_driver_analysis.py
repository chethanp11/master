from products.visual_insights.tools.driver_analysis import (
    DriverAnalysisInput,
    SegmentRow,
    driver_analysis,
)


def test_driver_analysis_top_drivers():
    rows = [
        SegmentRow(segment="A", before=100.0, after=130.0),
        SegmentRow(segment="B", before=50.0, after=60.0),
        SegmentRow(segment="C", before=20.0, after=80.0),
    ]
    payload = DriverAnalysisInput(rows=rows, top_k=2)
    result = driver_analysis(payload)
    assert result.total_before == 170.0
    assert result.total_after == 270.0
    assert result.total_delta == 100.0
    assert len(result.drivers) == 2
    assert result.drivers[0].segment == "C"
    assert result.drivers[1].segment == "A"


def test_driver_analysis_min_total_change_skips():
    rows = [
        SegmentRow(segment="A", before=10.0, after=10.2),
        SegmentRow(segment="B", before=5.0, after=5.1),
    ]
    payload = DriverAnalysisInput(rows=rows, min_total_change=1.0)
    result = driver_analysis(payload)
    assert result.drivers == []
    assert "no significant change" in result.summary
