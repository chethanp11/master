from products.ade.contracts.decision_section import DecisionSection
from products.ade.tools.assemble_decision_packet import (
    AssembleDecisionPacketInput,
    assemble_decision_packet,
)


def test_assemble_decision_packet_roundtrip():
    section = DecisionSection(
        section_id="s1",
        title="Data sufficiency",
        intent="assess",
        narrative="Inputs are sufficient for evaluation.",
        claim_strength="medium",
        visuals=[],
        evidence_refs=[{"dataset_id": "d1", "columns": ["a", "b"]}],
        rejected_alternatives=["data_outage"],
    )
    payload = AssembleDecisionPacketInput(
        sections=[section],
        confidence_level="medium",
        assumptions=["assumption_1"],
        limitations=["limitation_1"],
        question="Is the dataset adequate?",
        decision_summary="Sufficient to proceed with analysis.",
        trace_refs=[{"event": "trace_1"}],
    )
    result = assemble_decision_packet(payload)
    packet = result.decision_packet
    assert packet.confidence_level == "medium"
    assert packet.sections[0].section_id == "s1"
    assert packet.trace_refs == [{"event": "trace_1"}]
