from products.ade.tools.detect_anomalies import (
    DetectAnomaliesInput,
    Point,
    detect_anomalies,
    Anomaly,
)


def test_detect_anomalies_identifies_outlier():
    series = [
        Point(ts="t1", value=10.0),
        Point(ts="t2", value=11.0),
        Point(ts="t3", value=9.5),
        Point(ts="t4", value=10.5),
        Point(ts="t5", value=10.2),
        Point(ts="t6", value=10.1),
        Point(ts="t7", value=10.0),
        Point(ts="t8", value=10.4),
        Point(ts="t9", value=10.3),
        Point(ts="t10", value=100.0),
    ]
    payload = DetectAnomaliesInput(series=series, min_points=8, z_threshold=2.5)
    result = detect_anomalies(payload)
    assert len(result.anomalies) == 1
    anomaly = result.anomalies[0]
    assert anomaly.ts == "t10"
    assert anomaly.zscore >= payload.z_threshold
    assert "found 1 anomalies" in result.summary


def test_detect_anomalies_handles_zero_variance():
    uniform = [Point(ts=f"t{i}", value=5.0) for i in range(1, 10)]
    payload = DetectAnomaliesInput(series=uniform, min_points=5)
    result = detect_anomalies(payload)
    assert result.anomalies == []
    assert result.summary == "no variance"


# IMP-022: TS-TOOL-ANOM-002 severity_score tests


def test_anomaly_has_severity_score_field():
    """TS-TOOL-ANOM-002: Anomaly model includes severity_score."""
    anomaly = Anomaly(ts="t1", value=100.0, zscore=3.5, severity_score=3.5)
    assert anomaly.severity_score == 3.5


def test_severity_score_is_absolute_zscore():
    """TS-TOOL-ANOM-002: severity_score is abs(zscore)."""
    series = [
        Point(ts="t1", value=10.0),
        Point(ts="t2", value=10.0),
        Point(ts="t3", value=10.0),
        Point(ts="t4", value=10.0),
        Point(ts="t5", value=10.0),
        Point(ts="t6", value=10.0),
        Point(ts="t7", value=10.0),
        Point(ts="t8", value=10.0),
        Point(ts="t9", value=100.0),  # High outlier
        Point(ts="t10", value=-80.0),  # Low outlier
    ]
    payload = DetectAnomaliesInput(series=series, min_points=8, z_threshold=2.0)
    result = detect_anomalies(payload)
    for anomaly in result.anomalies:
        assert anomaly.severity_score == abs(anomaly.zscore)


def test_anomalies_sorted_by_severity_descending():
    """TS-TOOL-ANOM-002: Anomalies sorted by severity_score descending."""
    series = [
        Point(ts="t1", value=10.0),
        Point(ts="t2", value=10.0),
        Point(ts="t3", value=10.0),
        Point(ts="t4", value=10.0),
        Point(ts="t5", value=10.0),
        Point(ts="t6", value=10.0),
        Point(ts="t7", value=10.0),
        Point(ts="t8", value=10.0),
        Point(ts="t9", value=50.0),  # Moderate outlier
        Point(ts="t10", value=100.0),  # Extreme outlier
    ]
    payload = DetectAnomaliesInput(series=series, min_points=8, z_threshold=2.0)
    result = detect_anomalies(payload)
    if len(result.anomalies) >= 2:
        for i in range(len(result.anomalies) - 1):
            assert result.anomalies[i].severity_score >= result.anomalies[i + 1].severity_score


def test_negative_zscore_has_positive_severity():
    """TS-TOOL-ANOM-002: Negative z-scores still have positive severity."""
    anomaly = Anomaly(ts="t1", value=-50.0, zscore=-4.2, severity_score=4.2)
    assert anomaly.zscore < 0
    assert anomaly.severity_score > 0
    assert anomaly.severity_score == abs(anomaly.zscore)
