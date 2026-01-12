# ==============================
# Auto-Discovery Tests
# ==============================
"""
tests/unit/test_auto_discovery.py

Tests for the decorator-based auto-discovery system.
Validates that @agent and @tool decorators work correctly
and that auto-discovery finds all decorated components.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from core.agents.base import BaseAgent, agent
from core.tools.base import BaseTool, tool
from core.contracts.descriptors_schema import AgentDescriptor, ToolDescriptor, CostHint, SensitivityClass
from core.utils.product_loader import (
    auto_discover_agents,
    auto_discover_tools,
    auto_register,
    ProductRegistries,
)


class TestAgentDecorator:
    """Tests for the @agent decorator."""

    def test_agent_decorator_sets_attributes(self) -> None:
        """@agent decorator sets _auto_discover and _agent_descriptor."""

        @agent(
            name="test_agent",
            purpose="Test agent for decorator validation",
            capabilities=["testing", "validation"],
            cost_hint="LOW",
        )
        class TestAgent(BaseAgent):
            name = "test_agent"

            def run(self, params: Dict[str, Any], ctx: Any) -> Any:
                return {}

        assert hasattr(TestAgent, "_auto_discover")
        assert TestAgent._auto_discover is True
        assert hasattr(TestAgent, "_agent_descriptor")
        assert isinstance(TestAgent._agent_descriptor, AgentDescriptor)
        assert TestAgent._agent_descriptor.name == "test_agent"
        assert TestAgent._agent_descriptor.purpose == "Test agent for decorator validation"
        assert TestAgent._agent_descriptor.capabilities == ["testing", "validation"]
        assert TestAgent._agent_descriptor.cost_hint == CostHint.LOW

    def test_agent_decorator_with_allowed_step_types(self) -> None:
        """@agent decorator correctly handles allowed_step_types."""

        @agent(
            name="plan_agent",
            purpose="Agent that generates plans",
            capabilities=["planning"],
            cost_hint="MED",
            allowed_step_types=["agent", "plan_proposal"],
        )
        class PlanAgent(BaseAgent):
            name = "plan_agent"

            def run(self, params: Dict[str, Any], ctx: Any) -> Any:
                return {}

        assert PlanAgent._agent_descriptor.allowed_step_types == ["agent", "plan_proposal"]

    def test_agent_decorator_default_step_types(self) -> None:
        """@agent decorator uses default allowed_step_types when not specified."""

        @agent(
            name="default_agent",
            purpose="Agent with default step types",
            capabilities=["default"],
            cost_hint="LOW",
        )
        class DefaultAgent(BaseAgent):
            name = "default_agent"

            def run(self, params: Dict[str, Any], ctx: Any) -> Any:
                return {}

        assert DefaultAgent._agent_descriptor.allowed_step_types == ["agent"]


class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_tool_decorator_sets_attributes(self) -> None:
        """@tool decorator sets _auto_discover and _tool_descriptor."""

        @tool(
            name="test_tool",
            description="Test tool for decorator validation",
            capabilities=["testing", "validation"],
            read_only=True,
            side_effect=False,
            sensitivity_class="LOW",
            cost_hint="LOW",
        )
        class TestTool(BaseTool):
            name = "test_tool"
            description = "Test tool"

            def run(self, params: Dict[str, Any], ctx: Any) -> Any:
                return {}

        assert hasattr(TestTool, "_auto_discover")
        assert TestTool._auto_discover is True
        assert hasattr(TestTool, "_tool_descriptor")
        assert isinstance(TestTool._tool_descriptor, ToolDescriptor)
        assert TestTool._tool_descriptor.name == "test_tool"
        assert TestTool._tool_descriptor.description == "Test tool for decorator validation"
        assert TestTool._tool_descriptor.capabilities == ["testing", "validation"]
        assert TestTool._tool_descriptor.read_only is True
        assert TestTool._tool_descriptor.side_effect is False
        assert TestTool._tool_descriptor.sensitivity_class == SensitivityClass.LOW
        assert TestTool._tool_descriptor.cost_hint == CostHint.LOW

    def test_tool_decorator_with_side_effects(self) -> None:
        """@tool decorator correctly handles side_effect and read_only flags."""

        @tool(
            name="write_tool",
            description="Tool that writes data",
            capabilities=["writing"],
            read_only=False,
            side_effect=True,
            sensitivity_class="HIGH",
            cost_hint="MED",
        )
        class WriteTool(BaseTool):
            name = "write_tool"
            description = "Tool that writes"

            def run(self, params: Dict[str, Any], ctx: Any) -> Any:
                return {}

        assert WriteTool._tool_descriptor.read_only is False
        assert WriteTool._tool_descriptor.side_effect is True
        assert WriteTool._tool_descriptor.sensitivity_class == SensitivityClass.HIGH


class TestAutoDiscovery:
    """Tests for auto-discovery functions."""

    def test_auto_discover_agents_finds_decorated_classes(self, tmp_path: Path) -> None:
        """auto_discover_agents finds classes with @agent decorator."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "__init__.py").write_text("")
        
        agent_code = '''
from __future__ import annotations
from typing import Any, Dict
from core.agents.base import BaseAgent, agent

@agent(
    name="discovered_agent",
    purpose="Agent to be discovered",
    capabilities=["discovery"],
    cost_hint="LOW",
)
class DiscoveredAgent(BaseAgent):
    name = "discovered_agent"
    
    def run(self, params: Dict[str, Any], ctx: Any) -> Any:
        return {}

def build() -> DiscoveredAgent:
    return DiscoveredAgent()
'''
        (agents_dir / "discovered_agent.py").write_text(agent_code)

        discovered = auto_discover_agents(tmp_path)
        
        assert len(discovered) == 1
        name, factory, descriptor = discovered[0]
        assert name == "discovered_agent"
        assert callable(factory)
        assert isinstance(descriptor, AgentDescriptor)
        assert descriptor.name == "discovered_agent"

    def test_auto_discover_tools_finds_decorated_classes(self, tmp_path: Path) -> None:
        """auto_discover_tools finds classes with @tool decorator."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "__init__.py").write_text("")
        
        tool_code = '''
from __future__ import annotations
from typing import Any, Dict
from core.tools.base import BaseTool, tool

@tool(
    name="discovered_tool",
    description="Tool to be discovered",
    capabilities=["discovery"],
    read_only=True,
    side_effect=False,
    sensitivity_class="LOW",
    cost_hint="LOW",
)
class DiscoveredTool(BaseTool):
    name = "discovered_tool"
    description = "Discovered tool"
    
    def run(self, params: Dict[str, Any], ctx: Any) -> Any:
        return {}

def build() -> DiscoveredTool:
    return DiscoveredTool()
'''
        (tools_dir / "discovered_tool.py").write_text(tool_code)

        discovered = auto_discover_tools(tmp_path)
        
        assert len(discovered) == 1
        name, factory, descriptor = discovered[0]
        assert name == "discovered_tool"
        assert callable(factory)
        assert isinstance(descriptor, ToolDescriptor)
        assert descriptor.name == "discovered_tool"

    def test_auto_discover_ignores_non_decorated_classes(self, tmp_path: Path) -> None:
        """auto_discover_* ignores classes without decorators."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "__init__.py").write_text("")
        
        agent_code = '''
from __future__ import annotations
from typing import Any, Dict
from core.agents.base import BaseAgent

class NonDecoratedAgent(BaseAgent):
    name = "non_decorated"
    
    def run(self, params: Dict[str, Any], ctx: Any) -> Any:
        return {}

def build() -> NonDecoratedAgent:
    return NonDecoratedAgent()
'''
        (agents_dir / "non_decorated.py").write_text(agent_code)

        discovered = auto_discover_agents(tmp_path)
        assert len(discovered) == 0


class TestAutoRegister:
    """Tests for auto_register function."""

    def test_auto_register_registers_all_components(self, tmp_path: Path) -> None:
        """auto_register registers both agents and tools."""
        # Create agents directory
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "__init__.py").write_text("")
        
        agent_code = '''
from __future__ import annotations
from typing import Any, Dict
from core.agents.base import BaseAgent, agent

@agent(
    name="auto_agent",
    purpose="Auto-registered agent",
    capabilities=["auto"],
    cost_hint="LOW",
)
class AutoAgent(BaseAgent):
    name = "auto_agent"
    
    def run(self, params: Dict[str, Any], ctx: Any) -> Any:
        return {}

def build() -> AutoAgent:
    return AutoAgent()
'''
        (agents_dir / "auto_agent.py").write_text(agent_code)

        # Create tools directory
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "__init__.py").write_text("")
        
        tool_code = '''
from __future__ import annotations
from typing import Any, Dict
from core.tools.base import BaseTool, tool

@tool(
    name="auto_tool",
    description="Auto-registered tool",
    capabilities=["auto"],
    read_only=True,
    side_effect=False,
    sensitivity_class="LOW",
    cost_hint="LOW",
)
class AutoTool(BaseTool):
    name = "auto_tool"
    description = "Auto tool"
    
    def run(self, params: Dict[str, Any], ctx: Any) -> Any:
        return {}

def build() -> AutoTool:
    return AutoTool()
'''
        (tools_dir / "auto_tool.py").write_text(tool_code)

        # Create mock registries (ProductRegistries requires settings)
        mock_agent_registry = MagicMock()
        mock_tool_registry = MagicMock()
        mock_settings = MagicMock()
        registries = ProductRegistries(
            agent_registry=mock_agent_registry,
            tool_registry=mock_tool_registry,
            settings=mock_settings,
        )

        auto_register(registries, tmp_path)

        mock_agent_registry.register.assert_called_once()
        mock_tool_registry.register.assert_called_once()
        
        # Verify agent was registered with correct arguments
        agent_call = mock_agent_registry.register.call_args
        assert agent_call[0][0] == "auto_agent"
        assert callable(agent_call[0][1])
        assert isinstance(agent_call[1]["descriptor"], AgentDescriptor)
        
        # Verify tool was registered with correct arguments
        tool_call = mock_tool_registry.register.call_args
        assert tool_call[0][0] == "auto_tool"
        assert callable(tool_call[0][1])
        assert isinstance(tool_call[1]["descriptor"], ToolDescriptor)


class TestHelloWorldProduct:
    """Tests that hello_world product uses auto-discovery correctly."""

    def test_hello_world_registry_uses_auto_register(self) -> None:
        """hello_world registry.py uses auto_register."""
        from products.hello_world import registry
        import inspect
        
        source = inspect.getsource(registry.register)
        assert "auto_register" in source

    def test_hello_world_simple_agent_has_decorator(self) -> None:
        """hello_world SimpleAgent has @agent decorator."""
        from products.hello_world.agents.simple_agent import SimpleAgent
        
        assert hasattr(SimpleAgent, "_auto_discover")
        assert SimpleAgent._auto_discover is True
        assert hasattr(SimpleAgent, "_agent_descriptor")
        assert isinstance(SimpleAgent._agent_descriptor, AgentDescriptor)

    def test_hello_world_echo_tool_has_decorator(self) -> None:
        """hello_world EchoTool has @tool decorator."""
        from products.hello_world.tools.echo_tool import EchoTool
        
        assert hasattr(EchoTool, "_auto_discover")
        assert EchoTool._auto_discover is True
        assert hasattr(EchoTool, "_tool_descriptor")
        assert isinstance(EchoTool._tool_descriptor, ToolDescriptor)


class TestADEProduct:
    """Tests that ADE product uses auto-discovery correctly."""

    def test_ade_registry_uses_auto_register(self) -> None:
        """ADE registry.py uses auto_register."""
        from products.ade import registry
        import inspect
        
        source = inspect.getsource(registry.register)
        assert "auto_register" in source

    def test_ade_dashboard_agent_has_decorator(self) -> None:
        """ADE DashboardAgent has @agent decorator."""
        from products.ade.agents.dashboard_agent import DashboardAgent
        
        assert hasattr(DashboardAgent, "_auto_discover")
        assert DashboardAgent._auto_discover is True
        assert hasattr(DashboardAgent, "_agent_descriptor")
        assert isinstance(DashboardAgent._agent_descriptor, AgentDescriptor)

    def test_ade_data_reader_tool_has_decorator(self) -> None:
        """ADE DataReaderTool has @tool decorator."""
        from products.ade.tools.data_reader import DataReaderTool
        
        assert hasattr(DataReaderTool, "_auto_discover")
        assert DataReaderTool._auto_discover is True
        assert hasattr(DataReaderTool, "_tool_descriptor")
        assert isinstance(DataReaderTool._tool_descriptor, ToolDescriptor)

    def test_ade_all_agents_have_decorators(self) -> None:
        """All ADE agents have @agent decorators."""
        from products.ade.agents.dashboard_agent import DashboardAgent
        from products.ade.agents.intent_agent import IntentAgent
        from products.ade.agents.plan_agent import PlanAgent
        from products.ade.agents.plan_proposal_agent import PlanProposalAgent
        from products.ade.agents.planning_agent import PlanningAgent
        from products.ade.agents.sufficiency_evaluator import SufficiencyEvaluatorAgent

        agents = [
            DashboardAgent,
            IntentAgent,
            PlanAgent,
            PlanProposalAgent,
            PlanningAgent,
            SufficiencyEvaluatorAgent,
        ]

        for agent_cls in agents:
            assert hasattr(agent_cls, "_auto_discover"), f"{agent_cls.__name__} missing _auto_discover"
            assert agent_cls._auto_discover is True, f"{agent_cls.__name__} _auto_discover is not True"
            assert hasattr(agent_cls, "_agent_descriptor"), f"{agent_cls.__name__} missing _agent_descriptor"
            assert isinstance(agent_cls._agent_descriptor, AgentDescriptor), \
                f"{agent_cls.__name__} _agent_descriptor is not AgentDescriptor"

    def test_ade_all_tools_have_decorators(self) -> None:
        """All ADE tools have @tool decorators."""
        from products.ade.tools.data_reader import DataReaderTool
        from products.ade.tools.build_chart_spec import BuildChartSpecTool
        from products.ade.tools.recommend_chart import RecommendChartTool
        from products.ade.tools.detect_anomalies import DetectAnomaliesTool
        from products.ade.tools.driver_analysis import DriverAnalysisTool
        from products.ade.tools.assemble_insight_card import AssembleInsightCardTool
        from products.ade.tools.assemble_decision_packet import AssembleDecisionPacketTool
        from products.ade.tools.assemble_evidence_bundle import AssembleEvidenceBundleTool
        from products.ade.tools.build_reasoning_narrative import BuildReasoningNarrativeTool
        from products.ade.tools.compute_business_metrics import ComputeBusinessMetricsTool
        from products.ade.tools.assemble_business_report import AssembleBusinessReportTool
        from products.ade.tools.export_pdf import ExportPdfTool
        from products.ade.tools.render_business_report_html import RenderBusinessReportHtmlTool
        from products.ade.tools.render_decision_packet_html import RenderDecisionPacketHtmlTool
        from products.ade.tools.hypothesis_test_data_outage import HypothesisTestDataOutageTool
        from products.ade.tools.hypothesis_test_seasonality import HypothesisTestSeasonalityTool

        tools = [
            DataReaderTool,
            BuildChartSpecTool,
            RecommendChartTool,
            DetectAnomaliesTool,
            DriverAnalysisTool,
            AssembleInsightCardTool,
            AssembleDecisionPacketTool,
            AssembleEvidenceBundleTool,
            BuildReasoningNarrativeTool,
            ComputeBusinessMetricsTool,
            AssembleBusinessReportTool,
            ExportPdfTool,
            RenderBusinessReportHtmlTool,
            RenderDecisionPacketHtmlTool,
            HypothesisTestDataOutageTool,
            HypothesisTestSeasonalityTool,
        ]

        for tool_cls in tools:
            assert hasattr(tool_cls, "_auto_discover"), f"{tool_cls.__name__} missing _auto_discover"
            assert tool_cls._auto_discover is True, f"{tool_cls.__name__} _auto_discover is not True"
            assert hasattr(tool_cls, "_tool_descriptor"), f"{tool_cls.__name__} missing _tool_descriptor"
            assert isinstance(tool_cls._tool_descriptor, ToolDescriptor), \
                f"{tool_cls.__name__} _tool_descriptor is not ToolDescriptor"
