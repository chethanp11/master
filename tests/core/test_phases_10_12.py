from __future__ import annotations

"""Tests for Phases 10-12: Parallel Tools, Question Loop, Retrieval.

Tests cover:
- Phase 10: ToolBatchStepDef and parallel read-only tool execution
- Phase 11: QuestionSet with validation rules
- Phase 12: Retrieval augmentation with query_prior_runs and query_approved_sources
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pytest

from core.contracts.flow_schema import (
    StepDef,
    StepType,
    ToolBatchItem,
    ToolBatchStepDef,
)
from core.contracts.interaction_schema import (
    Question,
    QuestionSet,
    QuestionSetProvenance,
    UserAnswers,
)
from core.config.schema import PoliciesConfig, RetrievalPolicyConfig, Settings
from core.governance.gates import RetrievalGate
from core.orchestrator.user_input_handler import (
    validate_question_set_answers,
    _validate_field_rules,
)
from core.tools.retrieval import (
    RetrievalPolicy,
    query_prior_runs,
    query_approved_sources,
)


# =============================================================================
# Phase 10: ToolBatchStepDef Tests
# =============================================================================


def test_tool_batch_step_def_basic() -> None:
    """ToolBatchStepDef can be created with required fields."""
    step = ToolBatchStepDef(
        id="gather_evidence",
        tools=["tool_a", "tool_b", "tool_c"],
    )
    assert step.id == "gather_evidence"
    assert step.type == "tool_batch"
    assert step.tools == ["tool_a", "tool_b", "tool_c"]
    assert step.parallel is True  # Default
    assert step.merge_strategy == "by_tool_name"  # Default


def test_tool_batch_step_def_with_inputs() -> None:
    """ToolBatchStepDef supports per-tool inputs."""
    step = ToolBatchStepDef(
        id="batch",
        tools=["tool_a", "tool_b"],
        inputs={
            "tool_a": {"param1": "value1"},
            "tool_b": {"param2": "value2"},
        },
        parallel=False,
    )
    assert step.inputs["tool_a"]["param1"] == "value1"
    assert step.parallel is False


def test_tool_batch_step_def_validates_min_tools() -> None:
    """ToolBatchStepDef requires at least one tool."""
    with pytest.raises(ValueError):
        ToolBatchStepDef(id="empty", tools=[])


def test_tool_batch_step_def_validates_max_tools() -> None:
    """ToolBatchStepDef limits to max 20 tools."""
    tools = [f"tool_{i}" for i in range(21)]
    with pytest.raises(ValueError):
        ToolBatchStepDef(id="too_many", tools=tools)


def test_tool_batch_item_model() -> None:
    """ToolBatchItem can be created with tool_name and inputs."""
    item = ToolBatchItem(
        tool_name="test_tool",
        inputs={"query": "test"},
        alias="my_tool",
    )
    assert item.tool_name == "test_tool"
    assert item.inputs["query"] == "test"
    assert item.alias == "my_tool"


def test_step_def_tool_batch_type() -> None:
    """StepDef supports TOOL_BATCH type."""
    step = StepDef(
        id="batch_step",
        type=StepType.TOOL_BATCH,
        tools=[ToolBatchItem(tool_name="tool_a", inputs={})],
        parallel=True,
    )
    assert step.type == StepType.TOOL_BATCH
    assert len(step.tools) == 1
    assert step.parallel is True


# =============================================================================
# Phase 11: Question/QuestionSet Tests
# =============================================================================


def test_question_with_validation_rules() -> None:
    """Question supports validation field."""
    question = Question(
        key="age",
        prompt="What is your age?",
        type="number",
        required=True,
        validation={"min": 0, "max": 150},
    )
    assert question.validation["min"] == 0
    assert question.validation["max"] == 150


def test_question_with_default_value() -> None:
    """Question supports default value."""
    question = Question(
        key="country",
        prompt="Select country",
        type="string",
        default="US",
    )
    assert question.default == "US"


def test_question_set_with_context() -> None:
    """QuestionSet supports context field."""
    qs = QuestionSet(
        id="info_gather",
        title="Information Gathering",
        questions=[
            Question(key="name", prompt="Name?", type="string"),
        ],
        context="We need this info to proceed.",
        provenance=QuestionSetProvenance(created_from="test"),
    )
    assert qs.context == "We need this info to proceed."


def test_validate_question_set_answers_basic() -> None:
    """validate_question_set_answers validates required fields."""
    qs = QuestionSet(
        id="test",
        title="Test",
        questions=[
            Question(key="name", prompt="Name?", type="string", required=True),
        ],
        required_fields=["name"],
        provenance=QuestionSetProvenance(created_from="test"),
    )
    
    # Missing required field
    answers = UserAnswers(question_set_id="test", answers={})
    errors = validate_question_set_answers(qs, answers)
    assert "missing_required:name" in errors
    
    # Valid answer
    answers = UserAnswers(question_set_id="test", answers={"name": "John"})
    errors = validate_question_set_answers(qs, answers)
    assert len(errors) == 0


def test_validate_field_rules_number() -> None:
    """_validate_field_rules validates number min/max."""
    # Below minimum
    errors = _validate_field_rules("age", 5, {"min": 10, "max": 100}, "number")
    assert "validation_min:age" in errors
    
    # Above maximum
    errors = _validate_field_rules("age", 150, {"min": 0, "max": 120}, "number")
    assert "validation_max:age" in errors
    
    # Valid
    errors = _validate_field_rules("age", 25, {"min": 0, "max": 120}, "number")
    assert len(errors) == 0


def test_validate_field_rules_string_length() -> None:
    """_validate_field_rules validates string length."""
    # Too short
    errors = _validate_field_rules("code", "AB", {"minLength": 3}, "string")
    assert "validation_minLength:code" in errors
    
    # Too long
    errors = _validate_field_rules("code", "ABCDEFGH", {"maxLength": 5}, "string")
    assert "validation_maxLength:code" in errors
    
    # Valid
    errors = _validate_field_rules("code", "ABC", {"minLength": 2, "maxLength": 5}, "string")
    assert len(errors) == 0


def test_validate_field_rules_pattern() -> None:
    """_validate_field_rules validates regex pattern."""
    # Invalid pattern
    errors = _validate_field_rules("email", "invalid", {"pattern": r"^[\w.]+@[\w.]+$"}, "string")
    assert "validation_pattern:email" in errors
    
    # Valid pattern
    errors = _validate_field_rules("email", "test@example.com", {"pattern": r"^[\w.]+@[\w.]+$"}, "string")
    assert len(errors) == 0


def test_validate_question_set_with_validation_rules() -> None:
    """validate_question_set_answers applies custom validation rules."""
    qs = QuestionSet(
        id="test",
        title="Test",
        questions=[
            Question(
                key="score",
                prompt="Score?",
                type="number",
                required=True,
                validation={"min": 0, "max": 100},
            ),
        ],
        provenance=QuestionSetProvenance(created_from="test"),
    )
    
    # Score too high
    answers = UserAnswers(question_set_id="test", answers={"score": 150})
    errors = validate_question_set_answers(qs, answers)
    assert "validation_max:score" in errors
    
    # Valid score
    answers = UserAnswers(question_set_id="test", answers={"score": 85})
    errors = validate_question_set_answers(qs, answers)
    assert len(errors) == 0


# =============================================================================
# Phase 12: Retrieval Augmentation Tests
# =============================================================================


def test_retrieval_policy_is_allowed() -> None:
    """RetrievalPolicy.is_allowed checks allowed/blocked sources."""
    policy = RetrievalPolicy(
        allowed_sources=["runs:current_product", "trace_events"],
        blocked_sources=["runs:other_products"],
    )
    
    assert policy.is_allowed("runs:current_product") is True
    assert policy.is_allowed("trace_events") is True
    assert policy.is_allowed("runs:other_products") is False
    assert policy.is_allowed("unknown_source") is False


def test_retrieval_policy_empty_allowed() -> None:
    """RetrievalPolicy with empty allowed allows all not blocked."""
    policy = RetrievalPolicy(
        allowed_sources=[],
        blocked_sources=["blocked_source"],
    )
    
    assert policy.is_allowed("any_source") is True
    assert policy.is_allowed("blocked_source") is False


def test_retrieval_policy_from_config() -> None:
    """RetrievalPolicy.from_config creates policy from dict."""
    config = {
        "allowed_sources": ["source_a", "source_b"],
        "blocked_sources": ["source_c"],
    }
    policy = RetrievalPolicy.from_config(config)
    
    assert policy.is_allowed("source_a") is True
    assert policy.is_allowed("source_c") is False


def test_retrieval_policy_config_schema() -> None:
    """RetrievalPolicyConfig validates correctly."""
    config = RetrievalPolicyConfig(
        allowed_sources=["runs:current_product", "trace_events"],
        blocked_sources=["runs:other_products"],
    )
    assert len(config.allowed_sources) == 2
    assert "runs:other_products" in config.blocked_sources


def test_policies_config_with_retrieval() -> None:
    """PoliciesConfig supports retrieval_policy field."""
    config = PoliciesConfig(
        retrieval_policy=RetrievalPolicyConfig(
            allowed_sources=["runs:current_product"],
            blocked_sources=[],
        ),
    )
    assert config.retrieval_policy is not None
    assert "runs:current_product" in config.retrieval_policy.allowed_sources


def test_retrieval_gate_resolve_allowed_sources_global() -> None:
    """RetrievalGate resolves sources from global policy."""
    gate = RetrievalGate()
    
    settings = Settings(
        policies=PoliciesConfig(
            retrieval_policy=RetrievalPolicyConfig(
                allowed_sources=["runs:current_product", "trace_events"],
            ),
        ),
    )
    
    allowed = gate.resolve_allowed_sources(settings, product="test", flow="main")
    assert "runs:current_product" in allowed
    assert "trace_events" in allowed


def test_retrieval_gate_resolve_product_override() -> None:
    """RetrievalGate uses product-specific overrides."""
    gate = RetrievalGate()
    
    settings = Settings(
        policies=PoliciesConfig(
            retrieval_policy=RetrievalPolicyConfig(
                allowed_sources=["global_source"],
            ),
            by_product={
                "my_product": {
                    "retrieval_allowed_sources": ["product_source"],
                },
            },
        ),
    )
    
    # Product override takes precedence
    allowed = gate.resolve_allowed_sources(settings, product="my_product", flow="main")
    assert "product_source" in allowed
    assert "global_source" not in allowed
    
    # Other products use global
    allowed = gate.resolve_allowed_sources(settings, product="other", flow="main")
    assert "global_source" in allowed


def test_retrieval_gate_is_source_blocked() -> None:
    """RetrievalGate.is_source_blocked checks blocked sources."""
    gate = RetrievalGate()
    
    settings = Settings(
        policies=PoliciesConfig(
            retrieval_policy=RetrievalPolicyConfig(
                blocked_sources=["runs:other_products"],
            ),
        ),
    )
    
    assert gate.is_source_blocked(settings, source="runs:other_products", product="test") is True
    assert gate.is_source_blocked(settings, source="runs:current_product", product="test") is False


# =============================================================================
# Integration Tests
# =============================================================================


def test_tool_batch_with_step_def_validation() -> None:
    """StepDef validates tool_batch requirements."""
    # Valid tool_batch
    step = StepDef(
        id="batch",
        type=StepType.TOOL_BATCH,
        tools=[ToolBatchItem(tool_name="tool_a")],
    )
    assert step.type == StepType.TOOL_BATCH
    
    # Missing tools raises validation error
    with pytest.raises(ValueError, match="tool_batch steps require tools"):
        StepDef(id="empty_batch", type=StepType.TOOL_BATCH, tools=[])


def test_question_set_unique_keys() -> None:
    """QuestionSet validates unique question keys."""
    with pytest.raises(ValueError, match="question keys must be unique"):
        QuestionSet(
            id="dup",
            title="Duplicate Keys",
            questions=[
                Question(key="same", prompt="Q1", type="string"),
                Question(key="same", prompt="Q2", type="string"),
            ],
            provenance=QuestionSetProvenance(created_from="test"),
        )


def test_question_set_required_fields_exist() -> None:
    """QuestionSet validates required_fields exist in questions."""
    with pytest.raises(ValueError, match="required_fields not present"):
        QuestionSet(
            id="missing",
            title="Missing Required",
            questions=[
                Question(key="name", prompt="Name?", type="string"),
            ],
            required_fields=["name", "nonexistent"],
            provenance=QuestionSetProvenance(created_from="test"),
        )


def test_question_types() -> None:
    """Question supports all QuestionType values."""
    types = ["string", "number", "boolean", "enum", "object"]
    for qtype in types:
        q = Question(key=f"test_{qtype}", prompt=f"Test {qtype}?", type=qtype)  # type: ignore
        assert q.type == qtype


def test_question_enum_with_choices() -> None:
    """Question enum type uses enum field for choices."""
    q = Question(
        key="color",
        prompt="Favorite color?",
        type="enum",
        enum=["red", "green", "blue"],
    )
    assert q.enum == ["red", "green", "blue"]
