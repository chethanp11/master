from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.plan import CardSpec
from products.visual_insights.contracts.refs import DatasetRef, DocRef


class EvidenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card: CardSpec
    datasets: List[DatasetRef]
    docs: List[DocRef]


class EvidenceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_csv_columns: List[str]
    requires_pdf: bool
    notes: List[str]


def determine_evidence(payload: EvidenceInput) -> EvidenceOutput:
    intent = payload.card.intent.lower()
    required_csv_columns: List[str] = []
    requires_pdf = False
    notes: List[str] = []

    numeric_keywords = {"trend", "change", "anomaly", "driver", "distribution"}
    text_keywords = {"complaint", "policy", "reason", "text", "issue"}

    if numeric_keywords & set(intent.split()):
        for dataset in payload.datasets:
            required_csv_columns.extend(list(dataset.schema.keys()))
            break
        notes.append("requires numeric CSV columns for analysis")

    if text_keywords & set(intent.split()):
        requires_pdf = True
        notes.append("requires PDF context for text-heavy intent")

    if not required_csv_columns and payload.datasets:
        required_csv_columns = list(payload.datasets[0].schema.keys())

    return EvidenceOutput(
        required_csv_columns=sorted(dict.fromkeys(required_csv_columns)),
        requires_pdf=requires_pdf,
        notes=notes or ["default evidence set"],
    )
