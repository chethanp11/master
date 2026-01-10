from __future__ import annotations

from pydantic import BaseModel

from core.contracts.agent_schema import AgentResult
from core.contracts.evidence_schema import EvidenceItem
from core.contracts.run_schema import ArtifactRef, RunRecord, TraceEvent
from core.contracts.tool_schema import ToolResult


def test_boundary_contracts_are_pydantic() -> None:
    assert issubclass(ToolResult, BaseModel)
    assert issubclass(EvidenceItem, BaseModel)
    assert issubclass(ArtifactRef, BaseModel)
    assert issubclass(RunRecord, BaseModel)
    assert issubclass(TraceEvent, BaseModel)
    assert issubclass(AgentResult, BaseModel)
