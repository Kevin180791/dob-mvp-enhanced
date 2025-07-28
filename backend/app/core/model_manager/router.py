import logging
import random
from typing import Dict, List, Any, Optional, Union, Callable
import asyncio

from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Router for model requests with fallback and load balancing.
    """
    
    def __init__(self, registry: ModelRegistry):
        """
        Initialize the model router.
        
        Args:
            registry: The model registry.
        """
        self.registry = registry
        self.agent_assignments: Dict[str, Dict[str, Any]] = {}
    
    def assign_model_to_agent(
        self,
        agent_id: str,
        model_id: str,
        fallback_model_id: Optional[str] = None,
    ) -> None:
        """
        Assign a model to an agent.
        
        Args:
            agent_id: The ID of the agent.
            model_id: The ID of the model.
            fallback_model_id: The ID of the fallback model.
        """
        # Check if model exists
        model = self.registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        # Check if fallback model exists
        if fallback_model_id:
            fallback_model = self.registry.get_model(fallback_model_id)
            if not fallback_model:
                raise ValueError(f"Fallback model not found: {fallback_model_id}")
        
        # Create assignment
        assignment = {
            "agent_id": agent_id,
            "model_id": model_id,
            "fallback_model_id": fallback_model_id,
        }
        
        # Store assignment
        self.agent_assignments[agent_id] = assignment
        
        logger.info(f"Assigned model {model_id} to agent {agent_id}" + 
                   (f" with fallback {fallback_model_id}" if fallback_model_id else ""))
    
    def get_agent_model(self, agent_id: str) -> Optional[str]:
        """
        Get the model assigned to an agent.
        
        Args:
            agent_id: The ID of the agent.
            
        Returns:
            The ID of the assigned model, or None if not assigned.
        """
        assignment = self.agent_assignments.get(agent_id)
        if not assignment:
            return None
        
        return assignment["model_id"]
    
    def get_agent_fallback_model(self, agent_id: str) -> Optional[str]:
        """
        Get the fallback model assigned to an agent.
        
        Args:
            agent_id: The ID of the agent.
            
        Returns:
            The ID of the assigned fallback model, or None if not assigned.
        """
        assignment = self.agent_assignments.get(agent_id)
        if not assignment:
            return None
        
        return assignment.get("fallback_model_id")
    
    async def route_text_request(
        self,
        agent_id: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route a text generation request to the appropriate model.
        
        Args:
            agent_id: The ID of the agent making the request.
            prompt: The prompt to generate text from.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A dictionary containing the generated text and metadata.
        """
        # Get assigned model
        model_id = self.get_agent_model(agent_id)
        fallback_model_id = self.get_agent_fallback_model(agent_id)
        
        # If no model assigned, use default
        if not model_id:
            model_id = self.registry.get_default_model("text")
            if not model_id:
                raise ValueError(f"No model assigned to agent {agent_id} and no default text model set")
        
        try:
            # Try primary model
            result = await self.registry.generate_text(prompt, model_id, **kwargs)
            
            # Check for errors
            if "error" in result:
                raise ValueError(result["error"])
            
            return result
            
        except Exception as e:
            logger.warning(f"Error using primary model {model_id} for agent {agent_id}: {str(e)}")
            
            # Try fallback model if available
            if fallback_model_id:
                try:
                    logger.info(f"Using fallback model {fallback_model_id} for agent {agent_id}")
                    result = await self.registry.generate_text(prompt, fallback_model_id, **kwargs)
                    
                    # Add fallback information
                    result["fallback"] = True
                    result["primary_model_error"] = str(e)
                    
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Error using fallback model {fallback_model_id} for agent {agent_id}: {str(fallback_error)}")
                    raise ValueError(f"Both primary and fallback models failed: {str(e)} / {str(fallback_error)}")
            
            # No fallback available
            raise
    
    async def route_embedding_request(
        self,
        agent_id: str,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        Route an embedding generation request to the appropriate model.
        
        Args:
            agent_id: The ID of the agent making the request.
            texts: The texts to generate embeddings for.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embeddings, one for each input text.
        """
        # Get assigned model
        model_id = self.get_agent_model(agent_id)
        fallback_model_id = self.get_agent_fallback_model(agent_id)
        
        # If no model assigned, use default
        if not model_id:
            model_id = self.registry.get_default_model("embedding")
            if not model_id:
                raise ValueError(f"No model assigned to agent {agent_id} and no default embedding model set")
        
        try:
            # Try primary model
            result = await self.registry.generate_embeddings(texts, model_id, **kwargs)
            return result
            
        except Exception as e:
            logger.warning(f"Error using primary model {model_id} for agent {agent_id}: {str(e)}")
            
            # Try fallback model if available
            if fallback_model_id:
                try:
                    logger.info(f"Using fallback model {fallback_model_id} for agent {agent_id}")
                    result = await self.registry.generate_embeddings(texts, fallback_model_id, **kwargs)
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Error using fallback model {fallback_model_id} for agent {agent_id}: {str(fallback_error)}")
                    raise ValueError(f"Both primary and fallback models failed: {str(e)} / {str(fallback_error)}")
            
            # No fallback available
            raise

