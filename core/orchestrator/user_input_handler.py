"""
User Input Handler Module

This module handles user input lifecycle operations:
- User input step detection and pause
- User input validation
- User input response handling
- Context pack merging with user answers

Internal module - only imported by engine.py
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

from core.contracts.context_pack_schema import ContextPack
from core.contracts.interaction_schema import HitlInputSchema, HitlRequest, HitlResolution
from core.contracts.question_schema import QuestionSet, UserAnswers
from core.contracts.run_schema import (
    RunOperationResult,
    RunStatus,
    StepRecord,
    StepStatus,
)
from core.contracts.user_input_schema import (
    UserInputAnswer,
    UserInputModes,
    UserInputOption,
    UserInputPrompt,
    UserInputRequest,
    UserInputResponse,
)
from core.knowledge.context_pack_merge import merge_answers_into_context_pack
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.orchestrator.templating import render_params


# ============================================================================
# Validation Result
# ============================================================================


class ValidationResult:
    """Result of user input validation."""

    def __init__(
        self,
        *,
        valid: bool,
        errors: Optional[List[str]] = None,
        values: Optional[Dict[str, Any]] = None,
    ):
        self.valid = valid
        self.errors = errors or []
        self.values = values or {}

    @classmethod
    def success(cls, values: Dict[str, Any]) -> "ValidationResult":
        return cls(valid=True, values=values)

    @classmethod
    def failure(cls, errors: List[str]) -> "ValidationResult":
        return cls(valid=False, errors=errors)


# ============================================================================
# User Input Request Building
# ============================================================================


def build_user_input_prompt(
    run_ctx: RunContext,
    step_id: str,
    request: UserInputRequest,
) -> UserInputPrompt:
    """
    Build a UserInputPrompt from a UserInputRequest.

    Args:
        run_ctx: Run context
        step_id: Step ID
        request: User input request

    Returns:
        UserInputPrompt for display to user
    """
    allow_free_text = (
        request.mode == UserInputModes.FREE_TEXT_INPUT
        or request.input_type == "text"
    )
    question = request.prompt or request.title or request.form_id
    return UserInputPrompt(
        schema_version=request.schema_version,
        prompt_id=request.form_id,
        run_id=run_ctx.run_id,
        step_id=step_id,
        title=request.title,
        question=question,
        options=_options_from_request(request),
        defaults=request.defaults,
        required=request.required,
        allow_free_text=allow_free_text,
        schema=request.schema if isinstance(request.schema, dict) else {},
    )


def build_question_set_request(
    *,
    question_set: QuestionSet,
    question_set_key: str,
    context_pack_key: Optional[str],
) -> UserInputRequest:
    """
    Build a UserInputRequest from a QuestionSet.

    Args:
        question_set: The question set to build request for
        question_set_key: Key for storing question set in artifacts
        context_pack_key: Optional key for context pack to merge into

    Returns:
        UserInputRequest representing the question set
    """
    schema = question_set.validation_schema or _question_set_schema(question_set)
    constraints = {
        "question_set_id": question_set.id,
        "question_set_key": question_set_key,
    }
    if context_pack_key:
        constraints["context_pack_key"] = context_pack_key
    return UserInputRequest(
        form_id=question_set.id,
        prompt=question_set.title,
        title=question_set.title,
        mode=UserInputModes.CHOICE_INPUT,
        input_type="text",
        schema=schema,
        defaults={},
        required=list(question_set.required_fields),
        constraints=constraints,
        description=question_set.guidance,
    )


def build_hitl_request(
    *,
    request: UserInputRequest,
    run_ctx: RunContext,
    step_id: str,
    prompt: UserInputPrompt,
) -> HitlRequest:
    """
    Build a HitlRequest for a user input step.

    Args:
        request: User input request
        run_ctx: Run context
        step_id: Step ID
        prompt: User input prompt

    Returns:
        HitlRequest for HITL system
    """
    return HitlRequest(
        request_id=request.form_id,
        request_type="INPUT",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        created_at=int(time.time()),
        schema=HitlInputSchema(
            schema=request.schema if isinstance(request.schema, dict) else {},
            required=request.required,
            defaults=request.defaults,
            prompt=prompt.model_dump(mode="json"),
        ),
        payload={
            "title": request.title,
            "mode": request.mode,
            "input_type": request.input_type,
        },
    )


# ============================================================================
# User Input Validation
# ============================================================================


def validate_user_input(
    request: UserInputRequest,
    response: Optional[UserInputResponse],
    question_set: Optional[QuestionSet] = None,
    question_answers: Optional[UserAnswers] = None,
) -> ValidationResult:
    """
    Validate user input response against request schema.

    Supports flexible validation for different product requirements:
    - Text-only products (e.g., ADE): free_text is sufficient
    - Schema-based products: validate required fields against schema
    - Mixed mode: accept free_text alongside optional schema fields

    Args:
        request: The original user input request
        response: User input response (for non-question-set inputs)
        question_set: Optional question set
        question_answers: Optional answers to question set

    Returns:
        ValidationResult indicating success or errors
    """
    # Handle question set validation separately
    if question_set is not None:
        if question_answers is None:
            # Try to build answers from response
            if response is not None:
                question_answers = UserAnswers(
                    question_set_id=question_set.id,
                    answers=response.values,
                )
            else:
                return ValidationResult.failure(["missing_question_answers"])
        errors = validate_question_set_answers(question_set, question_answers)
        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success(question_answers.answers)
    
    # For non-question-set inputs
    if response is None:
        return ValidationResult.failure(["missing_response"])
    
    values = response.values or {}
    
    # Check for free text input (can come as "text", "response", or "free_text")
    has_free_text = bool(
        values.get("text") or 
        values.get("response") or 
        values.get("free_text")
    )
    has_values = bool(values)
    
    # Determine validation mode based on request configuration
    has_required_fields = bool(request.required)
    
    # If free_text is provided, accept it - skip schema validation
    if has_free_text:
        return ValidationResult.success(values)
    
    if has_required_fields:
        # Schema-based mode: validate all required fields
        errors = validate_user_input_values(request, values)
        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success(values)
    
    # No required fields - accept any input
    if has_values:
        return ValidationResult.success(values)
    
    return ValidationResult.failure(["no_input_provided"])


def validate_user_input_values(
    request: UserInputRequest,
    values: Dict[str, Any],
) -> List[str]:
    """
    Validate user input values against request schema.

    Args:
        request: User input request with schema
        values: Values provided by user

    Returns:
        List of validation error strings
    """
    errors: List[str] = []
    mode = request.mode or UserInputModes.CHOICE_INPUT

    if mode == UserInputModes.FREE_TEXT_INPUT:
        text_value = values.get("text")
        if not isinstance(text_value, str) or not text_value.strip():
            errors.append("missing_or_empty:text")
        return errors

    if mode != UserInputModes.CHOICE_INPUT:
        errors.append("invalid_mode")
        return errors

    for key in request.required:
        if key not in values:
            errors.append(f"missing_required:{key}")

    props = request.schema.get("properties") if isinstance(request.schema, dict) else {}
    if isinstance(props, dict):
        for key, spec in props.items():
            if key not in values:
                continue
            value = values.get(key)
            if not isinstance(spec, dict):
                continue
            expected_type = spec.get("type")
            if expected_type:
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"type_mismatch:{key}")
                if expected_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"type_mismatch:{key}")
                if expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"type_mismatch:{key}")
                if expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"type_mismatch:{key}")
            enum = spec.get("enum")
            if isinstance(enum, list) and value not in enum:
                errors.append(f"enum_mismatch:{key}")

    return errors


def validate_question_set_answers(
    question_set: QuestionSet,
    answers: UserAnswers,
) -> List[str]:
    """
    Validate answers against a question set.

    Args:
        question_set: The question set
        answers: User's answers

    Returns:
        List of validation error strings
    """
    errors: List[str] = []

    if answers.question_set_id != question_set.id:
        errors.append("question_set_id_mismatch")
        return errors

    question_map = {q.key: q for q in question_set.questions}

    for key in answers.answers.keys():
        if key not in question_map:
            errors.append(f"unexpected_field:{key}")

    for key in question_set.required_fields:
        if key not in answers.answers:
            errors.append(f"missing_required:{key}")

    for question in question_set.questions:
        if question.required and question.key not in answers.answers:
            errors.append(f"missing_required:{question.key}")
        if question.key not in answers.answers:
            continue
        value = answers.answers.get(question.key)
        if question.type == "number" and not isinstance(value, (int, float)):
            errors.append(f"type_mismatch:{question.key}")
        elif question.type == "boolean" and not isinstance(value, bool):
            errors.append(f"type_mismatch:{question.key}")
        elif question.type == "object" and not isinstance(value, dict):
            errors.append(f"type_mismatch:{question.key}")
        elif question.type in {"string", "enum"} and not isinstance(value, str):
            errors.append(f"type_mismatch:{question.key}")
        if question.enum and value not in question.enum:
            errors.append(f"enum_mismatch:{question.key}")

    return errors


# ============================================================================
# Context Pack Operations
# ============================================================================


def merge_into_context_pack(
    *,
    run_ctx: RunContext,
    question_set: QuestionSet,
    answers: UserAnswers,
    context_pack_key: Optional[str],
) -> Optional[ContextPack]:
    """
    Merge user answers into a context pack.

    Args:
        run_ctx: Run context with artifacts
        question_set: Question set that was answered
        answers: User's answers
        context_pack_key: Key to context pack in artifacts

    Returns:
        Merged ContextPack or None if not applicable
    """
    key = context_pack_key
    if key is None:
        # Find context pack in artifacts
        for candidate in sorted(run_ctx.artifacts.keys()):
            if candidate == "context_pack" or candidate.startswith("context_pack."):
                key = candidate
                break

    if key is None:
        return None

    payload = run_ctx.artifacts.get(key)
    if not isinstance(payload, dict):
        return None

    try:
        context_pack = ContextPack.model_validate(payload)
    except Exception:
        return None

    merged = merge_answers_into_context_pack(context_pack, question_set, answers)
    run_ctx.artifacts[key] = merged.model_dump(mode="json")
    return merged


# ============================================================================
# Response Parsing & Conversion
# ============================================================================


def looks_like_user_input_answer(payload: Dict[str, Any]) -> bool:
    """Check if payload looks like a UserInputAnswer."""
    if not isinstance(payload, dict):
        return False
    return any(key in payload for key in ("prompt_id", "selected_option_ids", "free_text"))


def looks_like_question_set_answers(payload: Dict[str, Any]) -> bool:
    """Check if payload looks like a UserAnswers (question set answers)."""
    if not isinstance(payload, dict):
        return False
    return "question_set_id" in payload or "answers" in payload


def answer_to_response(
    request: UserInputRequest,
    answer: UserInputAnswer,
    *,
    comment: Optional[str],
) -> UserInputResponse:
    """
    Convert a UserInputAnswer to a UserInputResponse.

    Args:
        request: Original user input request
        answer: User input answer
        comment: Optional comment

    Returns:
        UserInputResponse
    """
    values: Dict[str, Any] = {}
    selected = answer.selected_option_ids or []
    if selected:
        values[_primary_selection_key(request)] = selected[0]
    if answer.free_text:
        values["text"] = answer.free_text
    if answer.metadata:
        values["metadata"] = answer.metadata
    return UserInputResponse(
        schema_version=request.schema_version,
        form_id=request.form_id,
        values=values,
        comment=comment or "",
        metadata=answer.metadata,
    )


def store_user_input_artifacts(
    run_ctx: RunContext,
    form_id: str,
    values: Dict[str, Any],
    comment: Optional[str],
) -> None:
    """
    Store user input in run artifacts.

    Args:
        run_ctx: Run context
        form_id: Form ID
        values: User input values
        comment: Optional comment
    """
    bucket = run_ctx.artifacts.setdefault("user_input", {})
    if isinstance(bucket, dict):
        bucket[form_id] = {
            "values": values,
            "comment": comment or "",
            "metadata": values.get("metadata", {}),
        }


# ============================================================================
# Request Helpers
# ============================================================================


def resolve_question_set_from_request(
    request: UserInputRequest,
    run_ctx: RunContext,
) -> Optional[QuestionSet]:
    """
    Resolve a QuestionSet from a UserInputRequest.

    Args:
        request: User input request
        run_ctx: Run context with artifacts

    Returns:
        QuestionSet if found, None otherwise
    """
    constraints = request.constraints if isinstance(request.constraints, dict) else {}
    question_set_id = constraints.get("question_set_id")
    if not question_set_id:
        return None
    question_set_key = constraints.get("question_set_key") or f"question_set.{question_set_id}"
    payload = run_ctx.artifacts.get(question_set_key)
    if isinstance(payload, dict):
        try:
            return QuestionSet.model_validate(payload)
        except Exception:
            return None
    return None


def question_set_key_from_request(request: UserInputRequest) -> Optional[str]:
    """Extract question set key from request constraints."""
    constraints = request.constraints if isinstance(request.constraints, dict) else {}
    key = constraints.get("question_set_key")
    return key if isinstance(key, str) else None


def context_pack_key_from_request(request: UserInputRequest) -> Optional[str]:
    """Extract context pack key from request constraints."""
    constraints = request.constraints if isinstance(request.constraints, dict) else {}
    key = constraints.get("context_pack_key")
    return key if isinstance(key, str) else None


def summarize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a summary of a JSON schema for logging/tracing.

    Args:
        schema: JSON schema dict

    Returns:
        Summary dict with property count and hash
    """
    try:
        raw = str(schema)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    except Exception:
        digest = "unknown"

    props = schema.get("properties") if isinstance(schema, dict) else {}
    prop_keys: List[str] = []
    if isinstance(props, dict):
        prop_keys = list(props.keys())

    return {
        "properties": prop_keys[:10],
        "property_count": len(prop_keys),
        "sha256": digest,
    }


# ============================================================================
# Internal Helpers
# ============================================================================


def _primary_selection_key(request: UserInputRequest) -> str:
    """Get the primary selection key from request schema."""
    props = request.schema.get("properties") if isinstance(request.schema, dict) else {}
    if isinstance(props, dict) and len(props) == 1:
        return next(iter(props))
    if isinstance(props, dict):
        if "selection" in props:
            return "selection"
        if "value" in props:
            return "value"
    return "selection"


def _options_from_request(request: UserInputRequest) -> List[UserInputOption]:
    """Extract options from a UserInputRequest."""
    options: List[UserInputOption] = []
    if isinstance(request.choices, list):
        for item in request.choices:
            if not isinstance(item, dict):
                continue
            option_id = str(
                item.get("id") or item.get("value") or item.get("label") or ""
            ).strip()
            if not option_id:
                continue
            label = str(item.get("label") or item.get("value") or option_id)
            options.append(
                UserInputOption(
                    option_id=option_id,
                    label=label,
                    value=item.get("value"),
                    description=item.get("description"),
                )
            )
        return options

    props = request.schema.get("properties") if isinstance(request.schema, dict) else {}
    if isinstance(props, dict):
        for spec in props.values():
            if not isinstance(spec, dict):
                continue
            enum = spec.get("enum")
            if isinstance(enum, list):
                for item in enum:
                    option_id = str(item)
                    options.append(
                        UserInputOption(option_id=option_id, label=option_id, value=item)
                    )
                break
    return options


def _question_set_schema(question_set: QuestionSet) -> Dict[str, Any]:
    """Build a JSON schema from a QuestionSet."""
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for question in question_set.questions:
        spec: Dict[str, Any] = {}
        if question.type == "enum":
            spec["type"] = "string"
            if question.enum:
                spec["enum"] = list(question.enum)
        elif question.type == "number":
            spec["type"] = "number"
        elif question.type == "boolean":
            spec["type"] = "boolean"
        elif question.type == "object":
            spec["type"] = "object"
        else:
            spec["type"] = "string"
        properties[question.key] = spec
        if question.required or question.key in question_set.required_fields:
            required.append(question.key)
    return {"type": "object", "properties": properties, "required": required}
