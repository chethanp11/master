# ==============================
# Security & Redaction
# ==============================
"""
Security redaction helpers.

Goals:
- Scrub secrets/PII from anything that might be logged/traced or shown in UI.
- Keep it deterministic and testable.
- Configurable patterns via Settings.logging.redact_patterns (and defaults here).

Scope:
- Do NOT attempt "perfect PII detection" in v1.
- Provide practical regex-based redaction + key-based redaction (e.g., password, token).
"""

from __future__ import annotations



import re
from typing import Any, Dict, Iterable, List, Pattern

from core.config.schema import Settings

DEFAULT_MASK = "***REDACTED***"
DEFAULT_MAX_TEXT_CHARS = 4096

DEFAULT_KEY_HINTS: List[str] = [
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "cookie",
    "session",
    "private_key",
    "ssh_key",
]

DEFAULT_PATTERNS: List[str] = [
    r"sk-[A-Za-z0-9_-]{3,}",  # common key pattern (loose match)
    r"(?i)api[_-]?key\s*[:=]\s*\S+",
    r"(?i)authorization\s*:\s*bearer\s+\S+",
]

DEFAULT_PII_PATTERNS: List[str] = [
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)",  # simple card/PAN heuristic
    r"(?<!\d)(?:\+?\d[ -]?){7,15}(?!\d)",  # loose phone number
]


def _compile(patterns: Iterable[str]) -> List[Pattern[str]]:
    compiled: List[Pattern[str]] = []
    for p in patterns:
        try:
            compiled.append(re.compile(p))
        except re.error:
            continue
    return compiled


class SecurityRedactor:
    """
    Sanitizes payloads before they reach logs, traces, or persistence.

    - Key hints mask dictionary values eagerly.
    - Regex patterns scrub inline secrets/PII.
    - Strings are clamped to avoid unbounded payload growth.
    """

    def __init__(
        self,
        *,
        patterns: List[str] | None = None,
        key_hints: List[str] | None = None,
        mask: str = DEFAULT_MASK,
        include_pii: bool = True,
        max_text_chars: int = DEFAULT_MAX_TEXT_CHARS,
    ) -> None:
        base_patterns = list(DEFAULT_PATTERNS)
        if include_pii:
            base_patterns.extend(DEFAULT_PII_PATTERNS)
        if patterns:
            base_patterns.extend(patterns)

        self.mask = mask
        self.max_text_chars = max_text_chars
        self.key_hints = [k.lower() for k in (key_hints or DEFAULT_KEY_HINTS)]
        self.patterns = _compile(base_patterns)

    def redact_text(self, text: str) -> str:
        out = text
        for p in self.patterns:
            out = p.sub(self.mask, out)
        if len(out) > self.max_text_chars:
            return f"{out[: self.max_text_chars]}{self.mask}"
        return out

    def sanitize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Public helper used by tracing/executor code."""
        return self._redact_any(payload)  # type: ignore[return-value]

    # Backwards compatibility for older callers/tests
    scrub = sanitize
    redact_dict = sanitize

    def _redact_any(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, (int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._redact_any(v) for v in value]
        if isinstance(value, tuple):
            return [self._redact_any(v) for v in value]
        if isinstance(value, dict):
            masked: Dict[str, Any] = {}
            for k, v in value.items():
                key_lower = str(k).lower()
                if any(h in key_lower for h in self.key_hints):
                    masked[k] = self.mask
                else:
                    masked[k] = self._redact_any(v)
            return masked
        return self.redact_text(str(value))

    @classmethod
    def from_settings(cls, settings: Settings) -> "SecurityRedactor":
        logging_cfg = settings.logging
        if not getattr(logging_cfg, "redact", True):
            return cls(patterns=logging_cfg.redact_patterns, include_pii=False)
        max_chars = getattr(logging_cfg, "max_payload_chars", DEFAULT_MAX_TEXT_CHARS)
        return cls(patterns=logging_cfg.redact_patterns, max_text_chars=max_chars)


class Redactor(SecurityRedactor):
    """Compatibility alias used by older modules/tests."""

    pass
