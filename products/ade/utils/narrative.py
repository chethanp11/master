"""Narrative builder for ADE.

TS-AGENT-NARR-005: User-facing explanations derived from decision records,
not regenerated narratives.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class DecisionRecord:
    """Decision record from observability store."""

    def __init__(
        self,
        record_id: str,
        step_id: str,
        decision: str,
        rationale: str,
        confidence: str = "medium",
        timestamp: Optional[str] = None,
    ):
        self.record_id = record_id
        self.step_id = step_id
        self.decision = decision
        self.rationale = rationale
        self.confidence = confidence
        self.timestamp = timestamp


def build_explanation(decision_records: List[DecisionRecord]) -> str:
    """Build user-facing explanation from decision records.

    TS-AGENT-NARR-005: Explanations reference decision record IDs,
    not regenerated text.

    Args:
        decision_records: List of DecisionRecord objects from observability store.

    Returns:
        Formatted explanation string with decision record references.
    """
    if not decision_records:
        return "No decision records available for this run."

    sections: List[str] = []

    for record in decision_records:
        section = (
            f"[{record.record_id}] {record.decision}\n"
            f"  Rationale: {record.rationale}\n"
            f"  Confidence: {record.confidence}"
        )
        if record.timestamp:
            section += f"\n  Recorded: {record.timestamp}"
        sections.append(section)

    header = f"Analysis based on {len(decision_records)} recorded decisions:\n"
    return header + "\n\n".join(sections)


def build_explanation_from_dicts(decision_records: List[Dict[str, Any]]) -> str:
    """Build explanation from dictionary-formatted decision records.

    Args:
        decision_records: List of decision record dictionaries.

    Returns:
        Formatted explanation string.
    """
    records = [
        DecisionRecord(
            record_id=r.get("record_id", f"rec-{i}"),
            step_id=r.get("step_id", ""),
            decision=r.get("decision", ""),
            rationale=r.get("rationale", ""),
            confidence=r.get("confidence", "medium"),
            timestamp=r.get("timestamp"),
        )
        for i, r in enumerate(decision_records)
    ]
    return build_explanation(records)


def get_decision_records_summary(decision_records: List[DecisionRecord]) -> Dict[str, Any]:
    """Get summary of decision records for traceability.

    Args:
        decision_records: List of DecisionRecord objects.

    Returns:
        Summary dict with record IDs and count.
    """
    return {
        "total_records": len(decision_records),
        "record_ids": [r.record_id for r in decision_records],
        "steps_covered": list(set(r.step_id for r in decision_records)),
    }
