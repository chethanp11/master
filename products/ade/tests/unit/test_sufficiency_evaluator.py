from products.ade.agents.sufficiency_evaluator import evaluate_sufficiency


def test_sufficiency_high_confidence():
    series = [{"ts": f"2024-01-{day:02d}", "value": 100 + day} for day in range(1, 16)]
    result = evaluate_sufficiency(row_count=120, has_time=True, series=series)
    assert result["confidence_level"] == "high"
    assert result["downgrade_reasons"] == []


def test_sufficiency_medium_confidence_for_low_rows():
    series = [{"ts": f"2024-01-{day:02d}", "value": 50 + day} for day in range(1, 16)]
    result = evaluate_sufficiency(row_count=25, has_time=True, series=series)
    assert result["confidence_level"] == "medium"
    assert "insufficient_rows" in result["downgrade_reasons"]


def test_sufficiency_low_confidence_for_multiple_downgrades():
    series = [{"ts": "2024-01-01", "value": 10}, {"ts": "2024-01-02", "value": 200}]
    result = evaluate_sufficiency(row_count=10, has_time=False, series=series)
    assert result["confidence_level"] == "low"
    assert "insufficient_rows" in result["downgrade_reasons"]
    assert "insufficient_time_window" in result["downgrade_reasons"]
    assert "unstable_variance" in result["downgrade_reasons"]
