import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.model_providers import ModelProvider
from app.core.model_manager import ModelRegistry

logger = logging.getLogger(__name__)
router = APIRouter()

# Global model registry
model_registry = ModelRegistry()

# Models
class ProviderBase(BaseModel):
    name: str
    provider_type: str
    config: Dict[str, Any] = {}

class ProviderCreate(ProviderBase):
    pass

class Provider(ProviderBase):
    id: str
    status: str = "active"

class ModelBase(BaseModel):
    name: str
    provider_id: str
    model_id: str
    model_type: str = "text"
    parameters: Dict[str, Any] = {}
    is_active: bool = True
    is_default: bool = False

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: str
    info: Dict[str, Any] = {}

class ModelAssignmentBase(BaseModel):
    agent_id: str
    model_id: str
    fallback_model_id: Optional[str] = None

class ModelAssignmentCreate(ModelAssignmentBase):
    pass

class ModelAssignment(ModelAssignmentBase):
    id: str

class ModelTestRequest(BaseModel):
    model_id: str
    prompt: str
    parameters: Dict[str, Any] = {}

class ModelTestResponse(BaseModel):
    result: Dict[str, Any]
    execution_time: float
    success: bool
    error: Optional[str] = None

# In-memory storage (replace with database in production)
providers_db: Dict[str, Dict[str, Any]] = {}
models_db: Dict[str, Dict[str, Any]] = {}
assignments_db: Dict[str, Dict[str, Any]] = {}

# Endpoints
@router.get("/providers", response_model=List[Provider])
async def get_providers():
    """
    Get all model providers.
    """
    return list(providers_db.values())

@router.post("/providers", response_model=Provider)
async def create_provider(provider: ProviderCreate):
    """
    Create a new model provider.
    """
    # Generate ID
    provider_id = f"{provider.provider_type}_{len(providers_db) + 1}"
    
    # Create provider object
    provider_obj = {
        **provider.dict(),
        "id": provider_id,
        "status": "active",
    }
    
    # Store provider
    providers_db[provider_id] = provider_obj
    
    # Initialize provider
    try:
        await initialize_provider(provider_obj)
    except Exception as e:
        logger.error(f"Error initializing provider {provider_id}: {str(e)}")
        provider_obj["status"] = "error"
        provider_obj["error"] = str(e)
    
    return provider_obj

@router.get("/providers/{provider_id}", response_model=Provider)
async def get_provider(provider_id: str):
    """
    Get a specific provider by ID.
    """
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return providers_db[provider_id]

@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    """
    Delete a provider.
    """
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Delete provider
    del providers_db[provider_id]
    
    # Delete associated models
    models_to_delete = [mid for mid, model in models_db.items() if model["provider_id"] == provider_id]
    for model_id in models_to_delete:
        del models_db[model_id]
    
    return {"status": "success", "message": "Provider deleted"}

@router.get("/models", response_model=List[Model])
async def get_models(
    provider_id: Optional[str] = None,
    model_type: Optional[str] = None,
    active_only: bool = True,
):
    """
    Get all models with optional filtering.
    """
    filtered_models = list(models_db.values())
    
    # Apply filters
    if provider_id:
        filtered_models = [m for m in filtered_models if m["provider_id"] == provider_id]
    
    if model_type:
        filtered_models = [m for m in filtered_models if m["model_type"] == model_type]
    
    if active_only:
        filtered_models = [m for m in filtered_models if m["is_active"]]
    
    return filtered_models

@router.post("/models", response_model=Model)
async def create_model(model: ModelCreate):
    """
    Create a new model.
    """
    # Check if provider exists
    if model.provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Generate ID
    model_id = f"{model.provider_id}_{model.model_id}"
    
    # Create model object
    model_obj = {
        **model.dict(),
        "id": model_id,
        "info": {},
    }
    
    # Store model
    models_db[model_id] = model_obj
    
    # Initialize model
    try:
        await initialize_model(model_obj)
    except Exception as e:
        logger.error(f"Error initializing model {model_id}: {str(e)}")
        model_obj["info"]["error"] = str(e)
    
    return model_obj

@router.get("/models/{model_id}", response_model=Model)
async def get_model(model_id: str):
    """
    Get a specific model by ID.
    """
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return models_db[model_id]

@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """
    Delete a model.
    """
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Delete model
    del models_db[model_id]
    
    # Delete associated assignments
    assignments_to_delete = [aid for aid, assignment in assignments_db.items() if assignment["model_id"] == model_id]
    for assignment_id in assignments_to_delete:
        del assignments_db[assignment_id]
    
    return {"status": "success", "message": "Model deleted"}

@router.post("/models/{model_id}/test", response_model=ModelTestResponse)
async def test_model(model_id: str, test_request: ModelTestRequest):
    """
    Test a model with a prompt.
    """
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Get model
    model = models_db[model_id]
    
    # Get provider
    provider_id = model["provider_id"]
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    try:
        # Get provider instance
        provider_instance = model_registry.get_provider(provider_id)
        if not provider_instance:
            raise ValueError(f"Provider instance not found: {provider_id}")
        
        # Merge parameters
        params = {**model["parameters"], **test_request.parameters}
        
        # Start timer
        import time
        start_time = time.time()
        
        # Generate text
        result = await provider_instance.generate_text(
            test_request.prompt,
            model["model_id"],
            **params
        )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        return {
            "result": result,
            "execution_time": execution_time,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Error testing model {model_id}: {str(e)}")
        return {
            "result": {},
            "execution_time": 0,
            "success": False,
            "error": str(e),
        }

@router.get("/assignments", response_model=List[ModelAssignment])
async def get_assignments(
    agent_id: Optional[str] = None,
    model_id: Optional[str] = None,
):
    """
    Get all model assignments with optional filtering.
    """
    filtered_assignments = list(assignments_db.values())
    
    # Apply filters
    if agent_id:
        filtered_assignments = [a for a in filtered_assignments if a["agent_id"] == agent_id]
    
    if model_id:
        filtered_assignments = [a for a in filtered_assignments if a["model_id"] == model_id]
    
    return filtered_assignments

@router.post("/assignments", response_model=ModelAssignment)
async def create_assignment(assignment: ModelAssignmentCreate):
    """
    Create a new model assignment.
    """
    # Check if model exists
    if assignment.model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Check if fallback model exists
    if assignment.fallback_model_id and assignment.fallback_model_id not in models_db:
        raise HTTPException(status_code=404, detail="Fallback model not found")
    
    # Generate ID
    assignment_id = f"{assignment.agent_id}_{assignment.model_id}"
    
    # Create assignment object
    assignment_obj = {
        **assignment.dict(),
        "id": assignment_id,
    }
    
    # Store assignment
    assignments_db[assignment_id] = assignment_obj
    
    return assignment_obj

@router.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: str):
    """
    Delete a model assignment.
    """
    if assignment_id not in assignments_db:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Delete assignment
    del assignments_db[assignment_id]
    
    return {"status": "success", "message": "Assignment deleted"}

# Helper functions
async def initialize_provider(provider: Dict[str, Any]) -> None:
    """
    Initialize a provider.
    
    Args:
        provider: The provider information.
    """
    provider_type = provider["provider_type"]
    provider_id = provider["id"]
    config = provider["config"]
    
    try:
        # Create provider instance
        if provider_type == "openai":
            from app.core.model_providers import OpenAIProvider
            provider_instance = OpenAIProvider(
                api_key=config.get("api_key", ""),
                base_url=config.get("base_url", "https://api.openai.com/v1"),
                timeout=config.get("timeout", 60),
            )
        elif provider_type == "gemini":
            from app.core.model_providers import GeminiProvider
            provider_instance = GeminiProvider(
                api_key=config.get("api_key", ""),
                timeout=config.get("timeout", 60),
            )
        elif provider_type == "ollama":
            from app.core.model_providers import OllamaProvider
            provider_instance = OllamaProvider(
                host=config.get("host", "localhost"),
                port=config.get("port", 11434),
                timeout=config.get("timeout", 120),
            )
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # Register provider
        model_registry.register_provider(provider_id, provider_instance)
        
        # Test connection
        models = await provider_instance.list_models()
        provider["info"] = {"models_available": len(models)}
        
    except Exception as e:
        logger.error(f"Error initializing provider {provider_id}: {str(e)}")
        provider["status"] = "error"
        provider["error"] = str(e)
        raise

async def initialize_model(model: Dict[str, Any]) -> None:
    """
    Initialize a model.
    
    Args:
        model: The model information.
    """
    model_id = model["id"]
    provider_id = model["provider_id"]
    
    try:
        # Get provider
        provider_instance = model_registry.get_provider(provider_id)
        if not provider_instance:
            raise ValueError(f"Provider instance not found: {provider_id}")
        
        # Get model info
        model_info = await provider_instance.get_model_info(model["model_id"])
        model["info"] = model_info
        
        # Register model
        await model_registry.register_model(
            model_id=model["model_id"],
            provider_id=provider_id,
            model_type=model["model_type"],
            parameters=model["parameters"],
            is_default=model["is_default"],
            is_active=model["is_active"],
        )
        
    except Exception as e:
        logger.error(f"Error initializing model {model_id}: {str(e)}")
        model["info"] = {"error": str(e)}
        raise

