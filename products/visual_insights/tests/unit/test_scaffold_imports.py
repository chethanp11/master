from products.visual_insights.flows.v1_flow import run_visual_insights_v1


def test_flow_placeholder_exists():
    assert hasattr(run_visual_insights_v1, "__call__")
