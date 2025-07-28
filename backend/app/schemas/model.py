from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ModelProviderBase(BaseModel):
    """
    Base schema for model provider.
    """
    name: str = Field(..., description="Provider name")
    type: str = Field(..., description="Provider type (openai, gemini, ollama)")
    config: Dict[str, Any] = Field(..., description="Provider configuration")
    status: str = Field("active", description="Provider status (active, inactive)")


class ModelProviderCreate(ModelProviderBase):
    """
    Schema for creating a model provider.
    """
    pass


class ModelProviderUpdate(BaseModel):
    """
    Schema for updating a model provider.
    """
    name: Optional[str] = Field(None, description="Provider name")
    type: Optional[str] = Field(None, description="Provider type (openai, gemini, ollama)")
    config: Optional[Dict[str, Any]] = Field(None, description="Provider configuration")
    status: Optional[str] = Field(None, description="Provider status (active, inactive)")


class ModelProviderInDB(ModelProviderBase):
    """
    Schema for model provider in database.
    """
    id: str = Field(..., description="Provider ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True


class ModelBase(BaseModel):
    """
    Base schema for model.
    """
    name: str = Field(..., description="Model name")
    provider_id: str = Field(..., description="Provider ID")
    model_id: str = Field(..., description="Model ID used by the provider")
    type: str = Field(..., description="Model type (text, embedding, image, multimodal)")
    capabilities: List[str] = Field(..., description="Model capabilities")
    default: bool = Field(False, description="Whether this is a default model")
    active: bool = Field(True, description="Whether the model is active")
    config: Dict[str, Any] = Field({}, description="Model configuration")
    parameters: Dict[str, Any] = Field(..., description="Model parameters")


class ModelCreate(ModelBase):
    """
    Schema for creating a model.
    """
    pass


class ModelUpdate(BaseModel):
    """
    Schema for updating a model.
    """
    name: Optional[str] = Field(None, description="Model name")
    provider_id: Optional[str] = Field(None, description="Provider ID")
    model_id: Optional[str] = Field(None, description="Model ID used by the provider")
    type: Optional[str] = Field(None, description="Model type (text, embedding, image, multimodal)")
    capabilities: Optional[List[str]] = Field(None, description="Model capabilities")
    default: Optional[bool] = Field(None, description="Whether this is a default model")
    active: Optional[bool] = Field(None, description="Whether the model is active")
    config: Optional[Dict[str, Any]] = Field(None, description="Model configuration")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Model parameters")


class ModelInDB(ModelBase):
    """
    Schema for model in database.
    """
    id: str = Field(..., description="Model ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True


class ModelWithProvider(ModelInDB):
    """
    Schema for model with provider information.
    """
    provider: ModelProviderInDB = Field(..., description="Provider information")


class ModelAssignmentBase(BaseModel):
    """
    Base schema for model assignment.
    """
    agent_id: str = Field(..., description="Agent ID")
    model_id: str = Field(..., description="Model ID")
    priority: int = Field(1, description="Assignment priority")
    fallback_model_id: Optional[str] = Field(None, description="Fallback model ID")


class ModelAssignmentCreate(ModelAssignmentBase):
    """
    Schema for creating a model assignment.
    """
    pass


class ModelAssignmentUpdate(BaseModel):
    """
    Schema for updating a model assignment.
    """
    model_id: Optional[str] = Field(None, description="Model ID")
    priority: Optional[int] = Field(None, description="Assignment priority")
    fallback_model_id: Optional[str] = Field(None, description="Fallback model ID")


class ModelAssignmentInDB(ModelAssignmentBase):
    """
    Schema for model assignment in database.
    """
    id: str = Field(..., description="Assignment ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True


class ModelAssignmentWithModels(ModelAssignmentInDB):
    """
    Schema for model assignment with model information.
    """
    model: ModelInDB = Field(..., description="Model information")
    fallback_model: Optional[ModelInDB] = Field(None, description="Fallback model information")


class ModelStatusBase(BaseModel):
    """
    Base schema for model status.
    """
    model_id: str = Field(..., description="Model ID")
    available: bool = Field(True, description="Whether the model is available")
    response_time: Optional[int] = Field(None, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if not available")


class ModelStatusCreate(ModelStatusBase):
    """
    Schema for creating a model status.
    """
    pass


class ModelStatusUpdate(BaseModel):
    """
    Schema for updating a model status.
    """
    available: Optional[bool] = Field(None, description="Whether the model is available")
    response_time: Optional[int] = Field(None, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if not available")


class ModelStatusInDB(ModelStatusBase):
    """
    Schema for model status in database.
    """
    id: str = Field(..., description="Status ID")
    last_checked: datetime = Field(..., description="Last check timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True


class ModelStatusWithModel(ModelStatusInDB):
    """
    Schema for model status with model information.
    """
    model: ModelInDB = Field(..., description="Model information")


class ModelTestRequest(BaseModel):
    """
    Schema for testing a model.
    """
    model_id: str = Field(..., description="Model ID to test")
    prompt: str = Field("This is a test prompt. Please respond with a short message.", description="Test prompt")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Test parameters")


class ModelTestResponse(BaseModel):
    """
    Schema for model test response.
    """
    success: bool = Field(..., description="Whether the test was successful")
    response: Optional[str] = Field(None, description="Model response")
    response_time: Optional[int] = Field(None, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if test failed")


class ModelGenerateRequest(BaseModel):
    """
    Schema for generating text with a model.
    """
    model_id: str = Field(..., description="Model ID to use")
    prompt: str = Field(..., description="Input prompt")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")


class ModelGenerateResponse(BaseModel):
    """
    Schema for model generation response.
    """
    text: str = Field(..., description="Generated text")
    model_id: str = Field(..., description="Model ID used")
    provider: str = Field(..., description="Provider used")
    response_time: int = Field(..., description="Response time in milliseconds")


class ModelEmbedRequest(BaseModel):
    """
    Schema for generating embeddings with a model.
    """
    model_id: str = Field(..., description="Model ID to use")
    text: str = Field(..., description="Input text")


class ModelEmbedResponse(BaseModel):
    """
    Schema for model embedding response.
    """
    embedding: List[float] = Field(..., description="Embedding vector")
    model_id: str = Field(..., description="Model ID used")
    provider: str = Field(..., description="Provider used")
    response_time: int = Field(..., description="Response time in milliseconds")


class CacheStats(BaseModel):
    """
    Schema for cache statistics.
    """
    enabled: bool = Field(..., description="Whether the cache is enabled")
    size: int = Field(..., description="Current cache size")
    max_size: int = Field(..., description="Maximum cache size")
    ttl: int = Field(..., description="Time-to-live in seconds")
    expired_count: int = Field(..., description="Number of expired entries")
    avg_age: float = Field(..., description="Average age of cache entries in seconds")

