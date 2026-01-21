"""Advisory labeling utilities for ADE.

TS-BRD-DAB-001..005: Decision authority boundary and advisory language.
"""

from __future__ import annotations

from typing import Dict, List

# Advisory labels per confidence level
ADVISORY_LABELS: Dict[str, str] = {
    "high": "Based on the available evidence, we recommend",
    "medium": "The analysis suggests, pending further review",
    "low": "Initial indications point to, subject to validation",
}

# Non-decisional language replacements
DECISIONAL_TERMS = [
    ("decide", "recommend"),
    ("decided", "recommended"),
    ("decision", "recommendation"),
    ("must", "should consider"),
    ("will", "may"),
    ("definite", "likely"),
    ("certain", "probable"),
    ("guarantee", "support"),
]


def get_advisory_label(confidence: str) -> str:
    """Get advisory label for confidence level.

    TS-BRD-DAB-001: Confidence language is non-decisional.

    Args:
        confidence: Confidence level (high/medium/low).

    Returns:
        Advisory label string.
    """
    return ADVISORY_LABELS.get(confidence.lower(), ADVISORY_LABELS["medium"])


def apply_advisory_language(text: str) -> str:
    """Replace decisional terms with advisory alternatives.

    TS-BRD-DAB-002: Output uses recommendation/findings terminology.

    Args:
        text: Text to transform.

    Returns:
        Text with advisory language.
    """
    result = text
    for decisional, advisory in DECISIONAL_TERMS:
        # Case-insensitive replacement
        result = _replace_preserve_case(result, decisional, advisory)
    return result


def _replace_preserve_case(text: str, old: str, new: str) -> str:
    """Replace text preserving case patterns."""
    import re

    def replacer(match: "re.Match[str]") -> str:
        matched = match.group(0)
        if matched.isupper():
            return new.upper()
        if matched[0].isupper():
            return new.capitalize()
        return new

    pattern = re.compile(re.escape(old), re.IGNORECASE)
    return pattern.sub(replacer, text)


def format_advisory_header(title: str, confidence: str) -> str:
    """Format advisory header with confidence label.

    TS-BRD-DAB-003: Explicit advisory labeling in headers.

    Args:
        title: Report or section title.
        confidence: Confidence level.

    Returns:
        Formatted header with advisory note.
    """
    label = get_advisory_label(confidence)
    return f"{title}\n[Advisory Analysis - {label}]"


def format_recommendation_disclaimer(confidence: str) -> str:
    """Generate recommendation disclaimer.

    TS-BRD-DAB-004: Clear disclaimer on recommendations.

    Args:
        confidence: Confidence level.

    Returns:
        Disclaimer text.
    """
    if confidence.lower() == "high":
        return (
            "These recommendations are based on comprehensive analysis of available data. "
            "Final decisions should incorporate business context and expert judgment."
        )
    if confidence.lower() == "low":
        return (
            "These preliminary recommendations are based on limited data. "
            "Further investigation is strongly recommended before action."
        )
    return (
        "These recommendations are based on available analysis. "
        "Review with subject matter experts is advised before implementation."
    )


def format_findings_preamble() -> str:
    """Generate findings preamble.

    TS-BRD-DAB-005: Findings are presented as observations, not conclusions.

    Returns:
        Standard findings preamble text.
    """
    return (
        "The following observations emerge from the analysis. "
        "These findings represent patterns in the data and should be "
        "interpreted in the context of broader business knowledge."
    )


def validate_advisory_language(text: str) -> List[str]:
    """Check text for inappropriate decisional language.

    Args:
        text: Text to check.

    Returns:
        List of found decisional terms that should be replaced.
    """
    found = []
    lower_text = text.lower()
    for decisional, _ in DECISIONAL_TERMS:
        if decisional in lower_text:
            found.append(decisional)
    return found
