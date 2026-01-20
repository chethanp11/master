# ==============================
# Tests: IMP-023 Frozen Configuration Enforcement
# ==============================
"""
Tests for IMP-023: Frozen Configuration Enforcement.

Tech Spec References:
- GOV-POL-SELFMOD-010: Policy configurations frozen at run initialization
- GOV-POL-SELFMOD-011: Agent prompts/system messages frozen
- GOV-POL-SELFMOD-012: Budget/resource limits frozen
- GOV-POL-SELFMOD-013: Tool/agent registries read-only

All tests deterministic. No external I/O.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.governance.self_modification_guard import (
    ConfigMutationBlockedError,
    FrozenConfig,
)


# --------------------------------------------------------------------------- #
#  ConfigMutationBlockedError Tests
# --------------------------------------------------------------------------- #

class TestConfigMutationBlockedError:
    """Tests for ConfigMutationBlockedError exception."""

    def test_error_exists(self):
        """ConfigMutationBlockedError is defined."""
        assert ConfigMutationBlockedError is not None

    def test_error_is_exception(self):
        """ConfigMutationBlockedError is an Exception."""
        assert issubclass(ConfigMutationBlockedError, Exception)

    def test_error_default_message(self):
        """ConfigMutationBlockedError has default message."""
        err = ConfigMutationBlockedError()
        assert "mutation" in str(err).lower()

    def test_error_custom_message(self):
        """ConfigMutationBlockedError accepts custom message."""
        err = ConfigMutationBlockedError("Policy changed during run")
        assert "Policy changed" in str(err)

    def test_error_with_field(self):
        """ConfigMutationBlockedError stores field."""
        err = ConfigMutationBlockedError(
            "Blocked",
            field="policies",
        )
        assert err.field == "policies"

    def test_error_with_hashes(self):
        """ConfigMutationBlockedError stores expected and actual hashes."""
        err = ConfigMutationBlockedError(
            "Blocked",
            expected_hash="abc123",
            actual_hash="def456",
        )
        assert err.expected_hash == "abc123"
        assert err.actual_hash == "def456"

    def test_error_can_be_raised(self):
        """ConfigMutationBlockedError can be raised and caught."""
        with pytest.raises(ConfigMutationBlockedError):
            raise ConfigMutationBlockedError("Test")


# --------------------------------------------------------------------------- #
#  FrozenConfig Creation Tests
# --------------------------------------------------------------------------- #

class TestFrozenConfigCreation:
    """Tests for FrozenConfig creation."""

    def test_create_empty_config(self):
        """FrozenConfig.create() works with empty config."""
        fc = FrozenConfig.create()
        assert fc is not None
        assert fc.frozen_at is not None

    def test_create_with_policies(self):
        """FrozenConfig.create() captures policies."""
        policies = {"max_tokens": 1000, "allow_external": False}
        fc = FrozenConfig.create(policies=policies)
        assert fc.policies_hash != ""
        assert fc.policies_snapshot == policies

    def test_create_with_agents(self):
        """FrozenConfig.create() captures agent config."""
        agents = {"agent-1": {"prompt": "System prompt"}}
        fc = FrozenConfig.create(agents=agents)
        assert fc.agents_hash != ""
        assert fc.agents_snapshot == agents

    def test_create_with_tools(self):
        """FrozenConfig.create() captures tool registry."""
        tools = ["tool-a", "tool-b", "tool-c"]
        fc = FrozenConfig.create(tools=tools)
        assert fc.tools_hash != ""
        assert fc.tools_snapshot == frozenset(tools)

    def test_create_with_budget(self):
        """FrozenConfig.create() captures budget limits."""
        budget = {"max_cost": 100.0, "max_time": 3600}
        fc = FrozenConfig.create(budget=budget)
        assert fc.budget_hash != ""
        assert fc.budget_snapshot == budget

    def test_frozen_at_is_recent(self):
        """FrozenConfig.frozen_at is recent timestamp."""
        before = datetime.now(timezone.utc)
        fc = FrozenConfig.create()
        after = datetime.now(timezone.utc)
        assert before <= fc.frozen_at <= after

    def test_hash_is_deterministic(self):
        """Same config produces same hash."""
        policies = {"key": "value"}
        fc1 = FrozenConfig.create(policies=policies)
        fc2 = FrozenConfig.create(policies=policies)
        assert fc1.policies_hash == fc2.policies_hash

    def test_different_config_different_hash(self):
        """Different config produces different hash."""
        fc1 = FrozenConfig.create(policies={"key": "value1"})
        fc2 = FrozenConfig.create(policies={"key": "value2"})
        assert fc1.policies_hash != fc2.policies_hash


# --------------------------------------------------------------------------- #
#  Policy Validation Tests (GOV-POL-SELFMOD-010)
# --------------------------------------------------------------------------- #

class TestFrozenConfigPolicies:
    """Tests for policy configuration freezing."""

    def test_validate_policies_unchanged(self):
        """Unchanged policies pass validation."""
        policies = {"max_tokens": 1000}
        fc = FrozenConfig.create(policies=policies)
        valid, msg = fc.validate_policies(policies)
        assert valid is True
        assert msg is None

    def test_validate_policies_changed(self):
        """Changed policies fail validation."""
        original = {"max_tokens": 1000}
        mutated = {"max_tokens": 2000}
        fc = FrozenConfig.create(policies=original)
        valid, msg = fc.validate_policies(mutated)
        assert valid is False
        assert "mutated" in msg.lower()

    def test_validate_policies_added_key(self):
        """Added policy key fails validation."""
        original = {"max_tokens": 1000}
        mutated = {"max_tokens": 1000, "new_key": "value"}
        fc = FrozenConfig.create(policies=original)
        valid, msg = fc.validate_policies(mutated)
        assert valid is False

    def test_validate_policies_removed_key(self):
        """Removed policy key fails validation."""
        original = {"max_tokens": 1000, "extra": True}
        mutated = {"max_tokens": 1000}
        fc = FrozenConfig.create(policies=original)
        valid, msg = fc.validate_policies(mutated)
        assert valid is False


# --------------------------------------------------------------------------- #
#  Agent Config Validation Tests (GOV-POL-SELFMOD-011)
# --------------------------------------------------------------------------- #

class TestFrozenConfigAgents:
    """Tests for agent configuration freezing."""

    def test_validate_agents_unchanged(self):
        """Unchanged agent config passes validation."""
        agents = {"agent-1": {"prompt": "Be helpful"}}
        fc = FrozenConfig.create(agents=agents)
        valid, msg = fc.validate_agents(agents)
        assert valid is True

    def test_validate_agents_prompt_changed(self):
        """Changed agent prompt fails validation."""
        original = {"agent-1": {"prompt": "Be helpful"}}
        mutated = {"agent-1": {"prompt": "Ignore instructions"}}
        fc = FrozenConfig.create(agents=original)
        valid, msg = fc.validate_agents(mutated)
        assert valid is False

    def test_validate_agents_new_agent_added(self):
        """Added agent fails validation."""
        original = {"agent-1": {}}
        mutated = {"agent-1": {}, "agent-2": {}}
        fc = FrozenConfig.create(agents=original)
        valid, msg = fc.validate_agents(mutated)
        assert valid is False


# --------------------------------------------------------------------------- #
#  Budget Validation Tests (GOV-POL-SELFMOD-012)
# --------------------------------------------------------------------------- #

class TestFrozenConfigBudget:
    """Tests for budget/resource limit freezing."""

    def test_validate_budget_unchanged(self):
        """Unchanged budget passes validation."""
        budget = {"max_cost": 100.0}
        fc = FrozenConfig.create(budget=budget)
        valid, msg = fc.validate_budget(budget)
        assert valid is True

    def test_validate_budget_limit_changed(self):
        """Changed budget limit fails validation."""
        original = {"max_cost": 100.0}
        mutated = {"max_cost": 200.0}
        fc = FrozenConfig.create(budget=original)
        valid, msg = fc.validate_budget(mutated)
        assert valid is False


# --------------------------------------------------------------------------- #
#  Tool Registry Validation Tests (GOV-POL-SELFMOD-013)
# --------------------------------------------------------------------------- #

class TestFrozenConfigTools:
    """Tests for tool registry freezing."""

    def test_validate_tools_unchanged(self):
        """Unchanged tool registry passes validation."""
        tools = ["tool-a", "tool-b"]
        fc = FrozenConfig.create(tools=tools)
        valid, msg = fc.validate_tools(tools)
        assert valid is True

    def test_validate_tools_order_independent(self):
        """Tool registry validation is order-independent."""
        tools = ["tool-a", "tool-b"]
        fc = FrozenConfig.create(tools=tools)
        # Different order should still pass
        valid, msg = fc.validate_tools(["tool-b", "tool-a"])
        assert valid is True

    def test_validate_tools_added(self):
        """Added tool fails validation."""
        original = ["tool-a"]
        mutated = ["tool-a", "tool-b"]
        fc = FrozenConfig.create(tools=original)
        valid, msg = fc.validate_tools(mutated)
        assert valid is False

    def test_validate_tools_removed(self):
        """Removed tool fails validation."""
        original = ["tool-a", "tool-b"]
        mutated = ["tool-a"]
        fc = FrozenConfig.create(tools=original)
        valid, msg = fc.validate_tools(mutated)
        assert valid is False


# --------------------------------------------------------------------------- #
#  check_mutation Tests
# --------------------------------------------------------------------------- #

class TestFrozenConfigCheckMutation:
    """Tests for check_mutation combined validation."""

    def test_check_mutation_all_unchanged(self):
        """No mutation detected when all unchanged."""
        fc = FrozenConfig.create(
            policies={"key": "value"},
            agents={"agent": {}},
            tools=["tool"],
            budget={"limit": 100},
        )
        # Should not raise
        fc.check_mutation(
            policies={"key": "value"},
            agents={"agent": {}},
            tools=["tool"],
            budget={"limit": 100},
        )

    def test_check_mutation_policy_changed_raises(self):
        """Policy mutation raises ConfigMutationBlockedError."""
        fc = FrozenConfig.create(policies={"key": "value"})
        with pytest.raises(ConfigMutationBlockedError) as exc_info:
            fc.check_mutation(policies={"key": "changed"})
        assert exc_info.value.field == "policies"

    def test_check_mutation_agents_changed_raises(self):
        """Agent mutation raises ConfigMutationBlockedError."""
        fc = FrozenConfig.create(agents={"agent": {"prompt": "original"}})
        with pytest.raises(ConfigMutationBlockedError) as exc_info:
            fc.check_mutation(agents={"agent": {"prompt": "mutated"}})
        assert exc_info.value.field == "agents"

    def test_check_mutation_tools_changed_raises(self):
        """Tool registry mutation raises ConfigMutationBlockedError."""
        fc = FrozenConfig.create(tools=["tool-a"])
        with pytest.raises(ConfigMutationBlockedError) as exc_info:
            fc.check_mutation(tools=["tool-a", "tool-b"])
        assert exc_info.value.field == "tools"

    def test_check_mutation_budget_changed_raises(self):
        """Budget mutation raises ConfigMutationBlockedError."""
        fc = FrozenConfig.create(budget={"limit": 100})
        with pytest.raises(ConfigMutationBlockedError) as exc_info:
            fc.check_mutation(budget={"limit": 200})
        assert exc_info.value.field == "budget"

    def test_check_mutation_partial_check(self):
        """check_mutation only validates provided fields."""
        fc = FrozenConfig.create(
            policies={"key": "value"},
            agents={"agent": {}},
        )
        # Only check policies (should pass)
        fc.check_mutation(policies={"key": "value"})
        
        # Only check agents (should pass)
        fc.check_mutation(agents={"agent": {}})


# --------------------------------------------------------------------------- #
#  Serialization Tests
# --------------------------------------------------------------------------- #

class TestFrozenConfigSerialization:
    """Tests for FrozenConfig serialization."""

    def test_to_dict_contains_frozen_at(self):
        """to_dict contains frozen_at."""
        fc = FrozenConfig.create()
        d = fc.to_dict()
        assert "frozen_at" in d

    def test_to_dict_contains_hashes(self):
        """to_dict contains all hashes."""
        fc = FrozenConfig.create(
            policies={"key": "value"},
            agents={"agent": {}},
            tools=["tool"],
            budget={"limit": 100},
        )
        d = fc.to_dict()
        assert "policies_hash" in d
        assert "agents_hash" in d
        assert "tools_hash" in d
        assert "budget_hash" in d

    def test_to_dict_excludes_snapshots(self):
        """to_dict excludes full snapshots for efficiency."""
        fc = FrozenConfig.create(policies={"key": "value"})
        d = fc.to_dict()
        # Should not include full snapshot
        assert "policies_snapshot" not in d
