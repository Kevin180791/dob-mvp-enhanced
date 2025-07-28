import os
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DOB-MVP"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    PORT: int = int(os.getenv("PORT", "3001"))
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Gemini settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Ollama settings
    OLLAMA_HOST: Optional[str] = os.getenv("OLLAMA_HOST")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", "11434"))
    
    # Qdrant settings
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # Neo4j settings
    NEO4J_URI: Optional[str] = os.getenv("NEO4J_URI")
    NEO4J_USERNAME: Optional[str] = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD: Optional[str] = os.getenv("NEO4J_PASSWORD")
    
    # Langfuse settings
    LANGFUSE_URL: Optional[str] = os.getenv("LANGFUSE_URL", "http://langfuse:3000")
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    
    # File storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/dob-mvp/uploads")
    
    # RFI settings
    RFI_TIMEOUT_SECONDS: int = int(os.getenv("RFI_TIMEOUT_SECONDS", "300"))
    
    # Agent settings
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))
    
    # Model settings
    DEFAULT_TEXT_MODEL: str = os.getenv("DEFAULT_TEXT_MODEL", "gpt-3.5-turbo")
    DEFAULT_EMBEDDING_MODEL: str = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

