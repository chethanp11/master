from products.visual_insights.tools.detect_anomalies import (
    DetectAnomaliesInput,
    Point,
    detect_anomalies,
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
