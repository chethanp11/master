from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.visual_insights.contracts.refs import DatasetRef, DocRef, FileRef


class IngestFilesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    files: List[FileRef]


class IngestFilesOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_refs: List[DatasetRef]
    doc_refs: List[DocRef]


def ingest_files(payload: IngestFilesInput) -> IngestFilesOutput:
    dataset_refs: List[DatasetRef] = []
    doc_refs: List[DocRef] = []

    for file in payload.files:
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
    return IngestFilesOutput(dataset_refs=dataset_refs, doc_refs=doc_refs)


class IngestFilesTool(BaseTool):
    name = "ingest_files"
    description = "Creates dataset and document references from uploaded files."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = IngestFilesInput.model_validate(params or {})
            output = ingest_files(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> IngestFilesTool:
    return IngestFilesTool()
