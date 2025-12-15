from __future__ import annotations

from typing import Any, Dict, Literal

from pydantic import BaseModel, ConfigDict


class FileRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_id: str
    file_type: Literal["csv", "pdf"]
    name: str


class DatasetRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    schema: Dict[str, Any]
    row_count: int


class DocRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str
    page_count: int


class ArtifactRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: Literal["dataset", "document", "export"]
