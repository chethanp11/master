from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.io import FileRef, UploadRequest
from products.visual_insights.contracts.refs import DatasetRef, DocRef

STEP_NAME = "ingest"


class IngestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: UploadRequest


class IngestOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_refs: List[DatasetRef]
    doc_refs: List[DocRef]


def run_step(inputs: IngestInput, ctx: Dict[str, str]) -> IngestOutput:
    """
    Decide ingest intentions. Calls no agents and expects CSV/PDF ingest tools.
    """
    dataset_refs: List[DatasetRef] = []
    doc_refs: List[DocRef] = []
    for file in inputs.request.files:
        if file.file_type == "csv":
            dataset_refs.append(
                DatasetRef(
                    dataset_id=file.file_id,
                    schema={"date": "date", "category": "str", "value": "float"},
                    row_count=10,
                )
            )
        elif file.file_type == "pdf":
            doc_refs.append(DocRef(doc_id=file.file_id, page_count=1))
    return IngestOutput(dataset_refs=dataset_refs, doc_refs=doc_refs)
