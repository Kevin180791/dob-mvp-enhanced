import logging
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.mcp import MasterControlProgram

logger = logging.getLogger(__name__)
router = APIRouter()

# Global MCP instance
mcp = MasterControlProgram()

# Models
class RFIBase(BaseModel):
    subject: str
    description: str
    priority: str = "normal"
    category: str = "general"
    project_id: str
    requested_by: str
    due_date: Optional[datetime] = None

class RFICreate(RFIBase):
    attachments: List[str] = []

class RFIUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    response: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class RFIResponse(BaseModel):
    text: str
    generated_by: str
    confidence: float
    references: List[Dict[str, Any]] = []

class RFIAnalysis(BaseModel):
    category: str
    complexity: str
    priority: str
    estimated_response_time: str
    key_points: List[str] = []
    related_documents: List[Dict[str, Any]] = []

class RFI(RFIBase):
    id: str
    status: str = "pending"
    created_at: datetime
    updated_at: datetime
    response: Optional[RFIResponse] = None
    analysis: Optional[RFIAnalysis] = None
    attachments: List[Dict[str, Any]] = []
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

# In-memory storage for RFIs (replace with database in production)
rfi_db: Dict[str, Dict[str, Any]] = {}

# Endpoints
@router.get("/", response_model=List[RFI])
async def get_rfis(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
):
    """
    Get all RFIs with optional filtering.
    """
    filtered_rfis = list(rfi_db.values())
    
    # Apply filters
    if project_id:
        filtered_rfis = [rfi for rfi in filtered_rfis if rfi["project_id"] == project_id]
    
    if status:
        filtered_rfis = [rfi for rfi in filtered_rfis if rfi["status"] == status]
    
    # Apply pagination
    return filtered_rfis[skip:skip+limit]

@router.post("/", response_model=RFI)
async def create_rfi(
    background_tasks: BackgroundTasks,
    rfi: RFICreate,
):
    """
    Create a new RFI.
    """
    # Generate ID and timestamps
    rfi_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Create RFI object
    rfi_obj = {
        **rfi.dict(),
        "id": rfi_id,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    
    # Store RFI
    rfi_db[rfi_id] = rfi_obj
    
    # Process RFI in background
    background_tasks.add_task(process_rfi, rfi_id)
    
    return rfi_obj

@router.get("/{rfi_id}", response_model=RFI)
async def get_rfi(rfi_id: str):
    """
    Get a specific RFI by ID.
    """
    if rfi_id not in rfi_db:
        raise HTTPException(status_code=404, detail="RFI not found")
    
    return rfi_db[rfi_id]

@router.put("/{rfi_id}", response_model=RFI)
async def update_rfi(rfi_id: str, rfi_update: RFIUpdate):
    """
    Update an existing RFI.
    """
    if rfi_id not in rfi_db:
        raise HTTPException(status_code=404, detail="RFI not found")
    
    # Get current RFI
    rfi_obj = rfi_db[rfi_id]
    
    # Update fields
    update_data = rfi_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        rfi_obj[key] = value
    
    # Update timestamp
    rfi_obj["updated_at"] = datetime.now()
    
    # Store updated RFI
    rfi_db[rfi_id] = rfi_obj
    
    return rfi_obj

@router.delete("/{rfi_id}")
async def delete_rfi(rfi_id: str):
    """
    Delete an RFI.
    """
    if rfi_id not in rfi_db:
        raise HTTPException(status_code=404, detail="RFI not found")
    
    # Delete RFI
    del rfi_db[rfi_id]
    
    return {"status": "success", "message": "RFI deleted"}

@router.post("/{rfi_id}/approve", response_model=RFI)
async def approve_rfi(
    rfi_id: str,
    approved_by: str = Form(...),
):
    """
    Approve an RFI response.
    """
    if rfi_id not in rfi_db:
        raise HTTPException(status_code=404, detail="RFI not found")
    
    # Get current RFI
    rfi_obj = rfi_db[rfi_id]
    
    # Check if RFI has a response
    if not rfi_obj.get("response"):
        raise HTTPException(status_code=400, detail="RFI does not have a response to approve")
    
    # Update approval fields
    now = datetime.now()
    rfi_obj["approved_by"] = approved_by
    rfi_obj["approved_at"] = now
    rfi_obj["status"] = "approved"
    rfi_obj["updated_at"] = now
    
    # Store updated RFI
    rfi_db[rfi_id] = rfi_obj
    
    return rfi_obj

@router.post("/{rfi_id}/reject", response_model=RFI)
async def reject_rfi(
    rfi_id: str,
    feedback: str = Form(...),
):
    """
    Reject an RFI response.
    """
    if rfi_id not in rfi_db:
        raise HTTPException(status_code=404, detail="RFI not found")
    
    # Get current RFI
    rfi_obj = rfi_db[rfi_id]
    
    # Check if RFI has a response
    if not rfi_obj.get("response"):
        raise HTTPException(status_code=400, detail="RFI does not have a response to reject")
    
    # Update fields
    now = datetime.now()
    rfi_obj["status"] = "rejected"
    rfi_obj["feedback"] = feedback
    rfi_obj["updated_at"] = now
    
    # Store updated RFI
    rfi_db[rfi_id] = rfi_obj
    
    # Reprocess RFI with feedback
    background_tasks = BackgroundTasks()
    background_tasks.add_task(process_rfi, rfi_id, feedback)
    
    return rfi_obj

@router.post("/{rfi_id}/attachments")
async def add_attachment(
    rfi_id: str,
    file: UploadFile = File(...),
):
    """
    Add an attachment to an RFI.
    """
    if rfi_id not in rfi_db:
        raise HTTPException(status_code=404, detail="RFI not found")
    
    # Get current RFI
    rfi_obj = rfi_db[rfi_id]
    
    # Save file (in a real implementation, save to disk or cloud storage)
    file_id = str(uuid.uuid4())
    file_info = {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": 0,  # Would be actual file size in a real implementation
        "uploaded_at": datetime.now(),
    }
    
    # Add attachment to RFI
    if "attachments" not in rfi_obj:
        rfi_obj["attachments"] = []
    
    rfi_obj["attachments"].append(file_info)
    rfi_obj["updated_at"] = datetime.now()
    
    # Store updated RFI
    rfi_db[rfi_id] = rfi_obj
    
    return file_info

# Helper functions
async def process_rfi(rfi_id: str, feedback: Optional[str] = None):
    """
    Process an RFI using the MCP.
    """
    try:
        # Get RFI
        rfi_obj = rfi_db.get(rfi_id)
        if not rfi_obj:
            logger.error(f"RFI {rfi_id} not found for processing")
            return
        
        # Update status
        rfi_obj["status"] = "processing"
        rfi_obj["updated_at"] = datetime.now()
        rfi_db[rfi_id] = rfi_obj
        
        # Add feedback if provided
        if feedback:
            rfi_obj["feedback"] = feedback
        
        # Initialize MCP if needed
        if not mcp.initialized:
            await mcp.initialize_fallback()
        
        # Process RFI
        result = await mcp.process_rfi(rfi_obj)
        
        # Update RFI with results
        if "analysis" in result:
            rfi_obj["analysis"] = result["analysis"]
        
        if "response" in result:
            rfi_obj["response"] = result["response"]
        
        # Update status
        rfi_obj["status"] = "completed"
        rfi_obj["updated_at"] = datetime.now()
        
        # Store updated RFI
        rfi_db[rfi_id] = rfi_obj
        
        logger.info(f"RFI {rfi_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing RFI {rfi_id}: {str(e)}")
        
        # Update RFI with error
        if rfi_id in rfi_db:
            rfi_obj = rfi_db[rfi_id]
            rfi_obj["status"] = "error"
            rfi_obj["error"] = str(e)
            rfi_obj["updated_at"] = datetime.now()
            rfi_db[rfi_id] = rfi_obj

