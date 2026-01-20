# ==============================
# Tests: IMP-022 Self-Modification Prevention Core
# ==============================
"""
Tests for IMP-022: Runtime Self-Modification Prevention Core.

Tech Spec References:
- GOV-POL-SELFMOD-001: Agents cannot modify own config/prompts/policies
- GOV-POL-SELFMOD-002: No learning/weight updates during execution
- GOV-POL-SELFMOD-003: All attempts traced

All tests deterministic. No external I/O.
"""

from __future__ import annotations

import pytest

from core.governance.self_modification_guard import (
    SelfModificationBlockedError,
    SelfModificationAttempt,
    SelfModificationGuard,
    get_default_guard,
)
from core.memory.tracing import TraceEventType


# --------------------------------------------------------------------------- #
#  SelfModificationBlockedError Tests
# --------------------------------------------------------------------------- #

class TestSelfModificationBlockedError:
    """Tests for SelfModificationBlockedError exception."""

    def test_error_exists(self):
        """SelfModificationBlockedError is defined."""
        assert SelfModificationBlockedError is not None

    def test_error_is_exception(self):
        """SelfModificationBlockedError is an Exception."""
        assert issubclass(SelfModificationBlockedError, Exception)

    def test_error_default_message(self):
        """SelfModificationBlockedError has default message."""
        err = SelfModificationBlockedError()
        assert "not permitted" in str(err).lower()

    def test_error_custom_message(self):
        """SelfModificationBlockedError accepts custom message."""
        err = SelfModificationBlockedError("Custom blocked message")
        assert "Custom blocked message" in str(err)

    def test_error_with_agent_id(self):
        """SelfModificationBlockedError stores agent_id."""
        err = SelfModificationBlockedError(
            "Blocked",
            agent_id="agent-1",
        )
        assert err.agent_id == "agent-1"

    def test_error_with_target(self):
        """SelfModificationBlockedError stores target."""
        err = SelfModificationBlockedError(
            "Blocked",
            target="config",
        )
        assert err.target == "config"

    def test_error_with_reason(self):
        """SelfModificationBlockedError stores reason."""
        err = SelfModificationBlockedError(
            "Blocked",
            reason="Not allowed",
        )
        assert err.reason == "Not allowed"

    def test_error_can_be_raised(self):
        """SelfModificationBlockedError can be raised and caught."""
        with pytest.raises(SelfModificationBlockedError):
            raise SelfModificationBlockedError("Test")


# --------------------------------------------------------------------------- #
#  SelfModificationAttempt Tests
# --------------------------------------------------------------------------- #

class TestSelfModificationAttempt:
    """Tests for SelfModificationAttempt dataclass."""

    def test_attempt_creation(self):
        """SelfModificationAttempt can be created."""
        attempt = SelfModificationAttempt(
            agent_id="agent-1",
            target="config",
            reason="Blocked",
        )
        assert attempt.agent_id == "agent-1"
        assert attempt.target == "config"
        assert attempt.reason == "Blocked"
        assert attempt.blocked is True

    def test_attempt_blocked_default_true(self):
        """SelfModificationAttempt defaults to blocked=True."""
        attempt = SelfModificationAttempt(
            agent_id="agent-1",
            target="config",
            reason="Blocked",
        )
        assert attempt.blocked is True

    def test_attempt_blocked_can_be_false(self):
        """SelfModificationAttempt can have blocked=False."""
        attempt = SelfModificationAttempt(
            agent_id="agent-1",
            target="config",
            reason="Allowed",
            blocked=False,
        )
        assert attempt.blocked is False

    def test_attempt_to_dict(self):
        """SelfModificationAttempt.to_dict() returns correct dict."""
        attempt = SelfModificationAttempt(
            agent_id="agent-1",
            target="config",
            reason="Blocked by guard",
        )
        d = attempt.to_dict()
        assert d["agent_id"] == "agent-1"
        assert d["target"] == "config"
        assert d["reason"] == "Blocked by guard"
        assert d["blocked"] is True


# --------------------------------------------------------------------------- #
#  SelfModificationGuard Tests - Config Modification
# --------------------------------------------------------------------------- #

class TestSelfModificationGuardConfig:
    """Tests for config modification blocking."""

    def test_check_config_modification_raises(self):
        """check_config_modification raises SelfModificationBlockedError."""
        guard = SelfModificationGuard()
        with pytest.raises(SelfModificationBlockedError):
            guard.check_config_modification("agent-1", {"key": "value"})

    def test_check_config_modification_error_has_agent_id(self):
        """check_config_modification error has agent_id."""
        guard = SelfModificationGuard()
        try:
            guard.check_config_modification("agent-1", {"key": "value"})
        except SelfModificationBlockedError as e:
            assert e.agent_id == "agent-1"

    def test_check_config_modification_error_has_target(self):
        """check_config_modification error has target='config'."""
        guard = SelfModificationGuard()
        try:
            guard.check_config_modification("agent-1", {"key": "value"})
        except SelfModificationBlockedError as e:
            assert e.target == "config"

    def test_check_config_modification_disabled_guard(self):
        """Disabled guard allows config modification."""
        guard = SelfModificationGuard(enabled=False)
        result = guard.check_config_modification("agent-1", {"key": "value"})
        assert result.blocked is False

    def test_check_config_modification_exempt_agent(self):
        """Exempt agent can modify config."""
        guard = SelfModificationGuard(exempt_agents={"system-agent"})
        result = guard.check_config_modification("system-agent", {"key": "value"})
        assert result.blocked is False


# --------------------------------------------------------------------------- #
#  SelfModificationGuard Tests - Prompt Modification
# --------------------------------------------------------------------------- #

class TestSelfModificationGuardPrompt:
    """Tests for prompt modification blocking."""

    def test_check_prompt_modification_raises(self):
        """check_prompt_modification raises SelfModificationBlockedError."""
        guard = SelfModificationGuard()
        with pytest.raises(SelfModificationBlockedError):
            guard.check_prompt_modification("agent-1", "New prompt")

    def test_check_prompt_modification_error_has_target(self):
        """check_prompt_modification error has target='prompt'."""
        guard = SelfModificationGuard()
        try:
            guard.check_prompt_modification("agent-1", "New prompt")
        except SelfModificationBlockedError as e:
            assert e.target == "prompt"

    def test_check_prompt_modification_disabled_guard(self):
        """Disabled guard allows prompt modification."""
        guard = SelfModificationGuard(enabled=False)
        result = guard.check_prompt_modification("agent-1", "New prompt")
        assert result.blocked is False


# --------------------------------------------------------------------------- #
#  SelfModificationGuard Tests - Policy Modification
# --------------------------------------------------------------------------- #

class TestSelfModificationGuardPolicy:
    """Tests for policy modification blocking."""

    def test_check_policy_modification_raises(self):
        """check_policy_modification raises SelfModificationBlockedError."""
        guard = SelfModificationGuard()
        with pytest.raises(SelfModificationBlockedError):
            guard.check_policy_modification("agent-1", "allow_all")

    def test_check_policy_modification_error_has_target(self):
        """check_policy_modification error has target='policy'."""
        guard = SelfModificationGuard()
        try:
            guard.check_policy_modification("agent-1", "allow_all")
        except SelfModificationBlockedError as e:
            assert e.target == "policy"

    def test_check_policy_modification_disabled_guard(self):
        """Disabled guard allows policy modification."""
        guard = SelfModificationGuard(enabled=False)
        result = guard.check_policy_modification("agent-1", "allow_all")
        assert result.blocked is False


# --------------------------------------------------------------------------- #
#  SelfModificationGuard Tests - Learning Update
# --------------------------------------------------------------------------- #

class TestSelfModificationGuardLearning:
    """Tests for learning update blocking."""

    def test_check_learning_update_raises(self):
        """check_learning_update raises SelfModificationBlockedError."""
        guard = SelfModificationGuard()
        with pytest.raises(SelfModificationBlockedError):
            guard.check_learning_update("agent-1")

    def test_check_learning_update_error_has_target(self):
        """check_learning_update error has target='learning'."""
        guard = SelfModificationGuard()
        try:
            guard.check_learning_update("agent-1")
        except SelfModificationBlockedError as e:
            assert e.target == "learning"

    def test_check_learning_update_error_has_reason(self):
        """check_learning_update error has reason about learning."""
        guard = SelfModificationGuard()
        try:
            guard.check_learning_update("agent-1")
        except SelfModificationBlockedError as e:
            assert "learning" in e.reason.lower()

    def test_check_learning_update_disabled_guard(self):
        """Disabled guard allows learning update."""
        guard = SelfModificationGuard(enabled=False)
        result = guard.check_learning_update("agent-1")
        assert result.blocked is False


# --------------------------------------------------------------------------- #
#  SelfModificationGuard Tests - General
# --------------------------------------------------------------------------- #

class TestSelfModificationGuardGeneral:
    """General tests for SelfModificationGuard."""

    def test_guard_enabled_by_default(self):
        """Guard is enabled by default."""
        guard = SelfModificationGuard()
        assert guard.enabled is True

    def test_guard_can_be_disabled(self):
        """Guard can be disabled."""
        guard = SelfModificationGuard(enabled=False)
        assert guard.enabled is False

    def test_guard_exempt_agents_empty_by_default(self):
        """No exempt agents by default."""
        guard = SelfModificationGuard()
        assert not guard.is_exempt("agent-1")

    def test_guard_exempt_agents_check(self):
        """Exempt agents are correctly identified."""
        guard = SelfModificationGuard(exempt_agents={"system-agent", "admin-agent"})
        assert guard.is_exempt("system-agent")
        assert guard.is_exempt("admin-agent")
        assert not guard.is_exempt("regular-agent")

    def test_get_blocked_payload(self):
        """get_blocked_payload returns correct dict."""
        guard = SelfModificationGuard()
        payload = guard.get_blocked_payload(
            agent_id="agent-1",
            target="config",
            reason="Not permitted",
        )
        assert payload["agent_id"] == "agent-1"
        assert payload["target"] == "config"
        assert payload["reason"] == "Not permitted"
        assert payload["blocked"] is True


# --------------------------------------------------------------------------- #
#  Default Guard Tests
# --------------------------------------------------------------------------- #

class TestDefaultGuard:
    """Tests for default guard singleton."""

    def test_get_default_guard_returns_guard(self):
        """get_default_guard returns a SelfModificationGuard."""
        guard = get_default_guard()
        assert isinstance(guard, SelfModificationGuard)

    def test_get_default_guard_is_enabled(self):
        """Default guard is enabled."""
        guard = get_default_guard()
        assert guard.enabled is True


# --------------------------------------------------------------------------- #
#  Trace Event Type Tests
# --------------------------------------------------------------------------- #

class TestTraceEventType:
    """Tests for trace event type."""

    def test_self_modification_blocked_event_exists(self):
        """TraceEventType.SELF_MODIFICATION_BLOCKED is defined."""
        assert hasattr(TraceEventType, "SELF_MODIFICATION_BLOCKED")
        assert TraceEventType.SELF_MODIFICATION_BLOCKED.value == "self_modification_blocked"
