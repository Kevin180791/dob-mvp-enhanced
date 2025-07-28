"""
API-Endpunkte für das multimodale RAG-System.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
import logging
import base64
import json

from app.rag.multimodal_system import MultimodalRAGSystem
from app.core.model_manager.registry import ModelRegistry
from app.api.deps import get_multimodal_rag_system, get_model_registry

router = APIRouter()
logger = logging.getLogger(__name__)

class DocumentRequest(BaseModel):
    document_id: Optional[str] = None
    project_id: str
    content: str
    document_type: str
    metadata: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    query: str
    project_id: str
    document_types: List[str] = ["text", "image", "pdf", "plan", "cad", "bim"]
    top_k: int = 5
    filters: Dict[str, Any] = {}

class MultimodalQueryRequest(BaseModel):
    query_text: str
    query_images: List[str] = []
    project_id: str
    document_types: List[str] = ["text", "image", "pdf", "plan", "cad", "bim"]
    top_k: int = 5

class PlanFeaturesRequest(BaseModel):
    document_id: Optional[str] = None
    project_id: str
    content: str
    plan_type: str
    scale: str
    discipline: str

class PlanComparisonRequest(BaseModel):
    project_id: str
    document_ids: List[str]
    comparison_type: str = "version"

@router.post("/document", response_model=Dict[str, Any])
async def process_document(
    request: DocumentRequest,
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Verarbeitet ein Dokument und extrahiert Informationen basierend auf dem Dokumenttyp.
    """
    try:
        logger.info(f"Verarbeite Dokument vom Typ {request.document_type}")
        result = multimodal_rag_system.process_document(request.dict())
        return result
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung des Dokuments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Verarbeitung des Dokuments: {str(e)}")

@router.post("/query", response_model=Dict[str, Any])
async def query_documents(
    request: QueryRequest,
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Führt eine Abfrage über verschiedene Dokumenttypen durch.
    """
    try:
        logger.info(f"Führe Abfrage durch: {request.query}")
        result = multimodal_rag_system.query_documents(request.dict())
        return result
    except Exception as e:
        logger.error(f"Fehler bei der Abfrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Abfrage: {str(e)}")

@router.post("/multimodal-query", response_model=Dict[str, Any])
async def analyze_multimodal_query(
    request: MultimodalQueryRequest,
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Analysiert eine multimodale Abfrage, die Text und Bilder enthalten kann.
    """
    try:
        logger.info(f"Analysiere multimodale Abfrage")
        result = multimodal_rag_system.analyze_multimodal_query(request.dict())
        return result
    except Exception as e:
        logger.error(f"Fehler bei der multimodalen Abfrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der multimodalen Abfrage: {str(e)}")

@router.post("/upload-document", response_model=Dict[str, Any])
async def upload_document(
    document_id: Optional[str] = Form(None),
    project_id: str = Form(...),
    document_type: str = Form(...),
    metadata: str = Form("{}"),
    file: UploadFile = File(...),
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Lädt ein Dokument hoch und verarbeitet es.
    """
    try:
        logger.info(f"Lade Dokument vom Typ {document_type} hoch")
        
        # Lese die Datei
        content = await file.read()
        
        # Kodiere den Inhalt als Base64
        content_base64 = base64.b64encode(content).decode("utf-8")
        
        # Parse die Metadaten
        metadata_dict = json.loads(metadata)
        
        # Erstelle die Anfrage
        request = {
            "document_id": document_id,
            "project_id": project_id,
            "content": content_base64,
            "document_type": document_type,
            "metadata": metadata_dict
        }
        
        # Verarbeite das Dokument
        result = multimodal_rag_system.process_document(request)
        
        return result
    except Exception as e:
        logger.error(f"Fehler beim Hochladen des Dokuments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Hochladen des Dokuments: {str(e)}")

@router.post("/extract-plan-features", response_model=Dict[str, Any])
async def extract_plan_features(
    request: PlanFeaturesRequest,
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Extrahiert Features aus einem Bauplan.
    """
    try:
        logger.info(f"Extrahiere Features aus Plan")
        result = multimodal_rag_system.extract_plan_features(request.dict())
        return result
    except Exception as e:
        logger.error(f"Fehler bei der Extraktion von Plan-Features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Extraktion von Plan-Features: {str(e)}")

@router.post("/compare-plans", response_model=Dict[str, Any])
async def compare_plans(
    request: PlanComparisonRequest,
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Vergleicht mehrere Baupläne und identifiziert Unterschiede.
    """
    try:
        logger.info(f"Vergleiche Pläne")
        result = multimodal_rag_system.compare_plans(request.dict())
        return result
    except Exception as e:
        logger.error(f"Fehler beim Vergleich von Plänen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Vergleich von Plänen: {str(e)}")

@router.post("/upload-plan", response_model=Dict[str, Any])
async def upload_plan(
    document_id: Optional[str] = Form(None),
    project_id: str = Form(...),
    plan_type: str = Form(...),
    scale: str = Form(...),
    discipline: str = Form(...),
    file: UploadFile = File(...),
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Lädt einen Bauplan hoch und extrahiert Features.
    """
    try:
        logger.info(f"Lade Bauplan hoch")
        
        # Lese die Datei
        content = await file.read()
        
        # Kodiere den Inhalt als Base64
        content_base64 = base64.b64encode(content).decode("utf-8")
        
        # Erstelle die Anfrage
        request = {
            "document_id": document_id,
            "project_id": project_id,
            "content": content_base64,
            "plan_type": plan_type,
            "scale": scale,
            "discipline": discipline
        }
        
        # Extrahiere Features aus dem Plan
        result = multimodal_rag_system.extract_plan_features(request)
        
        return result
    except Exception as e:
        logger.error(f"Fehler beim Hochladen des Plans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Hochladen des Plans: {str(e)}")

@router.post("/multimodal-upload-query", response_model=Dict[str, Any])
async def multimodal_upload_query(
    query_text: str = Form(...),
    project_id: str = Form(...),
    document_types: str = Form("[]"),
    top_k: int = Form(5),
    files: List[UploadFile] = File([]),
    multimodal_rag_system: MultimodalRAGSystem = Depends(get_multimodal_rag_system)
):
    """
    Führt eine multimodale Abfrage mit hochgeladenen Bildern durch.
    """
    try:
        logger.info(f"Führe multimodale Abfrage mit hochgeladenen Bildern durch")
        
        # Parse die Dokumenttypen
        document_types_list = json.loads(document_types)
        if not document_types_list:
            document_types_list = ["text", "image", "pdf", "plan", "cad", "bim"]
        
        # Lese die Dateien
        query_images = []
        for file in files:
            content = await file.read()
            content_base64 = base64.b64encode(content).decode("utf-8")
            query_images.append(content_base64)
        
        # Erstelle die Anfrage
        request = {
            "query_text": query_text,
            "query_images": query_images,
            "project_id": project_id,
            "document_types": document_types_list,
            "top_k": top_k
        }
        
        # Analysiere die multimodale Abfrage
        result = multimodal_rag_system.analyze_multimodal_query(request)
        
        return result
    except Exception as e:
        logger.error(f"Fehler bei der multimodalen Abfrage mit hochgeladenen Bildern: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der multimodalen Abfrage mit hochgeladenen Bildern: {str(e)}")

