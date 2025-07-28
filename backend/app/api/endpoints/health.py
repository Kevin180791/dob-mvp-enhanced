from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()

@router.get("")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "DOB-MVP Backend",
        "version": "1.0.0",
    }

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    """
    # Check services
    services = {
        "api": {"status": "ok"},
        "database": _check_database(),
        "rag": _check_rag(),
        "agents": _check_agents(),
    }
    
    # Determine overall status
    overall_status = "ok"
    for service, info in services.items():
        if info["status"] != "ok":
            overall_status = "degraded"
            break
    
    return {
        "status": overall_status,
        "service": "DOB-MVP Backend",
        "version": "1.0.0",
        "services": services,
    }

def _check_database() -> Dict[str, Any]:
    """
    Check database health.
    """
    try:
        # Placeholder for actual database check
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _check_rag() -> Dict[str, Any]:
    """
    Check RAG system health.
    """
    try:
        # Placeholder for actual RAG check
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _check_agents() -> Dict[str, Any]:
    """
    Check agents health.
    """
    try:
        # Placeholder for actual agents check
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

