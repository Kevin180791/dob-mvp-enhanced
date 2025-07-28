import logging
from typing import Dict, List, Any, Optional, Union
import json

from app.core.model_providers.base import ModelProvider

logger = logging.getLogger(__name__)

class ModelRegistry:
    """
    Registry for model providers and models.
    """
    
    def __init__(self):
        """
        Initialize the model registry.
        """
        self.providers: Dict[str, ModelProvider] = {}
        self.models: Dict[str, Dict[str, Any]] = {}
        self.default_models: Dict[str, str] = {
            "text": None,
            "embedding": None,
            "image": None,
            "multimodal": None,
        }
    
    def register_provider(self, provider_id: str, provider: ModelProvider) -> None:
        """
        Register a model provider.
        
        Args:
            provider_id: The ID of the provider.
            provider: The provider instance.
        """
        self.providers[provider_id] = provider
        logger.info(f"Registered provider: {provider_id}")
    
    def get_provider(self, provider_id: str) -> Optional[ModelProvider]:
        """
        Get a model provider by ID.
        
        Args:
            provider_id: The ID of the provider.
            
        Returns:
            The provider instance, or None if not found.
        """
        return self.providers.get(provider_id)
    
    def list_providers(self) -> List[str]:
        """
        List all registered providers.
        
        Returns:
            A list of provider IDs.
        """
        return list(self.providers.keys())
    
    async def register_model(
        self,
        model_id: str,
        provider_id: str,
        model_type: str,
        parameters: Dict[str, Any] = None,
        is_default: bool = False,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """
        Register a model.
        
        Args:
            model_id: The ID of the model.
            provider_id: The ID of the provider.
            model_type: The type of the model (text, embedding, image, multimodal).
            parameters: Default parameters for the model.
            is_default: Whether this is the default model for its type.
            is_active: Whether the model is active.
            
        Returns:
            The registered model information.
        """
        # Get provider
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider not found: {provider_id}")
        
        # Get model info
        try:
            model_info = await provider.get_model_info(model_id)
        except Exception as e:
            logger.warning(f"Error getting model info for {model_id}: {str(e)}")
            model_info = {
                "id": model_id,
                "provider": provider_id,
            }
        
        # Create model entry
        model_entry = {
            "id": model_id,
            "provider": provider_id,
            "type": model_type,
            "parameters": parameters or {},
            "is_default": is_default,
            "is_active": is_active,
            "info": model_info,
        }
        
        # Register model
        self.models[model_id] = model_entry
        
        # Set as default if specified
        if is_default:
            self.set_default_model(model_type, model_id)
        
        logger.info(f"Registered model: {model_id} (provider: {provider_id}, type: {model_type})")
        
        return model_entry
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a model by ID.
        
        Args:
            model_id: The ID of the model.
            
        Returns:
            The model information, or None if not found.
        """
        return self.models.get(model_id)
    
    def list_models(
        self,
        provider_id: Optional[str] = None,
        model_type: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        List registered models.
        
        Args:
            provider_id: Filter by provider ID.
            model_type: Filter by model type.
            active_only: Only include active models.
            
        Returns:
            A list of model information.
        """
        models = list(self.models.values())
        
        # Apply filters
        if provider_id:
            models = [m for m in models if m["provider"] == provider_id]
        
        if model_type:
            models = [m for m in models if m["type"] == model_type]
        
        if active_only:
            models = [m for m in models if m["is_active"]]
        
        return models
    
    def set_default_model(self, model_type: str, model_id: str) -> None:
        """
        Set the default model for a type.
        
        Args:
            model_type: The type of the model.
            model_id: The ID of the model.
        """
        if model_type not in self.default_models:
            raise ValueError(f"Invalid model type: {model_type}")
        
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        # Update default model
        self.default_models[model_type] = model_id
        
        # Update is_default flag for all models of this type
        for mid, model in self.models.items():
            if model["type"] == model_type:
                model["is_default"] = (mid == model_id)
        
        logger.info(f"Set default {model_type} model to {model_id}")
    
    def get_default_model(self, model_type: str) -> Optional[str]:
        """
        Get the default model for a type.
        
        Args:
            model_type: The type of the model.
            
        Returns:
            The ID of the default model, or None if not set.
        """
        if model_type not in self.default_models:
            raise ValueError(f"Invalid model type: {model_type}")
        
        return self.default_models[model_type]
    
    async def generate_text(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using a model.
        
        Args:
            prompt: The prompt to generate text from.
            model_id: The ID of the model to use. If not provided, the default text model is used.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A dictionary containing the generated text and metadata.
        """
        # Get model ID
        if not model_id:
            model_id = self.get_default_model("text")
            if not model_id:
                raise ValueError("No default text model set")
        
        # Get model
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        # Get provider
        provider = self.get_provider(model["provider"])
        if not provider:
            raise ValueError(f"Provider not found: {model['provider']}")
        
        # Merge parameters
        params = {**model["parameters"], **kwargs}
        
        # Generate text
        result = await provider.generate_text(prompt, model_id, **params)
        
        return result
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model_id: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings using a model.
        
        Args:
            texts: The texts to generate embeddings for.
            model_id: The ID of the model to use. If not provided, the default embedding model is used.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embeddings, one for each input text.
        """
        # Get model ID
        if not model_id:
            model_id = self.get_default_model("embedding")
            if not model_id:
                raise ValueError("No default embedding model set")
        
        # Get model
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        # Get provider
        provider = self.get_provider(model["provider"])
        if not provider:
            raise ValueError(f"Provider not found: {model['provider']}")
        
        # Merge parameters
        params = {**model["parameters"], **kwargs}
        
        # Generate embeddings
        result = await provider.generate_embeddings(texts, model_id, **params)
        
        return result

