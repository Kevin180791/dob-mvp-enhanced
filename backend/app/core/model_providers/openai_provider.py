import logging
import os
from typing import Dict, List, Any, Optional, Union
import json
import httpx

from app.core.model_providers.base import ModelProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(ModelProvider):
    """
    OpenAI model provider implementation.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
    ):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: The OpenAI API key.
            base_url: The base URL for the OpenAI API.
            timeout: The timeout for API requests in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the OpenAI API.
        
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
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            
            if stop:
                payload["stop"] = stop
            
            # Add additional parameters
            for key, value in kwargs.items():
                payload[key] = value
            
            # Make API request
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract text from response
            text = result["choices"][0]["message"]["content"]
            
            return {
                "text": text,
                "model": model,
                "provider": "openai",
                "usage": result.get("usage", {}),
                "finish_reason": result["choices"][0].get("finish_reason"),
            }
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "provider": "openai",
            }
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings using the OpenAI API.
        
        Args:
            texts: The texts to generate embeddings for.
            model: The model to use.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embeddings, one for each input text.
        """
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "input": texts,
            }
            
            # Add additional parameters
            for key, value in kwargs.items():
                payload[key] = value
            
            # Make API request
            response = await self.client.post("/embeddings", json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract embeddings from response
            embeddings = [item["embedding"] for item in result["data"]]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {str(e)}")
            return []
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available OpenAI models.
        
        Returns:
            A list of available models with metadata.
        """
        try:
            # Make API request
            response = await self.client.get("/models")
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract models from response
            models = result.get("data", [])
            
            # Add provider information
            for model in models:
                model["provider"] = "openai"
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing OpenAI models: {str(e)}")
            return []
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific OpenAI model.
        
        Args:
            model: The model to get information about.
            
        Returns:
            A dictionary containing model information.
        """
        try:
            # Make API request
            response = await self.client.get(f"/models/{model}")
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Add provider information
            result["provider"] = "openai"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting OpenAI model info for {model}: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "provider": "openai",
            }

