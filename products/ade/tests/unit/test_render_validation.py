from products.ade.tools.render_decision_packet_html import RenderDecisionPacketHtmlTool


class DummyCtx:
    step_id = "render"
    run = None


def test_render_decision_packet_validation_error() -> None:
    tool = RenderDecisionPacketHtmlTool()
    result = tool.run({}, DummyCtx())
    assert not result.ok
    assert result.error
    assert "validation_error" in result.error.message
