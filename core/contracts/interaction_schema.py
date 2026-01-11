# ==============================
# Interaction Contracts
# ==============================
"""
Interaction contracts for master/.

This module consolidates human-in-the-loop (HITL) interactions and question/answer
schemas used for user input collection during flow execution.

Consolidated from:
- hitl_schema.py (HitlRequestType, HitlResolutionStatus, HitlInputSchema, HitlRequest, HitlResolution)
- question_schema.py (QuestionType, Question, QuestionSetProvenance, QuestionSet, UserAnswers)
"""

from __future__ import annotations

# ==============================
# Imports
# ==============================

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from typing_extensions import Literal as LiteralExt

from pydantic import BaseModel, Field, ConfigDict, model_validator


# ==============================
# HITL Types (from hitl_schema)
# ==============================

HitlRequestType = Literal["APPROVAL", "INPUT"]
HitlResolutionStatus = Literal["ACCEPTED", "REJECTED", "PROVIDED", "ABORTED"]


# ==============================
# Question Types (from question_schema)
# ==============================

QuestionType = Literal["string", "number", "boolean", "enum", "object"]

_MAX_QUESTIONS = 20


# ==============================
# HITL Models (from hitl_schema)
# ==============================

class HitlInputSchema(BaseModel):
    """
    Schema describing the expected input format for HITL requests.
    Used to render forms/prompts in UI.
    """
    model_config = ConfigDict(extra="forbid")

    schema: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    defaults: Dict[str, Any] = Field(default_factory=dict)
    prompt: Dict[str, Any] = Field(default_factory=dict)


class HitlRequest(BaseModel):
    """
    Represents a request for human-in-the-loop intervention.
    Created by the orchestrator when a step requires human input/approval.
    """
    model_config = ConfigDict(extra="forbid")

    request_id: str
    request_type: HitlRequestType
    run_id: str
    step_id: str
    product: str
    flow: str
    status: str = Field(default="PENDING")
    created_at: int
    schema: Optional[HitlInputSchema] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class HitlResolution(BaseModel):
    """
    Resolution of a HITL request, provided by the user/operator.
    """
    model_config = ConfigDict(extra="forbid")

    request_id: str
    request_type: HitlRequestType
    status: HitlResolutionStatus
    resolved_at: int
    decision: Optional[str] = None
    values: Dict[str, Any] = Field(default_factory=dict)
    comment: Optional[str] = None
    resolved_by: Optional[str] = None


# ==============================
# Question Models (from question_schema)
# ==============================

class Question(BaseModel):
    """
    A single question to be answered by the user.
    """
    model_config = ConfigDict(extra="forbid")

    key: str
    prompt: str
    type: QuestionType
    enum: Optional[List[str]] = None
    required: bool = False
    help: Optional[str] = None


class QuestionSetProvenance(BaseModel):
    """Provenance/source of a question set."""
    model_config = ConfigDict(extra="forbid")

    created_from: str
    evidence_refs: List[str] = Field(default_factory=list)


class QuestionSet(BaseModel):
    """
    A collection of questions to be presented to the user.
    """
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
    """
    User's answers to a question set.
    """
    model_config = ConfigDict(extra="forbid")

    question_set_id: str
    answers: Dict[str, Any]
    submitted_at: Optional[datetime] = None


# ==============================
# Exports
# ==============================

__all__ = [
    # HITL
    "HitlRequestType",
    "HitlResolutionStatus",
    "HitlInputSchema",
    "HitlRequest",
    "HitlResolution",
    # Questions
    "QuestionType",
    "Question",
    "QuestionSetProvenance",
    "QuestionSet",
    "UserAnswers",
]
