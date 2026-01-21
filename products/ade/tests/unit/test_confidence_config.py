"""Unit tests for confidence configuration.

Tests TS-AGENT-CONF-003.
"""

import pytest

from products.ade.utils.confidence import (
    ConfidenceConfig,
    SufficiencyThresholds,
    load_confidence_config,
    load_confidence_thresholds,
)


class TestConfidenceConfig:
    """Tests for ConfidenceConfig schema (TS-AGENT-CONF-003)."""

    def test_default_config_values(self):
        config = ConfidenceConfig()
        assert config.low_threshold == 0.4
        assert config.high_threshold == 0.7
        assert isinstance(config.sufficiency_thresholds, SufficiencyThresholds)

    def test_custom_thresholds(self):
        config = ConfidenceConfig(low_threshold=0.3, high_threshold=0.8)
        assert config.low_threshold == 0.3
        assert config.high_threshold == 0.8

    def test_sufficiency_thresholds_defaults(self):
        thresholds = SufficiencyThresholds()
        assert thresholds.min_rows == 30
        assert thresholds.critical_rows == 15
        assert thresholds.min_time_points == 12
        assert thresholds.max_cv == 0.6
        assert thresholds.min_non_null_rate == 0.7


class TestLoadConfidenceConfig:
    """Tests for load_confidence_config function."""

    def test_load_confidence_config_returns_config(self):
        # Clear cache to ensure fresh load
        load_confidence_config.cache_clear()
        config = load_confidence_config()
        assert isinstance(config, ConfidenceConfig)
        assert config.low_threshold >= 0.0
        assert config.high_threshold <= 1.0
        assert config.high_threshold >= config.low_threshold

    def test_load_confidence_config_has_sufficiency(self):
        load_confidence_config.cache_clear()
        config = load_confidence_config()
        assert config.sufficiency_thresholds is not None
        assert config.sufficiency_thresholds.min_rows > 0


class TestLoadConfidenceThresholds:
    """Tests for legacy load_confidence_thresholds function."""

    def test_returns_dict_with_high_and_medium(self):
        load_confidence_thresholds.cache_clear()
        thresholds = load_confidence_thresholds()
        assert "high" in thresholds
        assert "medium" in thresholds
        assert thresholds["high"] >= thresholds["medium"]
