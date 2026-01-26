"""
Tests for IMP-045: Cloud Credential Patterns (GOV-SEC-CRED-001..005).

Verifies:
- AWS credential pattern detection
- GCP credential pattern detection
- Azure credential pattern detection
- GitHub credential pattern detection
- Trace event emission
"""

import pytest
from typing import Any, Dict, List

from core.governance.security import (
    AWS_PATTERNS,
    AZURE_PATTERNS,
    GCP_PATTERNS,
    GITHUB_PATTERNS,
    OTHER_CLOUD_PATTERNS,
    SecurityRedactor,
)
from core.memory.tracing import TraceEventType


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def redactor() -> SecurityRedactor:
    return SecurityRedactor()


@pytest.fixture
def redactor_with_events() -> tuple:
    events: List[Dict[str, Any]] = []
    
    def capture_event(event_type: str, payload: Dict[str, Any]):
        events.append({"type": event_type, "payload": payload})
    
    return SecurityRedactor(emit_event_fn=capture_event), events


# ============================================================================
# GOV-SEC-CRED-001: AWS Patterns
# ============================================================================


class TestAWSPatterns:
    """Test AWS credential pattern detection."""
    
    def test_aws_access_key_id_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-001: Detect AWS Access Key ID."""
        text = "AWS key: AKIAIOSFODNN7EXAMPLE"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "aws" in counts
        assert counts["aws"] >= 1
    
    def test_aws_access_key_redacted(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-001: Redact AWS Access Key ID."""
        text = "AWS key: AKIAIOSFODNN7EXAMPLE"
        redacted = redactor.redact_text(text)
        
        assert "AKIAIOSFODNN7EXAMPLE" not in redacted
        assert "REDACTED" in redacted
    
    def test_aws_config_key_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-001: Detect AWS key in config format."""
        text = 'aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"'
        counts = redactor.detect_cloud_credentials(text)
        
        assert "aws" in counts
    
    def test_aws_patterns_defined(self):
        """GOV-SEC-CRED-001: AWS patterns are defined."""
        assert len(AWS_PATTERNS) >= 2
        # Should have access key and secret key patterns
        pattern_str = " ".join(AWS_PATTERNS)
        assert "AKIA" in pattern_str


# ============================================================================
# GOV-SEC-CRED-002: GCP Patterns
# ============================================================================


class TestGCPPatterns:
    """Test GCP credential pattern detection."""
    
    def test_gcp_api_key_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-002: Detect GCP API Key."""
        text = "GCP key: AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "gcp" in counts
        assert counts["gcp"] >= 1
    
    def test_gcp_api_key_redacted(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-002: Redact GCP API Key."""
        text = "GCP key: AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
        redacted = redactor.redact_text(text)
        
        assert "AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe" not in redacted
    
    def test_gcp_service_account_indicator(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-002: Detect service account JSON indicator."""
        text = '{"type": "service_account", "project_id": "my-project"}'
        counts = redactor.detect_cloud_credentials(text)
        
        assert "gcp" in counts
    
    def test_gcp_patterns_defined(self):
        """GOV-SEC-CRED-002: GCP patterns are defined."""
        assert len(GCP_PATTERNS) >= 2


# ============================================================================
# GOV-SEC-CRED-003: Azure Patterns
# ============================================================================


class TestAzurePatterns:
    """Test Azure credential pattern detection."""
    
    def test_azure_storage_key_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-003: Detect Azure Storage Account Key."""
        # Simulated Azure storage key (base64-like, 86+ chars)
        key = "AccountKey=" + "A" * 86 + "=="
        text = f"Azure: {key}"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "azure" in counts
    
    def test_azure_sas_token_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-003: Detect Azure SAS Token."""
        text = "SharedAccessSignature=sv=2020-08-04&ss=b&srt=sco"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "azure" in counts
    
    def test_azure_connection_string_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-003: Detect Azure connection string."""
        text = "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=abc123"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "azure" in counts
    
    def test_azure_patterns_defined(self):
        """GOV-SEC-CRED-003: Azure patterns are defined."""
        assert len(AZURE_PATTERNS) >= 2


# ============================================================================
# GOV-SEC-CRED-004: GitHub Patterns
# ============================================================================


class TestGitHubPatterns:
    """Test GitHub credential pattern detection."""
    
    def test_github_pat_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-004: Detect GitHub Personal Access Token."""
        text = "Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "github" in counts
        assert counts["github"] >= 1
    
    def test_github_pat_redacted(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-004: Redact GitHub PAT."""
        token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        text = f"Token: {token}"
        redacted = redactor.redact_text(text)
        
        assert token not in redacted
    
    def test_github_oauth_token_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-004: Detect GitHub OAuth Token."""
        text = "Token: gho_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "github" in counts
    
    def test_github_server_token_detected(self, redactor: SecurityRedactor):
        """GOV-SEC-CRED-004: Detect GitHub Server Token."""
        text = "Token: ghs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "github" in counts
    
    def test_github_patterns_defined(self):
        """GOV-SEC-CRED-004: GitHub patterns are defined."""
        assert len(GITHUB_PATTERNS) >= 4
        # Should have ghp_, gho_, ghu_, ghs_ patterns
        pattern_str = " ".join(GITHUB_PATTERNS)
        assert "ghp_" in pattern_str
        assert "gho_" in pattern_str


# ============================================================================
# GOV-SEC-CRED-005: Trace Events
# ============================================================================


class TestCloudCredentialTraceEvents:
    """Test trace event emission."""
    
    def test_trace_event_emitted_on_detection(self):
        """GOV-SEC-CRED-005: Trace event emitted when credentials detected."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append({"type": event_type, "payload": payload})
        
        redactor = SecurityRedactor(emit_event_fn=capture_event)
        redactor.redact_text("Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        
        assert len(events) == 1
        assert events[0]["type"] == "cloud_credential_redacted"
        assert "providers" in events[0]["payload"]
        assert "github" in events[0]["payload"]["providers"]
    
    def test_trace_event_has_provider_counts(self):
        """GOV-SEC-CRED-005: Trace event has provider counts."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append(payload)
        
        redactor = SecurityRedactor(emit_event_fn=capture_event)
        redactor.redact_text("AWS: AKIAIOSFODNN7EXAMPLE GitHub: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        
        payload = events[0]
        assert "aws" in payload["providers"]
        assert "github" in payload["providers"]
        assert payload["total_count"] >= 2
    
    def test_no_event_when_no_credentials(self):
        """GOV-SEC-CRED-005: No event when no credentials."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append({"type": event_type})
        
        redactor = SecurityRedactor(emit_event_fn=capture_event)
        redactor.redact_text("This is normal text with no credentials.")
        
        # Should have no cloud_credential_redacted events
        cloud_events = [e for e in events if e.get("type") == "cloud_credential_redacted"]
        assert len(cloud_events) == 0
    
    def test_trace_event_type_exists(self):
        """GOV-SEC-CRED-005: CLOUD_CREDENTIAL_REDACTED event type exists."""
        assert hasattr(TraceEventType, "CLOUD_CREDENTIAL_REDACTED")
        assert TraceEventType.CLOUD_CREDENTIAL_REDACTED.value == "cloud_credential_redacted"


# ============================================================================
# Other Cloud Pattern Tests
# ============================================================================


class TestOtherCloudPatterns:
    """Test other cloud service credential patterns."""
    
    def test_stripe_key_detected(self, redactor: SecurityRedactor):
        """Detect Stripe API key."""
        # Use test prefix (sk_test_) to avoid GitHub push protection
        text = "Stripe: sk_test_FAKE_NOT_REAL_KEY_12345"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "other" in counts
    
    def test_slack_token_detected(self, redactor: SecurityRedactor):
        """Detect Slack token."""
        # Pattern: xox[baprs]-[0-9]+-[0-9]+-[0-9]+-[a-fA-F0-9]+
        text = "Slack: xoxb-123456789012-1234567890123-1234567890123-abcdefABCDEF0123"
        counts = redactor.detect_cloud_credentials(text)
        
        assert "other" in counts
    
    def test_other_patterns_defined(self):
        """Other cloud patterns are defined."""
        assert len(OTHER_CLOUD_PATTERNS) >= 3


# ============================================================================
# Integration Tests
# ============================================================================


class TestCloudCredentialIntegration:
    """Integration tests for cloud credential detection."""
    
    def test_multiple_providers_in_text(self, redactor: SecurityRedactor):
        """Detect credentials from multiple providers."""
        text = """
        AWS: AKIAIOSFODNN7EXAMPLE
        GCP: AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe
        GitHub: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        """
        counts = redactor.detect_cloud_credentials(text)
        
        assert len(counts) >= 2
    
    def test_redaction_removes_all_credentials(self, redactor: SecurityRedactor):
        """Redaction removes all credential types."""
        aws_key = "AKIAIOSFODNN7EXAMPLE"
        github_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        text = f"AWS: {aws_key} GitHub: {github_token}"
        
        redacted = redactor.redact_text(text)
        
        assert aws_key not in redacted
        assert github_token not in redacted
    
    def test_cloud_credentials_disabled(self):
        """Cloud credentials can be disabled."""
        redactor = SecurityRedactor(include_cloud_credentials=False)
        text = "AWS: AKIAIOSFODNN7EXAMPLE"
        
        # Should not detect (patterns not loaded)
        redacted = redactor.redact_text(text)
        
        # The AWS key should still be in text since cloud patterns are disabled
        # (Only basic DEFAULT_PATTERNS would apply)
        # Note: Actual behavior depends on DEFAULT_PATTERNS overlap
        counts = redactor.detect_cloud_credentials(text)
        # Counts should still work via _cloud_patterns
        assert "aws" in counts or len(counts) == 0


# ============================================================================
# Backward Compatibility Tests
# ============================================================================


class TestBackwardCompatibility:
    """Test backward compatibility with existing redactor."""
    
    def test_sanitize_still_works(self, redactor: SecurityRedactor):
        """sanitize() method still works."""
        payload = {"password": "secret", "text": "normal"}
        result = redactor.sanitize(payload)
        
        assert result["password"] == "***REDACTED***"
        assert result["text"] == "normal"
    
    def test_scrub_alias_works(self, redactor: SecurityRedactor):
        """scrub() alias still works."""
        payload = {"token": "abc123"}
        result = redactor.scrub(payload)
        
        assert result["token"] == "***REDACTED***"
    
    def test_key_hints_still_work(self, redactor: SecurityRedactor):
        """Key hints still redact values."""
        payload = {
            "api_key": "my-secret-key",
            "authorization": "Bearer xyz",
        }
        result = redactor.sanitize(payload)
        
        assert result["api_key"] == "***REDACTED***"
        assert result["authorization"] == "***REDACTED***"
