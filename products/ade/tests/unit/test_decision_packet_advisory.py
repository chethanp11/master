from products.ade.schemas.decision_packet import DecisionPacket
from products.ade.schemas.decision_section import DecisionSection
from products.ade.tools.render_decision_packet_html import RenderDecisionPacketInput, render_decision_packet_html


def test_decision_packet_advisory_language() -> None:
    section = DecisionSection(
        section_id="s1",
        title="Data sufficiency",
        intent="assess",
        narrative="Inputs are sufficient.",
        claim_strength="medium",
        visuals=[],
        evidence_refs=[{"dataset_id": "sample.csv", "columns": ["a", "b"]}],
        rejected_alternatives=[],
    )
    packet = DecisionPacket(
        question="Recommendation Packet",
        decision_summary="Summary",
        confidence_level="medium",
        assumptions=["Inputs reflect dataset."],
        limitations=["Limited rows."],
        sections=[section],
        trace_refs=[{"step_id": "read"}],
    )
    html = render_decision_packet_html(RenderDecisionPacketInput(packet=packet)).html
    assert "Recommendation summary" in html
    assert "Advisory only" in html
