from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.refs import DatasetRef, DocRef

STEP_NAME = "profile_index"


class ProfileIndexInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_refs: List[DatasetRef]
    doc_refs: List[DocRef]


class ProfileIndexOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_profiles: List[Dict[str, str]]
    pdf_index_refs: List[Dict[str, str]]


def run_step(inputs: ProfileIndexInput, ctx: Dict[str, str]) -> ProfileIndexOutput:
    """
    Computes basic profiles. calls no agents. Expected profiling tools.
    """
    return ProfileIndexOutput(dataset_profiles=[], pdf_index_refs=[])
