# ==============================
# Tests for IMP-027: Version Tracking for Reproducibility
# ==============================
"""
Test suite for version tracking in runs.

IMP-027: MEM-REPRO-001, MEM-REPRO-002, MEM-REPRO-003
BRD: BRD-OPS-061
"""

import sys
import pytest

from core.contracts.run_schema import (
    RunRecord,
    RunStatus,
    Versions,
)


# ==============================
# MEM-REPRO-001: Versions Model
# ==============================

class TestVersionsModel:
    """Tests for Versions Pydantic model."""
    
    def test_versions_has_platform_version(self):
        """MEM-REPRO-001: Versions includes platform_version."""
        v = Versions(platform_version="2.0.0")
        assert v.platform_version == "2.0.0"
    
    def test_versions_has_flow_version(self):
        """MEM-REPRO-001: Versions includes flow_version."""
        v = Versions(flow_version="1.2.3")
        assert v.flow_version == "1.2.3"
    
    def test_versions_has_python_version(self):
        """MEM-REPRO-001: Versions includes python_version."""
        v = Versions(python_version="3.10.0")
        assert v.python_version == "3.10.0"
    
    def test_versions_has_models_dict(self):
        """MEM-REPRO-002: Versions includes models dict."""
        v = Versions(models={"gpt-4": "0613", "claude": "3.5-sonnet"})
        assert v.models == {"gpt-4": "0613", "claude": "3.5-sonnet"}
    
    def test_versions_defaults(self):
        """Versions has sensible defaults."""
        v = Versions()
        assert v.platform_version == "1.0.0"
        assert v.flow_version == "unknown"
        assert v.python_version == "unknown"
        assert v.models == {}
    
    def test_versions_extra_forbidden(self):
        """Extra fields are forbidden."""
        with pytest.raises(Exception):
            Versions(extra_field="not allowed")  # type: ignore


# ==============================
# MEM-REPRO-003: Versions.capture()
# ==============================

class TestVersionsCapture:
    """Tests for Versions.capture() factory method."""
    
    def test_capture_returns_versions(self):
        """capture() returns Versions instance."""
        v = Versions.capture()
        assert isinstance(v, Versions)
    
    def test_capture_python_version(self):
        """capture() gets Python version from sys.version_info."""
        v = Versions.capture()
        expected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert v.python_version == expected
    
    def test_capture_platform_version(self):
        """capture() accepts platform_version."""
        v = Versions.capture(platform_version="3.0.0")
        assert v.platform_version == "3.0.0"
    
    def test_capture_flow_version(self):
        """capture() accepts flow_version."""
        v = Versions.capture(flow_version="abc123")
        assert v.flow_version == "abc123"
    
    def test_capture_models(self):
        """capture() accepts models dict."""
        v = Versions.capture(models={"gpt-4": "turbo"})
        assert v.models == {"gpt-4": "turbo"}
    
    def test_capture_default_platform(self):
        """capture() defaults platform_version to 1.0.0."""
        v = Versions.capture()
        assert v.platform_version == "1.0.0"
    
    def test_capture_default_flow(self):
        """capture() defaults flow_version to unknown."""
        v = Versions.capture()
        assert v.flow_version == "unknown"
    
    def test_capture_default_models(self):
        """capture() defaults models to empty dict."""
        v = Versions.capture()
        assert v.models == {}


# ==============================
# RunRecord with Versions
# ==============================

class TestRunRecordVersions:
    """Tests for RunRecord.versions field."""
    
    def test_run_record_has_versions_field(self):
        """RunRecord includes versions field."""
        run = RunRecord(product="test", flow="test_flow")
        assert hasattr(run, "versions")
    
    def test_run_record_versions_optional(self):
        """versions field is optional (None by default)."""
        run = RunRecord(product="test", flow="test_flow")
        assert run.versions is None
    
    def test_run_record_with_versions(self):
        """RunRecord can include Versions object."""
        v = Versions(
            platform_version="2.0.0",
            flow_version="v1.0",
            python_version="3.10.0",
            models={"gpt-4": "0613"}
        )
        run = RunRecord(product="test", flow="test_flow", versions=v)
        assert run.versions is not None
        assert run.versions.platform_version == "2.0.0"
        assert run.versions.flow_version == "v1.0"
        assert run.versions.python_version == "3.10.0"
        assert run.versions.models == {"gpt-4": "0613"}
    
    def test_run_record_with_captured_versions(self):
        """RunRecord works with Versions.capture()."""
        v = Versions.capture(
            platform_version="1.5.0",
            flow_version="hash123",
            models={"claude": "3.5"}
        )
        run = RunRecord(product="test", flow="test_flow", versions=v)
        assert run.versions.platform_version == "1.5.0"
        assert run.versions.flow_version == "hash123"
        # Python version captured from runtime
        assert run.versions.python_version == f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


# ==============================
# Acceptance Checks
# ==============================

class TestAcceptanceChecks:
    """Acceptance criteria from imp_plan.md."""
    
    def test_run_record_includes_versions_object(self):
        """AC: RunRecord includes versions object."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            versions=Versions()
        )
        assert run.versions is not None
    
    def test_versions_includes_platform_version(self):
        """AC: versions includes platform_version."""
        v = Versions()
        assert hasattr(v, "platform_version")
        assert v.platform_version == "1.0.0"
    
    def test_versions_includes_flow_version(self):
        """AC: versions includes flow_version."""
        v = Versions()
        assert hasattr(v, "flow_version")
    
    def test_versions_includes_python_version(self):
        """AC: versions includes python_version."""
        v = Versions()
        assert hasattr(v, "python_version")
    
    def test_versions_includes_model_versions_dict(self):
        """AC: versions includes model versions dict."""
        v = Versions(models={"m1": "v1", "m2": "v2"})
        assert isinstance(v.models, dict)
        assert v.models == {"m1": "v1", "m2": "v2"}


# ==============================
# Serialization
# ==============================

class TestVersionsSerialization:
    """Tests for Versions serialization."""
    
    def test_versions_to_dict(self):
        """Versions serializes to dict."""
        v = Versions(
            platform_version="1.0.0",
            flow_version="v1",
            python_version="3.10.0",
            models={"m1": "v1"}
        )
        d = v.model_dump()
        assert d["platform_version"] == "1.0.0"
        assert d["flow_version"] == "v1"
        assert d["python_version"] == "3.10.0"
        assert d["models"] == {"m1": "v1"}
    
    def test_run_record_with_versions_serializes(self):
        """RunRecord with versions serializes correctly."""
        v = Versions(platform_version="2.0.0")
        run = RunRecord(product="test", flow="test_flow", versions=v)
        d = run.model_dump()
        assert d["versions"]["platform_version"] == "2.0.0"
    
    def test_versions_from_dict(self):
        """Versions can be created from dict."""
        d = {
            "platform_version": "1.0.0",
            "flow_version": "v1",
            "python_version": "3.10.0",
            "models": {"m1": "v1"}
        }
        v = Versions.model_validate(d)
        assert v.platform_version == "1.0.0"
        assert v.flow_version == "v1"


# ==============================
# Integration with start_run
# ==============================

class TestStartRunVersions:
    """Tests for start_run version capture integration."""
    
    def test_start_run_populates_versions(self):
        """start_run populates versions in RunRecord."""
        from unittest.mock import MagicMock
        from core.contracts.flow_schema import FlowDef, AutonomyLevel
        from core.orchestrator.context import RunContext
        from core.orchestrator.run_lifecycle import start_run
        
        # Create mock memory
        memory = MagicMock()
        memory.create_run = MagicMock()
        
        # Create flow def
        flow_def = MagicMock(spec=FlowDef)
        flow_def.autonomy_level = AutonomyLevel.SEMI_AUTO
        flow_def.steps = []
        flow_def.version = "1.2.3"
        
        # Create run context
        run_ctx = RunContext(
            run_id="test-run-001",
            product="test",
            flow="test_flow",
            payload={"key": "value"},
            meta={},
        )
        
        # Emit function
        emit_fn = MagicMock()
        
        # Call start_run
        run_record = start_run(
            memory=memory,
            flow_def=flow_def,
            run_ctx=run_ctx,
            emit_event_fn=emit_fn,
            platform_version="2.0.0",
            model_versions={"gpt-4": "turbo"},
        )
        
        # Verify versions populated
        assert run_record.versions is not None
        assert run_record.versions.platform_version == "2.0.0"
        assert run_record.versions.flow_version == "1.2.3"
        assert run_record.versions.python_version == f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert run_record.versions.models == {"gpt-4": "turbo"}
    
    def test_start_run_default_versions(self):
        """start_run uses default versions when not provided."""
        from unittest.mock import MagicMock
        from core.contracts.flow_schema import FlowDef, AutonomyLevel
        from core.orchestrator.context import RunContext
        from core.orchestrator.run_lifecycle import start_run
        
        memory = MagicMock()
        memory.create_run = MagicMock()
        
        flow_def = MagicMock(spec=FlowDef)
        flow_def.autonomy_level = AutonomyLevel.SEMI_AUTO
        flow_def.steps = []
        # No version attribute
        
        run_ctx = RunContext(
            run_id="test-run-002",
            product="test",
            flow="test_flow",
            payload={},
            meta={},
        )
        
        emit_fn = MagicMock()
        
        run_record = start_run(
            memory=memory,
            flow_def=flow_def,
            run_ctx=run_ctx,
            emit_event_fn=emit_fn,
        )
        
        assert run_record.versions is not None
        assert run_record.versions.platform_version == "1.0.0"
        # flow_version defaults to 'unknown' when not on flow_def
        assert run_record.versions.models == {}
