import logging
import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api.api import api_router
from app.core.config import settings
from app.core.mcp import MasterControlProgram
from app.core.model_providers import OpenAIProvider, GeminiProvider, OllamaProvider
from app.core.model_manager import ModelRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DOB-MVP API",
    description="API for the Digital Operating System for Construction (DOB-MVP)",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount API router
app.include_router(api_router, prefix="/api")

# Initialize MCP
mcp = None

@app.on_event("startup")
async def startup_event():
    global mcp
    logger.info("🚀 Starting DOB-MVP Backend...")
    
    try:
        logger.info("🔧 Initializing DOB-MVP services...")
        
        # Initialize MCP
        mcp = MasterControlProgram()
        
        # Initialize model providers
        try:
            # Register model providers
            registry = ModelRegistry()
            
            # Register OpenAI provider if configured
            if settings.OPENAI_API_KEY:
                openai_provider = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                )
                registry.register_provider("openai", openai_provider)
                logger.info("✅ OpenAI provider initialized")
            else:
                logger.warning("⚠️ OpenAI API key not configured, skipping provider")
            
            # Register Gemini provider if configured
            if settings.GEMINI_API_KEY:
                gemini_provider = GeminiProvider(
                    api_key=settings.GEMINI_API_KEY,
                )
                registry.register_provider("gemini", gemini_provider)
                logger.info("✅ Gemini provider initialized")
            else:
                logger.warning("⚠️ Gemini API key not configured, skipping provider")
            
            # Register Ollama provider if configured
            if settings.OLLAMA_HOST:
                ollama_provider = OllamaProvider(
                    host=settings.OLLAMA_HOST,
                    port=settings.OLLAMA_PORT,
                )
                registry.register_provider("ollama", ollama_provider)
                logger.info("✅ Ollama provider initialized")
            else:
                logger.warning("⚠️ Ollama host not configured, skipping provider")
            
            # Initialize MCP with model registry
            mcp.initialize(model_registry=registry)
            
        except Exception as e:
            logger.warning(f"⚠️ Using fallback services (external services not available): {str(e)}")
            mcp.initialize_fallback()
        
        logger.info("✅ Services initialized in fallback/minimal mode")
        
        # Initialize database
        try:
            from app.db.session import engine
            from app.db.base import Base
            
            # Create tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database not available, continuing without database: {str(e)}")
        
        logger.info("\n🎉 DOB-MVP Backend successfully started!")
        logger.info(f"📡 Server running on http://0.0.0.0:{settings.PORT}")
        logger.info(f"🔍 Health check: http://0.0.0.0:{settings.PORT}/health")
        logger.info(f"📊 API status: http://0.0.0.0:{settings.PORT}/api/status")
        
        # Log available endpoints
        logger.info("\nAvailable endpoints:")
        for route in app.routes:
            if hasattr(route, "methods") and route.path != "/api/openapi.json":
                for method in route.methods:
                    logger.info(f"   {method:4} {route.path}")
        
        logger.info("\n✅ Ready for frontend connection!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down DOB-MVP Backend...")
    
    # Clean up resources
    if mcp:
        await mcp.shutdown()
    
    logger.info("DOB-MVP Backend shutdown complete")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "service": "DOB-MVP Backend"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Mount static files for Swagger UI
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    logger.warning("Static directory not found, Swagger UI may not display correctly")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", settings.PORT))
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info",
    )

