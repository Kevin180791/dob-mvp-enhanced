import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import hashlib
import json

logger = logging.getLogger(__name__)

class ModelCache:
    """
    Cache for model responses to improve performance and reduce API costs.
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize the model cache.
        
        Args:
            max_size: The maximum number of items to store in the cache.
            ttl: The time-to-live for cache items in seconds.
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
    
    def _generate_key(self, model_id: str, prompt: str, **kwargs) -> str:
        """
        Generate a cache key for a model request.
        
        Args:
            model_id: The ID of the model.
            prompt: The prompt or input text.
            **kwargs: Additional parameters.
            
        Returns:
            A cache key.
        """
        # Create a dictionary with all parameters
        key_dict = {
            "model_id": model_id,
            "prompt": prompt,
            **kwargs
        }
        
        # Convert to JSON and hash
        key_json = json.dumps(key_dict, sort_keys=True)
        key_hash = hashlib.md5(key_json.encode()).hexdigest()
        
        return key_hash
    
    def get(self, model_id: str, prompt: str, **kwargs) -> Optional[Any]:
        """
        Get a cached response.
        
        Args:
            model_id: The ID of the model.
            prompt: The prompt or input text.
            **kwargs: Additional parameters.
            
        Returns:
            The cached response, or None if not found or expired.
        """
        # Generate key
        key = self._generate_key(model_id, prompt, **kwargs)
        
        # Check if key exists
        if key not in self.cache:
            return None
        
        # Get cached item
        value, timestamp = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl:
            # Remove expired item
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for model {model_id}")
        return value
    
    def set(self, model_id: str, prompt: str, value: Any, **kwargs) -> None:
        """
        Set a cached response.
        
        Args:
            model_id: The ID of the model.
            prompt: The prompt or input text.
            value: The response to cache.
            **kwargs: Additional parameters.
        """
        # Generate key
        key = self._generate_key(model_id, prompt, **kwargs)
        
        # Check if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
        
        # Store item
        self.cache[key] = (value, time.time())
        
        logger.debug(f"Cached response for model {model_id}")
    
    def clear(self) -> None:
        """
        Clear the cache.
        """
        self.cache.clear()
        logger.debug("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            A dictionary with cache statistics.
        """
        # Count expired items
        now = time.time()
        expired = sum(1 for _, timestamp in self.cache.values() if now - timestamp > self.ttl)
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "expired": expired,
            "ttl": self.ttl,
        }

