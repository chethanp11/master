from core.orchestrator.context import RunContext, StepContext
from core.contracts.flow_schema import StepDef, StepType
from products.ade.schemas.decision_section import DecisionSection
from products.ade.tools.assemble_decision_packet import AssembleDecisionPacketTool


def test_decision_packet_includes_version_metadata() -> None:
    tool = AssembleDecisionPacketTool()
    run = RunContext(
        run_id="run_1",
        product="ade",
        flow="ade_v1",
        payload={"dataset": "sample.csv"},
        artifacts={
            "tool.data_reader.output": {
                "columns": ["a", "b"],
                "rows": [[1, 2], [3, 4]],
            }
        },
    )
    step = StepDef(id="assemble_decision_packet", type=StepType.TOOL, tool="assemble_decision_packet")
    ctx = StepContext(run=run, step=step, step_id="assemble_decision_packet", type="tool")
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
    params = {
        "sections": [section.model_dump(mode="json")],
        "confidence_level": "medium",
        "assumptions": ["Inputs reflect dataset."],
        "limitations": ["Limited rows."],
        "question": "Question",
        "decision_summary": "Summary",
        "trace_refs": [],
    }
    result = tool.run(params, ctx)
    assert result.ok
    packet = result.data["decision_packet"]
    assert packet.get("version_metadata")
