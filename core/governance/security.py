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
from typing import Any, Dict, Iterable, List, Pattern, Union


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
    r"sk-[A-Za-z0-9]{20,}",  # common key pattern
    r"(?i)api[_-]?key\s*[:=]\s*\S+",
    r"(?i)authorization\s*:\s*bearer\s+\S+",
]


def _compile(patterns: Iterable[str]) -> List[Pattern[str]]:
    compiled: List[Pattern[str]] = []
    for p in patterns:
        try:
            compiled.append(re.compile(p))
        except re.error:
            # ignore invalid patterns to avoid runtime failures
            continue
    return compiled


class SecurityRedactor:
    def __init__(
        self,
        *,
        patterns: List[str] | None = None,
        key_hints: List[str] | None = None,
        mask: str = "[REDACTED]",
    ) -> None:
        self.mask = mask
        self.key_hints = [k.lower() for k in (key_hints or DEFAULT_KEY_HINTS)]
        pats = patterns or DEFAULT_PATTERNS
        self.patterns = _compile(pats)

    def redact_text(self, text: str) -> str:
        out = text
        for p in self.patterns:
            out = p.sub(self.mask, out)
        return out

    def redact_dict(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        return self._redact_any(obj)  # type: ignore[return-value]

    def _redact_any(self, x: Any) -> Any:
        if x is None:
            return None
        if isinstance(x, str):
            return self.redact_text(x)
        if isinstance(x, (int, float, bool)):
            return x
        if isinstance(x, list):
            return [self._redact_any(i) for i in x]
        if isinstance(x, tuple):
            return [self._redact_any(i) for i in x]
        if isinstance(x, dict):
            out: Dict[str, Any] = {}
            for k, v in x.items():
                ks = str(k).lower()
                if any(h in ks for h in self.key_hints):
                    out[k] = self.mask
                else:
                    out[k] = self._redact_any(v)
            return out
        # fallback: string-ify then redact
        return self.redact_text(str(x))