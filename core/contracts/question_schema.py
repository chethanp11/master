from __future__ import annotations

# ==============================
# Question Set Contracts
# ==============================
"""
Contracts for structured missing-info question sets.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


QuestionType = Literal["string", "number", "boolean", "enum", "object"]

_MAX_QUESTIONS = 20


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    prompt: str
    type: QuestionType
    enum: Optional[List[str]] = None
    required: bool = False
    help: Optional[str] = None


class QuestionSetProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    created_from: str
    evidence_refs: List[str] = Field(default_factory=list)


class QuestionSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    questions: List[Question]
    required_fields: List[str] = Field(default_factory=list)
    validation_schema: Dict[str, Any] = Field(default_factory=dict)
    guidance: Optional[str] = None
    provenance: QuestionSetProvenance

    @model_validator(mode="after")
    def _validate_questions(self) -> "QuestionSet":
        if len(self.questions) > _MAX_QUESTIONS:
            raise ValueError("question_set too large")
        keys = [q.key for q in self.questions]
        if len(keys) != len(set(keys)):
            raise ValueError("question_set question keys must be unique")
        missing = [key for key in self.required_fields if key not in keys]
        if missing:
            raise ValueError(f"required_fields not present in questions: {missing}")
        return self


class UserAnswers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_set_id: str
    answers: Dict[str, Any]
    submitted_at: Optional[datetime] = None
