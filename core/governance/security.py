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


# ============================================================================
# Cloud Credential Patterns (IMP-045: GOV-SEC-CRED-001...005)
# ============================================================================

# AWS Credential Patterns
AWS_PATTERNS: List[str] = [
    r"AKIA[0-9A-Z]{16}",  # AWS Access Key ID
    r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])",  # AWS Secret Key (context-dependent)
    r"aws_access_key_id\s*[:=]\s*['\"]?[A-Z0-9]{20}['\"]?",  # Key in config
    r"aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",  # Secret in config
]

# GCP Credential Patterns
GCP_PATTERNS: List[str] = [
    r"AIza[0-9A-Za-z\-_]{35}",  # GCP API Key
    r'"type"\s*:\s*"service_account"',  # Service account JSON indicator
    r'"private_key"\s*:\s*"-----BEGIN',  # Private key in JSON
    r'"client_email"\s*:\s*"[^"]+@[^"]+\.iam\.gserviceaccount\.com"',  # Service account email
]

# Azure Credential Patterns
AZURE_PATTERNS: List[str] = [
    r"AccountKey=[A-Za-z0-9+/=]{86,}",  # Azure Storage Account Key
    r"SharedAccessSignature=sv=[^&]+",  # Azure SAS Token
    r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+",  # Connection string
    r"azure_[a-z_]+_key\s*[:=]\s*['\"]?[A-Za-z0-9+/=]{20,}['\"]?",  # Azure keys in config
]

# GitHub Credential Patterns
GITHUB_PATTERNS: List[str] = [
    r"ghp_[a-zA-Z0-9]{36}",  # GitHub Personal Access Token
    r"gho_[a-zA-Z0-9]{36}",  # GitHub OAuth Token
    r"ghu_[a-zA-Z0-9]{36}",  # GitHub User-to-Server Token
    r"ghs_[a-zA-Z0-9]{36}",  # GitHub Server-to-Server Token
    r"ghr_[a-zA-Z0-9]{36}",  # GitHub Refresh Token
    r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}",  # Fine-grained PAT
]

# Other Cloud/Service Credential Patterns
OTHER_CLOUD_PATTERNS: List[str] = [
    r"xox[baprs]-[0-9]+-[0-9]+-[0-9]+-[a-fA-F0-9]+",  # Slack Token
    r"sk_live_[a-zA-Z0-9]{24,}",  # Stripe Live Key
    r"sk_test_[a-zA-Z0-9]{24,}",  # Stripe Test Key
    r"sq0csp-[a-zA-Z0-9\-_]{43}",  # Square OAuth Secret
    r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}",  # SendGrid API Key
    r"key-[a-zA-Z0-9]{32}",  # Mailgun API Key
]

# Combined cloud credential patterns
DEFAULT_CLOUD_PATTERNS: List[str] = (
    AWS_PATTERNS + 
    GCP_PATTERNS + 
    AZURE_PATTERNS + 
    GITHUB_PATTERNS + 
    OTHER_CLOUD_PATTERNS
)

# Provider name mapping for trace events
CLOUD_PROVIDER_PATTERNS: Dict[str, List[str]] = {
    "aws": AWS_PATTERNS,
    "gcp": GCP_PATTERNS,
    "azure": AZURE_PATTERNS,
    "github": GITHUB_PATTERNS,
    "other": OTHER_CLOUD_PATTERNS,
}


def _compile(patterns: Iterable[str]) -> List[Pattern[str]]:
    compiled: List[Pattern[str]] = []
    for p in patterns:
        try:
            compiled.append(re.compile(p))
        except re.error:
            continue
    return compiled


def _compile_provider_patterns() -> Dict[str, List[Pattern[str]]]:
    """Compile provider-specific patterns for credential detection."""
    return {
        provider: _compile(patterns)
        for provider, patterns in CLOUD_PROVIDER_PATTERNS.items()
    }


class SecurityRedactor:
    """
    Sanitizes payloads before they reach logs, traces, or persistence.

    - Key hints mask dictionary values eagerly.
    - Regex patterns scrub inline secrets/PII.
    - Cloud credential patterns detect AWS/GCP/Azure/GitHub credentials.
    - Strings are clamped to avoid unbounded payload growth.
    
    IMP-045: GOV-SEC-CRED-001...005 - Cloud credential pattern detection.
    """

    def __init__(
        self,
        *,
        patterns: List[str] | None = None,
        key_hints: List[str] | None = None,
        mask: str = DEFAULT_MASK,
        include_pii: bool = True,
        include_cloud_credentials: bool = True,
        max_text_chars: int = DEFAULT_MAX_TEXT_CHARS,
        emit_event_fn: Any = None,
    ) -> None:
        base_patterns = list(DEFAULT_PATTERNS)
        if include_pii:
            base_patterns.extend(DEFAULT_PII_PATTERNS)
        if include_cloud_credentials:
            base_patterns.extend(DEFAULT_CLOUD_PATTERNS)
        if patterns:
            base_patterns.extend(patterns)

        self.mask = mask
        self.max_text_chars = max_text_chars
        self.key_hints = [k.lower() for k in (key_hints or DEFAULT_KEY_HINTS)]
        self.patterns = _compile(base_patterns)
        self._emit_event = emit_event_fn
        self._cloud_patterns = _compile_provider_patterns()
    
    def detect_cloud_credentials(self, text: str) -> Dict[str, int]:
        """
        Detect cloud credentials by provider.
        
        GOV-SEC-CRED-001: Detect AWS/GCP/Azure/GitHub credentials.
        
        Args:
            text: Text to scan
            
        Returns:
            Dictionary of provider -> count of matches
        """
        counts: Dict[str, int] = {}
        for provider, patterns in self._cloud_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(pattern.findall(text))
            if count > 0:
                counts[provider] = count
        return counts

    def redact_text(self, text: str) -> str:
        # Detect cloud credentials before redaction for trace event
        cloud_counts = self.detect_cloud_credentials(text)
        if cloud_counts and self._emit_event:
            self._emit_event("cloud_credential_redacted", {
                "providers": cloud_counts,
                "total_count": sum(cloud_counts.values()),
            })
        
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


# ============================================================================
# Automatic Redaction Enforcement (IMP-046: GOV-SEC-AUTO-001...005)
# ============================================================================

class AutoRedactionEnforcer:
    """
    Automatic redaction enforcer that applies to all output paths.
    
    GOV-SEC-AUTO-001: Enforce redaction on all output paths.
    GOV-SEC-AUTO-002: Apply to trace event payloads.
    GOV-SEC-AUTO-003: Apply to API responses.
    GOV-SEC-AUTO-004: Apply to artifact contents.
    GOV-SEC-AUTO-005: Make non-bypassable (no disable mechanism).
    
    This class is a singleton-like enforcer that wraps output paths
    with automatic redaction. It cannot be disabled.
    """
    
    # Class-level flag - cannot be disabled
    _ENABLED: bool = True
    
    def __init__(
        self,
        *,
        redactor: SecurityRedactor | None = None,
        emit_event_fn: Any = None,
    ) -> None:
        """
        Initialize auto-redaction enforcer.
        
        Args:
            redactor: SecurityRedactor to use (creates default if None)
            emit_event_fn: Optional callback to emit trace events
            
        Note:
            There is no 'enabled' parameter - auto-redaction is always on.
        """
        self._redactor = redactor or SecurityRedactor()
        self._emit_event = emit_event_fn
        self._redaction_count = 0
    
    @property
    def is_enabled(self) -> bool:
        """Check if auto-redaction is enabled. Always returns True."""
        return self._ENABLED
    
    @property
    def redaction_count(self) -> int:
        """Number of redactions performed by this enforcer."""
        return self._redaction_count
    
    def enforce_on_output(self, data: Any) -> Any:
        """
        Apply automatic redaction to output data.
        
        GOV-SEC-AUTO-001: Enforce on all output paths.
        
        Args:
            data: Any data structure to redact
            
        Returns:
            Redacted version of the data
        """
        if data is None:
            return None
        
        original = data
        result = self._redactor._redact_any(data)
        
        # Track if redaction occurred
        if result != original:
            self._redaction_count += 1
            self._emit_auto_redaction_event(original, result)
        
        return result
    
    def enforce_on_trace_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply redaction to trace event payloads.
        
        GOV-SEC-AUTO-002: Apply to trace event payloads.
        
        Args:
            payload: Trace event payload dictionary
            
        Returns:
            Redacted payload
        """
        return self.enforce_on_output(payload)
    
    def enforce_on_api_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply redaction to API response bodies.
        
        GOV-SEC-AUTO-003: Apply to API responses.
        
        Args:
            response: API response dictionary
            
        Returns:
            Redacted response
        """
        return self.enforce_on_output(response)
    
    def enforce_on_artifact(self, artifact: Any) -> Any:
        """
        Apply redaction to artifact contents.
        
        GOV-SEC-AUTO-004: Apply to artifact contents.
        
        Args:
            artifact: Artifact data (dict, string, etc.)
            
        Returns:
            Redacted artifact
        """
        return self.enforce_on_output(artifact)
    
    def enforce_on_log_message(self, message: str) -> str:
        """
        Apply redaction to log messages.
        
        Args:
            message: Log message string
            
        Returns:
            Redacted message
        """
        result = self._redactor.redact_text(message)
        if result != message:
            self._redaction_count += 1
            self._emit_auto_redaction_event(message, result)
        return result
    
    def _emit_auto_redaction_event(self, original: Any, redacted: Any) -> None:
        """Emit auto_redaction_applied trace event."""
        if self._emit_event:
            # Calculate change summary
            original_str = str(original)
            redacted_str = str(redacted)
            mask_count = redacted_str.count(DEFAULT_MASK)
            
            self._emit_event("auto_redaction_applied", {
                "original_length": len(original_str),
                "redacted_length": len(redacted_str),
                "mask_count": mask_count,
                "data_type": type(original).__name__,
            })
    
    def wrap_emit_function(self, emit_fn: Any) -> Any:
        """
        Wrap a trace event emit function with auto-redaction.
        
        GOV-SEC-AUTO-002: Auto-redact all trace event payloads.
        
        Args:
            emit_fn: Original emit function
            
        Returns:
            Wrapped function that redacts before emitting
        """
        def wrapped_emit(event: Any) -> Any:
            # Handle dict events first
            if isinstance(event, dict) and "payload" in event and event["payload"]:
                redacted_payload = self.enforce_on_trace_payload(event["payload"])
                event = {**event, "payload": redacted_payload}
            # Handle object-style events with 'payload' attribute
            elif hasattr(event, 'payload') and event.payload:
                redacted_payload = self.enforce_on_trace_payload(event.payload)
                if hasattr(event, 'model_copy'):
                    # Pydantic model
                    event = event.model_copy(update={"payload": redacted_payload})
                elif hasattr(event, '_replace'):
                    # Named tuple
                    event = event._replace(payload=redacted_payload)
            return emit_fn(event)
        return wrapped_emit
    
    def wrap_response_handler(self, handler: Any) -> Any:
        """
        Wrap an API response handler with auto-redaction.
        
        GOV-SEC-AUTO-003: Auto-redact all API responses.
        
        Args:
            handler: Original handler function
            
        Returns:
            Wrapped function that redacts response
        """
        def wrapped_handler(*args: Any, **kwargs: Any) -> Any:
            result = handler(*args, **kwargs)
            if isinstance(result, dict):
                return self.enforce_on_api_response(result)
            return result
        return wrapped_handler


# Global enforcer instance - always available
_global_auto_enforcer: AutoRedactionEnforcer | None = None


def get_auto_redaction_enforcer(
    *,
    redactor: SecurityRedactor | None = None,
    emit_event_fn: Any = None,
) -> AutoRedactionEnforcer:
    """
    Get or create the global auto-redaction enforcer.
    
    This function provides a singleton-like access pattern for
    the auto-redaction enforcer, ensuring consistent redaction
    across all output paths.
    
    Args:
        redactor: Optional SecurityRedactor to use
        emit_event_fn: Optional callback for trace events
        
    Returns:
        AutoRedactionEnforcer instance
    """
    global _global_auto_enforcer
    if _global_auto_enforcer is None:
        _global_auto_enforcer = AutoRedactionEnforcer(
            redactor=redactor,
            emit_event_fn=emit_event_fn,
        )
    return _global_auto_enforcer


def reset_auto_redaction_enforcer() -> None:
    """
    Reset the global auto-redaction enforcer.
    
    Primarily for testing purposes.
    """
    global _global_auto_enforcer
    _global_auto_enforcer = None
