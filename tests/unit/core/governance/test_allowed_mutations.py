# ==============================
# Tests: IMP-024 Allowed Runtime Mutations
# ==============================
"""
Tests for IMP-024: Allowed Runtime Mutations.

Tech Spec References:
- GOV-POL-SELFMOD-020: Budget consumption counters MAY be updated
- GOV-POL-SELFMOD-021: Run artifacts/evidence MAY be accumulated
- GOV-POL-SELFMOD-022: Run/step status MAY transition per state machine

All tests deterministic. No external I/O.
"""

from __future__ import annotations

import pytest

from core.governance.self_modification_guard import (
    AllowedMutationType,
    SelfModificationBlockedError,
    check_mutation_allowed,
    get_allowed_mutation_rationale,
    is_allowed_mutation,
)


# --------------------------------------------------------------------------- #
#  AllowedMutationType Tests
# --------------------------------------------------------------------------- #

class TestAllowedMutationType:
    """Tests for AllowedMutationType enumeration."""

    def test_budget_consumption_defined(self):
        """BUDGET_CONSUMPTION mutation type is defined."""
        assert AllowedMutationType.BUDGET_CONSUMPTION == "budget_consumption"

    def test_run_artifacts_defined(self):
        """RUN_ARTIFACTS mutation type is defined."""
        assert AllowedMutationType.RUN_ARTIFACTS == "run_artifacts"

    def test_evidence_accumulation_defined(self):
        """EVIDENCE_ACCUMULATION mutation type is defined."""
        assert AllowedMutationType.EVIDENCE_ACCUMULATION == "evidence_accumulation"

    def test_run_status_defined(self):
        """RUN_STATUS mutation type is defined."""
        assert AllowedMutationType.RUN_STATUS == "run_status"

    def test_step_status_defined(self):
        """STEP_STATUS mutation type is defined."""
        assert AllowedMutationType.STEP_STATUS == "step_status"

    def test_trace_events_defined(self):
        """TRACE_EVENTS mutation type is defined."""
        assert AllowedMutationType.TRACE_EVENTS == "trace_events"

    def test_all_is_frozenset(self):
        """ALL is a frozenset."""
        assert isinstance(AllowedMutationType.ALL, frozenset)

    def test_all_contains_all_types(self):
        """ALL contains all defined mutation types."""
        assert AllowedMutationType.BUDGET_CONSUMPTION in AllowedMutationType.ALL
        assert AllowedMutationType.RUN_ARTIFACTS in AllowedMutationType.ALL
        assert AllowedMutationType.EVIDENCE_ACCUMULATION in AllowedMutationType.ALL
        assert AllowedMutationType.RUN_STATUS in AllowedMutationType.ALL
        assert AllowedMutationType.STEP_STATUS in AllowedMutationType.ALL
        assert AllowedMutationType.TRACE_EVENTS in AllowedMutationType.ALL

    def test_all_count(self):
        """ALL has expected number of allowed types."""
        assert len(AllowedMutationType.ALL) == 6


# --------------------------------------------------------------------------- #
#  is_allowed_mutation Tests
# --------------------------------------------------------------------------- #

class TestIsAllowedMutation:
    """Tests for is_allowed_mutation function."""

    def test_budget_consumption_allowed(self):
        """Budget consumption is allowed (GOV-POL-SELFMOD-020)."""
        assert is_allowed_mutation("budget_consumption") is True

    def test_run_artifacts_allowed(self):
        """Run artifacts are allowed (GOV-POL-SELFMOD-021)."""
        assert is_allowed_mutation("run_artifacts") is True

    def test_evidence_accumulation_allowed(self):
        """Evidence accumulation is allowed (GOV-POL-SELFMOD-021)."""
        assert is_allowed_mutation("evidence_accumulation") is True

    def test_run_status_allowed(self):
        """Run status transitions allowed (GOV-POL-SELFMOD-022)."""
        assert is_allowed_mutation("run_status") is True

    def test_step_status_allowed(self):
        """Step status transitions allowed (GOV-POL-SELFMOD-022)."""
        assert is_allowed_mutation("step_status") is True

    def test_trace_events_allowed(self):
        """Trace events allowed."""
        assert is_allowed_mutation("trace_events") is True

    def test_config_change_not_allowed(self):
        """Config changes are NOT allowed."""
        assert is_allowed_mutation("config_change") is False

    def test_prompt_change_not_allowed(self):
        """Prompt changes are NOT allowed."""
        assert is_allowed_mutation("prompt_change") is False

    def test_policy_change_not_allowed(self):
        """Policy changes are NOT allowed."""
        assert is_allowed_mutation("policy_change") is False

    def test_learning_not_allowed(self):
        """Learning updates are NOT allowed."""
        assert is_allowed_mutation("learning") is False

    def test_arbitrary_mutation_not_allowed(self):
        """Arbitrary mutations are NOT allowed."""
        assert is_allowed_mutation("arbitrary_modification") is False

    def test_empty_string_not_allowed(self):
        """Empty string is NOT allowed."""
        assert is_allowed_mutation("") is False


# --------------------------------------------------------------------------- #
#  get_allowed_mutation_rationale Tests
# --------------------------------------------------------------------------- #

class TestGetAllowedMutationRationale:
    """Tests for get_allowed_mutation_rationale function."""

    def test_budget_consumption_rationale(self):
        """Budget consumption has rationale."""
        rationale = get_allowed_mutation_rationale("budget_consumption")
        assert rationale is not None
        assert "governance" in rationale.lower()

    def test_run_artifacts_rationale(self):
        """Run artifacts has rationale."""
        rationale = get_allowed_mutation_rationale("run_artifacts")
        assert rationale is not None

    def test_evidence_accumulation_rationale(self):
        """Evidence accumulation has rationale."""
        rationale = get_allowed_mutation_rationale("evidence_accumulation")
        assert rationale is not None
        assert "evidence" in rationale.lower()

    def test_run_status_rationale(self):
        """Run status has rationale."""
        rationale = get_allowed_mutation_rationale("run_status")
        assert rationale is not None
        assert "lifecycle" in rationale.lower()

    def test_step_status_rationale(self):
        """Step status has rationale."""
        rationale = get_allowed_mutation_rationale("step_status")
        assert rationale is not None
        assert "lifecycle" in rationale.lower()

    def test_trace_events_rationale(self):
        """Trace events has rationale."""
        rationale = get_allowed_mutation_rationale("trace_events")
        assert rationale is not None
        assert "observability" in rationale.lower()

    def test_unknown_mutation_no_rationale(self):
        """Unknown mutation has no rationale."""
        rationale = get_allowed_mutation_rationale("unknown_mutation")
        assert rationale is None


# --------------------------------------------------------------------------- #
#  check_mutation_allowed Tests
# --------------------------------------------------------------------------- #

class TestCheckMutationAllowed:
    """Tests for check_mutation_allowed function."""

    def test_allowed_mutation_no_raise(self):
        """Allowed mutations do not raise."""
        # Should not raise for any allowed type
        check_mutation_allowed("budget_consumption")
        check_mutation_allowed("run_artifacts")
        check_mutation_allowed("evidence_accumulation")
        check_mutation_allowed("run_status")
        check_mutation_allowed("step_status")
        check_mutation_allowed("trace_events")

    def test_disallowed_mutation_raises(self):
        """Disallowed mutations raise SelfModificationBlockedError."""
        with pytest.raises(SelfModificationBlockedError):
            check_mutation_allowed("config_change")

    def test_disallowed_mutation_error_has_target(self):
        """Error includes the attempted mutation as target."""
        try:
            check_mutation_allowed("policy_change")
        except SelfModificationBlockedError as e:
            assert e.target == "policy_change"

    def test_disallowed_mutation_error_has_reason(self):
        """Error includes reason with allowed mutations."""
        try:
            check_mutation_allowed("learning_update")
        except SelfModificationBlockedError as e:
            assert e.reason is not None
            assert "allowed mutations" in e.reason.lower()


# --------------------------------------------------------------------------- #
#  Integration Tests
# --------------------------------------------------------------------------- #

class TestAllowedMutationsIntegration:
    """Integration tests for allowed mutations."""

    def test_all_allowed_types_have_rationale(self):
        """All allowed mutation types have documented rationale."""
        for mutation_type in AllowedMutationType.ALL:
            rationale = get_allowed_mutation_rationale(mutation_type)
            assert rationale is not None, f"Missing rationale for {mutation_type}"

    def test_all_allowed_types_pass_check(self):
        """All allowed types pass check_mutation_allowed."""
        for mutation_type in AllowedMutationType.ALL:
            # Should not raise
            check_mutation_allowed(mutation_type)

    def test_allowed_types_consistent_with_is_allowed(self):
        """AllowedMutationType.ALL is consistent with is_allowed_mutation."""
        for mutation_type in AllowedMutationType.ALL:
            assert is_allowed_mutation(mutation_type) is True
