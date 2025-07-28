from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class ModelProvider(Base):
    """
    Model provider database model.
    """
    __tablename__ = "model_providers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # openai, gemini, ollama
    config = Column(Text, nullable=False)  # JSON string
    status = Column(String, nullable=False, default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    models = relationship("Model", back_populates="provider", cascade="all, delete-orphan")


class Model(Base):
    """
    Model database model.
    """
    __tablename__ = "models"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider_id = Column(String, ForeignKey("model_providers.id"), nullable=False)
    model_id = Column(String, nullable=False)  # ID used by the provider
    type = Column(String, nullable=False)  # text, embedding, image, multimodal
    capabilities = Column(Text, nullable=False)  # JSON string of capabilities
    default = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    config = Column(Text, nullable=False)  # JSON string
    parameters = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("ModelProvider", back_populates="models")
    assignments = relationship("ModelAssignment", back_populates="model", cascade="all, delete-orphan")
    fallback_for = relationship(
        "ModelAssignment",
        foreign_keys="ModelAssignment.fallback_model_id",
        back_populates="fallback_model"
    )


class ModelAssignment(Base):
    """
    Model assignment database model.
    Maps agents to models.
    """
    __tablename__ = "model_assignments"
    
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    priority = Column(Integer, default=1)
    fallback_model_id = Column(String, ForeignKey("models.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model = relationship("Model", foreign_keys=[model_id], back_populates="assignments")
    fallback_model = relationship("Model", foreign_keys=[fallback_model_id], back_populates="fallback_for")


class ModelStatus(Base):
    """
    Model status database model.
    Tracks the status of models.
    """
    __tablename__ = "model_status"
    
    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    available = Column(Boolean, default=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Integer, nullable=True)  # in milliseconds
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

