"""
API-Abhängigkeiten für das DOB-MVP.
"""
from typing import Generator, Dict, Any
from fastapi import Depends

from app.core.mcp import MCP
from app.rag.system import RAGSystem
from app.rag.multimodal_system import MultimodalRAGSystem
from app.core.model_manager.registry import ModelRegistry
from app.core.workflow import WorkflowEngine
from app.agents.base import BaseAgent
from app.agents.rfi_analyst import RFIAnalystAgent
from app.agents.plan_reviewer import PlanReviewerAgent
from app.agents.communication_agent import CommunicationAgent
from app.agents.cost_estimation_agent import CostEstimationAgent
from app.agents.schedule_impact_agent import ScheduleImpactAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.document_analysis_agent import DocumentAnalysisAgent
from app.agents.coordination_agent import CoordinationAgent

# Singleton-Instanzen
_model_registry = ModelRegistry()
_rag_system = RAGSystem(_model_registry)
_multimodal_rag_system = MultimodalRAGSystem(_model_registry, _rag_system)
_workflow_engine = WorkflowEngine()
_mcp = MCP(_model_registry, _rag_system, _workflow_engine)

# Agent-Instanzen
_rfi_analyst_agent = RFIAnalystAgent(_model_registry, _rag_system)
_plan_reviewer_agent = PlanReviewerAgent(_model_registry, _rag_system)
_communication_agent = CommunicationAgent(_model_registry, _rag_system)
_cost_estimation_agent = CostEstimationAgent(_model_registry, _rag_system)
_schedule_impact_agent = ScheduleImpactAgent(_model_registry, _rag_system)
_compliance_agent = ComplianceAgent(_model_registry, _rag_system)
_document_analysis_agent = DocumentAnalysisAgent(_model_registry, _multimodal_rag_system)
_coordination_agent = CoordinationAgent(_model_registry, _rag_system, _workflow_engine)

# Registriere die Agenten beim MCP
_mcp.register_agent("rfi_analyst", _rfi_analyst_agent)
_mcp.register_agent("plan_reviewer", _plan_reviewer_agent)
_mcp.register_agent("communication", _communication_agent)
_mcp.register_agent("cost_estimation", _cost_estimation_agent)
_mcp.register_agent("schedule_impact", _schedule_impact_agent)
_mcp.register_agent("compliance", _compliance_agent)
_mcp.register_agent("document_analysis", _document_analysis_agent)
_mcp.register_agent("coordination", _coordination_agent)

def get_model_registry() -> ModelRegistry:
    """
    Gibt die Singleton-Instanz des ModelRegistry zurück.
    """
    return _model_registry

def get_rag_system() -> RAGSystem:
    """
    Gibt die Singleton-Instanz des RAGSystem zurück.
    """
    return _rag_system

def get_multimodal_rag_system() -> MultimodalRAGSystem:
    """
    Gibt die Singleton-Instanz des MultimodalRAGSystem zurück.
    """
    return _multimodal_rag_system

def get_workflow_engine() -> WorkflowEngine:
    """
    Gibt die Singleton-Instanz der WorkflowEngine zurück.
    """
    return _workflow_engine

def get_mcp() -> MCP:
    """
    Gibt die Singleton-Instanz des MCP zurück.
    """
    return _mcp

def get_rfi_analyst_agent() -> RFIAnalystAgent:
    """
    Gibt die Singleton-Instanz des RFIAnalystAgent zurück.
    """
    return _rfi_analyst_agent

def get_plan_reviewer_agent() -> PlanReviewerAgent:
    """
    Gibt die Singleton-Instanz des PlanReviewerAgent zurück.
    """
    return _plan_reviewer_agent

def get_communication_agent() -> CommunicationAgent:
    """
    Gibt die Singleton-Instanz des CommunicationAgent zurück.
    """
    return _communication_agent

def get_cost_estimation_agent() -> CostEstimationAgent:
    """
    Gibt die Singleton-Instanz des CostEstimationAgent zurück.
    """
    return _cost_estimation_agent

def get_schedule_impact_agent() -> ScheduleImpactAgent:
    """
    Gibt die Singleton-Instanz des ScheduleImpactAgent zurück.
    """
    return _schedule_impact_agent

def get_compliance_agent() -> ComplianceAgent:
    """
    Gibt die Singleton-Instanz des ComplianceAgent zurück.
    """
    return _compliance_agent

def get_document_analysis_agent() -> DocumentAnalysisAgent:
    """
    Gibt die Singleton-Instanz des DocumentAnalysisAgent zurück.
    """
    return _document_analysis_agent

def get_coordination_agent() -> CoordinationAgent:
    """
    Gibt die Singleton-Instanz des CoordinationAgent zurück.
    """
    return _coordination_agent

