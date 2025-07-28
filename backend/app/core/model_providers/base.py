from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

class ModelProvider(ABC):
    """
    Base class for model providers.
    """
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from.
            model: The model to use.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for generation.
            stop: A list of strings to stop generation at.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A dictionary containing the generated text and metadata.
        """
        pass
    
    @abstractmethod
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: The texts to generate embeddings for.
            model: The model to use.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embeddings, one for each input text.
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.
        
        Returns:
            A list of available models with metadata.
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model: The model to get information about.
            
        Returns:
            A dictionary containing model information.
        """
        pass

