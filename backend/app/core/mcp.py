import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
import json

from app.core.model_manager import ModelRegistry

logger = logging.getLogger(__name__)

class MasterControlProgram:
    """
    Master Control Program (MCP) is the central orchestration engine for the DOB-MVP.
    It manages the workflow, coordinates agents, and handles the overall system state.
    """
    
    def __init__(self):
        """
        Initialize the Master Control Program.
        """
        self.initialized = False
        self.model_registry = None
        self.agents = {}
        self.tools = {}
        self.workflows = {}
        self.fallback_mode = False
        
    async def initialize(self, model_registry: Optional[ModelRegistry] = None):
        """
        Initialize the MCP with all required services.
        """
        if self.initialized:
            logger.warning("MCP already initialized")
            return
        
        try:
            # Store model registry
            self.model_registry = model_registry
            
            # Initialize RAG system
            await self._initialize_rag_system()
            
            # Initialize agents
            await self._initialize_agents()
            
            # Initialize tools
            await self._initialize_tools()
            
            # Initialize workflows
            await self._initialize_workflows()
            
            self.initialized = True
            self.fallback_mode = False
            logger.info("✅ MCP initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MCP: {str(e)}")
            logger.warning("Falling back to minimal mode")
            await self.initialize_fallback()
    
    async def initialize_fallback(self):
        """
        Initialize the MCP in fallback mode with minimal functionality.
        """
        try:
            # Initialize minimal functionality
            self.fallback_mode = True
            self.initialized = True
            
            # Register fallback agents
            self.agents = {
                "rfi_analyst": self._create_fallback_agent("rfi_analyst"),
                "plan_reviewer": self._create_fallback_agent("plan_reviewer"),
                "communication_agent": self._create_fallback_agent("communication_agent"),
            }
            
            # Register fallback tools
            self.tools = {
                "document_analyzer": self._create_fallback_tool("document_analyzer"),
                "rfi_formatter": self._create_fallback_tool("rfi_formatter"),
                "plan_analyzer": self._create_fallback_tool("plan_analyzer"),
            }
            
            # Register fallback workflows
            self.workflows = {
                "rfi_processing": self._create_fallback_workflow("rfi_processing"),
            }
            
            logger.info("✅ MCP initialized in fallback mode")
            
        except Exception as e:
            logger.error(f"Error initializing MCP in fallback mode: {str(e)}")
            self.initialized = False
            raise
    
    async def shutdown(self):
        """
        Shutdown the MCP and release resources.
        """
        if not self.initialized:
            return
        
        try:
            # Shutdown agents
            for agent_name, agent in self.agents.items():
                if hasattr(agent, "shutdown") and callable(agent.shutdown):
                    await agent.shutdown()
            
            # Shutdown tools
            for tool_name, tool in self.tools.items():
                if hasattr(tool, "shutdown") and callable(tool.shutdown):
                    await tool.shutdown()
            
            # Reset state
            self.initialized = False
            self.fallback_mode = False
            
            logger.info("MCP shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during MCP shutdown: {str(e)}")
    
    async def process_rfi(self, rfi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Request for Information (RFI).
        
        Args:
            rfi_data: The RFI data to process.
            
        Returns:
            The processed RFI data with analysis and response.
        """
        if not self.initialized:
            raise RuntimeError("MCP not initialized")
        
        try:
            # Check if we're in fallback mode
            if self.fallback_mode:
                return await self._process_rfi_fallback(rfi_data)
            
            # Get the RFI workflow
            workflow = self.workflows.get("rfi_processing")
            if not workflow:
                raise ValueError("RFI processing workflow not found")
            
            # Execute the workflow
            result = await workflow.execute(rfi_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing RFI: {str(e)}")
            # Try fallback if available
            if not self.fallback_mode:
                logger.warning("Falling back to minimal RFI processing")
                return await self._process_rfi_fallback(rfi_data)
            raise
    
    async def _process_rfi_fallback(self, rfi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an RFI in fallback mode.
        
        Args:
            rfi_data: The RFI data to process.
            
        Returns:
            The processed RFI data with basic analysis and response.
        """
        # Create a basic response
        response = {
            "id": rfi_data.get("id", "unknown"),
            "status": "processed",
            "analysis": {
                "category": "general",
                "complexity": "medium",
                "priority": "normal",
                "estimated_response_time": "24-48 hours",
            },
            "response": {
                "text": f"This is an automated response to your RFI regarding '{rfi_data.get('subject', 'unknown subject')}'. "
                       f"Your request has been received and is being processed. "
                       f"A detailed response will be provided by the appropriate team member.",
                "generated_by": "fallback_system",
                "confidence": 0.7,
            },
            "metadata": {
                "processed_at": "2023-07-19T10:00:00Z",
                "processing_time": 1.5,
                "fallback_mode": True,
            }
        }
        
        return response
    
    async def _initialize_rag_system(self):
        """
        Initialize the Retrieval-Augmented Generation (RAG) system.
        """
        try:
            from app.rag.system import RAGSystem
            
            # Initialize RAG system
            self.rag_system = RAGSystem()
            await self.rag_system.initialize()
            
            logger.info("✅ RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {str(e)}")
            logger.warning("RAG system not available, continuing without RAG")
            self.rag_system = None
    
    async def _initialize_agents(self):
        """
        Initialize all agents.
        """
        try:
            from app.agents.rfi_analyst import RFIAnalystAgent
            from app.agents.plan_reviewer import PlanReviewerAgent
            from app.agents.communication_agent import CommunicationAgent
            
            # Initialize agents
            self.agents = {
                "rfi_analyst": RFIAnalystAgent(model_registry=self.model_registry),
                "plan_reviewer": PlanReviewerAgent(model_registry=self.model_registry),
                "communication_agent": CommunicationAgent(model_registry=self.model_registry),
            }
            
            # Initialize each agent
            for agent_name, agent in self.agents.items():
                await agent.initialize()
            
            logger.info("✅ Core TGA agents registered successfully")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            logger.warning("Agents not available, using fallback agents")
            
            # Register fallback agents
            self.agents = {
                "rfi_analyst": self._create_fallback_agent("rfi_analyst"),
                "plan_reviewer": self._create_fallback_agent("plan_reviewer"),
                "communication_agent": self._create_fallback_agent("communication_agent"),
            }
    
    async def _initialize_tools(self):
        """
        Initialize all tools.
        """
        try:
            # Initialize tools (placeholder for actual tool initialization)
            self.tools = {
                "document_analyzer": {},
                "rfi_formatter": {},
                "plan_analyzer": {},
            }
            
            logger.info("✅ Core tools registered successfully")
            
        except Exception as e:
            logger.error(f"Error initializing tools: {str(e)}")
            logger.warning("Tools not available, using fallback tools")
            
            # Register fallback tools
            self.tools = {
                "document_analyzer": self._create_fallback_tool("document_analyzer"),
                "rfi_formatter": self._create_fallback_tool("rfi_formatter"),
                "plan_analyzer": self._create_fallback_tool("plan_analyzer"),
            }
    
    async def _initialize_workflows(self):
        """
        Initialize all workflows.
        """
        try:
            from app.core.workflow import Workflow
            
            # Define the RFI processing workflow
            rfi_workflow = Workflow(
                name="rfi_processing",
                description="Process a Request for Information (RFI)",
                steps=[
                    {
                        "name": "analyze_rfi",
                        "agent": "rfi_analyst",
                        "input": lambda data: data,
                        "output": lambda result, data: {**data, "analysis": result},
                    },
                    {
                        "name": "review_plans",
                        "agent": "plan_reviewer",
                        "input": lambda data: {
                            "rfi": data,
                            "analysis": data.get("analysis", {}),
                        },
                        "output": lambda result, data: {**data, "plan_review": result},
                    },
                    {
                        "name": "generate_response",
                        "agent": "communication_agent",
                        "input": lambda data: {
                            "rfi": data,
                            "analysis": data.get("analysis", {}),
                            "plan_review": data.get("plan_review", {}),
                        },
                        "output": lambda result, data: {**data, "response": result},
                    },
                ],
            )
            
            # Register workflows
            self.workflows = {
                "rfi_processing": rfi_workflow,
            }
            
            logger.info("✅ Agent Framework initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing workflows: {str(e)}")
            logger.warning("Workflows not available, using fallback workflows")
            
            # Register fallback workflows
            self.workflows = {
                "rfi_processing": self._create_fallback_workflow("rfi_processing"),
            }
    
    def _create_fallback_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Create a fallback agent.
        
        Args:
            agent_name: The name of the agent.
            
        Returns:
            A fallback agent.
        """
        return {
            "name": agent_name,
            "type": "fallback",
            "execute": self._fallback_execute,
        }
    
    def _create_fallback_tool(self, tool_name: str) -> Dict[str, Any]:
        """
        Create a fallback tool.
        
        Args:
            tool_name: The name of the tool.
            
        Returns:
            A fallback tool.
        """
        return {
            "name": tool_name,
            "type": "fallback",
            "execute": self._fallback_execute,
        }
    
    def _create_fallback_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        Create a fallback workflow.
        
        Args:
            workflow_name: The name of the workflow.
            
        Returns:
            A fallback workflow.
        """
        return {
            "name": workflow_name,
            "type": "fallback",
            "execute": self._fallback_workflow_execute,
        }
    
    async def _fallback_execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Fallback execution function for agents and tools.
        
        Args:
            input_data: The input data.
            
        Returns:
            A basic response.
        """
        return {
            "status": "processed",
            "result": "This is a fallback response. The system is operating in minimal mode.",
            "confidence": 0.5,
            "fallback": True,
        }
    
    async def _fallback_workflow_execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Fallback execution function for workflows.
        
        Args:
            input_data: The input data.
            
        Returns:
            A basic workflow response.
        """
        if isinstance(input_data, dict) and "id" in input_data:
            return await self._process_rfi_fallback(input_data)
        
        return {
            "status": "processed",
            "result": "This is a fallback workflow response. The system is operating in minimal mode.",
            "steps_executed": 0,
            "fallback": True,
        }

