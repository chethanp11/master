from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, ConfigDict, Field


class VersionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str
    product_version: str
    flow_id: str
    flow_version: str
    schema_version: str
    dataset_hash: str
    input_hash: str
    dependency_versions: Dict[str, str] = Field(default_factory=dict)
