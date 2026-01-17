from products.ade.schemas.decision_packet import DecisionPacket
from products.ade.schemas.decision_section import DecisionSection
from products.ade.tools.assemble_business_report import AssembleBusinessReportInput, assemble_business_report
from products.ade.tools.compute_business_metrics import BusinessMetricsInput, compute_business_metrics


def test_assemble_business_report_quality_checks() -> None:
    metrics = compute_business_metrics(
        BusinessMetricsInput(
            dataset_id="sample.csv",
            columns=["Expense", "H1", "H2"],
            rows=[["A", 10, 20], ["B", 5, 8]],
            metric_focus="mean",
            chart_type="line",
            include_hypothesis_checks=True,
        )
    )
    section = DecisionSection(
        section_id="s1",
        title="Data sufficiency",
        intent="assess",
        narrative="Inputs are sufficient for evaluation.",
        claim_strength="medium",
        visuals=[],
        evidence_refs=[{"dataset_id": "sample.csv", "columns": ["Expense", "H1", "H2"]}],
        rejected_alternatives=[],
    )
    packet = DecisionPacket(
        question="Summarize spend",
        decision_summary="Recommendation summary.",
        confidence_level="medium",
        assumptions=["Inputs reflect uploaded dataset."],
        limitations=["Limited to uploaded rows."],
        sections=[section],
        trace_refs=[{"step_id": "read"}],
    )
    output = assemble_business_report(
        AssembleBusinessReportInput(
            metrics=metrics,
            packet=packet,
            downgrade_reasons=[],
            chart_type="line",
            metric_focus="mean",
            include_hypothesis_checks=True,
        )
    )
    assert output.report.executive_summary
