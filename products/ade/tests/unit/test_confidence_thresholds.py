from products.ade.utils.confidence import load_confidence_thresholds


def test_load_confidence_thresholds_defaults() -> None:
    thresholds = load_confidence_thresholds()
    assert thresholds["high"] >= thresholds["medium"]
