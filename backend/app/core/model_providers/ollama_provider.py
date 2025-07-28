import logging
import os
from typing import Dict, List, Any, Optional, Union
import json
import httpx

from app.core.model_providers.base import ModelProvider

logger = logging.getLogger(__name__)

class OllamaProvider(ModelProvider):
    """
    Ollama model provider implementation for local models.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 11434,
        timeout: int = 120,
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            host: The hostname or IP address of the Ollama server.
            port: The port of the Ollama server.
            timeout: The timeout for API requests in seconds.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
        )
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "llama2",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the Ollama API.
        
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
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                }
            }
            
            # Add stop sequences if provided
            if stop:
                payload["options"]["stop"] = stop
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in ["model", "prompt", "options"]:
                    payload["options"][key] = value
            
            # Make API request
            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            return {
                "text": result.get("response", ""),
                "model": model,
                "provider": "ollama",
                "usage": {
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0),
                },
                "finish_reason": result.get("done", True) and "stop" or "length",
            }
            
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "provider": "ollama",
            }
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "llama2",
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings using the Ollama API.
        
        Args:
            texts: The texts to generate embeddings for.
            model: The model to use.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embeddings, one for each input text.
        """
        try:
            embeddings = []
            
            # Process each text separately
            for text in texts:
                # Prepare request payload
                payload = {
                    "model": model,
                    "prompt": text,
                }
                
                # Make API request
                response = await self.client.post("/api/embeddings", json=payload)
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                
                # Extract embedding from response
                embedding = result.get("embedding", [])
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings with Ollama: {str(e)}")
            return []
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available Ollama models.
        
        Returns:
            A list of available models with metadata.
        """
        try:
            # Make API request
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract models from response
            models = result.get("models", [])
            
            # Add provider information
            for model in models:
                model["provider"] = "ollama"
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing Ollama models: {str(e)}")
            return []
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific Ollama model.
        
        Args:
            model: The model to get information about.
            
        Returns:
            A dictionary containing model information.
        """
        try:
            # Make API request to show model details
            response = await self.client.post("/api/show", json={"name": model})
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Add provider information
            result["provider"] = "ollama"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Ollama model info for {model}: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "provider": "ollama",
            }

