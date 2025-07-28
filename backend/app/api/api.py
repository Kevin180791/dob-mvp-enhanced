"""
API-Router für das DOB-MVP.
"""
from fastapi import APIRouter

from app.api.endpoints import health, rfi, models, multimodal, workflow

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(rfi.router, prefix="/rfi", tags=["rfi"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(multimodal.router, prefix="/multimodal", tags=["multimodal"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])

@api_router.get("/status")
async def get_status():
    """
    Get the API status.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "name": "DOB-MVP API",
    }

