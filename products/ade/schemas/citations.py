
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict

from .slices import FilterSpec


class CsvCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    columns: List[str]
    filters: List[FilterSpec]


class PdfCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str
    page: int
    text_span: str


class CitationRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["csv", "pdf"]
    csv: Optional[CsvCitation] = None
    pdf: Optional[PdfCitation] = None
