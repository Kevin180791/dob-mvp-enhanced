import logging
import os
from typing import Dict, List, Any, Optional, Union
import json
import httpx

from app.core.model_providers.base import ModelProvider

logger = logging.getLogger(__name__)

class GeminiProvider(ModelProvider):
    """
    Google Gemini model provider implementation.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1",
        timeout: int = 60,
    ):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: The Google API key.
            base_url: The base URL for the Gemini API.
            timeout: The timeout for API requests in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "gemini-pro",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the Gemini API.
        
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
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 40),
                }
            }
            
            # Add stop sequences if provided
            if stop:
                payload["generationConfig"]["stopSequences"] = stop
            
            # Make API request
            url = f"/models/{model}:generateContent?key={self.api_key}"
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract text from response
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            return {
                "text": text,
                "model": model,
                "provider": "gemini",
                "usage": {
                    "prompt_tokens": result.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "completion_tokens": result.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    "total_tokens": result.get("usageMetadata", {}).get("totalTokenCount", 0),
                },
                "finish_reason": result["candidates"][0].get("finishReason", "STOP"),
            }
            
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "provider": "gemini",
            }
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "embedding-001",
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings using the Gemini API.
        
        Args:
            texts: The texts to generate embeddings for.
            model: The model to use.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embeddings, one for each input text.
        """
        try:
            embeddings = []
            
            # Process each text separately (Gemini API doesn't support batch embedding)
            for text in texts:
                # Prepare request payload
                payload = {
                    "model": f"models/{model}",
                    "content": {
                        "parts": [
                            {
                                "text": text
                            }
                        ]
                    },
                }
                
                # Make API request
                url = f"/models/{model}:embedContent?key={self.api_key}"
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                
                # Extract embedding from response
                embedding = result["embedding"]["values"]
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings with Gemini: {str(e)}")
            return []
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available Gemini models.
        
        Returns:
            A list of available models with metadata.
        """
        try:
            # Make API request
            url = f"/models?key={self.api_key}"
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract models from response
            models = result.get("models", [])
            
            # Add provider information
            for model in models:
                model["provider"] = "gemini"
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing Gemini models: {str(e)}")
            return []
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific Gemini model.
        
        Args:
            model: The model to get information about.
            
        Returns:
            A dictionary containing model information.
        """
        try:
            # Make API request
            url = f"/models/{model}?key={self.api_key}"
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Add provider information
            result["provider"] = "gemini"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Gemini model info for {model}: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "provider": "gemini",
            }

