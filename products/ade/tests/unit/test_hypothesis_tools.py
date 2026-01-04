from products.ade.tools.hypothesis_test_data_outage import DataOutageInput, hypothesis_test_data_outage
from products.ade.tools.hypothesis_test_seasonality import SeasonalityInput, hypothesis_test_seasonality


def test_data_outage_plausible_when_zeros_dominate():
    series = [{"ts": f"t{i}", "value": 0.0} for i in range(5)]
    payload = DataOutageInput(series=series, recent_window=5, outage_threshold=0.6)
    result = hypothesis_test_data_outage(payload)
    assert result.status == "plausible"


def test_data_outage_rejected_when_values_present():
    series = [{"ts": f"t{i}", "value": 1.0} for i in range(5)]
    payload = DataOutageInput(series=series, recent_window=5, outage_threshold=0.6)
    result = hypothesis_test_data_outage(payload)
    assert result.status == "rejected"


def test_seasonality_plausible_for_repeating_pattern():
    values = [10, 20, 30, 10, 20, 30, 10, 20, 30, 10, 20, 30]
    series = [{"ts": f"t{i}", "value": v} for i, v in enumerate(values)]
    payload = SeasonalityInput(series=series, period=3, min_points=9, strength_threshold=0.2)
    result = hypothesis_test_seasonality(payload)
    assert result.status == "plausible"


def test_seasonality_rejected_for_flat_series():
    series = [{"ts": f"t{i}", "value": 10.0} for i in range(12)]
    payload = SeasonalityInput(series=series, period=4, min_points=12, strength_threshold=0.2)
    result = hypothesis_test_seasonality(payload)
    assert result.status == "rejected"
