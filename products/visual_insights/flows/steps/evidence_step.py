from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict

from products.visual_insights.agents.evidence_agent import EvidenceInput, EvidenceOutput, determine_evidence
from products.visual_insights.contracts.plan import CardSpec
from products.visual_insights.contracts.refs import DatasetRef, DocRef

STEP_NAME = "evidence"


class EvidenceStepInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[CardSpec]
    dataset_refs: List[DatasetRef]
    doc_refs: List[DocRef]


class EvidenceStepOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_per_card: Dict[str, EvidenceOutput]


def run_step(inputs: EvidenceStepInput, ctx: Dict[str, str]) -> EvidenceStepOutput:
    """
    Calls EvidenceAgent per card. Tool intents for chunk retrieval implied.
    """
    per_card = {}
    for card in inputs.cards:
        agent_input = EvidenceInput(card=card, datasets=inputs.dataset_refs, docs=inputs.doc_refs)
        per_card[card.card_id] = determine_evidence(agent_input)
    return EvidenceStepOutput(evidence_per_card=per_card)
