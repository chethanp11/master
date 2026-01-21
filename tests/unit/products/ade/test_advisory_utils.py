"""Tests for advisory labeling utilities.

IMP-015: TS-BRD-DAB-001..005 decision authority boundary tests.
"""

import pytest

from products.ade.utils.advisory import (
    ADVISORY_LABELS,
    get_advisory_label,
    apply_advisory_language,
    format_advisory_header,
    format_recommendation_disclaimer,
    format_findings_preamble,
    validate_advisory_language,
)


class TestGetAdvisoryLabel:
    """Tests for get_advisory_label function."""

    def test_high_confidence_label(self):
        """Test high confidence advisory label."""
        label = get_advisory_label("high")
        assert "recommend" in label

    def test_medium_confidence_label(self):
        """Test medium confidence advisory label."""
        label = get_advisory_label("medium")
        assert "suggests" in label

    def test_low_confidence_label(self):
        """Test low confidence advisory label."""
        label = get_advisory_label("low")
        assert "Initial" in label

    def test_unknown_defaults_to_medium(self):
        """Test unknown confidence defaults to medium."""
        label = get_advisory_label("unknown")
        assert label == ADVISORY_LABELS["medium"]

    def test_case_insensitive(self):
        """Test case insensitive lookup."""
        assert get_advisory_label("HIGH") == get_advisory_label("high")


class TestApplyAdvisoryLanguage:
    """Tests for apply_advisory_language function."""

    def test_replaces_decide(self):
        """Test 'decide' is replaced with 'recommend'."""
        text = "We decide to proceed."
        result = apply_advisory_language(text)
        assert "decide" not in result.lower()
        assert "recommend" in result

    def test_replaces_must(self):
        """Test 'must' is replaced."""
        text = "You must review the data."
        result = apply_advisory_language(text)
        assert "must" not in result
        assert "should consider" in result

    def test_preserves_case(self):
        """Test case is preserved in replacements."""
        text = "MUST review. Must check. must verify."
        result = apply_advisory_language(text)
        assert "SHOULD CONSIDER" in result
        assert "Should consider" in result

    def test_no_change_for_clean_text(self):
        """Test no changes for already advisory text."""
        text = "We recommend reviewing the analysis."
        result = apply_advisory_language(text)
        assert "recommend" in result


class TestFormatAdvisoryHeader:
    """Tests for format_advisory_header function."""

    def test_includes_title(self):
        """Test header includes title."""
        header = format_advisory_header("Q4 Analysis", "high")
        assert "Q4 Analysis" in header

    def test_includes_advisory_label(self):
        """Test header includes advisory label."""
        header = format_advisory_header("Report", "medium")
        assert "Advisory Analysis" in header


class TestFormatRecommendationDisclaimer:
    """Tests for format_recommendation_disclaimer function."""

    def test_high_confidence_disclaimer(self):
        """Test high confidence disclaimer."""
        disclaimer = format_recommendation_disclaimer("high")
        assert "comprehensive analysis" in disclaimer
        assert "expert judgment" in disclaimer

    def test_low_confidence_disclaimer(self):
        """Test low confidence disclaimer."""
        disclaimer = format_recommendation_disclaimer("low")
        assert "preliminary" in disclaimer
        assert "investigation" in disclaimer

    def test_medium_confidence_disclaimer(self):
        """Test medium confidence disclaimer."""
        disclaimer = format_recommendation_disclaimer("medium")
        assert "subject matter experts" in disclaimer


class TestFormatFindingsPreamble:
    """Tests for format_findings_preamble function."""

    def test_preamble_content(self):
        """Test preamble uses observation language."""
        preamble = format_findings_preamble()
        assert "observations" in preamble
        assert "interpreted" in preamble
        assert "business knowledge" in preamble


class TestValidateAdvisoryLanguage:
    """Tests for validate_advisory_language function."""

    def test_detects_decisional_terms(self):
        """Test detection of decisional terms."""
        text = "We must decide now and guarantee success."
        issues = validate_advisory_language(text)
        assert "must" in issues
        assert "decide" in issues
        assert "guarantee" in issues

    def test_clean_text_returns_empty(self):
        """Test clean text returns no issues."""
        text = "We recommend reviewing the findings."
        issues = validate_advisory_language(text)
        assert len(issues) == 0
